


# Query per il recupero delle macro categorie utenze
pst_macro_categorie: str = """
       SELECT DISTINCT
       CASE
	   WHEN NOT ( (   i.categoria IN (90, 300, 301)
                       OR (    i.categoria = 3
                           AND i.utilizzo IN (85, 86, 137)
                           AND i.superficie < 80)))
            AND i.categoria NOT IN (97) THEN 'NON DOMESTICHE'
       WHEN i.categoria IN (90, 300, 301)
                 OR (    i.categoria = 3
                     AND i.utilizzo IN (85, 86, 137)
                     AND i.superficie < 80)
       THEN 'DOMESTICHE'
       ELSE 'NC'
       END AS CLASSIFICAZIONE,
       CATEGORIA, DESCR_CATEGORIA, UTILIZZO, DESCR_UTILIZZO FROM strade.PP_IMMOBILI i
       where i.stato_utenza =2
       ORDER BY 1,2
    """