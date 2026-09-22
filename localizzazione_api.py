from fastapi import APIRouter, Query, HTTPException, Depends, Request
from business.permission import check_permissions
from business.query_helpers import execute_simple_query
from typing import Any, List
from config.database import DbConnection
from models.models import Point2Area
from repository.localizzazione_repo import pst_point2area
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/point2area",
    response_model=List[Point2Area],
    description="Restituisce le informazioni sull'area (comune, municipio, quartiere, etc.) corrispondente a un punto geografico dato in coordinate WGS84. Richiede autenticazione (Bearer Token)."
)
def get_area_from_point(
    request: Request,
    lat: float = Query(..., description="Latitudine in gradi decimali (WGS84)", ge=-90, le=90),
    lon: float = Query(..., description="Longitudine in gradi decimali (WGS84)", ge=-180, le=180),
    payload: dict[str, Any] = Depends(check_permissions)
):
    """
    Dato un punto geografico (lat, lon), restituisce le informazioni sull'area geografica di appartenenza.
    """
    result_list = execute_simple_query(request, pst_point2area, Point2Area, DbConnection.SIT, {"lat": lat, "lon": lon})
    if not result_list:
        raise HTTPException(status_code=404, detail="Nessuna area trovata per le coordinate fornite.")
    return result_list
