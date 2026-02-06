
def prepared_statement_point2area() -> str:
    """
    Prepara la query per trovare le informazioni di un'area (ambito, comune, zona, etc.)
    a partire da coordinate geografiche (lon, lat).
    """
    return """
        SELECT 
            a.id_ambito, 
            a.descr_ambito AS ambito,  
            cca.id AS id_comune, 
            c.descr_comune AS comune,
            -- Gestione logica per il comune di Genova (ID 1)
            CASE 
                WHEN c.id_comune = 1 THEN u.id_zona
                ELSE 6
            END AS id_zona,
            CASE 
                WHEN c.id_comune = 1 THEN za.cod_zona 
                ELSE (SELECT cod_zona FROM topo.zone_amiu WHERE id_zona = 6)
            END AS zona,
            CASE 
                WHEN c.id_comune = 1 THEN u.id_ut
                ELSE u2.id_ut 
            END AS id_ut,
            CASE 
                WHEN c.id_comune = 1 THEN u.descrizione
                ELSE u2.descrizione
            END AS ut,
            mac.codice_municipio AS id_municicio, 
            mac.nome_municipio AS municipio,
            CASE 
                WHEN c.id_comune = 1 THEN qa.id
                ELSE q.id_quartiere 
            END AS id_quartiere,
            CASE 
                WHEN c.id_comune = 1 THEN qa.descrizione
                ELSE q.nome 
            END AS quartiere
        FROM (
            -- Creazione del punto geografico dai parametri :lon e :lat
            SELECT 1 AS id, ST_Transform(ST_SetSRID(ST_Point(:lon, :lat), 4326), 3003) AS geom
        ) p
        JOIN geo.confini_comuni_area cca ON ST_Intersects(cca.geoloc, p.geom)
        JOIN topo.comuni c ON c.id_comune = cca.id
        JOIN topo.comuni_ut cu ON cu.id_comune = c.id_comune 
        JOIN topo.ut u2 ON u2.id_ut = cu.id_ut 
        JOIN topo.ambiti a ON c.id_ambito = a.id_ambito 
        LEFT JOIN geo.confini_ut_zona cuz ON ST_Intersects(cuz.geoloc, p.geom)
        LEFT JOIN topo.ut u ON u.descrizione = cuz.descrizione 
        LEFT JOIN topo.zone_amiu za ON za.id_zona = u.id_zona 
        LEFT JOIN geo.municipi_area_comune mac ON ST_Intersects(mac.geom, p.geom)
        LEFT JOIN geo.quartieri_area qa ON ST_Intersects(qa.geoloc, p.geom)
        LEFT JOIN topo.quartieri q ON q.id_comune = c.id_comune
    """
