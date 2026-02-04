def prepared_statement_vie() -> str:
    """Preparazione della query per il recupero delle vie con filtri opzionali(comune)"""
    return  """
        select id_via, nome, id_comune from topo.vie v
        where (:comune is null or id_comune = :comune)
        order by nome
        limit coalesce(:limit, 10000)
        offset coalesce(:offset,0)
    """
def prepared_statement_vie_with_count() -> str:
    """Query unificata per il recupero delle vie con conteggio totale e filtri opzionali."""
    return """
        WITH vie_data AS (
            SELECT id_via, nome, id_comune
            FROM topo.vie v
            WHERE (:comune IS NULL OR id_comune = :comune)
            ORDER BY nome
            LIMIT COALESCE(:limit, 10000)
            OFFSET COALESCE(:offset, 0)
        )
        SELECT (SELECT COUNT(*) FROM topo.vie v WHERE (:comune IS NULL OR id_comune = :comune)) AS total_count, *
        FROM vie_data;
    """

