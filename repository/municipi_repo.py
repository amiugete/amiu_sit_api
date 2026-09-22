
# Query per il recupero dei municipi di Genova
pst_municipi_genova: str = """
        SELECT 
            mac.codice_municipio::int AS id_municipio, 
            1 AS id_comune,
            nome_municipio AS descrizione
        FROM geo.municipi_area_comune mac
    """
