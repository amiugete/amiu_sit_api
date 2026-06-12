"""Helper generici per l'esecuzione di query SQL tramite i repository.

Fornisce due funzioni riutilizzabili in tutti i router:
- execute_simple_query   : lista semplice, nessuna paginazione
- execute_paginated_query: lista semplice oppure PaginatedResponse, in base a page/size
"""
import logging
from typing import List, Optional, Type, TypeVar, Union

from fastapi import Request

from business.utility import get_route_path_from_request, get_total_count_from_rows
from config.database import DbConnection, fetch_list_by_engine, fetch_count_by_engine
from models.models import PaginatedResponse

logger = logging.getLogger(__name__)

DEFAULT_QUERY_LIMIT = 10000


def _append_limit_offset(query: str, limit: int, offset: int, db_conn: DbConnection) -> str:
    query = query.strip().rstrip(";")
    if db_conn == DbConnection.STRADE:
        if offset == 0:
            return f"SELECT * FROM ({query}) subq__ WHERE ROWNUM <= {limit}"
        return (
            "SELECT * FROM ("
            " SELECT subq__.*, ROWNUM rnum FROM ("
            f"{query}"
            ") subq__ WHERE ROWNUM <= "
            f"{offset + limit}"
            ") WHERE rnum > "
            f"{offset}"
        )
    return f"{query} LIMIT {limit} OFFSET {offset}"

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
    auto_paginazione: Optional[bool] = False,
    default_limit: Optional[int] = DEFAULT_QUERY_LIMIT,
) -> PaginatedResponse:
    """Esegue una query con supporto opzionale di paginazione.

    Se auto_paginazione è True, calcola il totale eseguendo un COUNT(*) sulla
    query base (senza LIMIT/OFFSET) e aggiunge LIMIT/OFFSET automaticamente;
    se è False, la query deve includere già :limit/:offset come parametri e
    la colonna total_count nel risultato per il totale.

    Args:
        query: prepared statement SQL.
        model_class: classe Pydantic per mappare le righe.
        db_conn: connessione al database.
        params: parametri di filtro (limit/offset vengono aggiunti internamente).
        page: numero di pagina (1-based), None = nessuna paginazione.
        size: dimensione della pagina, None = nessuna paginazione.
        request: oggetto Request di FastAPI, usato per il logging.
        auto_paginazione: se True, LIMIT/OFFSET vengono aggiunti automaticamente
            e il totale viene calcolato con un COUNT(*) separato; se False, la
            query deve includere :limit/:offset e total_count nel risultato.
        default_limit: limite di righe per il caso non paginato. Se None, la
            query viene chiamata senza aggiungere limit/offset.
            Valore predefinito: 10000.
    """
    endpoint = get_route_path_from_request(request)

    if page is not None and size is not None and size > 0:
        offset = (page - 1) * size

        if auto_paginazione:
            count_query = f"SELECT COUNT(*) FROM ({query.strip().rstrip(';')}) subq__"
            total = fetch_count_by_engine(count_query, db_conn, params) or 0
            if total == 0:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return PaginatedResponse(total=0, content=[], page=page, size=size, pages=0)
            paginated_query = _append_limit_offset(query, size, offset, db_conn)
            rows = fetch_list_by_engine(paginated_query, db_conn, params)
            if not rows:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return PaginatedResponse(total=0, content=[], page=page, size=size, pages=0)
        else:
            pagination_params = {**params, "limit": size, "offset": offset}
            rows = fetch_list_by_engine(query, db_conn, pagination_params)
            if not rows:
                logger.info(f"[{endpoint}] Nessun risultato (paginato).")
                return PaginatedResponse(total=0, content=[], page=page, size=size, pages=0)
            total = get_total_count_from_rows(rows)

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
        if auto_paginazione:
            if default_limit is not None:
                bounded_query = _append_limit_offset(query, default_limit, 0, db_conn)
                rows = fetch_list_by_engine(bounded_query, db_conn, params)
            else:
                rows = fetch_list_by_engine(query, db_conn, params)
        else:
            extra = {"limit": default_limit, "offset": 0} if default_limit is not None else {}
            rows = fetch_list_by_engine(query, db_conn, {**params, **extra})

        if not rows:
            logger.info(f"[{endpoint}] Nessun risultato.")
            return PaginatedResponse(total=0, content=[], page=1, size=0, pages=0)
        items = [model_class(**row) for row in rows]
        total = len(items)
        logger.info(f"[{endpoint}] Restituiti {total} elementi.")
        return PaginatedResponse(
            total=total,
            content=items,
            page=1,
            size=total,
            pages=1 if total > 0 else 0,
        )
