from fastapi import APIRouter, Query, Depends, Request
from business.permission import check_permissions
from business.query_helpers import execute_paginated_query
from business.query_helpers import execute_simple_query
from typing import Any, List, Optional, Union
from business.utility import get_route_path_from_request
from config.database import DbConnection
from models.models import  Deposito, ElementoAmiu,MezzoEkovision, ItinerarioPercorsoPsteriore, PaginatedResponse, PiazzolaAmiu, PosterioriPercorso
from repository.depositi_repo import pst_depositi
from repository.elementi_amiu_repo import pst_elementi_amiu
from repository.itinerari_percorsi_posteriori import pst_percorsi_posteriori_aggiornata
from repository.piazzole_amiu_repo import pst_piazzole_amiu
from repository.posteriori_repo import pst_posteriori
from repository.mezzi_ekovision_repo import pst_mezzi_ekovision
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
    request: Request,
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    logger.info("Ricevuta richiesta GET /piazzole_amiu")
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")   
    return execute_paginated_query(
        pst_piazzole_amiu, PiazzolaAmiu, 
        DbConnection.SIT,
        {"last_update": last_update},
        page,
        size,
        endpoint,
        default_limit=10000,
        query_with_count=None
    )



@router.get(
    "/elementi_p",
    response_model=Union[List[ElementoAmiu], PaginatedResponse[ElementoAmiu]],
    description="""Restituisce la lista delle componenti in piazzola. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). 
    Richiede autenticazione (Bearer Token)."""
)
def lista_elementi_p(
    request: Request,
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")
    return execute_paginated_query(
        pst_elementi_amiu, ElementoAmiu, DbConnection.SIT,
        {"last_update": last_update}, 
        page,
        size,
        endpoint,
        default_limit=10000,
        query_with_count=None
    )




@router.get(
    "/percorsi_p",
    response_model=Union[List[PosterioriPercorso], PaginatedResponse[PosterioriPercorso]],
    description="""Restituisce la lista dei percorsi posteriori. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). 
    Richiede autenticazione (Bearer Token)."""
)
def lista_percorsi_p(
    request: Request,
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")
    return execute_paginated_query(
        pst_posteriori, PosterioriPercorso, DbConnection.SIT,
        {"last_update": last_update}, 
        page, 
        size,
        endpoint,
        default_limit=10000,
        query_with_count=None
    )



@router.get(
    "/itinerari_p",
    response_model=Union[List[ItinerarioPercorsoPsteriore], PaginatedResponse[ItinerarioPercorsoPsteriore]],
    description="""Restituisce il dettaglio dei percorsi dei posteriori amiu. 
    Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. 
    È possibile filtrare anche per data di ultimo aggiornamento (formato YYYYMMDD). Richiede autenticazione (Bearer Token)."""
)
def lista_itinerari_p(
    request: Request,
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")
    return execute_paginated_query(
        pst_percorsi_posteriori_aggiornata, ItinerarioPercorsoPsteriore, DbConnection.SIT,
        {"last_update": last_update}, page,
        size,
        endpoint,
        default_limit=10000,
        query_with_count=None
    )

@router.get(
    "/mezzi_ekovision",
    response_model=Union[List[MezzoEkovision], PaginatedResponse[MezzoEkovision]],
    description="Restituisce la lista dei mezzi ekovision. Permette filtri opzionali e supporta la paginazione tramite i parametri 'page' e 'size'. È possibile filtrare anche per data di esecuzione prevista (formato YYYYMMDD). Richiede autenticazione (Bearer Token)."
)
def lista_mezzi_ekovision(
    request: Request,
    check_date: str = Query(..., description="Filtra per data di esecuzione prevista in formato YYYYMMDD",pattern=r"^\d{8}$"),
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint} ")
    return execute_paginated_query(
        pst_mezzi_ekovision, MezzoEkovision, DbConnection.SIT,
        {"check_date": check_date}, 
        page,
        size,
        endpoint,
        default_limit=1000,
        query_with_count=None
    )


@router.get(
    "/depositi",
    response_model=Union[List[Deposito], PaginatedResponse[Deposito]],
    description="Restituisce la lista delle Unità Territoriali e delle Rimesse. Supporta la paginazione e il filtro per data di ultimo aggiornamento. Richiede autenticazione (Bearer Token)."
)
def lista_depositi(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD", pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")
    return execute_paginated_query(
        pst_depositi, Deposito, DbConnection.SIT,
        {"last_update": last_update},
        page,
        size,
        endpoint,
        default_limit=10000,
        query_with_count=None
    )

