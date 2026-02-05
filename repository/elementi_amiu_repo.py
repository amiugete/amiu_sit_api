def prepared_statement_elementi_amiu() -> str:
    """Query per il recupero degli elementi dei posteriori, con paginazione, filtro last_update e total_count."""
    return """
        SELECT *, CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
        FROM (
            SELECT id_elemento, id_piazzola, ee.tipo_elemento AS id_tipo_elemento,
                   te.descrizione AS tipo_elemento, tr.nome AS rifiuto, te.volume AS volume_litri,
                   matricola, tag, serratura, matricola_serratura,
                   coalesce(data_inserimento,  '19700101') AS data_inserimento,
                   data_eliminazione,
                   coalesce(greatest(data_inserimento, data_eliminazione, data_ultima_modifica), '19700101') AS data_ultima_modifica
            FROM (
                SELECT id_elemento, id_piazzola, tipo_elemento, matricola, tag, serratura, matricola_serratura,
                       to_char(e.data_inserimento, 'YYYYMMDD') AS data_inserimento,
                       to_char(e.data_ultima_modifica, 'YYYYMMDD') AS data_ultima_modifica,
                       NULL AS data_eliminazione
                FROM elem.elementi e
                UNION
                SELECT id_elemento, id_piazzola, tipo_elemento, matricola, tag, serratura, matricola_serratura,
                       to_char(e2.data_inserimento, 'YYYYMMDD') AS data_inserimento,
                       to_char(e2.data_ultima_modifica, 'YYYYMMDD') AS data_ultima_modifica,
                       to_char(e2.data_eliminazione, 'YYYYMMDD') AS data_eliminazione
                FROM history.elementi e2
            ) ee
            JOIN elem.tipi_elemento te ON te.tipo_elemento = ee.tipo_elemento
            JOIN elem.tipi_rifiuto tr ON te.tipo_rifiuto = tr.tipo_rifiuto
            WHERE te.tipo_elemento IN (
                SELECT tipo_elemento
                FROM elem.tipi_elemento te
                WHERE tipologia_elemento IN ('P', 'T', 'A') AND in_piazzola = 1
            )
            -- Filtro opzionale per last_update
            AND (:last_update IS NULL OR greatest(data_inserimento, data_eliminazione, data_ultima_modifica) >= :last_update)
        ) sub
        ORDER BY id_elemento
        LIMIT :limit
        OFFSET :offset
    """
