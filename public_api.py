from fastapi import APIRouter, Query, Depends
from business.email.email_engine import send_email_territorio
from business.permission import get_current_user
from typing import Any, List, Optional, Union
import logging


# database
from business.utility import get_total_count_from_rows
from config.database import fetch_list_by_query

# modelli
from models.models import   GeoJSNONModel, Municipio, MyFutureModel, Piazzola, PaginatedResponse, PaginatedGeoJSONResponse, Via, Comune, Civico, Quartiere, Ambito, PointOfInterest, Elemento



#repository
from repository.municipi_repo import prepared_statement_municipi_genova
from repository.vie_repo import prepared_statement_vie, prepared_statement_vie_with_count
from repository.piazzole_repo import prepared_statement_piazzole, prepared_statement_piazzole_with_count
from repository.elementi_repo import prepared_statement_elementi, prepared_statement_elementi_with_count
from repository.comuni_repo import prepared_statement_comuni
from repository.civici_repo import prepared_statement_civici_with_count, prepared_statement_civici
from repository.quartieri_repo import prepared_statement_quartieri
from repository.ambiti_repo import prepared_statement_ambiti
from repository.aste_repo_geoloc import prepared_statement_aste_geoloc
from repository.point_of_interest_repo import prepared_statement_pointofinterest
from sqlalchemy import CursorResult



logger = logging.getLogger(__name__)

#router = APIRouter()
router = APIRouter(tags=["Servizi generici"])

# In questo router sono definite delle api che restituiscono dati geografici di vario tipo (comuni, vie, piazzole, civici, quartieri, ambiti, municipi, point of interest) con filtri opzionali e paginazione. Tutti questi endpoint richiedono autenticazione tramite Bearer Token e verificano i permessi dell'utente prima di restituire i dati.
# I servizi che restituiscono i dati in un oggetto di tipo PaginatedResponse sono quelli che possono potenzialmente restituire liste molto grandi di risultati, mentre quelli che restituiscono i dati in formato JSON sono quelli che restituiscono liste più piccole di risultati quasi identici agli oggetti restituiti da ws_amiugis.
# I modelli dei dati response e request sono definiti in models/models.py e i prepared statement per le query al database sono definiti nei repository corrispondenti alla tipologia di dato restituito (es. repository/vie_repo.py per le vie, repository/piazzole_repo.py per le piazzole, ecc.).

# nel main richiamerò questi router e li inizializzo

##############################################################

@router.get("/ambiti", response_model=List[Ambito], 
            description="Recupera la lista degli ambiti territoriali AMIU (livello sovra-comunale). Richiede autenticazione (Bearer Token).")
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

##############################################################
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



##############################################################
@router.get("/municipi", response_model=List[Municipio], 
            description="Recupera la lista dei municipi (per il solo Comune di Genova). Richiede autenticazione (Bearer Token).")
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



##############################################################
@router.get("/quartieri", response_model=List[Quartiere],
            description="Recupera la lista dei quartieri (per il solo Comune di Genova, fuori Genova quartiere = Comune). Richiede autenticazione (Bearer Token).")
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



##############################################################
@router.get("/vie", response_model=Union[List[Via], PaginatedResponse[Via]],
            description="""Recupera la lista delle vie con filtri opzionali. 
             Richiede autenticazione (Bearer Token).
             Paginazione opzionale gestita tramite parametri page e size nella request.""", )
def lista_vie(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
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

    params = {"comune": id_comune}

    if limit is not None and offset is not None:
        query_select = prepared_statement_vie_with_count()
        listVie = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listVie is None or len(listVie) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        total = get_total_count_from_rows(listVie)
        listVie = [Via(**row) for row in listVie]
        result = PaginatedResponse[Via]()
        result.total = total
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



##############################################################
@router.get(
    "/aste",
    response_model=GeoJSNONModel,
    description="""Recupera le Aste in formato GeoJSON con paginazione.
        Richiede autenticazione (Bearer Token).
        I filtri opzionali includono ID via, ID municipio e data di ultimo aggiornamento (YYYYMMDD).
        La risposta include il conteggio totale degli elementi e i dettagli di ogni asta,
        inclusa la geometria in formato GeoJSON.
        Paginazione opzionale gestita tramite parametri page e size nella request."""
)
def lista_aste(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_via: Optional[int] = Query(None, description="Filtra per ID via"),
    id_municipio: Optional[int] = Query(None, description="Filtra per ID municipio"),
    last_update: Optional[str] = Query(None, description="Filtra per data di ultima modifica (YYYYMMDD)"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /aste")
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"limit": limit, "offset": offset, "last_update": last_update, "id_via": id_via, "id_municipio": id_municipio}
    query_aste = prepared_statement_aste_geoloc()
    listAste = fetch_list_by_query(query_aste, params)
    total = 0
    if listAste is None or len(listAste) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        paginated = PaginatedGeoJSONResponse(
            total=0,
            page=page,
            size=size,
            pages=0,
            content=GeoJSNONModel(type="FeatureCollection", features=[])
        )
        return paginated
    # Se la query restituisce il conteggio totale 
    if "total_count" in listAste[0]:
        total = listAste[0]["total_count"]

    features = []

    for row in listAste:
        # La query restituisce la geometria che verrà mappata nella classe MyFutureModel come LineStringModel grazie al parsing definito nel modello. Gli altri campi vengono mappati nelle proprietà del feature model.
        features.append(
        MyFutureModel(
            properties={
                "id_asta": row["id_asta"],
                "id_via": row["id_via"],
                "last_update": row["last_update"],
                "lung_db_m": row["lung_db_m"],
                "transitabilita": row["transitabilita"],
                "lungh_geom_m": row["lungh_geom_m"],
                "nome_via": row["nome_via"],
                "id_quartiere": row["id_quartiere"],
                "id_municipio": row["id_municipio"]
            },
            geometry=row["geometry"]
        ))
    
    return GeoJSNONModel(type="FeatureCollection", features=features, total=total, page=page, size=size, pages=(total + size - 1) // size if size else 0)



##############################################################
@router.get("/civici", response_model=Union[PaginatedResponse[Civico], List[Civico]] , 
            description="""Recupera la lista dei civici (per ora del solo Comune di Genova) con filtri opzionali.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""")
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
        # estrazione total_count colonna per paginazione
        total = get_total_count_from_rows(listCivici)
        listCivici = [Civico(**row) for row in listCivici]
        result = PaginatedResponse[Civico]()
        result.total = total
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



##############################################################
@router.get("/piazzole", response_model=Union[List[Piazzola],PaginatedResponse[Piazzola]],
            description="""Recupera la lista delle piazzole con filtri opzionali.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""", )
def lista_piazzole(
    page:  Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
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

    params = {"pap": pap if pap is not None else 0, "via": id_via, "comune": id_comune, "municipio": id_municipio}

    # Query per il ritorno del risultato paginato
    if limit is not None and offset is not None:
        query_select = prepared_statement_piazzole_with_count()
        listPiazzole = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listPiazzole is None or len(listPiazzole) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        # estrazione total_count colonna per paginazione
        total = get_total_count_from_rows(listPiazzole)
        
        listPiazzole = [Piazzola(**row) for row in listPiazzole]
        result = PaginatedResponse[Piazzola]()
        result.total = total
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


@router.get("/elementi", response_model=Union[List[Elemento], PaginatedResponse[Elemento]],
            description="""Recupera la lista degli elementi associati alle piazzole con filtro opzionale.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""")
def lista_elementi(
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_piazzola: Optional[int] = Query(None, description="Filtra per ID piazzola"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD", pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /elementi")
    listElementi: CursorResult[Any]
    query_select = ''
    offset = None
    limit = None

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size
        limit = size

    params = {"id_piazzola": id_piazzola, "last_update": last_update}

    # Query per il ritorno del risultato paginato
    if limit is not None and offset is not None:
        query_select = prepared_statement_elementi_with_count()
        listElementi = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listElementi is None or len(listElementi) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []
        # estrazione total_count colonna per paginazione
        total = get_total_count_from_rows(listElementi)

        listElementi = [Elemento(**row) for row in listElementi]
        result = PaginatedResponse[Elemento]()
        result.total = total
        result.content = listElementi
        result.page = page
        result.size = size
        result.pages = (result.total + size - 1) // size if size else 0
        logger.info(f"Restituiti {result.total} elementi.")
    # Query per il ritorno del risultato non paginato
    else:
        query_select = prepared_statement_elementi()
        listElementi = fetch_list_by_query(query_select, {**params, "limit": limit, "offset": offset})

        if listElementi is None or len(listElementi) == 0:
            logger.info("Nessun risultato ottenuto dalla query.")
            return []

        listElementi = [Elemento(**row) for row in listElementi]
        logger.info(f"Restituiti {len(listElementi)} elementi.")
        return listElementi

    return result

@router.get("/POI", response_model=List[PointOfInterest],
            description="""Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari). 
            Richiede autenticazione (Bearer Token).""")
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





    








