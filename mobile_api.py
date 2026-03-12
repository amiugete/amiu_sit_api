from fastapi import APIRouter, Query, HTTPException,Depends,Response,Body
from business.permission import get_current_user
from typing import Any
from models.models import ImmagineUploadFromSitMobile
import logging
from pathlib import Path
import base64
import os
from dotenv import load_dotenv

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

    return Response(status_code=204)

