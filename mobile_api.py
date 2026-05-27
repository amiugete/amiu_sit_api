
from fastapi import APIRouter, Query, HTTPException,Depends,Response,Body
from business.permission import get_current_user
from typing import Any, List, Optional
from config.database import fetch_list_by_engine, update_query_by_engine, DbConnection
from models.models import AstaMobile, ImmagineUploadFromSitMobile,PiazzolaMobile
import logging
from pathlib import Path
import base64
import os
from dotenv import load_dotenv

from repository.aste_repo_geoloc import prepared_statement_aste_mobile
from repository.piazzole_repo import prepared_statement_aste_mobile_update_foto, prepared_statement_piazzole, prepared_statement_piazzole_mobile, prepared_statement_piazzole_mobile_all_date, prepared_statement_piazzole_with_count

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Servizi mobile"])



@router.post("/piazzola/upload/foto", description="Effettua un upload dell'immagine di una piazzola verifica se esiste e la crea o la sostituisce qualora esistesse. Richiede autenticazione (Bearer Token)."
)
def upload_foto_piazzola(
    payload: dict[str, Any] = Depends(get_current_user), 
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

    query_update = prepared_statement_aste_mobile_update_foto()

    params = {"id_piazzola": imageBody.id_piazzola, "foto": 1}

    row = update_query_by_engine(query_update, DbConnection.SIT, params)

    return Response(status_code=204) if row is not None and row > 0 else Response(status_code=500, content="Errore durante l'aggiornamento del database.")



####################### Servizio delle piazzole con data di ultimo aggiornamento e data eliminazione #######################################
@router.get("/piazzole", response_model=List[PiazzolaMobile],
            description="""Recupera la lista delle piazzole per l'applicazione mobile con filtri opzionali.
            Richiede autenticazione (Bearer Token).""", )
def lista_piazzole(
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    last_update: Optional[str] = Query(None, description="Filtra per data di ultimo aggiornamento (formato YYYYMMDDHHMM)"),
    data_eliminazione: Optional[str] = Query(None, description="Filtra per data di eliminazione (formato YYYYMMDDHHMM)"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /piazzole")
    
    params = { "via": id_via, "comune": id_comune, "last_update": last_update, "data_eliminazione": data_eliminazione }

    query_select = prepared_statement_piazzole_mobile_all_date() if last_update is not None and data_eliminazione is not None else prepared_statement_piazzole_mobile()
    listPiazzole = fetch_list_by_engine(query_select, DbConnection.SIT, {**params})

    if listPiazzole is None or len(listPiazzole) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []

    listPiazzole = [PiazzolaMobile(**row) for row in listPiazzole]
    logger.info(f"Restituiti {len(listPiazzole)} piazzole.")
    
    return listPiazzole


####################### Servizio delle aste con data di ultimo aggiornamento e data eliminazione #######################################
@router.get("/aste", response_model=List[AstaMobile],
            description="""Recupera la lista delle aste per l'applicazione mobile con filtri opzionali.
            Richiede autenticazione (Bearer Token).""", )
def lista_aste(
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    data_ultima_modifica: Optional[str] = Query(None, description="Filtra per data di ultimo aggiornamento (formato YYYYMMDDHHmm)"),
    payload: dict[str, Any] = Depends(get_current_user)
):
    logger.info("Ricevuta richiesta GET /aste")
    
    params = { "id_via": id_via, "data_ultima_modifica": data_ultima_modifica }

    query_select = prepared_statement_aste_mobile()
    listAste = fetch_list_by_engine(query_select, DbConnection.SIT, {**params})

    if listAste is None or len(listAste) == 0:
        logger.info("Nessun risultato ottenuto dalla query.")
        return []

    listAste = [AstaMobile(**row) for row in listAste]
    logger.info(f"Restituiti {len(listAste)} aste.")
    
    return listAste

