
        # Query aggiornata per percorsi posteriori (come da richiesta)
def prepared_statement_percorsi_posteriori_aggiornata() -> str:
        """Query per elenco deglui elementi posteriori, con paginazione, filtro last_update e total_count."""
        return """
            SELECT DISTINCT codice_modello_servizio AS cod_percorso, ordine, codice AS id_elemento, frequenza AS id_frequenza,
                fo.descrizione_long, data_inizio, data_fine, id_asta_percorso, ripasso, ep.freq_settimane AS periodicita,
                to_char(dmi.data_ultima_modifica, 'YYYYMMDD') AS data_ultima_modifica,
                CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
            FROM (
                SELECT codice_modello_servizio, ordine, objecy_type, codice, quantita, lato_servizio, percent_trattamento, frequenza,
                    ripasso, numero_passaggi, replace(replace(coalesce(nota,''),'DA PIAZZOLA',''),';', ' - ') AS nota,
                    codice_qualita, codice_tipo_servizio, data_inizio, coalesce(data_fine, '20991231') AS data_fine, id_asta_percorso
                FROM anagrafe_percorsi.v_percorsi_elementi_tratti WHERE data_inizio < coalesce(data_fine, '20991231')
                UNION
                SELECT codice_modello_servizio, ordine, objecy_type, codice, quantita, lato_servizio, percent_trattamento, frequenza,
                    ripasso, numero_passaggi, replace(replace(coalesce(nota,''),'DA PIAZZOLA',''),';', ' - ') AS nota,
                    codice_qualita, codice_tipo_servizio, data_inizio, coalesce(data_fine, '20991231') AS data_fine, id_asta_percorso
                FROM anagrafe_percorsi.v_percorsi_elementi_tratti_ovs WHERE data_inizio < coalesce(data_fine, '20991231')
                UNION
                SELECT codice_modello_servizio, ordine, objecy_type, codice, quantita, lato_servizio, percent_trattamento, frequenza,
                    ripasso, numero_passaggi, replace(replace(coalesce(nota,''),'DA PIAZZOLA',''),';', ' - ') AS nota,
                    codice_qualita, codice_tipo_servizio, data_inizio, coalesce(data_fine, '20991231') AS data_fine, id_asta_percorso
                FROM anagrafe_percorsi.mv_percorsi_elementi_tratti_dismessi WHERE data_inizio < coalesce(data_fine, '20991231')
            ) tab
            JOIN etl.frequenze_ok fo ON fo.cod_frequenza = tab.frequenza
            LEFT JOIN anagrafe_percorsi.date_modifica_itinerari dmi ON dmi.cod_percorso = tab.codice_modello_servizio
            JOIN anagrafe_percorsi.elenco_percorsi ep ON ep.cod_percorso = tab.codice_modello_servizio
                AND ep.versione_testata = (
                    SELECT max(versione_testata) FROM anagrafe_percorsi.elenco_percorsi ep2 WHERE cod_percorso = tab.codice_modello_servizio
                )
            JOIN anagrafe_percorsi.anagrafe_tipo at2 ON at2.id = ep.id_tipo
            JOIN anagrafe_percorsi.percorsi_ut pu ON pu.cod_percorso = ep.cod_percorso
                AND (pu.data_attivazione = ep.data_inizio_validita OR pu.data_disattivazione = ep.data_fine_validita)
                AND pu.solo_visualizzazione = 'N' AND pu.data_attivazione < pu.data_disattivazione
            JOIN anagrafe_percorsi.cons_mapping_uo cmu ON cmu.id_uo = pu.id_ut
            JOIN topo.ut u ON u.id_ut = cmu.id_uo_sit
            WHERE tab.codice_tipo_servizio = 'RACC'
                AND at2.id_servizio_sit IN (
                    SELECT id_servizio FROM elem.servizi s
                    WHERE riempimento = 1
                        AND id_servizio IN (
                            SELECT id_servizio FROM elem.elementi_servizio es WHERE tipo_elemento IN (
                                SELECT tipo_elemento FROM elem.tipi_elemento te WHERE tipologia_elemento IN ('P', 'T')
                            )
                        )
                )
                AND u.id_zona IN (1,2,3,5,6)
                AND (:last_update IS NULL OR dmi.data_ultima_modifica >= to_date(:last_update, 'YYYYMMDD'))
            ORDER BY codice_modello_servizio, ordine, codice, data_inizio, ripasso
            LIMIT :limit
            OFFSET :offset
        """
        


