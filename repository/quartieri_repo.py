

# Preparazione della query per il recupero dei quartieri con filtri opzionali(id_municipio)
pst_quartieri: str = """
          select q.id_quartiere, 
          q.id_municipio, 
          q.id_comune, 
          nome as descrizione
          from topo.quartieri q
          where (:id_municipio is null or q.id_municipio = :id_municipio)
            """

