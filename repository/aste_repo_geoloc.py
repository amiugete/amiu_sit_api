def prepared_statement_aste_geoloc() -> str:
    """Preparazione della query per il recupero delle aste data la circoscrizione con filtri opzionali(municipio(circoscrizione),via,last_update)
       con paginazione e total_count.
    """
    return  """
            SELECT id_asta, id_via, id_quartiere, id_circoscrizione as id_municipio,
              lung_asta as lung_db_m,
              round(st_length(geoloc)) as lungh_geom_m,
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



def prepared_statement_aste_mobile() -> str:
    """
    Aste per app mobile sit
    """
    return  """
       SELECT 
            a.id_asta,
            a.id_via, 
            a.id_circoscrizione AS id_municipio,
            a.id_quartiere, 
            a.lung_asta AS lung_db_m,
            ROUND(ST_Length(g.geoloc)) AS lungh_geom_m,
            TO_CHAR(GREATEST(g.data_ultima_modifica, a.data_ultima_modifica), 'YYYYMMDDHH24MI') AS data_last_update,
            -- Calcolo della data eliminazione combinata
            TO_CHAR(LEAST(COALESCE(a.dt_elim, g.dt_elim), COALESCE(g.dt_elim, a.dt_elim)), 'YYYYMMDDHH24MI') AS data_eliminazione,
            ST_AsGeoJSON(ST_Transform(g.geoloc, 4326)) AS geom
         FROM (
            -- Sottoquery G
            SELECT id, geoloc, data_ultima_modifica, NULL::timestamp AS dt_elim FROM geo.grafostradale
            UNION ALL
            SELECT id, geoloc, data_ultima_modifica, data_eliminazione AS dt_elim FROM history.grafostradale
         ) g
         JOIN (
            -- Sottoquery A
            SELECT id_asta, id_via, id_quartiere, id_circoscrizione, lung_asta, data_ultima_modifica, NULL::timestamp AS dt_elim FROM elem.aste
            UNION ALL
            SELECT id_asta, id_via, id_quartiere, id_circoscrizione, lung_asta, data_ultima_modifica, data_eliminazione AS dt_elim FROM history.aste
         ) a ON a.id_asta = g.id
         -- Filtra se ALMENO una delle due date (Asta o Grafo) è successiva al parametro
          WHERE (:id_via IS NULL OR a.id_via = :id_via)
          AND (:data_ultima_modifica IS NULL OR TO_CHAR(GREATEST(COALESCE(a.dt_elim, '1900-01-01'::timestamp), COALESCE(g.dt_elim, '1900-01-01'::timestamp)), 'YYYYMMDDHH24MI') > :data_ultima_modifica
               OR TO_CHAR(GREATEST(a.data_ultima_modifica, g.data_ultima_modifica), 'YYYYMMDDHH24MI') > :data_ultima_modifica)
            """
