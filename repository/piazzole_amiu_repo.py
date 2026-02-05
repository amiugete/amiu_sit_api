

def prepared_statement_piazzole_amiu() -> str:
    """Preparazione della query per il recupero dei posteriori con filtri opzionali(pap,via,comune,municipio)"""
    return  """
              SELECT *,CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
              from
                (select 
                p.id_piazzola, 
                v.nome AS via, 
                p.numero_civico, 
                p.riferimento,
                p.note,
                st_y(st_transform(p2.geoloc,4326)) AS lat,
                st_x(st_transform(p2.geoloc,4326)) AS lon,
                coalesce(to_char(p.data_inserimento, 'YYYYMMDD'), '19700101') AS data_inserimento, 
                to_char(p.data_eliminazione, 'YYYYMMDD') AS data_eliminazione, 
                coalesce(
                  to_char(greatest(p.data_ultima_modifica, p2.data_ultima_modifica, p.data_eliminazione), 'YYYYMMDD'), 
                  '19700101'
                ) AS data_ultima_modifica
              FROM elem.piazzole p 
              JOIN elem.aste a ON a.id_asta = p.id_asta 
              JOIN topo.vie v ON v.id_via = a.id_via 
              JOIN geo.piazzola p2 ON p2.id = p.id_piazzola
              WHERE 
              (:last_update IS NULL OR greatest(p.data_inserimento, p.data_ultima_modifica,
              p2.data_ultima_modifica,
                p.data_eliminazione) >= to_date(:last_update, 'YYYYMMDD'))
                ) sub
              ORDER BY id_piazzola
              limit :limit
              offset :offset
"""

