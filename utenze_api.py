from fastapi import APIRouter, Query, Depends,Request
from typing import Any, List, Optional, Union
from business.permission import check_permissions
from business.query_helpers import execute_simple_query, execute_paginated_query

from models.models import UtenzeDomestichePerCivico, UtenzeNonDomestichePerCivico,FasceEtaCivico, PaginatedResponse, MacroCategoria, Utenza
import logging
from enum import Enum

# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.civici_anagrafe_fasce_eta import  pst_fasce_eta_with_count
from repository.utenze_repo import pst_utenze_UD_with_count, pst_utenze_UND_with_count, pst_utenze_domestiche_per_civico, pst_utenze_domestiche_per_civico_total_count, pst_utenze_non_domestiche_per_civico, pst_utenze_non_domestiche_per_civico_total_count
from repository.macro_categorie_repo import pst_macro_categorie

# Per la scelta del database da utilizzare per ogni query, utilizzo DbConnection definito in config/database.py, che contiene i nomi dei database configurati in config/database.py. In questo modo, se in futuro dovessi cambiare il database o aggiungerne uno nuovo, basterà modificare la configurazione senza dover modificare le query nei repository o le chiamate a queste query negli endpoint.
from config.database import fetch_list_by_engine, fetch_count_by_engine, DbConnection


# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Tutti questi endpoint richiedono autenticazione tramite Bearer Token e verificano i permessi dell'utente prima di restituire i dati.
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis. Richiede autenticazione (Bearer Token).
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
# nel main richiamerò questi router e li inizializzo

class TipoUtenza(str, Enum):
    UD = "UD"
    UND = "UND"

logger = logging.getLogger(__name__)


router = APIRouter()


# Endpoint per il recupero dei layer filtrati in base a titolo mappa, livello e nome
@router.get("/macro_categorie", description="""Recupera le macro categorie TARI delle utenze del Comune di Genova.
            Richiede autenticazione (Bearer Token).""")
def macro_categorie(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(request, pst_macro_categorie, MacroCategoria, DbConnection.STRADE, {})


@router.get("/utenze_tari", response_model= PaginatedResponse[Utenza],
                        description="""Recupera la lista delle utenze tari con filtri opzionali .
                            Paginazione opzionale gestita tramite parametri page e size nella request.
                            Richiede autenticazione (Bearer Token).
                            Per motivi di privacy l'acceso è consentito solo agli utenti con permessi specifici per accedere a questo endpoint, altrimenti viene restituito un errore 403 Forbidden.""")
def lista_utenze( 
    request: Request,
    tipo: TipoUtenza = Query(..., description="Filtra per tipo di utenza (UD = Domestica o UND = Non Domestica)"),
    payload: dict[str, Any] = Depends(check_permissions),
    page: int = Query(..., ge=1, description="Numero della pagina"),
    size: int = Query(..., ge=1, le=1000, description="Dimensione della pagina")
):
    """Endpoint per recuperare la lista delle utenze con autenticazione."""
    query = pst_utenze_UD_with_count if tipo == TipoUtenza.UD else pst_utenze_UND_with_count
    return execute_paginated_query(request,
                                   query,
                                   Utenza,
                                   DbConnection.SIT, 
                                   {},
                                   page,
                                   size
                                   )

@router.get(
    "/civici/utenze_tari",
    response_model=PaginatedResponse[Union[UtenzeDomestichePerCivico, UtenzeNonDomestichePerCivico]],
    description="""Recupera il numero delle utenze tari. Si richiede la scelta fra utenze domestiche e non domestiche (UD = Domestica, UND = Non Domestica).
    Paginazione opzionale gestita tramite parametri page e size nella request.
    Se non specificati vengono restituiti tutti i risultati con limite di 10000 risultati.
    Richiede autenticazione (Bearer Token)."""
)
def lista_utenze_civici(
    request: Request,
    tipo: TipoUtenza = Query(..., description="Filtra per tipo di utenza (UD = Domestica o UND = Non Domestica)"),
    payload: dict[str, Any] = Depends(check_permissions),
    id_via: Optional[int] = Query(None, description="Filtra per via"),
    cod_civico: Optional[int] = Query(None, description="Filtra per civico"),
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=1000, description="Dimensione della pagina")
):
    """Endpoint per recuperare la lista delle utenze con autenticazione."""

    lista_dict_utenze: List[dict] | Any = None
    result: PaginatedResponse[Any] = PaginatedResponse[Any]()
    query_select = ''
    offset = None
    limit = None

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size
        limit = size
    
    if tipo == TipoUtenza.UD:
        query_select = pst_utenze_domestiche_per_civico
        if limit is not None and offset is not None:
            totale_pagination_query = pst_utenze_domestiche_per_civico_total_count
            total_count = fetch_count_by_engine(totale_pagination_query, DbConnection.STRADE, {"id_via": id_via, "cod_civico": cod_civico})
            if total_count is not None:
                result.total = total_count
    else:
        query_select = pst_utenze_non_domestiche_per_civico
        if limit is not None and offset is not None:
            totale_pagination_query = pst_utenze_non_domestiche_per_civico_total_count
            total_count = fetch_count_by_engine(totale_pagination_query, DbConnection.STRADE, {"id_via": id_via, "cod_civico": cod_civico})
            if total_count is not None:
                result.total = total_count

    lista_dict_utenze = fetch_list_by_engine(query_select, DbConnection.STRADE, {"limit": limit,
                                                                  "offset": offset, 
                                                                  "id_via": id_via,
                                                                  "cod_civico": cod_civico})

    if lista_dict_utenze is None or len(lista_dict_utenze) == 0:
        logger.info(f"Nessun risultato ottenuto dalla query per endpoint {request.url.path}.")
        result.content = []
        result.total = 0
        result.page = page
        result.size = size
        result.pages = 0
        return result
    
    if tipo == TipoUtenza.UD:
        list_utenze = [UtenzeDomestichePerCivico(**row) for row in lista_dict_utenze]
    else:
        list_utenze = [UtenzeNonDomestichePerCivico(**row) for row in lista_dict_utenze]

    result.content = list_utenze
    result.page = page
    result.size = size
    result.pages = (result.total + size - 1) // size if size else 0
    logger.info(f"Restituite {result.total} utenze per endpoint {request.url.path}.")
    logger.info(f"Restituite {len(list_utenze)} utenze per endpoint {request.url.path}.")

    return result
    



@router.get("/civici/anagrafe/fasce_eta", response_model=Union[PaginatedResponse[FasceEtaCivico ], List[FasceEtaCivico]]  , description="Recupera la lista dei civici ragruppandoli per le fasce di età con filtri opzionali. Paginazione opzionale gestita tramite parametri page e size nella request. Richiede autenticazione (Bearer Token).")
def lista_civici_fasce_eta(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=1000, description="Dimensione della pagina"),
    id_via: Optional[int] = Query(None, description="Filtra per via"),
    cod_civico: Optional[int] = Query(None, description="Filtra per civico"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_fasce_eta_with_count, 
        FasceEtaCivico,
        DbConnection.STRADE,
        {"id_via": id_via, "cod_civico": cod_civico},
        page, 
        size
    )



