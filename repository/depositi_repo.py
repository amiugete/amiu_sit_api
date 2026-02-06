
def prepared_statement_depositi() -> str:
    """
    Prepara la query per recuperare le Unità Territoriali e le Rimesse, 
    con supporto per paginazione e filtro sulla data di ultima modifica.
    """
    return """
        SELECT *, COUNT(*) OVER() as total_count 
        FROM (
            -- Parte 1: Rimessa
            SELECT 
                e.id_elemento as id_ut,
                concat('RIMESSA - Rif. ', e.riferimento, ' (', e.note,')') as descrizione, 
                st_x(st_transform(r.geoloc, 4326)) as long,
                st_y(st_transform(r.geoloc, 4326)) as lat, 
                100 as raggio, 
                coalesce(to_char(data_inserimento, 'YYYYMMDD'), '19700101') as data_inizio,
                to_char(least(r.data_eliminazione, e.data_eliminazione), 'YYYYMMDD') as data_fine, 
                coalesce(to_char(greatest(r.data_ultima_modifica, e.data_ultima_modifica), 'YYYYMMDD'), '19700101') as data_ultima_modifica
            FROM (
                SELECT id_elemento, riferimento, note, data_inserimento, NULL AS data_eliminazione, data_ultima_modifica 
                FROM elem.elementi 
                WHERE tipo_elemento = 128 /*rimessa*/
                UNION 
                SELECT id_elemento, riferimento, note, data_inserimento, data_eliminazione, data_ultima_modifica 
                FROM history.elementi 
                WHERE tipo_elemento = 128
            ) e
            JOIN (
                SELECT id, geoloc, data_ultima_modifica, NULL AS data_eliminazione FROM geo.rimesse
                UNION 
                SELECT id, geoloc, data_ultima_modifica, data_eliminazione FROM history.rimesse 
            ) r ON e.id_elemento = r.id 

            UNION 

            -- Parte 2: Unità Territoriali (UT)
            SELECT 
                e.id_elemento as id_ut,
                concat('UT - Rif. ', e.riferimento, ' (', e.note,')') as descrizione, 
                st_x(st_transform(ut.geoloc, 4326)) as long,
                st_y(st_transform(ut.geoloc, 4326)) as lat, 
                60 as raggio, 
                coalesce(to_char(data_inserimento, 'YYYYMMDD'), '19700101') as data_inizio,
                to_char(least(ut.data_eliminazione, e.data_eliminazione), 'YYYYMMDD') as data_fine, 
                to_char(greatest(ut.data_ultima_modifica, e.data_ultima_modifica), 'YYYYMMDD') as data_ultima_modifica
            FROM (
                SELECT id_elemento, riferimento, note, data_inserimento, NULL AS data_eliminazione, data_ultima_modifica 
                FROM elem.elementi 
                WHERE tipo_elemento = 166 /*UT*/
                UNION 
                SELECT id_elemento, riferimento, note, data_inserimento, data_eliminazione, data_ultima_modifica 
                FROM history.elementi 
                WHERE tipo_elemento = 166
            ) e
            JOIN (
                SELECT id, geoloc, data_ultima_modifica, NULL AS data_eliminazione FROM geo.unita_territoriali 
                UNION 
                SELECT id, geoloc, data_ultima_modifica, data_eliminazione FROM history.unita_territoriali 
            ) ut ON e.id_elemento = ut.id 
        ) a 

        WHERE (:last_update IS NULL OR greatest(a.data_inizio, a.data_fine, a.data_ultima_modifica) >= :last_update)
        ORDER BY 1 
        LIMIT :limit
        OFFSET :offset
    """
