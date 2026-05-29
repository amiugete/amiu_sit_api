from fastapi import APIRouter, Query, Depends, Request
from business.permission import check_permissions
from typing import Any, List, Optional, Union
import logging

# helpers
from business.query_helpers import execute_simple_query, execute_paginated_query

# database
from config.database import fetch_list_by_engine, DbConnection

# modelli
from models.models import   GeoJSNONModel, Municipio, MyFutureModel, Piazzola, PaginatedResponse, PaginatedGeoJSONResponse, Via, Comune, Civico, Quartiere, Ambito, PointOfInterest, Elemento



#repository
from repository.municipi_repo import pst_municipi_genova
from repository.vie_repo import pst_vie
from repository.piazzole_repo import pst_piazzole
from repository.elementi_repo import pst_elementi
from repository.comuni_repo import pst_comuni
from repository.civici_repo import pst_civici
from repository.quartieri_repo import pst_quartieri
from repository.ambiti_repo import pst_ambiti
from repository.aste_repo_geoloc import pst_aste_geoloc
from repository.point_of_interest_repo import pst_pointofinterest



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
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(request, pst_ambiti, Ambito, DbConnection.SIT, {})

##############################################################
@router.get("/comuni", response_model=List[Comune],
            description="Recupera la lista dei comuni. Richiede autenticazione (Bearer Token).")
def lista_comuni(
    request: Request,
    id_ambito: Optional[int] = Query(None, description="Filtra per ambito"),
    cod_istat: Optional[str] = Query(None, description="Filtra per codice ISTAT"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(
        request,
        pst_comuni,
        Comune, 
        DbConnection.SIT,
        {"id_ambito": id_ambito, "cod_istat": cod_istat},
    )



##############################################################
@router.get("/municipi", response_model=List[Municipio],
            description="Recupera la lista dei municipi (per il solo Comune di Genova). Richiede autenticazione (Bearer Token).")
def lista_municipi(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(request, pst_municipi_genova, Municipio, DbConnection.SIT, {})



##############################################################
@router.get("/quartieri", response_model=List[Quartiere],
            description="Recupera la lista dei quartieri (per il solo Comune di Genova, fuori Genova quartiere = Comune). Richiede autenticazione (Bearer Token).")
def lista_quartieri(
    request: Request,
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(
        request,
        pst_quartieri, Quartiere, DbConnection.SIT,
        {"id_municipio": id_municipio},
    )



##############################################################
@router.get("/vie", response_model=Union[List[Via], PaginatedResponse[Via]],
            description="""Recupera la lista delle vie con filtri opzionali.
             Richiede autenticazione (Bearer Token).
             Paginazione opzionale gestita tramite parametri page e size nella request.""")
def lista_vie(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_vie,
        Via, DbConnection.SIT,
        {"comune": id_comune},
        page,
        size,
        default_limit=10000,
        query_with_count = None
    )



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
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_via: Optional[int] = Query(None, description="Filtra per ID via"),
    id_municipio: Optional[int] = Query(None, description="Filtra per ID municipio"),
    last_update: Optional[str] = Query(None, description="Filtra per data di ultima modifica (YYYYMMDD)"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    offset = 0
    limit = 1000

    if page is not None and size is not None and size > 0 and page > 0:
        offset = (page - 1) * size
        limit = size

    params = {"limit": limit, "offset": offset, "last_update": last_update, "id_via": id_via, "id_municipio": id_municipio}
    query_aste = pst_aste_geoloc
    listAste = fetch_list_by_engine(query_aste, DbConnection.SIT, params)
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
@router.get("/civici", response_model=Union[PaginatedResponse[Civico], List[Civico]],
            description="""Recupera la lista dei civici (per ora del solo Comune di Genova) con filtri opzionali.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""")
def lista_civici(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per via"),
    last_update: Optional[str] = Query(None, description="Filtra per ultimo aggiornamento in formato YYYYMMDD", pattern=r"^\d{8}$"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_civici,
        Civico, DbConnection.SIT,
        {"id_municipio": id_municipio, "id_via": id_via, "ins_date": last_update},
        page,
        size, 
        default_limit=10000,
        query_with_count=None
    )



##############################################################
@router.get("/piazzole", response_model=Union[List[Piazzola], PaginatedResponse[Piazzola]],
            description="""Recupera la lista delle piazzole con filtri opzionali.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""")
def lista_piazzole(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    id_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    pap: Optional[int] = Query(None, ge=0, le=1, description="Filtra per PAP (1 = Sì, 0 = No)"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_piazzole,
        Piazzola,
        DbConnection.SIT,
        {"pap": pap if pap is not None else 0, "via": id_via, "comune": id_comune, "municipio": id_municipio},
        page, 
        size,
        default_limit=10000,
        query_with_count=None
    )


@router.get("/elementi", response_model=Union[List[Elemento], PaginatedResponse[Elemento]],
            description="""Recupera la lista degli elementi associati alle piazzole con filtro opzionale.
            Richiede autenticazione (Bearer Token).
            Paginazione opzionale gestita tramite parametri page e size nella request.""")
def lista_elementi(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_piazzola: Optional[int] = Query(None, description="Filtra per ID piazzola"),
    last_update: Optional[str] = Query(
        None,
        description="Filtra per ultimo aggiornamento nel formato YYYYMMDDHHMM (es. 202603301230)",
        pattern=r"^(?:19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([01]\d|2[0-3])([0-5]\d)$"
    ),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_elementi,
        Elemento, 
        DbConnection.SIT,
        {"id_piazzola": id_piazzola, "last_update": last_update},
        page,
        size,
        default_limit=10000,
        query_with_count=None
    )

@router.get("/POI", response_model=List[PointOfInterest],
            description="""Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari).
            Richiede autenticazione (Bearer Token).""")
def lista_point_of_interest(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(request, pst_pointofinterest, PointOfInterest, DbConnection.SIT, {})





    








