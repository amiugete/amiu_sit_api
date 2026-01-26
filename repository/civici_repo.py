

def prepared_statement_civici() -> str:
    """Preparazione della query per i civici  con filtri opzionali(id_municipio, id:_via)"""
    return  """
        select cc.cod_civico, 
        numero::int, 
        lettera,
        colore, 
        testo,
        cod_strada,
        v.nome as nome_via,
        1 as id_comune, 
        id_municipio, 
        g.id_quartiere,
        st_y(st_transform(geoloc,4326)) as lat,
        st_x(st_transform(geoloc,4326)) as lon,
        cc.ins_date as insert_date,
        cc.mod_date as update_date 
        from etl.civici_comune cc
        left join topo.vie v on v.id_via  = cc.cod_strada
        left join lateral (
          select id_quartiere
          from geo.v_grafostradale g
          order by g.geoloc <-> cc.geoloc
          limit 1
          ) g on true
        where (:id_municipio is null or id_municipio = :id_municipio)
        and (:id_via is null or cc.cod_strada= :id_via)
        order by id_municipio asc, v.nome asc, numero::int asc, lettera asc
        limit coalesce(:limit, 10000)
        offset coalesce(:offset,0)
    """
def prepared_statement_count_civici() -> str:
    """Preparazione della query per la count dei civici  con filtri opzionali(id_municipio, id:_via)"""
    return  """
        select count(*)
        from etl.civici_comune cc
        left join topo.vie v on v.id_via  = cc.cod_strada
        left join lateral (
          select id_quartiere
          from geo.v_grafostradale g
          order by g.geoloc <-> cc.geoloc
          limit 1
          ) g on true
        where (:id_municipio is null or id_municipio = :id_municipio)
        and (:id_via is null or cc.cod_strada= :id_via)
    """

