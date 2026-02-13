from fastapi import APIRouter, Query, HTTPException,Depends
from business.permission import get_current_user
from typing import Any, List, Optional, Union
from enum import Enum
from config.database import fetch_list_by_query,fetch_list_by_query_mappe
from models.models import LayerFilterResponse, Mappa, Municipio, Piazzola, PaginatedResponse, Via, Comune, Civico, Quartiere, Ambito, PointOfInterest
from repository.layer_filter_repo import get_layer_filter_query
from repository.municipi_repo import prepared_statement_municipi_genova
from repository.vie_repo import prepared_statement_vie, prepared_statement_vie_with_count
from repository.piazzole_repo import prepared_statement_piazzole, prepared_statement_piazzole_with_count
from repository.comuni_repo import prepared_statement_comuni
from repository.civici_repo import prepared_statement_civici_with_count, prepared_statement_civici
from repository.quartieri_repo import prepared_statement_quartieri
from repository.ambiti_repo import prepared_statement_ambiti
from repository.mappe_repo import prepared_statement_mappe
from repository.point_of_interest_repo import prepared_statement_pointofinterest
from sqlalchemy import CursorResult
import logging


logger = logging.getLogger(__name__)

router = APIRouter()


# Endpoint per il recupero dei layer filtrati in base a titolo mappa, livello e nome
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

@router.get("/piazzole", response_model=Union[List[Piazzola],PaginatedResponse[Piazzola]],description="Recupera la lista delle piazzole con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request. Richiede autenticazione (Bearer Token).", )
def lista_piazzole(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    comune: Optional[int] = Query(None, description="Filtra per comune"),
    municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    via: Optional[int] = Query(None, description="Filtra per ID della via"),
    pap: Optional[int] = Query(None, ge=0, le=1, description="Filtra per PAP (1 = Sì, 0 = No)"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /piazzole")
    listPiazzole: CursorResult[Any]
    query_select = ''
    offset = None
    limit = None 

    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size

    params = {"pap": pap, "via": via, "comune": comune, "municipio": municipio}

    # Query per il ritorno del risultato paginato
    if limit is not None and offset is not None:
        query_select = prepared_statement_piazzole_with_count()
        listPiazzole = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listPiazzole is None or len(listPiazzole) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

        listPiazzole = [Piazzola(**row) for row in listPiazzole]
        result = PaginatedResponse[Piazzola]()
        result.total = listPiazzole[0].total_count if listPiazzole else 0
        result.content = listPiazzole
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituiti {result.total} piazzole.")
    # Query per il ritorno del risultato non paginato
    else:
        query_select = prepared_statement_piazzole()
        listPiazzole = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listPiazzole is None or len(listPiazzole) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

        listPiazzole = [Piazzola(**row) for row in listPiazzole]
        logger.info(f"Restituiti {len(listPiazzole)} piazzole.") 
        return listPiazzole

    return result


@router.get("/vie", response_model=Union[List[Via], PaginatedResponse[Via]],description="Recupera la lista delle vie con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request. Richiede autenticazione (Bearer Token).", )
def lista_vie(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    comune: Optional[int] = Query(None, description="Filtra per comune"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /vie")
    listVie: CursorResult[Any]
    query_select = ''
    offset = None
    limit = None 

    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size

    params = {"comune": comune}

    if limit is not None and offset is not None:
        query_select = prepared_statement_vie_with_count()
        listVie = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listVie is None or len(listVie) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

        listVie = [Via(**row) for row in listVie]
        result = PaginatedResponse[Via]()
        result.total = listVie[0].total_count if listVie else 0
        result.content = listVie
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituite {result.total} vie.")
    else:
        query_select = prepared_statement_vie()
        listVie = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listVie is None or len(listVie) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

        listVie = [Via(**row) for row in listVie]
        logger.info(f"Restitute {len(listVie)} vie.") 
        return listVie

    return result

@router.get("/comuni", response_model=List[Comune],
         description="Recupera la lista dei comuni. Richiede autenticazione (Bearer Token).")
def lista_comuni(
    id_ambito: Optional[int] = Query(None, description="Filtra per ambito"),
    cod_istat: Optional[str] = Query(None, description="Filtra per codice ISTAT"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    
    """Endpoint per recuperare la lista dei comuni"""
    logger.info("Ricevuta richiesta GET /comuni")
    params = {
        "id_ambito": id_ambito,
        "cod_istat": cod_istat
    }
    query_select = prepared_statement_comuni()
    listComuni = fetch_list_by_query(query_select, params)
    if listComuni is None or len(listComuni) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listComuni = [Comune(**row) for row in listComuni]
    logger.info(f"Restituiti {len(listComuni)} comuni.")
    return listComuni


@router.get("/civici", response_model=Union[PaginatedResponse[Civico], List[Civico]]  , description="Recupera la lista dei civici con filtri opzionali e paginazione se vengono indicati i parametri page e size nella request. Richiede autenticazione (Bearer Token).")
def lista_civici(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per via"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD",pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /civici")
    listCivici: List[dict] | None
    query_select = ''
    offset = None
    limit = None 
    
    if page is not None and size is not None and size > 0:     
        offset = (page - 1) * size
        limit = size
    
    params = {"id_municipio": id_municipio, "id_via": id_via, "ins_date": last_update}
    
    if limit is not None and offset is not None:
        query_select = prepared_statement_civici_with_count()
        listCivici = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listCivici is None or len(listCivici) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        
        listCivici = [Civico(**row) for row in listCivici]
        result = PaginatedResponse[Civico]()
        result.total = listCivici[0].total_count if listCivici else 0
        result.content = listCivici
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituiti {result.total} civici.")
    else:
        query_select = prepared_statement_civici()
        listCivici = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listCivici is None or len(listCivici) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        
        listCivici = [Civico(**row) for row in listCivici]
        logger.info(f"Restituiti {len(listCivici)} civici.") 
        return listCivici
    
    return result


@router.get("/quartieri", response_model=List[Quartiere], description="Recupera la lista dei quartieri. Richiede autenticazione (Bearer Token).")
def lista_quartieri(
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /quartieri")
    params = {"id_municipio": id_municipio}
    query_select = prepared_statement_quartieri()
    listQuartieri = fetch_list_by_query(query_select, params)
    if listQuartieri is None or len(listQuartieri) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listQuartieri = [Quartiere(**row) for row in listQuartieri]
    logger.info(f"Restituiti {len(listQuartieri)} quartieri.")
    return listQuartieri


@router.get("/ambiti", response_model=List[Ambito], description="Recupera la lista degli ambiti. Richiede autenticazione (Bearer Token).")
def lista_ambiti(
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /ambiti")
    query_select = prepared_statement_ambiti()
    listAmbiti = fetch_list_by_query(query_select, {})
    if listAmbiti is None or len(listAmbiti) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listAmbiti = [Ambito(**row) for row in listAmbiti]
    logger.info(f"Restituiti {len(listAmbiti)} ambiti.")
    return listAmbiti

@router.get("/municipi", response_model=List[Municipio], description="Recupera la lista dei municipi. Richiede autenticazione (Bearer Token).")
def lista_municipi(
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /municipi")
    query_select = prepared_statement_municipi_genova()
    municipi_row = fetch_list_by_query(query_select, {})
    if municipi_row is None or len(municipi_row) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    municipi_list = [Municipio(**row) for row in municipi_row]
    logger.info(f"Restituiti {len(municipi_list)} municipi.")
    return municipi_list


@router.get("/POI", response_model=List[PointOfInterest], description="Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari). Richiede autenticazione (Bearer Token).")
def lista_point_of_interest(
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /point of interest")
    query_select = prepared_statement_pointofinterest()
    listPointOfInterest = fetch_list_by_query(query_select, {})
    if listPointOfInterest is None or len(listPointOfInterest) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []
    listPointOfInterest = [PointOfInterest(**row) for row in listPointOfInterest]
    logger.info(f"Restituiti {len(listPointOfInterest)} point of interest.")
    return listPointOfInterest







