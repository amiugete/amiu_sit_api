
# Query unificata per il recupero delle vie con conteggio totale e filtri opzionali
pst_vie: str = """
        WITH vie_data AS (
            SELECT id_via, nome, id_comune
            FROM topo.vie v
            WHERE (:comune IS NULL OR id_comune = :comune)
            ORDER BY nome
            LIMIT COALESCE(:limit, 1000000)
            OFFSET COALESCE(:offset, 0)
        )
        SELECT (SELECT COUNT(*) FROM topo.vie v WHERE (:comune IS NULL OR id_comune = :comune)) AS total_count, *
        FROM vie_data;
    """

