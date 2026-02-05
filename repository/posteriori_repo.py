

def prepared_statement_posteriori_with_count() -> str:
    """Preparazione della query per il recupero dei posteriori con filtri opzionali(pap,via,comune,municipio)"""
    return  """
SELECT *,
       CASE WHEN :limit = 1000 AND :offset = 0 THEN 1000 ELSE COUNT(*) OVER() END AS total_count
FROM (
  SELECT
    ep.cod_percorso,
    ep.descrizione,
    at2.descrizione AS servizio,
    pu.id_ut,
    u.descrizione AS ut_rimessa,
    ep.freq_testata,
    fo.descrizione_long AS freq,
    ep.id_turno,
    t.descrizione AS turno,
    ep.codice_cer,
    TO_CHAR(pu.data_attivazione, 'YYYYMMDD') AS data_inizio_validita,
    TO_CHAR((pu.data_disattivazione - INTERVAL '1' DAY), 'YYYYMMDD') AS data_fine_validita,
    TO_CHAR(COALESCE(ep.data_ultima_modifica, '2023-07-27'), 'YYYYMMDD') AS data_ultima_modifica,
    ep.versione_testata,
    ep.freq_settimane AS periodicita,
    0 AS doppia_antenna
  FROM anagrafe_percorsi.elenco_percorsi ep
  JOIN anagrafe_percorsi.anagrafe_tipo at2
    ON (SELECT MAX(id_tipo)
        FROM anagrafe_percorsi.elenco_percorsi ep2
        WHERE ep2.cod_percorso = ep.cod_percorso) = at2.id
  JOIN etl.frequenze_ok fo ON fo.cod_frequenza = ep.freq_testata
  JOIN elem.turni t ON t.id_turno = ep.id_turno
  JOIN anagrafe_percorsi.percorsi_ut pu
    ON pu.cod_percorso = ep.cod_percorso
    AND (pu.data_attivazione = ep.data_inizio_validita OR pu.data_disattivazione = ep.data_fine_validita)
    AND pu.solo_visualizzazione = 'N'
    AND pu.data_attivazione < pu.data_disattivazione
  JOIN anagrafe_percorsi.cons_mapping_uo cmu ON cmu.id_uo = pu.id_ut
  JOIN topo.ut u ON u.id_ut = cmu.id_uo_sit
  WHERE (
      ep.cod_percorso IN (
        SELECT DISTINCT cod_percorso
        FROM anagrafe_percorsi.elenco_percorsi ep
        WHERE data_fine_validita >= NOW()::date
           OR data_ultima_modifica >= NOW()::date - INTERVAL '1' DAY
      )
      OR data_fine_validita >= NOW()::date - INTERVAL '1' MONTH
    )
    AND at2.id_servizio_sit IN (
      SELECT id_servizio
      FROM elem.servizi s
      WHERE riempimento = 1
        AND id_servizio IN (
          SELECT id_servizio
          FROM elem.elementi_servizio es
          WHERE tipo_elemento IN (
            SELECT tipo_elemento
            FROM elem.tipi_elemento te
            WHERE tipologia_elemento IN ('P', 'T')
          )
        )
    )
    AND u.id_zona IN (1, 2, 3, 5, 6)
    AND (:last_update IS NULL OR ep.data_ultima_modifica >= TO_DATE(:last_update, 'YYYYMMDD'))
  ORDER BY cod_percorso, ep.versione_testata
) sub
LIMIT :limit
OFFSET :offset
"""

