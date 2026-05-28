
from fastapi import APIRouter, Query, HTTPException, Depends, Response, Body, Request
from business.permission import check_permissions
from business.utility import get_route_path_from_request
from business.query_helpers import execute_simple_query
from typing import Any, List, Optional
from config.database import DbConnection, update_query_by_engine
from models.models import AstaMobile, ImmagineUploadFromSitMobile,PiazzolaMobile
import logging
from pathlib import Path
import base64
import os
from dotenv import load_dotenv

from repository.aste_repo_geoloc import pst_aste_mobile
from repository.piazzole_repo import pst_aste_mobile_update_foto, pst_piazzole_mobile, pst_piazzole_mobile_all_date

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Servizi mobile"])



@router.post("/piazzola/upload/foto", description="Effettua un upload dell'immagine di una piazzola verifica se esiste e la crea o la sostituisce qualora esistesse. Richiede autenticazione (Bearer Token)."
)
def upload_foto_piazzola(
    request: Request,
    payload: dict[str, Any] = Depends(check_permissions), 
    imageBody: ImmagineUploadFromSitMobile = Body(..., description="Dati dell'immagine da caricare, inclusi il nome del file e il contenuto in base64")):
    """
    """
    base_path : Path = Path(os.getenv("BASE_PATH_FOTO_PIAZZOLE"))

    if(imageBody is None or imageBody.image is None or imageBody.id_piazzola is None):
        logger.error("Dati dell'immagine mancanti o non validi.")
        raise HTTPException(status_code=400, detail="Dati dell'immagine mancanti o non validi.")
    
    file_bytes = base64.b64decode(imageBody.image)
    file_path = base_path / f"/{imageBody.id_piazzola}.jpg"

    if(file_path.exists()):
        logger.info(f"File {file_path} esistente, verrà sovrascritto.")
    
    file_path.write_bytes(file_bytes)

    query_update = pst_aste_mobile_update_foto

    params = {"id_piazzola": imageBody.id_piazzola, "foto": 1}

    row = update_query_by_engine(query_update, DbConnection.SIT, params)

    return Response(status_code=204) if row is not None and row > 0 else Response(status_code=500, content="Errore durante l'aggiornamento del database.")



####################### Servizio delle piazzole con data di ultimo aggiornamento e data eliminazione #######################################
@router.get("/piazzole", response_model=List[PiazzolaMobile],
            description="""Recupera la lista delle piazzole per l'applicazione mobile con filtri opzionali.
            Richiede autenticazione (Bearer Token).""", )
def lista_piazzole(
    request: Request,
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    last_update: Optional[str] = Query(None, description="Filtra per data di ultimo aggiornamento (formato YYYYMMDDHHMM)"),
    data_eliminazione: Optional[str] = Query(None, description="Filtra per data di eliminazione (formato YYYYMMDDHHMM)"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint} ")
    query = pst_piazzole_mobile_all_date if last_update is not None and data_eliminazione is not None else pst_piazzole_mobile
    return execute_simple_query(
        query, PiazzolaMobile, DbConnection.SIT,
        {"via": id_via, "comune": id_comune, "last_update": last_update, "data_eliminazione": data_eliminazione},
        endpoint
    )


####################### Servizio delle aste con data di ultimo aggiornamento e data eliminazione #######################################
@router.get("/aste", response_model=List[AstaMobile],
            description="""Recupera la lista delle aste per l'applicazione mobile con filtri opzionali.
            Richiede autenticazione (Bearer Token).""", )
def lista_aste(
    request: Request,
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    data_ultima_modifica: Optional[str] = Query(None, description="Filtra per data di ultimo aggiornamento (formato YYYYMMDDHHmm)"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    endpoint = get_route_path_from_request(request)
    logger.info(f"Ricevuta richiesta GET {endpoint}")
    return execute_simple_query(
        pst_aste_mobile,
        AstaMobile,
        DbConnection.SIT,
        {"id_via": id_via, "data_ultima_modifica": data_ultima_modifica},
        endpoint
    )

