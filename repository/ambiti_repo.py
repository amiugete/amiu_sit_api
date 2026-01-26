

def prepared_statement_ambiti() -> str:
    """Preparazione della query per il recupero degli ambiti"""
    return  """
            select id_ambito, descr_ambito from topo.ambiti a
            """

