def prepared_statement_utenze_UD_with_count() -> str:
    """Query unificata per il recupero delle utenze per UD."""
    return """
            SELECT *, COUNT(*) OVER() AS totale_record
            FROM etl.utenze_tia_domestiche_idea
            ORDER BY id_utenza
            LIMIT :limit
            OFFSET :offset
           """
def prepared_statement_utenze_UND_with_count() -> str:
    """Query unificata per il recupero delle utenze per UND."""
    return """
            SELECT *, COUNT(*) OVER() AS totale_record
            FROM etl.utenze_tia_non_domestiche_idea
            ORDER BY id_utenza
            LIMIT :limit
            OFFSET :offset
           """