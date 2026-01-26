

def prepared_statement_pointofinterest() -> str:
    """Preparazione della query per il recupero dei point of interest con filtri opzionali(id_municipio)"""
    return  """
        select id_elemento as id, nome as via, numero_civico, 
        riferimento, note, lat, lon, tipo from idea.v_poi
        order by tipo
            """

