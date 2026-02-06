from fastapi import APIRouter, Query, HTTPException
from typing import Any, List
from config.database import execute_query
from models.models import Point2Area
from repository.localizzazione_repo import prepared_statement_point2area
from sqlalchemy import CursorResult
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Servizi di Localizzazione"])

@router.get(
    "/point2area",
    response_model=List[Point2Area],
    description="Restituisce le informazioni sull'area (comune, municipio, quartiere, etc.) corrispondente a un punto geografico dato in coordinate WGS84."
)
def get_area_from_point(
    lat: float = Query(..., description="Latitudine in gradi decimali (WGS84)", ge=-90, le=90),
    lon: float = Query(..., description="Longitudine in gradi decimali (WGS84)", ge=-180, le=180)
):
    """
    Dato un punto geografico (lat, lon), restituisce le informazioni sull'area geografica di appartenenza.
    """
    logger.info(f"Ricevuta richiesta GET /point2area con lat={lat}, lon={lon}")
    
    query = prepared_statement_point2area()
    params = {"lat": lat, "lon": lon}
    
    area_rows: CursorResult[Any] = execute_query(query, params)

    if area_rows is None:
        logger.warning(f"Nessun risultato per le coordinate lat={lat}, lon={lon}.")
        raise HTTPException(status_code=404, detail="Nessuna area trovata per le coordinate fornite.")

    result_list = [Point2Area(**row) for row in area_rows.mappings()]

    if not result_list:
        logger.warning(f"Nessun risultato mappato per le coordinate lat={lat}, lon={lon}.")
        raise HTTPException(status_code=404, detail="Nessuna area trovata per le coordinate fornite.")

    return result_list
