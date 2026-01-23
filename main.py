from typing import List,Optional
from fastapi import FastAPI,Query
from config.database import execute_query
from models.models import Piazzola,PaginatedResponse
from repository.piazzoleRepo import prepared_statement_piazzole,prepared_statement_count_piazzole
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

app = FastAPI()


@app.get("/piazzole",response_model=PaginatedResponse[Piazzola])
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
    piazzole = execute_query(query_select,{**params,"limit": limit, "offset": offset})

    if piazzole is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    piazzole = [Piazzola(**row) for row in piazzole.mappings()]
    count = count_piazzole.scalar()

    result = PaginatedResponse[Piazzola]()
    result.total = count #total piazzole con paginazione
    result.content = piazzole
    result.page = page
    result.size = size
    result.pages = (result.total + size - 1) // size  # Calcolo delle pagine totali
    result.content = piazzole
    logger.info(f"Restituiti {result.total} piazzole.")
    return result