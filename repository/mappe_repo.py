# Preparazione della query per il recupero delle mappe
pst_mappe: str = """
        select title as titolo, descrizione from geo.api_layers
        """
