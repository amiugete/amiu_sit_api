

from typing import List, Optional
from fastapi import Request


def get_total_count_from_rows(rows: Optional[List[dict]], count_key: str = "total_count") -> int:
    """Estrae il conteggio totale da una lista di dizionari, restituendo 0 se la chiave non è presente o se la lista è vuota."""
    if not rows or count_key not in rows[0]:
        return 0
    return rows[0][count_key]


def get_route_path_from_request(request: Request) -> str:
    """Recupera il percorso dell'endpoint effettivo a partire dalla request FastAPI.

    Usa la mappatura endpoint_local_paths configurata in request.app.state quando disponibile,
    altrimenti ricava il path direttamente dalla route.
    """
    local_paths = getattr(request.app.state, "endpoint_local_paths", {})
    return local_paths.get(request.scope["route"].endpoint, request.scope["route"].path)