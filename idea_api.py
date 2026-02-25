from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Any, List, Optional, Union
from business.permission import get_current_user, verifica_permesso_utenze
from config.database import fetch_list_by_query,fetch_one_by_query

from models.models import  FasceEtaCivico, PaginatedResponse,MacroCategoria, PaginatedResponse, PaginatedGeoJSONResponse, Utenza, PercorsoDettaglio,Utenza,Bilaterali_albero
import logging
from enum import Enum



# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.civici_anagrafe_fasce_eta import prepared_statement_fasce_eta, prepared_statement_fasce_eta_with_count
from repository.bilaterali_repo import prepared_statement_bilaterali_albero,prepared_statement_bilaterali, prepared_statement_percorso_dettaglio
from repository.utenze_repo import prepared_statement_utenze_UD_with_count,prepared_statement_utenze_UND_with_count
from repository.macro_categorie_repo import prepared_statement_macro_categorie



from config.database import fetch_list_by_query,fetch_list_by_query_mappe, fetch_list_by_query_strade


# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Tutti questi endpoint richiedono autenticazione tramite Bearer Token e verificano i permessi dell'utente prima di restituire i dati.
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
# nel main richiamerò questi router e li inizializzo

class TipoUtenza(str, Enum):
    UD = "UD"
    UND = "UND"

logger = logging.getLogger(__name__)

router = APIRouter(tags=["API Percorsi Bilaterali (ID&A)"])


# Endpoint per il recupero dei layer filtrati in base a titolo mappa, livello e nome
@router.get("/macro_categorie", description="""Recupera le macro categorie TARI delle utenze del Comune di Genova.
            Richiede autenticazione (Bearer Token).""")
def macro_categorie(
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /macro_categorie")
    query_select = prepared_statement_macro_categorie()
    listaMacroCategorie = fetch_list_by_query_strade(query_select, {})
    if listaMacroCategorie is None or len(listaMacroCategorie) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listaMacroCategorie = [MacroCategoria(**row) for row in listaMacroCategorie]
    logger.info(f"Restituite {len(listaMacroCategorie)} macro categorie.")
    return listaMacroCategorie


@router.get("/utenze_tari", response_model= PaginatedResponse[Utenza],description="Recupera la lista delle utenze tari con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request", )
def lista_utenze(
    tipo: TipoUtenza = Query(..., description="Filtra per tipo di utenza (UD = Domestica o UND = Non Domestica)"),
    payload: dict[str, Any] = Depends(get_current_user),
    page: int = Query(..., ge=1, description="Numero della pagina"),
    size: int = Query(..., ge=1, le=100, description="Dimensione della pagina")
):
    """Endpoint per recuperare la lista delle utenze con autenticazione."""
    
    # Verifica dei permessi dell'utente per accedere a questo endpoint prendendo le informazioni dal payload ottenuto con get_current_user
    is_auth,msg = verifica_permesso_utenze(payload)

    if not is_auth:
        logger.warning(f"Accesso non autorizzato all'endpoint /utenze_tari per l'utente ID {payload.get('user_id')}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{msg}"
        )
    
    logger.info("Ricevuta richiesta GET /utenze_tari")
    lista_dict_utenze: List[dict] | Any = None
    list_utenze : List[Utenza] = []
    result: PaginatedResponse[Utenza] = PaginatedResponse[Utenza]()
    query_select = ''
    offset = None
    limit = None 

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size
        limit = size

    if limit is not None and offset is not None:
        if tipo == TipoUtenza.UD:
            query_select = prepared_statement_utenze_UD_with_count()
        else:
            query_select = prepared_statement_utenze_UND_with_count()

        lista_dict_utenze = fetch_list_by_query(query_select, {"limit": limit, "offset": offset})

        if lista_dict_utenze is None or len(lista_dict_utenze) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            result.content = []
            result.total = 0
            result.page = page
            result.size = size
            result.pages = 0
            return result

        list_utenze = [Utenza(**row) for row in lista_dict_utenze]
    

        utenza = tuple(ut.civico for ut in list_utenze)

        result.total = list_utenze[0].totale_record
        result.content = list_utenze
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituite {result.total} utenze.")

        logger.info(f"Restituite {len(list_utenze)} utenze.") 
        return result

    return result



@router.get("/civici/anagrafe/fasce_eta", response_model=Union[PaginatedResponse[FasceEtaCivico ], List[FasceEtaCivico]]  , description="Recupera la lista dei civici ragruppandoli per le fasce di età con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request. Richiede autenticazione (Bearer Token).")
def lista_civici_fasce_eta(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_via: Optional[int] = Query(None, description="Filtra per via"),
    cod_civico: Optional[int] = Query(None, description="Filtra per civico"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /civici/anagrafe/fasce_eta")
    listCivici: List[dict] | None
    query_select = ''
    offset = None
    limit = None 
    
    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size
    
    params = {"id_via": id_via, "cod_civico": cod_civico}
    
    if limit is not None and offset is not None:
        query_select = prepared_statement_fasce_eta_with_count()
        listCivici = fetch_list_by_query_strade(query_select, {**params, "limit": limit, "offset": offset})

        if listCivici is None or len(listCivici) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        
        listCivici = [FasceEtaCivico(**row) for row in listCivici]
        result = PaginatedResponse[FasceEtaCivico]()
        result.total = listCivici[0].total_count if listCivici else 0
        result.content = listCivici
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituiti {result.total} record.")
    else:
        query_select = prepared_statement_fasce_eta()
        listCivici = fetch_list_by_query_strade(query_select, {**params})

        if listCivici is None or len(listCivici) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        
        listCivici = [FasceEtaCivico(**row) for row in listCivici]
        logger.info(f"Restituiti {len(listCivici)} record.") 
        return listCivici
    
    return result



