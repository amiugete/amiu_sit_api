from fastapi import APIRouter, Query, Depends, Request
from typing import Any, List, Optional
from business.permission import check_permissions
from business.query_helpers import execute_simple_query
from config.database import DbConnection
import logging

# i prepared statement per le query al database sono definiti nei repository corrispondenti 
# alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
from repository.bilaterali_repo import pst_bilaterali_albero, pst_bilaterali, pst_percorso_dettaglio

from models.models import PercorsoDettaglio,Bilaterali_albero,Bilaterali





# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Richiede autenticazione (Bearer Token).
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).
# nel main richiamerò questi router e li inizializzo


logger = logging.getLogger(__name__)


router = APIRouter(tags=["API Percorsi Bilaterali (ID&A)"])


@router.get("/elenco_percorsi_bilaterali_tree", response_model=List[Bilaterali_albero],
            description="Recupera la lista dei percorsi bilaterali ad albero. Richiede autenticazione (Bearer Token).")
def elenco_percorsi_bilaterali_tree(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    """Endpoint per recuperare la lista dei percorsi bilaterali ad albero con autenticazione."""
    return execute_simple_query(request, pst_bilaterali_albero, Bilaterali_albero, DbConnection.SIT, {})


@router.get("/elenco_percorsi_bilaterali",
            response_model=List[Bilaterali], description="Recupera la lista dei percorsi bilaterali. Richiede autenticazione (Bearer Token).")
def elenco_percorsi_bilaterali(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    """Endpoint per recuperare la lista dei percorsi bilaterali con autenticazione."""
    return execute_simple_query(request, pst_bilaterali, Bilaterali, DbConnection.SIT, {})




@router.get("/dettagli_percorso", response_model=List[PercorsoDettaglio], 
            description="Recupera il dettaglio dei percorsi bilaterali. Richiede autenticazione (Bearer Token).")
def dettagli_percorso(
    request: Request,
    id: Optional[str] = Query(..., description="ID del percorso per filtrare i percorsi bilaterali"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    """Endpoint per recuperare i dettagli del percorso con autenticazione."""
    return execute_simple_query(request, pst_percorso_dettaglio, PercorsoDettaglio, DbConnection.SIT, {"id": id})

