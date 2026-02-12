from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Any, List, Optional
from business.permission import get_current_user, verifica_permesso_utenze
from config.database import fetch_list_by_query,fetch_one_by_query
from models.models import  PaginatedResponse, PercorsoDettaglio,Utenza,Bilaterali_albero,Bilaterali
from repository.bilaterali_repo import prepared_statement_bilaterali_albero,prepared_statement_bilaterali, prepared_statement_percorso_dettaglio
from repository.utenze_repo import prepared_statement_utenze_UD_with_count,prepared_statement_utenze_UND_with_count
import logging
from enum import Enum


# I servizi in alcuni casi restituiscono liste potenzialmente molto grandi, per questo motivo è stata implementata la paginazione.per
# per vedere un esempio di implementazione della paginazione si può guardare l'endpoint /utenze_tari che restituisce la lista delle utenze tari con i relativi filtri e parametri di paginazione. 


class TipoUtenza(str, Enum):
    UD = "UD"
    UND = "UND"

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Servizi IDEA"])

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

        result.total = list_utenze[0].totale_record
        result.content = list_utenze
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituite {result.total} utenze.")

        logger.info(f"Restituite {len(list_utenze)} utenze.") 
        return result

    return result

@router.get("/elenco_percorsi_bilaterali_tree", response_model=List[Bilaterali_albero], description="Recupera la lista dei percorsi bilaterali ad albero")
def elenco_percorsi_bilaterali_tree(
    payload: dict[str, Any] = Depends(get_current_user)
):
    """Endpoint per recuperare la lista dei percorsi bilaterali ad albero con autenticazione."""
    
    logger.info("Ricevuta richiesta GET /elenco_percorsi_bilaterali_tree")

    query_select = prepared_statement_bilaterali_albero()
    list_bilaterali_albero = fetch_list_by_query(query_select, {})

    if list_bilaterali_albero is None or len(list_bilaterali_albero) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    list_bilaterali_albero = [Bilaterali_albero(**row) for row in list_bilaterali_albero]
    logger.info(f"Restituiti {len(list_bilaterali_albero)} percorsi bilaterali ad albero.")
    return list_bilaterali_albero


@router.get("/elenco_percorsi_bilaterali", response_model=List[Bilaterali], description="Recupera la lista dei percorsi bilaterali")
def elenco_percorsi_bilaterali(
    payload: dict[str, Any] = Depends(get_current_user)
):
    """Endpoint per recuperare la lista dei percorsi bilaterali con autenticazione."""
      
    logger.info("Ricevuta richiesta GET /elenco_percorsi_bilaterali")

    query_select = prepared_statement_bilaterali()
    list_bilaterali = fetch_list_by_query(query_select, {})

    if list_bilaterali is None or len(list_bilaterali) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    list_bilaterali = [Bilaterali(**row) for row in list_bilaterali]
    logger.info(f"Restituiti {len(list_bilaterali)} percorsi bilaterali.")
    return list_bilaterali

@router.get("/dettagli_percorso", response_model=List[PercorsoDettaglio], description="Recupera la lista dei percorsi bilaterali")
def dettagli_percorso(
    id: Optional[str] = Query(..., description="ID del percorso per filtrare i percorsi bilaterali"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    """Endpoint per recuperare i dettagli del percorso con autenticazione."""
    
    logger.info("Ricevuta richiesta GET /dettagli_percorso")
    query_select = prepared_statement_percorso_dettaglio()
    dettaglio_list = fetch_list_by_query(query_select, {"id": id})

    if dettaglio_list is None or len(dettaglio_list) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    
    dettaglio_list = [PercorsoDettaglio(**row) for row in dettaglio_list]
    logger.info(f"Restituiti {len(dettaglio_list)} dettagli percorso.")

    return dettaglio_list

