
# Preparazione della query per le fasce di età con paginazione e filtri opzionali
pst_fasce_eta_with_count: str = """
        SELECT * FROM (
            SELECT a.*, ROWNUM AS rnum
            FROM (
                SELECT cod_civico, cod_via, n0_10, n11_20, n21_30, n31_40, n41_50, n51_60, n60_70, n70_80, npiu80,
                    COUNT(*) OVER() AS total_count
                FROM strade.anagrafe_resid_civici
                WHERE (cod_via = :id_via OR :id_via IS NULL)
                AND (cod_civico = :cod_civico OR :cod_civico IS NULL)
                ORDER BY cod_civico -- L'ordinamento è fondamentale per ROWNUM
            ) a
            WHERE ROWNUM <= (:offset + :limit) -- Limite superiore
                    )
        WHERE rnum > :offset
        """
