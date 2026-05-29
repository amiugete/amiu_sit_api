"""Helper generici per l'esecuzione di query SQL tramite i repository.

Fornisce due funzioni riutilizzabili in tutti i router:
- execute_simple_query   : lista semplice, nessuna paginazione
- execute_paginated_query: lista semplice oppure PaginatedResponse, in base a page/size
"""
import logging
from typing import List, Optional, Type, TypeVar, Union

from fastapi import Request

from business.utility import get_route_path_from_request, get_total_count_from_rows
from config.database import DbConnection, fetch_list_by_engine
from models.models import PaginatedResponse

logger = logging.getLogger(__name__)

_T = TypeVar("_T")


def execute_simple_query(
    request: Request,
    query: str,
    model_class: Type[_T],
    db_conn: DbConnection,
    params: dict,
) -> List:
    """Esegue una query semplice e mappa i risultati sul modello dato.

    Args:
        query: prepared statement SQL.
        model_class: classe Pydantic per mappare le righe.
        db_conn: connessione al database (DbConnection enum).
        params: dizionario dei parametri da passare alla query.
        request: oggetto Request di FastAPI, usato per il logging.
    """
    endpoint = get_route_path_from_request(request)
    
    rows = fetch_list_by_engine(query, db_conn, params)
    if not rows:
        logger.info(f"[{endpoint}] Nessun risultato.")
        return []
    result = [model_class(**row) for row in rows]
    logger.info(f"[{endpoint}] Restituiti {len(result)} elementi.")
    return result


def execute_paginated_query(
    request: Request,
    query: str,
    model_class: Type[_T],
    db_conn: DbConnection,
    params: dict,
    page: Optional[int],
    size: Optional[int],
    default_limit: Optional[int] = None,
    query_with_count: Optional[str] = None,
) -> Union[List, PaginatedResponse]:
    """Esegue una query con supporto opzionale di paginazione.

    Se page e size sono valorizzati usa query_with_count (che deve includere
    la colonna total_count) e restituisce un PaginatedResponse; altrimenti
    usa query e restituisce una lista semplice.

    Args:
        query: prepared statement senza conteggio totale.
        query_with_count: prepared statement con colonna total_count; se None la query
            incorpora già COUNT(*) OVER() AS total_count e viene usata anche nel ramo paginato.
        model_class: classe Pydantic per mappare le righe.
        db_conn: connessione al database.
        params: parametri di filtro (limit/offset vengono aggiunti internamente).
        page: numero di pagina (1-based), None = nessuna paginazione.
        size: dimensione della pagina, None = nessuna paginazione.
        request: oggetto Request di FastAPI, usato per il logging.
        default_limit: limite di righe per il caso non paginato; necessario
            quando la query SQL contiene :limit/:offset (es. query Tellus).
            Se None, la query viene chiamata senza aggiungere limit/offset.
    """
    endpoint = get_route_path_from_request(request)

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size

        if query_with_count is None:
            # La query incorpora già COUNT(*) OVER() AS total_count
            rows = fetch_list_by_engine(query, db_conn, {**params, "limit": size, "offset": offset})
            if not rows:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return []
            total = get_total_count_from_rows(rows)
        else:
            # query_with_count è una query separata che restituisce un semplice COUNT(*)
            count_rows = fetch_list_by_engine(query_with_count, db_conn, params)
            total = list(count_rows[0].values())[0] if count_rows else 0
            if total == 0:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return []
            rows = fetch_list_by_engine(query, db_conn, {**params, "limit": size, "offset": offset})
            if not rows:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return []

        items = [model_class(**row) for row in rows]
        logger.info(f"[{endpoint}] Restituiti {total} elementi (paginati).")
        return PaginatedResponse(
            total=total,
            content=items,
            page=page,
            size=size,
            pages=(total + size - 1) // size if size else 0,
        )
    else:
        extra = {"limit": default_limit, "offset": 0} if default_limit is not None else {}
        rows = fetch_list_by_engine(query, db_conn, {**params, **extra})
        if not rows:
            logger.info(f"[{endpoint}] Nessun risultato.")
            return []
        items = [model_class(**row) for row in rows]
        logger.info(f"[{endpoint}] Restituiti {len(items)} elementi.")
        return items
