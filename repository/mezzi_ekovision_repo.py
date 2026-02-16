def prepared_statement_mezzi_ekovision() -> str:
    """Query per elenco mezzi ekovision, con paginazione e total_count."""
    return """
        SELECT m.id_scheda_ekovision, 
               see.data_esecuzione_prevista, 
               see.orario_esecuzione, 
               see.fascia_turno,
               m.sportello,
               CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
        FROM consunt.mezzi m
        JOIN consunt.schede_eseguite_ekovision see ON see.id_scheda = m.id_scheda_ekovision
        WHERE see.data_esecuzione_prevista = :check_date
        ORDER BY see.data_esecuzione_prevista, m.sportello
        LIMIT :limit
        OFFSET :offset
    """