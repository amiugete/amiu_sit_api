from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Any, List, Optional
from business.permission import get_current_user, verifica_permesso_utenze
from config.database import fetch_list_by_query,fetch_one_by_query
from models.models import  PaginatedResponse, PercorsoDettaglio,Utenza,Bilaterali_albero,Bilaterali
import logging
from enum import Enum


# database
from config.database import fetch_list_by_query,fetch_list_by_query_mappe



# models
from models.models import  GeoJSNONModel,LayerFilterResponse, MacroCategoria, Mappa, Municipio, MyFutureModel, Piazzola, PaginatedResponse, PaginatedGeoJSONResponse, Via, Comune, Civico, Quartiere, Ambito, PointOfInterest


# repository
from repository.layer_filter_repo import get_layer_filter_query
from repository.mappe_repo import prepared_statement_mappe



from sqlalchemy import CursorResult



logger = logging.getLogger(__name__)

#router = APIRouter()
router = APIRouter(tags=["Servizi per il portale Duale"])

# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Richiede autenticazione (Bearer Token).
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).

# nel main richiamerò questi router e li inizializzo

@router.get("/mappe", description="Recupera le mappe disponibili. Richiede autenticazione (Bearer Token).")
def mappe(
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /mappe")
    query_select = prepared_statement_mappe()
    listaMappe = fetch_list_by_query_mappe(query_select, {})
    if listaMappe is None or len(listaMappe) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listaMappe = [Mappa(**row) for row in listaMappe]
    logger.info(f"Restituite {len(listaMappe)} mappe.")
    return listaMappe




class LivelloFiltro(str, Enum):
    ambito = "ambito"
    comune = "comune"
    municipio = "municipio"

@router.get(
    "/layer_filter",
    response_model=List[LayerFilterResponse],
    description="Recupera i layer filtrati in base a titolo mappa, livello e nome. Richiede autenticazione (Bearer Token)."
)
def get_layer_filter(
    t: str = Query(..., description="Titolo della mappa"), 
    l: LivelloFiltro = Query(..., description="Livello del filtro"),
    n: str = Query(..., description="Nome da usare nel filtro"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info(f"Ricevuta richiesta GET /layer_filter con t={t}, l={l.value}, n={n}")
    
    try:
        query = get_layer_filter_query(level=l.value)
    except ValueError as e:
        # Questo errore viene sollevato dalla funzione del repository se il livello è invalido
        raise HTTPException(status_code=400, detail=str(e))

    # In linea con il codice PHP, non aggiungo wildcard. L'utente deve fornirli se necessario.
    params = {"title": t, "name": n}

    layer_rows = fetch_list_by_query(query, params)
    
    if layer_rows is None or len(layer_rows) == 0:
        logger.info(f"Nessun risultato ottenuto dalla query per /layer_filter con parametri t={t}, l={l.value}, n={n}")
        return []

    result_list = [LayerFilterResponse(**row) for row in layer_rows]

    logger.info(f"Restituiti {len(result_list)} risultati per il filtro layer.")
    return result_list