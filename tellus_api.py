from fastapi import APIRouter, Query
from typing import Any, List, Optional, Union
from config.database import execute_query
from models.models import  Deposito, ElementoAmiu, ItinerarioPercorsoPsteriore, PaginatedResponse, PiazzolaAmiu, PosterioriPercorso
from repository.depositi_repo import prepared_statement_depositi
from repository.elementi_amiu_repo import prepared_statement_elementi_amiu
from repository.itinerari_percorsi_posteriori import prepared_statement_percorsi_posteriori_aggiornata
from repository.piazzole_amiu_repo import prepared_statement_piazzole_amiu
from repository.posteriori_repo import prepared_statement_posteriori_with_count
from sqlalchemy import CursorResult
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Servizi TELLUS"])

@router.get(
    "/percorsi_p",
    response_model=Union[List[PosterioriPercorso], PaginatedResponse[PosterioriPercorso]],
    description="Restituisce la lista dei percorsi posteriori. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD)."
)
def lista_percorsi_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$")
):
    logger.info("Ricevuta richiesta GET /percorsi_p")
    listPercorsi_row: CursorResult[Any]
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"last_update": last_update}
    query_select = prepared_statement_posteriori_with_count()
    listPercorsi_row = execute_query(query_select, {**params, "limit": limit, "offset": offset})

    if listPercorsi_row is None:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []

    lista_percorsi_p = [PosterioriPercorso(**row) for row in listPercorsi_row.mappings()]
    # Query per il ritorno del risultato paginato
    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[PosterioriPercorso]()
        result.total = lista_percorsi_p[0].total_count
        result.content = lista_percorsi_p
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result

    return lista_percorsi_p

@router.get(
    "/piazzole_amiu",
    response_model=Union[List[PiazzolaAmiu], PaginatedResponse[PiazzolaAmiu]],
    description="Restituisce la lista delle piazzole amiu. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD)."
)
def lista_piazzole_amiu(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$")
):
    logger.info("Ricevuta richiesta GET /piazzole_amiu")
    piazzole_row: CursorResult[Any]
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"last_update": last_update}

    query_select = prepared_statement_piazzole_amiu()
    piazzole_row = execute_query(query_select, {**params, "limit": limit, "offset": offset})

    if piazzole_row is None:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

    ## Creazione della lista delle piazzole amiu
    lista_piazzole_paginata = [PiazzolaAmiu(**row) for row in piazzole_row.mappings()]


    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[PiazzolaAmiu]()
        result.total = lista_piazzole_paginata[0].total_count
        result.content = lista_piazzole_paginata
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_piazzole_paginata


@router.get(
    "/elementi_p",
    response_model=Union[List[ElementoAmiu], PaginatedResponse[ElementoAmiu]],
    description="Restituisce la lista delle piazzole amiu. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD)."
)
def lista_elementi_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$")
):
    logger.info("Ricevuta richiesta GET /elementi_p")
    elementi_row: CursorResult[Any]
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size


    query_select = prepared_statement_elementi_amiu()
    elementi_row = execute_query(query_select, {"last_update": last_update,"limit": limit, "offset": offset})

    if elementi_row is None:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

    ## Creazione della lista delle piazzole amiu
    lista_elementi = [ElementoAmiu(**row) for row in elementi_row.mappings()]


    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[ElementoAmiu]()
        result.total = lista_elementi[0].total_count
        result.content = lista_elementi
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_elementi


@router.get(
    "/itinerari_p",
    response_model=Union[List[ItinerarioPercorsoPsteriore], PaginatedResponse[ItinerarioPercorsoPsteriore]],
    description="Restituisce la lista degli itinerari dei percorsi dei posteriori amiu. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD)."
)
def lista_itinerari_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$")
):
    logger.info("Ricevuta richiesta GET /itinerari_p")
    itinerari_row: CursorResult[Any]
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size


    query_select = prepared_statement_percorsi_posteriori_aggiornata()
    itinerari_row = execute_query(query_select, {"last_update": last_update,"limit": limit, "offset": offset})

    if itinerari_row is None:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

    ## Creazione della lista degli itinerari amiu
    lista_itinerari = [ItinerarioPercorsoPsteriore(**row) for row in itinerari_row.mappings()]

    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[ItinerarioPercorsoPsteriore]()
        result.total = lista_itinerari[0].total_count
        result.content = lista_itinerari
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    

    return lista_itinerari


@router.get(
    "/depositi",
    response_model=Union[List[Deposito], PaginatedResponse[Deposito]],
    description="Restituisce la lista delle Unità Territoriali e delle Rimesse. Supporta la paginazione e il filtro per data di ultimo aggiornamento."
)
def lista_depositi(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD", pattern=r"^\d{8}$")
):
    logger.info("Ricevuta richiesta GET /depositi")
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    query_select = prepared_statement_depositi()
    depositi_rows = execute_query(query_select, {"last_update": last_update, "limit": limit, "offset": offset})

    if depositi_rows is None:
        logger.info("Nessun risultato ottenuto dalla query per /depositi.")
        return []

    lista_depositi_res = [Deposito(**row) for row in depositi_rows.mappings()]

    if not lista_depositi_res:
        return []

    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[Deposito]()
        result.total = lista_depositi_res[0].total_count
        result.content = lista_depositi_res
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_depositi_res

