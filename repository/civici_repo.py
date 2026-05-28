

# Query per il recupero dei civici con paginazione
pst_civici: str = """
               WITH data AS (
           SELECT cc.cod_civico, 
           numero::int, 
           lettera,
           colore, 
           testo,
           cod_strada,
           v.nome AS nome_via,
           1 AS id_comune, 
           id_municipio, 
           g.id_quartiere,
           ST_Y(ST_Transform(geoloc, 4326)) AS lat,
           ST_X(ST_Transform(geoloc, 4326)) AS lon,
           cc.ins_date AS insert_date,
           cc.mod_date AS update_date
           FROM etl.civici_comune cc
           LEFT JOIN topo.vie v ON v.id_via = cc.cod_strada
           LEFT JOIN LATERAL (
           SELECT id_quartiere
           FROM geo.v_grafostradale g
           ORDER BY g.geoloc <-> cc.geoloc
           LIMIT 1
    ) g ON true
    WHERE (:id_municipio IS NULL OR id_municipio = :id_municipio)
      AND (:id_via IS NULL OR cc.cod_strada = :id_via)
      AND (:ins_date IS NULL OR cc.ins_date >= TO_DATE(:ins_date, 'YYYYMMDD'))
    ORDER BY id_municipio ASC, v.nome ASC, numero::int ASC, lettera ASC
    LIMIT COALESCE(:limit, 10000)
    OFFSET COALESCE(:offset, 0)
)
SELECT (SELECT COUNT(*) 
        FROM etl.civici_comune cc
        WHERE (:id_municipio IS NULL OR id_municipio = :id_municipio)
          AND (:id_via IS NULL OR cc.cod_strada = :id_via)
          AND (:ins_date IS NULL OR cc.ins_date >= TO_DATE(:ins_date, 'YYYYMMDD'))
       ) AS total_count,
       data.*
FROM data
    """