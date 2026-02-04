def prepared_statement_mappe() -> str:
    """Preparazione della query per il recupero delle mappe"""
    return  """
            select title as titolo, descrizione from geo.api_layers
            """
