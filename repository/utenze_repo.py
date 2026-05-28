
# Repository per le utenze, con query SQL predefinite per il recupero dei dati.

# Query unificata per il recupero delle utenze per UD
pst_utenze_UD_with_count: str = """
            SELECT id_utente, 
            progr_utenza as progressivo,
            cod_via, 
            cod_civico, 
            cod_interno,
            nominativo, 
            superficie,
            num_occupanti, abitazione_di_residenza, 
            categoria, 
            utilizzo,
            COUNT(*) OVER() AS total_count
                        FROM etl.utenze_tia_domestiche
                        ORDER BY id_utente
            LIMIT :limit
            OFFSET :offset
                    """
# Query unificata per il recupero delle utenze per UND
pst_utenze_UND_with_count: str = """
            SELECT id_utente, 
            progr_utenza as progressivo,
            nominativo, 
            cod_via,
            cod_civico, 
            cod_interno,
            superficie,
            num_occupanti, abitazione_di_residenza, 
            categoria, 
            utilizzo,
            COUNT(*) OVER() AS total_count
                        FROM etl.utenze_tia_non_domestiche
            ORDER BY id_utente
            LIMIT :limit
            OFFSET :offset
                    """


# Repository per le utenze Id&A (query analoghe alle precedenti ma su tabelle ristrette dedicate a Id&A, senza total count)

# Query unificata per il recupero delle utenze UD (Id&A)
pst_utenze_UD_idea_with_count: str = """
            SELECT *, COUNT(*) OVER() AS total_count
            FROM etl.utenze_tia_domestiche_idea
            ORDER BY id_utenza
            LIMIT :limit
            OFFSET :offset
           """
# Query unificata per il recupero delle utenze UND (Id&A)
pst_utenze_UND_idea_with_count: str = """
            SELECT *, COUNT(*) OVER() AS total_count
            FROM etl.utenze_tia_non_domestiche_idea
            ORDER BY id_utenza
            LIMIT :limit
            OFFSET :offset
           """





################

# utenze per civico (query più complesse, con raggruppamenti e total count separato)

# Query per il recupero delle utenze domestiche per civico (paginata)
pst_utenze_domestiche_per_civico: str = """
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


# Query per il total count delle utenze domestiche per civico
pst_utenze_domestiche_per_civico_total_count: str = """
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


# Query per il recupero delle utenze non domestiche per civico (paginata)
pst_utenze_non_domestiche_per_civico: str = """
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

# Query per il total count delle utenze non domestiche per civico
pst_utenze_non_domestiche_per_civico_total_count: str = """
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