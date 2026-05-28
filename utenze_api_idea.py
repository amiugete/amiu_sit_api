# qua richiamo le query delle utenze filtrate per Id&A



from fastapi import APIRouter, Query, Depends, Request
from typing import Any
from business.permission import check_permissions
from business.query_helpers import execute_paginated_query
from business.utility import get_route_path_from_request
from config.database import DbConnection
from models.models import UtenzaIdea, PaginatedResponse
import logging
from enum import Enum

# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.utenze_repo import pst_utenze_UD_idea_with_count, pst_utenze_UND_idea_with_count


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
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")

    query = pst_utenze_UD_idea_with_count if tipo == TipoUtenza.UD else pst_utenze_UND_idea_with_count
    return execute_paginated_query(query, UtenzaIdea, DbConnection.SIT, {},
                                   page,
                                   size, 
                                   endpoint, 
                                   default_limit=10000, 
                                   query_with_count=None)
