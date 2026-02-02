from typing import List,Optional,Union
from fastapi import FastAPI,Query,Depends, HTTPException, status
from config.database import execute_query
from models.models import  Piazzola,PaginatedResponse, User,Via,Comune,Civico,Quartiere,Ambito,PointOfInterest
from repository.vie_repo import prepared_statement_count_vie,prepared_statement_vie
from repository.piazzole_repo import prepared_statement_piazzole,prepared_statement_count_piazzole
from repository.comuni_repo import prepared_statement_comuni
from repository.civici_repo import prepared_statement_civici,prepared_statement_count_civici
from repository.quartieri_repo import prepared_statement_quartieri
from repository.ambiti_repo import prepared_statement_ambiti
from repository.point_of_interest_repo import prepared_statement_pointofinterest
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm,HTTPBearer,HTTPAuthorizationCredentials
from passlib.context import CryptContext
from config.ldap_amiu import verifica_utente_amiu_LDAP
from config.jwt_token_config import create_access_token,check_jwt_token
from repository.users_repo import check_user_db
from fastapi.openapi.utils import get_openapi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"), # Scrive su file
        logging.StreamHandler()         # Scrive su console
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# Utility per l'hashing delle password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()
# Inizializza l'app FastAPI##############################
app = FastAPI(title="API AMIU SIT", version="1.0.0", description="API per l'accesso ai dati geografici di AMIU")


# Dipendenza per ottenere l'utente corrente dal token JWT
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    # Verifica il token JWT
    token = credentials.credentials
    logger.info("Verifica del token JWT in corso...")
    logger.info(token)
    try:
        payload = check_jwt_token(token)
        logger.info(f"Token valido per l'utente {payload.get('sub')}")
    except Exception as e:
        logger.warning(f"Token non valido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

    



@app.post("/token", tags=["Autenticazione"], description="Genera un token JWT per autenticare")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint per l'autenticazione e la generazione del token JWT"""
    username = form_data.username
    password = form_data.password
    logger.info(f"Ricevuta richiesta di login per l'utente {username}")
    # Verifica le credenziali tramite LDAP
    is_authenticated, msg = verifica_utente_amiu_LDAP(username, password)

    # Se non è in Active directory, ritorna errore Credenziali non valide
    if not is_authenticated:
        logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Verifica l'esistenza dell'utente nel database
    user_query = check_user_db(username)
    user_record = execute_query(user_query, {"name": username})

    user_record = user_record.mappings().first() if user_record else None

    if not user_record:
        logger.warning(f"Utente {username} non trovato nel database.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = User(**user_record)

    try:
        access_token = create_access_token(data={"sub": username, "user_id": user.id_user, "email": user.email})
        logger.info(f"Utente {username} autenticato con successo.")
    except Exception as e:
     logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
     raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non autorizzato",
            headers={"WWW-Authenticate": "Bearer"},
        )
  
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/piazzole", response_model=Union[List[Piazzola],PaginatedResponse[Piazzola]],description="Recupera la lista delle piazzole con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request",tags=["Interazione con IDEA"])
def lista_piazzole(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    comune: Optional[int] = Query(None, description="Filtra per comune"),
    municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    via: Optional[int] = Query(None, description="Filtra per ID della via"),
    pap: Optional[int] = Query(None, ge=0, le=1, description="Filtra per PAP (1 = Sì, 0 = No)"),
):
    logger.info("Ricevuta richiesta GET /piazzole")
    #Offset a 0 di default
    offset = None
    limit = None 

    if page is not None and size is not None and  size > 0:     
        offset = (page - 1) * size
        limit = size

    params = {
        "comune": comune,
        "municipio": municipio,
        "via": via,
        "pap": pap,
        }

    # Esecuzione query di conteggio totale piazzole con filtri    
    query_count_select = prepared_statement_count_piazzole()
    count_piazzole = execute_query(query_count_select,params)


    query_select = prepared_statement_piazzole()
    listPiazzole = execute_query(query_select,{**params,"limit": limit, "offset": offset})

    if listPiazzole is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listPiazzole = [Piazzola(**row) for row in listPiazzole.mappings()]
    count = count_piazzole.scalar()


    if page is None or size is None:
        logger.info(f"Restituite {count} piazzole.")
        return listPiazzole
    
    result = PaginatedResponse[Piazzola]()
    result.total = count #total piazzole con paginazione
    result.content = listPiazzole
    result.page = page
    result.size = size
    result.pages = (result.total + size - 1) // size if size else 0  # Calcolo delle pagine totali
    result.content = listPiazzole
    logger.info(f"Restituiti {result.total} piazzole.")
    return result


@app.get("/vie", response_model=Union[List[Via], PaginatedResponse[Via]],description="Recupera la lista delle vie con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request",tags=["Interazione con IDEA"])
def lista_vie(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    comune: Optional[int] = Query(None, description="Filtra per comune")
):
    logger.info("Ricevuta richiesta GET /vie")
    
    offset = None
    limit = None 
    
    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size
    
    params = {"comune": comune}
    
    # Query di conteggio
    query_count_select = prepared_statement_count_vie()
    count_vie = execute_query(query_count_select, params)
    
    # Query principale
    query_select = prepared_statement_vie()
    listVie = execute_query(query_select, {**params, "limit": limit, "offset": offset})
    
    if listVie is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listVie = [Via(**row) for row in listVie.mappings()]
    count = count_vie.scalar()

    if page is None or size is None:
        logger.info(f"Restituite {count} vie.")
        return listVie

    listVie = PaginatedResponse[Via]()
    listVie.total = count
    listVie.content = listVie
    listVie.page = page
    listVie.size = size
    listVie.pages = (listVie.total + size - 1) // size if size else 0
    
    logger.info(f"Restituite {listVie.total} vie.")
    return listVie


@app.get("/comuni", response_model=List[Comune],tags=["Interazione con IDEA"],
         description="Recupera la lista dei comuni. Richiede un Bearer Token per l'autenticazione.")
def lista_comuni(
    payload: str = Depends(get_current_user),
    id_ambito: Optional[int] = Query(None, description="Filtra per ambito"),
    cod_istat: Optional[str] = Query(None, description="Filtra per codice ISTAT")
):
    """Endpoint per recuperare la lista dei comuni con autenticazione."""
    logger.info("Ricevuta richiesta GET /comuni")
    logger.info(f"Utente autenticato: {payload.get('sub')} (ID: {payload.get('user_id')})")


    params = {
        "id_ambito": id_ambito,
        "cod_istat": cod_istat
    }
    
    query_select = prepared_statement_comuni()
    listComuni = execute_query(query_select, params)

    if listComuni is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listComuni = [Comune(**row) for row in listComuni.mappings()]
    logger.info(f"Restituiti {len(listComuni)} comuni.")
    return listComuni


@app.get("/civici", response_model=Union[PaginatedResponse[Civico], List[Civico]], tags=["Interazione con IDEA"], description="Recupera la lista dei civici con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request")
def lista_civici(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per via")
):
    logger.info("Ricevuta richiesta GET /civici")
    
    offset = None
    limit = None 
    
    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size
    
    params = {"id_municipio": id_municipio, "id_via": id_via}
    
    # Query di conteggio
    query_count_select = prepared_statement_count_civici()
    count_civici = execute_query(query_count_select, params)
    
    # Query principale
    query_select = prepared_statement_civici()
    listCivici = execute_query(query_select, {**params, "limit": limit, "offset": offset})
    
    if listCivici is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listCivici = [Civico(**row) for row in listCivici.mappings()]
    count = count_civici.scalar()

    if page is None or size is None:
        logger.info(f"Restituiti {count} civici.")
        return listCivici

    result = PaginatedResponse[Civico]()
    result.total = count
    result.content = listCivici
    result.page = page
    result.size = size
    result.pages = (result.total + size - 1) // size if size else 0
    logger.info(f"Restituiti {result.total} civici.")
    return result


@app.get("/quartieri", response_model=List[Quartiere], description="Recupera la lista dei quartieri", tags=["Interazione con IDEA"])
def lista_quartieri(
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio")
):
    logger.info("Ricevuta richiesta GET /quartieri")
    
    params = {"id_municipio": id_municipio}
    
    query_select = prepared_statement_quartieri()
    listQuartieri = execute_query(query_select, params)
    
    if listQuartieri is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listQuartieri = [Quartiere(**row) for row in listQuartieri.mappings()]
    logger.info(f"Restituiti {len(listQuartieri)} quartieri.")
    return listQuartieri


@app.get("/ambiti", response_model=List[Ambito], description="Recupera la lista degli ambiti", tags=["Interazione con IDEA"])
def lista_ambiti():
    logger.info("Ricevuta richiesta GET /ambiti")
    
    query_select = prepared_statement_ambiti()
    listAmbiti = execute_query(query_select, {})
    
    if listAmbiti is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listAmbiti = [Ambito(**row) for row in listAmbiti.mappings()]
    logger.info(f"Restituiti {len(listAmbiti)} ambiti.")
    return listAmbiti


@app.get("/pointofinterest", response_model=List[PointOfInterest], description="Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari)", tags=["Interazione con IDEA"])
def lista_point_of_interest():
    logger.info("Ricevuta richiesta GET /point of interest")
    
    query_select = prepared_statement_pointofinterest()
    listPointOfInterest = execute_query(query_select, {})
    
    if listPointOfInterest is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    listPointOfInterest = [PointOfInterest(**row) for row in listPointOfInterest.mappings()]
    logger.info(f"Restituiti {len(listPointOfInterest)} point of interest.")
    return listPointOfInterest
