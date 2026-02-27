from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Any, List, Optional
from business.permission import get_current_user, verifica_permesso_utenze
from config.database import fetch_list_by_query,fetch_one_by_query
import logging
from enum import Enum



# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.bilaterali_repo import prepared_statement_bilaterali_albero,prepared_statement_bilaterali, prepared_statement_percorso_dettaglio
from repository.utenze_repo import prepared_statement_utenze_UD_with_count,prepared_statement_utenze_UND_with_count
from repository.macro_categorie_repo import prepared_statement_macro_categorie




from config.database import fetch_list_by_query,fetch_list_by_query_mappe, fetch_list_by_query_strade



from models.models import  PaginatedResponse, PercorsoDettaglio,Utenza,Bilaterali_albero,Bilaterali





# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Richiede autenticazione (Bearer Token).
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
# nel main richiamerò questi router e li inizializzo


logger = logging.getLogger(__name__)


router = APIRouter(tags=["API Percorsi Bilaterali (ID&A)"])


@router.get("/elenco_percorsi_bilaterali_tree", response_model=List[Bilaterali_albero],
            description="Recupera la lista dei percorsi bilaterali ad albero. Richiede autenticazione (Bearer Token).")
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


@router.get("/elenco_percorsi_bilaterali",
            response_model=List[Bilaterali], description="Recupera la lista dei percorsi bilaterali. Richiede autenticazione (Bearer Token).")
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




@router.get("/dettagli_percorso", response_model=List[PercorsoDettaglio], 
            description="Recupera il dettaglio dei percorsi bilaterali. Richiede autenticazione (Bearer Token).")
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

