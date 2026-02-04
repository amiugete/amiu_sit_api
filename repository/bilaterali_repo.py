def prepared_statement_bilaterali_albero() -> str:
    """Query unificata per il recupero dell'albero dei percorsi dei bilaterali."""
    return """
                select * from  
                (
                    select * from etl.v_percorsi_bilaterali_1
                    union 
                    select * from etl.v_percorsi_bilaterali_2
                    union 
                    select * from etl.v_percorsi_bilaterali_3
                    union
                    select * from etl.v_percorsi_bilaterali_4
                    union 
                    select * from etl.v_percorsi_bilaterali_5
                ) a
                order by coalesce(id_padre,0),
                    CASE 
                        WHEN descrizione  = 'Lun' THEN 1
                        WHEN descrizione  = 'Mar' THEN 2
                        WHEN descrizione = 'Mer' THEN 3
                        WHEN descrizione = 'Gio' THEN 4
                        WHEN descrizione = 'Ven' THEN 5
                        WHEN descrizione = 'Sab' THEN 6
                        WHEN descrizione = 'Dom' THEN 7
                        else  0
                    end
              """

def prepared_statement_bilaterali() -> str:
    """Query unificata per il recupero dei percorsi dei bilaterali."""
    return """
            select f.id_area as id_padre, 
                ut_responsabile, 
                id_tipo_rifiuto, 
                tipi_rifiuto, 
                desc_turno, 
                id_percorso_ok as id_percorso, 
                cod_percorso,
                concat(desc_percorso, ' (',frequenza,')') as desc_percorso, 
                frequenza
            from etl.v_percorsi_bilaterali_giorno a
            join etl.v_percorsi_bilaterali_5 f on f.descrizione = a.frequenza
            join etl.v_percorsi_bilaterali_4 e on e.descrizione = concat(a.cod_percorso, ' - ', a.desc_percorso) and e.id_area = f.id_padre
            join etl.v_percorsi_bilaterali_3 d on d.descrizione = a.desc_turno and d.id_area = e.id_padre
            join etl.v_percorsi_bilaterali_2 c on c.descrizione = a.tipi_rifiuto and c.id_area = d.id_padre
            join etl.v_percorsi_bilaterali_1 b on b.descrizione = a.ut_responsabile and b.id_area = c.id_padre
            group by f.id_area, ut_responsabile, id_tipo_rifiuto, tipi_rifiuto, desc_turno, id_percorso_ok, 
            cod_percorso, desc_percorso, frequenza
              """

def prepared_statement_percorso_dettaglio() -> str:
    """Query unificata per il recupero dei percorsi dei bilaterali."""
    return """
        select
            row_number() OVER (order by ap2.num_seq) AS seq,
            e.id_piazzola, v.nome as via,
            p2.numero_civico as civ, p2.riferimento, p2.note as note_piazzola,
            te.nome as tipo_elem, count(distinct e.id_elemento) as num
        from elem.elementi_aste_percorso eap 
        join etl.frequenze_ok fo on fo.cod_frequenza = eap.frequenza::int 
        join elem.elementi e on e.id_elemento = eap.id_elemento 
        join elem.piazzole p2 on p2.id_piazzola = e.id_piazzola 
        join elem.aste a on a.id_asta = e.id_asta 
        join topo.vie v on v.id_via = a.id_via 
        join elem.tipi_elemento te on te.tipo_elemento = e.tipo_elemento 
        join elem.aste_percorso ap2  on ap2.id_asta_percorso = eap.id_asta_percorso 
        where eap.id_asta_percorso in ( 
            select id_asta_percorso 
            from elem.aste_percorso ap
            where id_percorso = :id and id_percorso in (select id_percorso from elem.percorsi where id_categoria_uso=3)
            -- qui può essere aggiunto un filtro opzionale per il giorno:
            -- and fo.descrizione_long ilike '%<giorno>%'
        )
        group by ap2.num_seq,
            e.id_piazzola, v.nome, p2.numero_civico, p2.riferimento, p2.note, te.nome
    """




