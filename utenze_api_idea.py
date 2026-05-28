# qua richiamo le query delle utenze filtrate per Id&A



from fastapi import APIRouter, Query, Depends, HTTPException, status, Request
from typing import Any, List, Optional, Union
from business.permission import check_permissions, verifica_permessi_endpoint_utente
from business.utility import get_total_count_from_rows
from config.database import fetch_list_by_engine, DbConnection
from models.models import UtenzaIdea, PaginatedResponse
import logging
from enum import Enum

# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.utenze_repo import prepared_statement_utenze_UD_idea_with_count,prepared_statement_utenze_UND_idea_with_count


# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Tutti questi endpoint richiedono autenticazione tramite Bearer Token e verificano i permessi dell'utente prima di restituire i dati.
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis. Richiede autenticazione (Bearer Token).
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
# nel main richiamerò questi router e li inizializzo

class TipoUtenza(str, Enum):
    UD = "UD"
    UND = "UND"

logger = logging.getLogger(__name__)


router = APIRouter(tags=["Utenze TARI Genova per Id&A"])






@router.get("/utenze_tari_idea", response_model= PaginatedResponse[UtenzaIdea],
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
    
    # Verifica dei permessi dell'utente per accedere a questo endpoint prendendo le informazioni dal payload ottenuto con get_current_user
    is_auth,msg = verifica_permessi_endpoint_utente(payload, "/utenze_tari_idea")

    if not is_auth:
        logger.warning(f"Accesso non autorizzato all'endpoint /utenze_tari per l'utente ID {payload.get('user_id')}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{msg}"
        )
    
    logger.info("Ricevuta richiesta GET /utenze_tari")
    lista_dict_utenze: List[dict] | Any = None
    list_utenze : List[UtenzaIdea] = []
   
    result: PaginatedResponse[UtenzaIdea] = PaginatedResponse[UtenzaIdea]()
    query_select = ''
    offset = None
    limit = None 

    

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size
        limit = size

    if limit is not None and offset is not None:
        if tipo == TipoUtenza.UD:
            query_select = prepared_statement_utenze_UD_idea_with_count()
        else:
            query_select = prepared_statement_utenze_UND_idea_with_count()

        lista_dict_utenze = fetch_list_by_engine(query_select, DbConnection.SIT, {"limit": limit, "offset": offset})

        if lista_dict_utenze is None or len(lista_dict_utenze) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            result.content = []
            result.total = 0
            result.page = page
            result.size = size
            result.pages = 0
            return result

            # estrazione total_count colonna per paginazione
        total = get_total_count_from_rows(lista_dict_utenze)

        list_utenze = [UtenzaIdea(**row) for row in lista_dict_utenze]

        result.total = total
        result.content = list_utenze
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituite {result.total} utenze.")

        logger.info(f"Restituite {len(list_utenze)} utenze.") 
        return result

    return result
