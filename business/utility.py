

from typing import List, Optional


def get_total_count_from_rows(rows: Optional[List[dict]], count_key: str = "total_count") -> int:
    """Estrae il conteggio totale da una lista di dizionari, restituendo 0 se la chiave non è presente o se la lista è vuota."""
    if not rows or count_key not in rows[0]:
        return 0
    return rows[0][count_key]