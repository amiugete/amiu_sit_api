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




def prepared_statement_utenze_domestiche_per_civico() -> str:
    """Query per il recupero delle utenze domestiche per civico (paginata, senza total count)."""
    return """
            SELECT * FROM (
                SELECT a.*, ROWNUM AS rnum
                FROM (
                    SELECT 
                        utd.COD_CIVICO, 
                        utd.COD_VIA,
                        DESCR_CATEGORIA,
                        UTILIZZO,
                        DESCR_UTILIZZO,
                        count(id_utente) AS num_utenze,
                        sum(NUM_OCCUPANTI) AS NUM_OCCUPANTI
                    FROM STRADE.UTENZE_TIA_DOMESTICHE utd
                    GROUP BY utd.COD_CIVICO, utd.COD_VIA, CATEGORIA,
                            DESCR_CATEGORIA, UTILIZZO, DESCR_UTILIZZO
                    ORDER BY utd.COD_CIVICO, utd.COD_VIA
                ) a
                WHERE ROWNUM <= (NVL(:offset,0) + NVL(:limit,10000))
            )
            WHERE rnum > NVL(:offset,0)
            AND (:id_via  IS NULL OR COD_VIA = :id_via )
            AND (:cod_civico IS NULL OR COD_CIVICO = :cod_civico)
           """


def prepared_statement_utenze_domestiche_per_civico_total_count() -> int:
    """Query per il recupero del total count delle utenze domestiche per civico."""
    return """
            SELECT COUNT(*) AS total_count
            FROM (
                SELECT 
                    utd.COD_CIVICO, 
                    utd.COD_VIA,
                    DESCR_CATEGORIA,
                    UTILIZZO,
                    DESCR_UTILIZZO
                FROM STRADE.UTENZE_TIA_DOMESTICHE utd
                GROUP BY utd.COD_CIVICO, utd.COD_VIA, CATEGORIA,
                DESCR_CATEGORIA, UTILIZZO, DESCR_UTILIZZO
            )
            WHERE (:id_via  IS NULL OR COD_VIA = :id_via )
            AND (:cod_civico IS NULL OR COD_CIVICO = :cod_civico)
           """


def prepared_statement_utenze_non_domestiche_per_civico() -> str:
    """Query per il recupero delle utenze non domestiche per civico (paginata, senza total count)."""
    return """
            SELECT * FROM (
                SELECT a.*, ROWNUM AS rnum
                FROM (
                    SELECT 
                        utnd.COD_CIVICO,
                        utnd.COD_VIA,
                        DESCR_CATEGORIA,
                        UTILIZZO, 
                        DESCR_UTILIZZO,
                        count(id_utente) AS num_utenze
                    FROM STRADE.UTENZE_TIA_NON_DOMESTICHE utnd
                    GROUP BY utnd.COD_CIVICO, utnd.COD_VIA, CATEGORIA,
                            DESCR_CATEGORIA, UTILIZZO, DESCR_UTILIZZO
                    ORDER BY utnd.COD_CIVICO, utnd.COD_VIA
                ) a
                WHERE ROWNUM <= (NVL(:offset,0) + NVL(:limit,10000))
            )
            WHERE rnum > NVL(:offset,0)
            AND (:id_via IS NULL OR COD_VIA = :id_via)
            AND (:cod_civico IS NULL OR COD_CIVICO = :cod_civico)
        """

def prepared_statement_utenze_non_domestiche_per_civico_total_count() -> int:
    """Query per il recupero del total count delle utenze non domestiche per civico."""
    return """
            SELECT COUNT(*) AS total_count
            FROM (
                SELECT 
                    utnd.COD_CIVICO,
                    utnd.COD_VIA,
                    DESCR_CATEGORIA,
                    UTILIZZO, 
                    DESCR_UTILIZZO
                FROM STRADE.UTENZE_TIA_NON_DOMESTICHE utnd
                GROUP BY utnd.COD_CIVICO, utnd.COD_VIA, CATEGORIA,
                        DESCR_CATEGORIA, UTILIZZO, DESCR_UTILIZZO
            )
            WHERE (:id_via IS NULL OR COD_VIA = :id_via)
              AND (:cod_civico IS NULL OR COD_CIVICO = :cod_civico)
        """