

def prepared_statement_quartieri() -> str:
    """Preparazione della query per il recupero dei quartieri con filtri opzionali(id_municipio)"""
    return  """
          select q.id_quartiere, 
          q.id_municipio, 
          q.id_comune, 
          nome as descrizione
          from topo.quartieri q
          where (:id_municipio is null or q.id_municipio = :id_municipio)
            """

