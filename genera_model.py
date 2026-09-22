#!/usr/bin/env python3
"""
generate_model.py – utility that creates Pydantic models from a SQL query.
"""

import sys, os, re
from decimal import Decimal
from datetime import datetime, date, time
from config.database import DbConnection, _ENGINE_MAP
from sqlalchemy import text

# ---------------------------------------------------------------------------
# Mappatura tipo Python → annotazione Pydantic (identica al originale)
# ---------------------------------------------------------------------------
_PY_TO_PYDANTIC = {
    int: "int",
    float: "float",
    str: "str",
    bool: "bool",
    datetime: "datetime",
    date: "date",
    time: "str",          # non è importato → usiamo stringa
    Decimal: "float",
    bytes: "bytes",
}

_EXTRA_IMPORTS = {
    "date":  "from datetime import date",
    "datetime":"from datetime import datetime",
}

_FIELDS_TO_SKIP = {"total_count"}

# ---------------------------------------------------------------------------
# Helpers (unchanged)
# ---------------------------------------------------------------------------

def _pydantic_type(value):
    if value is None:
        return "Any", True
    return _PY_TO_PYDANTIC.get(type(value), "Any"), False


def _wrap_limit(sql: str, db):
    sql = sql.strip().rstrip(";")
    is_cte = sql.upper().lstrip().startswith("WITH")

    if db == DbConnection.STRADE:
        if is_cte:
            return f"{sql} FETCH FIRST 1 ROW ONLY"
        return f"SELECT * FROM ({sql}) subq__ WHERE ROWNUM <= 1"
    else:                         # PostgreSQL
        if is_cte:
            return f"{sql} LIMIT 1"
        return f"SELECT * FROM ({sql}) AS q__ LIMIT 1"


def _execute(sql: str, db):
    try:
        engine = _ENGINE_MAP[db]()
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            row = dict(result.mappings().first())
        return columns, row
    except Exception as exc:
        print(f"\n[ERRORE] Connessione/query [{db.value}]: {exc}")
        return [], None


# ---------------------------------------------------------------------------
# ----------  MODEL GENERATION ----------
# ---------------------------------------------------------------------------

def _generate_model(name: str, columns: list[str], row: dict) -> str:
    """
    Genera la classe Pydantic da un risultato di query (una sola riga).
    Tutti i campi sono `Optional[tipo] = None` per massima compatibilità.
    """
    lines = [f"class {name}(BaseModel):"]

    visible = [c for c in columns if c not in _FIELDS_TO_SKIP]
    if not visible:
        lines.append("   pass")
    else:
        for col in visible:
            val = row.get(col) if row else None
            pydantic_type, _ = _pydantic_type(val)
            lines.append(f"   {col}: Optional[{pydantic_type}] = None")

    return "\n".join(lines) + "\n"


def main():
    print("\n=== Generatore Pydantic da Query (modalità rapida) ===")

    # 1️⃣  Nome classe modello
    while True:
        name = input("\nNome classe modello (es. MioRisultato): ").strip()
        if name and name.isidentifier():
            break

    # 2️⃣  Connessione DB
    from config.database import DbConnection, _ENGINE_MAP   # <-- same module
    dbs = list(DbConnection)
    print("\nConnessioni disponibili:")
    for i, db in enumerate(dbs, 1):
        print(f"  {i}. {db.value}")

    while True:
        raw = input("Seleziona connessione [numero]: ").strip()
        try:
            db_conn = dbs[int(raw) - 1]
            break
        except (ValueError, IndexError):
            print("Scelta non valida.")

    # 3️⃣  Query SQL (unica riga, LIMIT 1)
    print("\nInserisci la query SQL. Invio su riga vuota = fine input.")
    sql_lines = []
    while True:
        line = input("  ")
        if not line:
            break
        sql_lines.append(line)

    if not sql_lines:
        print("Query vuota → uscita.")
        sys.exit(1)

    sql = " ".join(sql_lines).strip()
    wrapped = _wrap_limit(sql, db_conn)
    columns, row = _execute(wrapped, db_conn)

    if not columns:
        print("Impossibile recuperare i metadati. Controlla la query.")
        sys.exit(1)

    # 4️⃣  Anteprima del modello
    code = _generate_model(name, columns, row)
    print("\n=== Modello generato ===")
    print("─" * 40)
    print(code.strip())
    print("─" * 40)

    # 5️⃣  Scrivi il modello in `models/models.py`
    models_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "models", "models.py"
    )
    confirm = input(f"\nAggiungere `{name}` in coda a {os.path.basename(models_path)}? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operazione annullata.")
        sys.exit(0)

    with open(models_path, "a", encoding="utf-8") as f:
        f.write(code)          # <-- solo il modello, niente commenti extra

    print(f"\n✅  Classe '{name}' aggiunta a {os.path.basename(models_path)}")

if __name__ == "__main__":
    main()
