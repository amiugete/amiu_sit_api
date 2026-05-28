

# Preparazione della query per il recupero dei point of interest
pst_pointofinterest: str = """
        select id_elemento as id, nome as via, numero_civico, 
        riferimento, note, lat, lon, tipo from idea.v_poi
        order by tipo
            """

