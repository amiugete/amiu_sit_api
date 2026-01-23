from typing import List,Optional,Union
from fastapi import FastAPI,Query
from config.database import execute_query
from models.models import Piazzola,PaginatedResponse,Via
from repository.vie_repo import prepared_statement_count_vie,prepared_statement_vie
from repository.piazzole_repo import prepared_statement_piazzole,prepared_statement_count_piazzole
import logging


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

# Inizializza l'app FastAPI##############################
app = FastAPI()


@app.get("/piazzole", response_model=Union[PaginatedResponse[Piazzola], List[Piazzola]])
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


@app.get("/vie", response_model=Union[PaginatedResponse[Via], List[Via]])
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