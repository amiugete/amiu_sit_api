from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Any, List, Optional, Union
from business.permission import get_current_user, verifica_permesso_utente_endpoint
from config.database import execute_query
from models.models import  PaginatedResponse, Via,Utenza
from repository.vie_repo import prepared_statement_vie, prepared_statement_vie_with_count
from repository.utenze_repo import prepared_statement_utenze_UD_with_count,prepared_statement_utenze_UND_with_count
from sqlalchemy import CursorResult
import logging
from enum import Enum

class TipoUtenza(str, Enum):
    UD = "UD"
    UND = "UND"

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

router = APIRouter(tags=["Servizi Utenze"])

@router.get("/utenze_tari", response_model= PaginatedResponse[Utenza],description="Recupera la lista delle utenze tari con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request", )
def lista_utenze(
    tipo: TipoUtenza = Query(..., description="Filtra per tipo di utenza (UD = Domestica o UND = Non Domestica)"),
    payload: dict[str, Any] = Depends(get_current_user),
    page: int = Query(..., ge=1, description="Numero della pagina"),
    size: int = Query(..., ge=1, le=100, description="Dimensione della pagina")
):
    """Endpoint per recuperare la lista delle utenze con autenticazione."""
    
    is_auth,msg =  verifica_permesso_utente_endpoint("/utenze_tari", payload.get("user_id"))

    if not is_auth:
        logger.warning(f"Accesso non autorizzato all'endpoint /utenze_tari per l'utente ID {payload.get('user_id')}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{msg}"
        )
    
    logger.info("Ricevuta richiesta GET /utenze_tari")
    cursor_Utenze: CursorResult[Any]
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

        cursor_Utenze = execute_query(query_select, {"limit": limit, "offset": offset})

        if cursor_Utenze is None or cursor_Utenze.rowcount == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            result.content = []
            result.total = 0
            result.page = page
            result.size = size
            result.pages = 0
            return result

        list_utenze = [Utenza(**row) for row in cursor_Utenze.mappings()]

        result.total = list_utenze[0].totale_record
        result.content = list_utenze
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituite {result.total} utenze.")

        logger.info(f"Restituite {len(list_utenze)} utenze.") 
        return result

    return result



