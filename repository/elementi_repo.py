def prepared_statement_elementi() -> str:
    """Query per il recupero degli elementi con filtro opzionale id_piazzola."""
    return """
        SELECT
            e.id_piazzola,
            e.id_elemento,
            tr.ordinamento AS ordine_rifiuto,
            tr.nome AS desc_rifiuto,
            tr.colore AS colore_rifiuto,
            e.tipo_elemento,
            te.descrizione AS desc_tipo_elemento,
            te.volume,
            te.tipologia_elemento,
            te2.descrizione AS tipo_raccolta,
            e.matricola,
            e.tag,
            e.serratura,
            e.matricola_serratura,
            e.data_ultima_modifica,
            ep.id_macro_categoria,
            mc.descrizione AS macro_categoria,
            ep.descrizione,
            ep.nome_attivita,
            ep.nota AS nota_privati
        FROM elem.elementi e
        JOIN elem.tipi_elemento te ON te.tipo_elemento = e.tipo_elemento
        JOIN elem.tipi_rifiuto tr ON tr.tipo_rifiuto = te.tipo_rifiuto
        JOIN elem.tipologie_elemento te2 ON te2.tipologia_elemento = te.tipologia_elemento
        LEFT JOIN elem.elementi_privati ep ON ep.id_elemento = e.id_elemento
        LEFT JOIN utenze.macro_categorie mc ON ep.id_macro_categoria = mc.id_macro_categoria
        WHERE e.id_piazzola IS NOT NULL
          AND (:id_piazzola IS NULL OR e.id_piazzola = :id_piazzola)
          AND (:last_update IS NULL OR TO_CHAR(e.data_ultima_modifica,'YYYYMMDDHH24MI') = :last_update)
          AND te.tipologia_elemento NOT IN ('N')
        ORDER BY e.id_piazzola, tr.ordinamento, te.volume
        LIMIT COALESCE(:limit, 1000000)
        OFFSET COALESCE(:offset, 0)
    """


def prepared_statement_elementi_with_count() -> str:
    """Query per il recupero degli elementi con conteggio totale e filtro opzionale id_piazzola."""
    return """
        WITH queryElementi AS (
            SELECT
                e.id_piazzola,
                e.id_elemento,
                tr.ordinamento AS ordine_rifiuto,
                tr.nome AS desc_rifiuto,
                tr.colore AS colore_rifiuto,
                e.tipo_elemento,
                te.descrizione AS desc_tipo_elemento,
                te.volume,
                te.tipologia_elemento,
                te2.descrizione AS tipo_raccolta,
                e.matricola,
                e.tag,
                e.serratura,
                e.matricola_serratura,
                e.data_ultima_modifica,
                ep.id_macro_categoria,
                mc.descrizione AS macro_categoria,
                ep.descrizione,
                ep.nome_attivita,
                ep.nota AS nota_privati
            FROM elem.elementi e
            JOIN elem.tipi_elemento te ON te.tipo_elemento = e.tipo_elemento
            JOIN elem.tipi_rifiuto tr ON tr.tipo_rifiuto = te.tipo_rifiuto
            JOIN elem.tipologie_elemento te2 ON te2.tipologia_elemento = te.tipologia_elemento
            LEFT JOIN elem.elementi_privati ep ON ep.id_elemento = e.id_elemento
            LEFT JOIN utenze.macro_categorie mc ON ep.id_macro_categoria = mc.id_macro_categoria
            WHERE e.id_piazzola IS NOT NULL
              AND (:id_piazzola IS NULL OR e.id_piazzola = :id_piazzola)
              AND te.tipologia_elemento NOT IN ('N')
              AND (:last_update IS NULL OR TO_CHAR(e.data_ultima_modifica,'YYYYMMDDHH24MI') = :last_update)
        )
        SELECT (SELECT COUNT(*) FROM queryElementi) AS total_count, *
        FROM queryElementi
        ORDER BY id_piazzola, ordine_rifiuto, volume
        LIMIT COALESCE(:limit, 1000000)
        OFFSET COALESCE(:offset, 0);
    """
