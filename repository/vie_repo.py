

def prepared_statement_vie() -> str:
    """Preparazione della query per il recupero delle vie con filtri opzionali(comune)"""
    return  """
        select id_via, nome, id_comune from topo.vie v
        where (:comune is null or id_comune = :comune)
        order by nome
        limit coalesce(:limit, 10000)
        offset coalesce(:offset,0)
    """
def prepared_statement_count_vie() -> str:
    """Preparazione della query per il recupero del numero di vie con filtri opzionali(comune)"""
    return  """
        select count(*) from topo.vie v
        where (:comune is null or id_comune = :comune)
    """
