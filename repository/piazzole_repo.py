def prepared_statement_piazzole() -> str:
    """Preparazione della query per il recupero delle piazzole con filtri opzionali(pap,via,comune,municipio)"""
    return  """
		with queryPiazzole as (
        select p.id_piazzola ,v.id_via, v.nome as via, c.id_comune, c.descr_comune as comune,m.id_municipio, m.descrizione as municipio,
        q.nome  as quartiere, p.numero_civico,
        p.riferimento, p.note, string_agg(concat(foo.num, ' x ', foo.descrizione),',') as elementi,
        case 
        when (select count(id_elemento) from elem.elementi where id_piazzola = p.id_piazzola) = 
        (select count(id_elemento) from elem.elementi_privati where id_elemento in
            (select id_elemento from elem.elementi where id_piazzola = p.id_piazzola)
        )  then 1
        else 0
        end pap,
        (select count(id_elemento) from elem.elementi where id_piazzola = p.id_piazzola) as num_elementi,
        (select count(id_elemento) from elem.elementi_privati where id_elemento in
            (select id_elemento from elem.elementi where id_piazzola = p.id_piazzola)
        ) as num_elementi_privati,
        st_y(st_transform(p2.geoloc,4326)) as lat, st_x(st_transform(p2.geoloc,4326)) as lon
        from elem.piazzole p 
        join geo.piazzola p2 on p.id_piazzola = p2.id
        join elem.aste a on a.id_asta = p.id_asta
        join topo.vie v on v.id_via = a.id_via  
        join topo.comuni c on v.id_comune = c.id_comune 
        left join topo.quartieri q on a.id_quartiere = q.id_quartiere
        left join topo.municipi m on m.id_municipio = q.id_municipio
        join (
        SELECT count(e.id_elemento) as num , t.nome, t.descrizione, t.tipo_rifiuto, t.tipo_elemento, t.volume,
            te.tipologia_elemento, te.descrizione as descrizione_tipologia,
            tr.nome as nome_rifiuto, tr.colore as colore_rifiuto, p.id_piazzola,
                    string_agg(e.id_elemento::text, ','::text) AS elementi
                FROM elem.elementi e
            JOIN elem.tipi_elemento t ON e.tipo_elemento = t.tipo_elemento
            JOIN elem.tipi_rifiuto tr ON tr.tipo_rifiuto = t.tipo_rifiuto
            JOIN elem.tipologie_elemento te ON t.tipologia_elemento = te.tipologia_elemento
            JOIN elem.piazzole p ON e.id_piazzola = p.id_piazzola
            GROUP BY t.tipo_elemento, tr.tipo_rifiuto, te.tipologia_elemento, p.id_piazzola 
            ORDER BY tr.nome, t.descrizione
        ) as foo on p.id_piazzola =foo.id_piazzola
        where p.data_eliminazione is null
        group by p.id_piazzola, v.nome,v.id_via, p.numero_civico,
        p.riferimento, p.note, p2.geoloc, c.descr_comune,c.id_comune,q.nome, m.descrizione,m.id_municipio)
        -- query sulla cte
		select * from queryPiazzole 
		where (:pap IS NULL OR pap = :pap)
		and(:via is null or id_via = :via)
		and(:comune is null or id_comune = :comune)
		and(:municipio is null or id_municipio = :municipio)
        limit coalesce(:limit, 10000) 
        offset coalesce(:offset,0)
    """

def prepared_statement_piazzole_with_count() -> str:
    """Query unificata per il recupero delle piazzole con conteggio totale e filtri opzionali."""
    return """
        WITH queryPiazzole AS (
            SELECT p.id_piazzola, v.id_via, v.nome AS via, c.id_comune, c.descr_comune AS comune, m.id_municipio, m.descrizione AS municipio,
                   q.nome AS quartiere, p.numero_civico, p.riferimento, p.note,
                   string_agg(concat(foo.num, ' x ', foo.descrizione), ',') AS elementi,
                   CASE 
                       WHEN (SELECT COUNT(id_elemento) FROM elem.elementi WHERE id_piazzola = p.id_piazzola) = 
                            (SELECT COUNT(id_elemento) FROM elem.elementi_privati WHERE id_elemento IN
                             (SELECT id_elemento FROM elem.elementi WHERE id_piazzola = p.id_piazzola))
                       THEN 1
                       ELSE 0
                   END AS pap,
                   (SELECT COUNT(id_elemento) FROM elem.elementi WHERE id_piazzola = p.id_piazzola) AS num_elementi,
                   (SELECT COUNT(id_elemento) FROM elem.elementi_privati WHERE id_elemento IN
                    (SELECT id_elemento FROM elem.elementi WHERE id_piazzola = p.id_piazzola)) AS num_elementi_privati,
                   ST_Y(ST_Transform(p2.geoloc, 4326)) AS lat, ST_X(ST_Transform(p2.geoloc, 4326)) AS lon
            FROM elem.piazzole p 
            JOIN geo.piazzola p2 ON p.id_piazzola = p2.id
            JOIN elem.aste a ON a.id_asta = p.id_asta
            JOIN topo.vie v ON v.id_via = a.id_via  
            JOIN topo.comuni c ON v.id_comune = c.id_comune 
            LEFT JOIN topo.quartieri q ON a.id_quartiere = q.id_quartiere
            LEFT JOIN topo.municipi m ON m.id_municipio = q.id_municipio
            JOIN (
                SELECT COUNT(e.id_elemento) AS num, t.nome, t.descrizione, t.tipo_rifiuto, t.tipo_elemento, t.volume,
                       te.tipologia_elemento, te.descrizione AS descrizione_tipologia,
                       tr.nome AS nome_rifiuto, tr.colore AS colore_rifiuto, p.id_piazzola,
                       string_agg(e.id_elemento::text, ','::text) AS elementi
                FROM elem.elementi e
                JOIN elem.tipi_elemento t ON e.tipo_elemento = t.tipo_elemento
                JOIN elem.tipi_rifiuto tr ON tr.tipo_rifiuto = t.tipo_rifiuto
                JOIN elem.tipologie_elemento te ON t.tipologia_elemento = te.tipologia_elemento
                JOIN elem.piazzole p ON e.id_piazzola = p.id_piazzola
                GROUP BY t.tipo_elemento, tr.tipo_rifiuto, te.tipologia_elemento, p.id_piazzola 
                ORDER BY tr.nome, t.descrizione
            ) AS foo ON p.id_piazzola = foo.id_piazzola
            WHERE p.data_eliminazione IS NULL
            GROUP BY p.id_piazzola, v.nome, v.id_via, p.numero_civico, p.riferimento, p.note, p2.geoloc, c.descr_comune, c.id_comune, q.nome, m.descrizione, m.id_municipio
        )
        SELECT (SELECT COUNT(*) FROM queryPiazzole) AS total_count, *
        FROM queryPiazzole
        WHERE (:pap IS NULL OR pap = :pap)
          AND (:via IS NULL OR id_via = :via)
          AND (:comune IS NULL OR id_comune = :comune)
          AND (:municipio IS NULL OR id_municipio = :municipio)
        LIMIT COALESCE(:limit, 10000)
        OFFSET COALESCE(:offset, 0);
    """
