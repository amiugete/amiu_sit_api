

def prepared_statement_comuni() -> str:
    """Preparazione della query per il recupero dei comuni con filtri opzionali(id_ambito, cod_istat)"""
    return  """
      select id_comune, descr_comune, descr_provincia, prefisso_utenti, id_ambito, cod_istat
      from topo.comuni c 
      where (:id_ambito is null  or c.id_ambito = :id_ambito)
      and (:cod_istat is null or cod_istat = :cod_istat)
    """

