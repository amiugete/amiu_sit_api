from fastapi import APIRouter, Form, HTTPException, status #, Query, Depends
from config.database import fetch_one_by_query
from models.models import User,UserRoles
from repository.users_repo import check_user_db, get_user_roles
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from config.ldap_amiu import verifica_utente_amiu_LDAP
from config.jwt_token_config import create_access_token


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

router = APIRouter()

################################ SERVIZIO COMMENTATO COMPRENSIVO DELL'OGGETTO PROGETTATO PER IL GRANT TYPE CHE CONTIENE ANCHE SCOPE CLIENT_ID CHE AL MOMENTO NON SERVONO ##########################################
# @router.post("/token", description="Genera un token JWT per autenticare")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     """Endpoint per l'autenticazione e la generazione del token JWT"""
#     username = form_data.username
#     password = form_data.password
#     logger.info(f"Ricevuta richiesta di login per l'utente {username}")

#     ## Verifica lDAP#####################
#     is_authenticated, msg = verifica_utente_amiu_LDAP(username, password)
#     if not is_authenticated:
#         logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenziali non valide",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     ############### VErifica presenza utente nel database #######################
#     user_query = check_user_db(username)

#     try:
#         user_record = fetch_one_by_query(user_query, {"name": username})
#         if not user_record:
#             logger.warning(f"Utente {username} non trovato nel database.")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Utente non trovato",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#     except Exception as e:
#         logger.error(f"Errore durante la verifica dell'utente {username} nel database: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Errore utente non trovato",
#         )    

    
#     # Creazione dell'oggetto User con i dati recuperati dal database per inserimento parametri nel token JWT
#     user = User(**user_record)

#     # Una volta ottenuto l'utente verifico se ha il permesso per l'utenze e lo aggiungo al token come parametro per poterlo utilizzare nei servizi che richiedono questo permesso specifico####
#     # Per eventuali futuri permessi, si potrebbe implementare una logica simile per aggiungere altri parametri al token in base ai permessi dell'utente, in modo da avere un token più ricco di informazioni sui privilegi dell'utente.
#     user_roles_query = get_user_roles()
#     utente_role = fetch_one_by_query(user_roles_query, {"id_user": user.id_user})
#     utente_role = UserRoles(**utente_role) if utente_role else None
#     utenze_param = {"utenze": utente_role.utenze if utente_role is not None and utente_role.utenze else False}
#     ########################################################
#     try:
#         access_token = create_access_token(data={"sub": username, "user_id": user.id_user, "email": user.email, "role": user.role_name,**utenze_param})
#         logger.info(f"Utente {username} autenticato con successo.")
#     except Exception as e:
#         logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Utente non autorizzato",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", description="Genera un token JWT per autenticare")
async def login( username: str = Form(...), password: str = Form(...)):
    """Endpoint per l'autenticazione e la generazione del token JWT"""
    logger.info(f"Ricevuta richiesta di login per l'utente {username}")

    ## Verifica lDAP#####################
    is_authenticated, msg = verifica_utente_amiu_LDAP(username, password)
    if not is_authenticated:
        logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    ############### VErifica presenza utente nel database #######################
    user_query = check_user_db(username)

    try:
        user_record = fetch_one_by_query(user_query, {"name": username})
        if not user_record:
            logger.warning(f"Utente {username} non trovato nel database.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non trovato",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Errore durante la verifica dell'utente {username} nel database: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Errore utente non trovato",
        )    

    
    # Creazione dell'oggetto User con i dati recuperati dal database per inserimento parametri nel token JWT
    user = User(**user_record)

    # Una volta ottenuto l'utente verifico se ha il permesso per l'utenze e lo aggiungo al token come parametro per poterlo utilizzare nei servizi che richiedono questo permesso specifico####
    # Per eventuali futuri permessi, si potrebbe implementare una logica simile per aggiungere altri parametri al token in base ai permessi dell'utente, in modo da avere un token più ricco di informazioni sui privilegi dell'utente.
    user_roles_query = get_user_roles()
    utente_role = fetch_one_by_query(user_roles_query, {"id_user": user.id_user})
    utente_role = UserRoles(**utente_role) if utente_role else None
    utenze_param = {"utenze": utente_role.utenze if utente_role is not None and utente_role.utenze else False}
    ########################################################
    try:
        access_token = create_access_token(data={"sub": username, "user_id": user.id_user, "email": user.email, "role": user.role_name,**utenze_param})
        logger.info(f"Utente {username} autenticato con successo.")
    except Exception as e:
        logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non autorizzato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}
