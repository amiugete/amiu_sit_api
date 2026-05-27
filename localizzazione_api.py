from fastapi import APIRouter, Query, HTTPException,Depends
from business.permission import get_current_user
from typing import Any, List
from config.database import fetch_list_by_engine, DbConnection
from models.models import Point2Area
from repository.localizzazione_repo import prepared_statement_point2area
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Servizi di Localizzazione"])

@router.get(
    "/point2area",
    response_model=List[Point2Area],
    description="Restituisce le informazioni sull'area (comune, municipio, quartiere, etc.) corrispondente a un punto geografico dato in coordinate WGS84. Richiede autenticazione (Bearer Token)."
)
def get_area_from_point(
    lat: float = Query(..., description="Latitudine in gradi decimali (WGS84)", ge=-90, le=90),
    lon: float = Query(..., description="Longitudine in gradi decimali (WGS84)", ge=-180, le=180),
    payload: dict[str, Any] = Depends(get_current_user)
):
    """
    Dato un punto geografico (lat, lon), restituisce le informazioni sull'area geografica di appartenenza.
    """
    logger.info(f"Ricevuta richiesta GET /point2area con lat={lat}, lon={lon}")
    
    query = prepared_statement_point2area()
    params = {"lat": lat, "lon": lon}
    
    area_rows: List[dict] | None = fetch_list_by_engine(query, DbConnection.SIT, params)

    if area_rows is None or len(area_rows) == 0:
        logger.warning(f"Nessun risultato per le coordinate lat={lat}, lon={lon}.")
        raise HTTPException(status_code=404, detail="Nessuna area trovata per le coordinate fornite.")

    result_list = [Point2Area(**row) for row in area_rows]

    if not result_list:
        logger.warning(f"Nessun risultato mappato per le coordinate lat={lat}, lon={lon}.")
        raise HTTPException(status_code=404, detail="Nessuna area trovata per le coordinate fornite.")

    return result_list
