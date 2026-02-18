def prepared_statement_aste_geoloc() -> str:
    """Preparazione della query per il recupero delle aste data la circoscrizione con filtri opzionali(municipio(circoscrizione),via,last_update)
       con paginazione e total_count.
    """
    return  """
            SELECT id_asta, id_via, id_quartiere, id_circoscrizione as id_municipio,
              lung_asta as lung_db_m,
              transitabilita, nome_via,
              TO_CHAR(data_ultima_modifica, 'YYYYMMDD') AS last_update,
              ST_AsGeoJSON(ST_Transform(geoloc, 4326)) AS geometry,
              CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
              FROM GEO.V_GRAFOSTRADALE
              WHERE (:last_update IS NULL OR data_ultima_modifica::date >= TO_DATE(:last_update, 'YYYYMMDD'))
              AND (:id_via IS NULL OR id_via = :id_via)
              AND (:id_municipio IS NULL OR id_circoscrizione = :id_municipio)
              LIMIT :limit
              OFFSET :offset
	        """