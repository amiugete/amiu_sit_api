from fastapi import APIRouter, Query,Depends
from business.permission import get_current_user
from typing import Any, List, Optional, Union
from business.utility import get_total_count_from_rows
from config.database import fetch_list_by_query
from models.models import  Deposito, ElementoAmiu,MezzoEkovision, ItinerarioPercorsoPsteriore, PaginatedResponse, PiazzolaAmiu, PosterioriPercorso
from repository.depositi_repo import prepared_statement_depositi
from repository.elementi_amiu_repo import prepared_statement_elementi_amiu
from repository.itinerari_percorsi_posteriori import prepared_statement_percorsi_posteriori_aggiornata
from repository.piazzole_amiu_repo import prepared_statement_piazzole_amiu
from repository.posteriori_repo import prepared_statement_posteriori_with_count
from repository.mezzi_ekovision_repo import prepared_statement_mezzi_ekovision
import logging


logger = logging.getLogger(__name__)

router = APIRouter(tags=["API Percorsi Posteriori (Tellus)"])



# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Tutti questi endpoint richiedono autenticazione tramite Bearer Token e verificano i permessi dell'utente prima di restituire i dati.
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).

# nel main richiamerò questi router e li inizializzo




@router.get(
    "/piazzole_amiu",
    response_model=Union[List[PiazzolaAmiu], PaginatedResponse[PiazzolaAmiu]],
    description="Restituisce la lista delle piazzole amiu. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). Richiede autenticazione (Bearer Token)."
)
def lista_piazzole_amiu(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /piazzole_amiu")
    piazzole_row: List[dict] | None
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"last_update": last_update}

    query_select = prepared_statement_piazzole_amiu()
    piazzole_row = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

    if piazzole_row is None or len(piazzole_row) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

    total = get_total_count_from_rows(piazzole_row)
    ## Creazione della lista delle piazzole amiu
    lista_piazzole_paginata = [PiazzolaAmiu(**row) for row in piazzole_row]


    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[PiazzolaAmiu]()
        result.total = total
        result.content = lista_piazzole_paginata
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_piazzole_paginata



@router.get(
    "/elementi_p",
    response_model=Union[List[ElementoAmiu], PaginatedResponse[ElementoAmiu]],
    description="""Restituisce la lista delle componenti in piazzola. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). 
    Richiede autenticazione (Bearer Token)."""
)
def lista_elementi_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /elementi_p")
    elementi_row: List[dict] | None
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size


    query_select = prepared_statement_elementi_amiu()
    elementi_row = fetch_list_by_query(query_select, {"last_update": last_update,"limit": limit, "offset": offset})

    if elementi_row is None or len(elementi_row) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []


    total = get_total_count_from_rows(elementi_row)

    ## Creazione della lista delle piazzole amiu
    lista_elementi = [ElementoAmiu(**row) for row in elementi_row]


    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[ElementoAmiu]()
        result.total = total
        result.content = lista_elementi
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_elementi




@router.get(
    "/percorsi_p",
    response_model=Union[List[PosterioriPercorso], PaginatedResponse[PosterioriPercorso]],
    description="""Restituisce la lista dei percorsi posteriori. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). 
    Richiede autenticazione (Bearer Token)."""
)
def lista_percorsi_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /percorsi_p")
    listPercorsi_row: List[dict] | None
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"last_update": last_update}
    query_select = prepared_statement_posteriori_with_count()
    listPercorsi_row = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

    if listPercorsi_row is None or len(listPercorsi_row) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    # estrazione total_count colonna per paginazione
    total = get_total_count_from_rows(listPercorsi_row)

    lista_percorsi_p = [PosterioriPercorso(**row) for row in listPercorsi_row]
    # Query per il ritorno del risultato paginato
    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[PosterioriPercorso]()
        result.total = total
        result.content = lista_percorsi_p
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result

    return lista_percorsi_p



@router.get(
    "/itinerari_p",
    response_model=Union[List[ItinerarioPercorsoPsteriore], PaginatedResponse[ItinerarioPercorsoPsteriore]],
    description="""Restituisce il dettaglio dei percorsi dei posteriori amiu. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). Richiede autenticazione (Bearer Token)."""
)
def lista_itinerari_p(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /itinerari_p")
    itinerari_row: List[dict] | None
    query_select = ''
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size


    query_select = prepared_statement_percorsi_posteriori_aggiornata()
    itinerari_row = fetch_list_by_query(query_select, {"last_update": last_update,"limit": limit, "offset": offset})

    if itinerari_row is None or len(itinerari_row) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
    # estrazione total_count colonna per paginazione
    total = get_total_count_from_rows(itinerari_row)
    ## Creazione della lista degli itinerari amiu
    lista_itinerari = [ItinerarioPercorsoPsteriore(**row) for row in itinerari_row]

    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[ItinerarioPercorsoPsteriore]()
        result.total = total
        result.content = lista_itinerari
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    

    return lista_itinerari

@router.get(
    "/mezzi_ekovision",
    response_model=Union[List[MezzoEkovision], PaginatedResponse[MezzoEkovision]],
    description="Restituisce la lista dei mezzi ekovision. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di esecuzione prevista (formato YYYYMMDD). Richiede autenticazione (Bearer Token)."
)
def lista_mezzi_ekovision(
    check_date: str = Query(..., description="Filtra per data di esecuzione prevista in formato YYYYMMDD",pattern=r"^\d{8}$"),
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /mezzi_ekovision")
    mezzi_row: List[dict] | None
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size


    query_select = prepared_statement_mezzi_ekovision()
    mezzi_row = fetch_list_by_query(query_select, {"check_date": check_date,"limit": limit, "offset": offset})

    if mezzi_row is None or len(mezzi_row) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

    # estrazione total_count colonna per paginazione
    total = get_total_count_from_rows(mezzi_row)
    ## Creazione della lista dei mezzi ekovision
    lista_mezzi = [MezzoEkovision(**row) for row in mezzi_row]

    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[MezzoEkovision]()
        result.total = total
        result.content = lista_mezzi
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result

    return lista_mezzi


@router.get(
    "/depositi",
    response_model=Union[List[Deposito], PaginatedResponse[Deposito]],
    description="Restituisce la lista delle Unità Territoriali e delle Rimesse. Supporta la paginazione e il filtro per data di ultimo aggiornamento. Richiede autenticazione (Bearer Token)."
)
def lista_depositi(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD", pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /depositi")
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    query_select = prepared_statement_depositi()
    depositi_rows = fetch_list_by_query(query_select, {"last_update": last_update, "limit": limit, "offset": offset})

    if depositi_rows is None or len(depositi_rows) == 0:
        logger.info("Nessun risultato ottenuto dalla query per /depositi.")
        return []

    # estrazione total_count colonna per paginazione
    total = get_total_count_from_rows(depositi_rows)
    lista_depositi_res = [Deposito(**row) for row in depositi_rows]

    if not lista_depositi_res:
        return []

    if page is not None and size is not None and size > 0 and page > 0:
        result = PaginatedResponse[Deposito]()
        result.total = total
        result.content = lista_depositi_res
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        return result
    
    return lista_depositi_res

