#!/usr/bin/env python3
"""
generate_model.py
-----------------
Utility per generare automaticamente classi Pydantic da query SQL.

Esegue la query sul database scelto (LIMIT 1 per efficienza), ispeziona i tipi
Python delle colonne restituite e aggiunge il modello generato in coda a
models/models.py.

Uso:
    python generate_servizio.py
"""

import sys
import os
import re
from decimal import Decimal
from datetime import datetime, date, time

# Rende importabili i moduli del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DbConnection, _ENGINE_MAP
from sqlalchemy import text

# ---------------------------------------------------------------------------
# Mappatura tipo Python → annotazione Pydantic
# ---------------------------------------------------------------------------
_PY_TO_PYDANTIC: dict[type, str] = {
    int:      "int",
    float:    "float",
    str:      "str",
    bool:     "bool",
    datetime: "datetime",
    date:     "date",
    time:     "str",       # 'time' non è importato in models.py → si usa str
    Decimal:  "float",
    bytes:    "bytes",
}

# Se viene rilevato uno di questi tipi, potrebbe servire un import aggiuntivo
_EXTRA_IMPORTS: dict[str, str] = {
    "date":     "from datetime import date",
    "datetime": "from datetime import datetime",
}

# Tipi selezionabili per parametri definiti dall'utente (query params / body)
_PARAM_TYPE_CHOICES: list[tuple[str, str]] = [
    ("str",      "str"),
    ("int",      "int"),
    ("float",    "float"),
    ("bool",     "bool"),
    ("date",     "date"),
    ("datetime", "datetime"),
    ("Any",      "Any"),
]

# Colonne da non includere nel modello (usate solo internamente dal framework)
_FIELDS_TO_SKIP: set[str] = {"total_count"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pydantic_type(value) -> tuple[str, bool]:
    """Restituisce (tipo_pydantic, is_none) dato un valore Python."""
    if value is None:
        return "Any", True
    return _PY_TO_PYDANTIC.get(type(value), "Any"), False


def _wrap_limit(sql: str, db: DbConnection) -> str:
    """
    Racchiude la query in una sotto-query LIMIT 1 / FETCH FIRST 1 ROW ONLY.
    Per query WITH CTE aggiunge il LIMIT direttamente in coda.
    """
    sql = sql.strip().rstrip(";")
    is_cte = sql.upper().lstrip().startswith("WITH")

    if db == DbConnection.STRADE:
        # Oracle: FETCH FIRST (standard SQL:2008, supportato da Oracle 12c+)
        if is_cte:
            return f"{sql} FETCH FIRST 1 ROW ONLY"
        return f"SELECT * FROM ({sql}) subq__ WHERE ROWNUM <= 1"
    else:
        # PostgreSQL
        if is_cte:
            return f"{sql} LIMIT 1"
        return f"SELECT * FROM ({sql}) AS q__ LIMIT 1"


def _extract_bind_params(sql: str) -> set[str]:
    """Estrae i parametri bind di tipo :name ignorando stringhe e cast ::."""
    params: set[str] = set()
    in_single = False
    in_double = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if in_single:
            if ch == "'":
                if i + 1 < len(sql) and sql[i + 1] == "'":
                    i += 1
                else:
                    in_single = False
        elif in_double:
            if ch == '"':
                if i + 1 < len(sql) and sql[i + 1] == '"':
                    i += 1
                else:
                    in_double = False
        else:
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            elif ch == ":" and i + 1 < len(sql) and sql[i + 1] != ":" and re.match(r"[A-Za-z_]", sql[i + 1]):
                j = i + 2
                while j < len(sql) and re.match(r"[A-Za-z0-9_]", sql[j]):
                    j += 1
                params.add(sql[i + 1:j])
                i = j - 1
        i += 1
    return params


def _execute(sql: str, db: DbConnection, params: dict | None = None) -> tuple[list[str], dict | None]:
    """
    Esegue la query e restituisce (nomi_colonne, prima_riga | None).
    I nomi colonne vengono estratti dal cursore anche se non ci sono righe.
    """
    try:
        engine = _ENGINE_MAP[db]()
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            columns = list(result.keys())
            row = result.mappings().first()
            return columns, dict(row) if row is not None else None
    except Exception as exc:
        print(f"\n[ERRORE] Connessione/query [{db.value}]: {exc}")
        return [], None


def _generate_class(name: str, columns: list[str], row: dict | None) -> str:
    """
    Genera il codice Python della classe Pydantic.
    Tutti i campi sono Optional[tipo] = None per massima compatibilità
    con i pattern già usati nel progetto.
    """
    lines = [f"\nclass {name}(BaseModel):"]

    visible = [c for c in columns if c not in _FIELDS_TO_SKIP]
    if not visible:
        lines.append("    pass")
    else:
        for col in visible:
            value = row.get(col) if row else None
            pydantic_type, _ = _pydantic_type(value)
            lines.append(f"    {col}: Optional[{pydantic_type}] = None")

    return "\n".join(lines) + "\n"


def _missing_imports(columns: list[str], row: dict | None, models_path: str) -> list[str]:
    """
    Restituisce gli import mancanti in models.py per i tipi rilevati.
    """
    with open(models_path, encoding="utf-8") as f:
        existing = f.read()
    needed = []
    for col in columns:
        value = row.get(col) if row else None
        pydantic_type, _ = _pydantic_type(value)
        imp = _EXTRA_IMPORTS.get(pydantic_type)
        if imp and imp not in existing:
            needed.append(imp)
    return list(set(needed))


def _generate_repo_content(repo_name: str, sql: str) -> str:
    """Genera il contenuto di un file di repository con la query SQL."""
    return (
        f"# Preparazione della query per il recupero di {repo_name}\n"
        f"pst_{repo_name}: str = \"\"\"\n"
        f"        {sql.strip()}\n"
        f"        \"\"\"\n"
    )


def _ask_param_type() -> str:
    """Chiede all'utente di selezionare il tipo di un parametro da una lista."""
    print("  Tipi disponibili:")
    for i, (label, _) in enumerate(_PARAM_TYPE_CHOICES, 1):
        print(f"    {i}. {label}")
    while True:
        raw = _ask("  Tipo [numero]: ").strip()
        try:
            return _PARAM_TYPE_CHOICES[int(raw) - 1][1]
        except (ValueError, IndexError):
            print("  Scelta non valida.")


def _ask_params_list(section_label: str) -> list[dict]:
    """
    Chiede all'utente di definire una lista di parametri (query params o campi body).
    Restituisce una lista di dict con chiavi: name, type, required.
    """
    params: list[dict] = []
    print(f"\nDefinisci i {section_label} (lascia il nome vuoto per terminare):")
    while True:
        p_name = _ask("  Nome parametro (vuoto per terminare): ").strip()
        if not p_name:
            break
        if not p_name.isidentifier():
            print("  Nome non valido: usa solo lettere, cifre e underscore.")
            continue
        p_type = _ask_param_type()
        req_raw = _ask(f"  '{p_name}' è obbligatorio? (s/n): ").strip().lower()
        params.append({
            "name":     p_name,
            "type":     p_type,
            "required": req_raw == "s",
        })
    return params


def _generate_request_body_model(model_name: str, fields: list[dict]) -> str:
    """Genera una classe Pydantic per il body della request."""
    lines = [f"\nclass {model_name}(BaseModel):"]
    if not fields:
        lines.append("    pass")
    else:
        for field in fields:
            f_name = field["name"]
            f_type = field["type"]
            f_req  = field.get("required", False)
            if f_req:
                lines.append(f"    {f_name}: {f_type}")
            else:
                lines.append(f"    {f_name}: Optional[{f_type}] = None")
    return "\n".join(lines) + "\n"


def _generate_router_header(
    model_name: str,
    repo_name: str,
    paginated: bool,
    body_model_name: str | None = None,
    extra_types: list[str] | None = None,
) -> str:
    """Genera gli import standard per un nuovo file router FastAPI."""
    paginated_import = ", PaginatedResponse" if paginated else ""

    # Import del modello response (e body se presente e distinto)
    if body_model_name and body_model_name != model_name:
        models_import_line = (
            f"from models.models import {model_name}, {body_model_name}{paginated_import}"
        )
    else:
        models_import_line = f"from models.models import {model_name}{paginated_import}"

    lines = [
        "from fastapi import APIRouter, Query, Depends, Request",
        "from business.permission import check_permissions",
        "from typing import Any, List, Optional, Union",
        "import logging",
    ]

    # Eventuali import aggiuntivi per date/datetime usati nei parametri
    for t in sorted(set(extra_types or [])):
        imp = _EXTRA_IMPORTS.get(t)
        if imp:
            lines.append(imp)

    lines += [
        "",
        "# helpers",
        "from business.query_helpers import execute_simple_query, execute_paginated_query",
        "",
        "# database",
        "from config.database import DbConnection",
        "",
        "# modelli",
        models_import_line,
        "",
        "# repository",
        f"from repository.pst_{repo_name} import pst_{repo_name}",
        "",
        "",
        'logger = logging.getLogger(__name__)',
        "router = APIRouter()",
        "",
    ]
    return "\n".join(lines)


def _generate_endpoint_imports(
    model_name: str,
    repo_name: str,
    target_content: str,
    body_model_name: str | None = None,
    has_query_params: bool = False,
    extra_types: list[str] | None = None,
) -> str:
    """Costruisce gli import mancanti per un endpoint in un router esistente."""
    imports: list[str] = []
    model_import = f"from models.models import {model_name}"
    repo_import = f"from repository.pst_{repo_name} import pst_{repo_name}"

    if model_import not in target_content:
        imports.append(model_import)
    if repo_import not in target_content:
        imports.append(repo_import)

    # Import del modello body se distinto dal modello response
    if body_model_name and body_model_name != model_name:
        body_import = f"from models.models import {body_model_name}"
        if body_import not in target_content:
            imports.append(body_import)

    # Assicura che Query sia importato da fastapi
    if has_query_params and not re.search(r"from fastapi import[^\n]*\bQuery\b", target_content):
        imports.append("from fastapi import Query")

    # Import date/datetime se usati nei parametri o nel body
    for t in sorted(set(extra_types or [])):
        imp = _EXTRA_IMPORTS.get(t)
        if imp and imp not in target_content:
            imports.append(imp)

    if not imports:
        return ""
    return "\n" + "\n".join(imports) + "\n"


def _generate_endpoint(
    model_name: str,
    endpoint_path: str,
    method: str,
    paginated: bool,
    db_conn: DbConnection,
    repo_name: str = "",
    query_params: list[dict] | None = None,
    body_model_name: str | None = None,
) -> str:
    """
    Genera il guscio di un endpoint FastAPI compatibile con i pattern del progetto.
    Il codice usa check_permissions, Request e (se paginato) execute_paginated_query,
    altrimenti execute_simple_query.
    """
    func_name = endpoint_path.strip("/").replace("/", "_").replace("-", "_")
    repo_var  = f"pst_{repo_name}" if repo_name else f"pst_{func_name}"
    db_enum   = f"DbConnection.{db_conn.name}"
    qps       = query_params or []

    if paginated:
        resp_model = f"Union[List[{model_name}], PaginatedResponse[{model_name}]]"
    else:
        resp_model = f"List[{model_name}]"

    lines = [
        f"\n\n##############################################################",
        f"@router.{method}(",
        f'    "/{endpoint_path.strip("/")}",',
        f"    response_model={resp_model},",
        f'    description="TODO: descrizione endpoint. Richiede autenticazione (Bearer Token)."',
        f")",
        f"def {func_name}(",
        f"    request: Request,",
    ]

    if paginated:
        lines += [
            '    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),',
            '    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),',
        ]

    # Query parameters definiti dall'utente
    for qp in qps:
        qp_name = qp["name"]
        qp_type = qp["type"]
        qp_req  = qp.get("required", False)
        if qp_req:
            lines.append(f'    {qp_name}: {qp_type} = Query(..., description="{qp_name}"),')
        else:
            lines.append(f'    {qp_name}: Optional[{qp_type}] = Query(None, description="{qp_name}"),')

    # Body della request
    if method == "post":
        if body_model_name:
            lines.append(f"    body: {body_model_name},")
        else:
            lines.append(
                f"    body: {model_name}Request,  # TODO: definire il modello request in models/models.py"
            )

    lines += [
        "    payload: dict[str, Any] = Depends(check_permissions)",
        "):",
    ]

    # Costruisce il dict parametri SQL dai query params
    if qps:
        pairs = ", ".join(f'"{qp["name"]}": {qp["name"]}' for qp in qps)
        params_dict = "{" + pairs + "}"
        params_comment = ""
    else:
        params_dict = "{}"
        params_comment = "  # TODO: aggiungi i parametri di filtro"

    if paginated:
        lines += [
            f"    return execute_paginated_query(",
            f"        request,",
            f"        {repo_var},",
            f"        {model_name},",
            f"        {db_enum},",
            f"        {params_dict},{params_comment}",
            f"        page,",
            f"        size,",
            f"        auto_paginazione=True,",
            f"    )",
        ]
    else:
        lines.append(
            f"    return execute_simple_query(request, {repo_var}, {model_name}, {db_enum}, {params_dict}){params_comment}"
        )

    return "\n".join(lines) + "\n"


def _normalize_prefix(prefix: str, default: str) -> str:
    prefix = prefix.strip()
    if not prefix:
        prefix = default
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    return prefix


def _sanitize_tag(tag: str, default: str) -> str:
    tag = tag.strip()
    return tag if tag else default


def _update_main_py_with_router(new_router_name: str, prefix: str, tag_label: str) -> None:
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    with open(main_path, encoding="utf-8") as f:
        content = f.read()

    import_line = f"from {new_router_name}_api import router as {new_router_name}_router\n"
    if import_line not in content:
        marker = "# Usa la data odierna per il nome del file log"
        if marker not in content:
            raise RuntimeError("Impossibile trovare il punto di inserimento degli import in main.py")
        insert_at = content.index(marker)
        content = content[:insert_at] + import_line + "\n" + content[insert_at:]

    comment_line = f"# Router aggiunto automaticamente da genera_servizio.py per {new_router_name}_router\n"
    include_line = f'app.include_router(prefix="{prefix}", router={new_router_name}_router,tags=["{tag_label}"])\n'
    if include_line not in content:
        marker = "# Mappa endpoint → path locale (senza prefisso del router), usata da check_permissions"
        if marker not in content:
            raise RuntimeError("Impossibile trovare il punto di inserimento di app.include_router in main.py")
        insert_at = content.index(marker)
        content = content[:insert_at] + comment_line + include_line + "\n" + content[insert_at:]

    endpoint_entry = f"        ({new_router_name}_router,   \"{prefix}\"),\n"
    endpoint_marker = "\n    ]\n    for route in sub_router.routes"
    if endpoint_entry not in content:
        if endpoint_marker not in content:
            raise RuntimeError("Impossibile trovare il blocco endpoint_local_paths in main.py")
        content = content.replace(endpoint_marker, endpoint_entry + endpoint_marker, 1)

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Interfaccia interattiva
# ---------------------------------------------------------------------------

def _ask(prompt: str) -> str:
    """Input con prompt, esce se EOF (CTRL+D/Z)."""
    try:
        return input(prompt)
    except EOFError:
        print()
        sys.exit(0)


def main() -> None:
    print()
    print("=" * 55)
    print("   Generatore Pydantic Model da Query SQL")
    print("=" * 55)

    # --- Nome classe modello ---
    while True:
        name = _ask("\nNome classe modello (es. MioRisultato): ").strip()
        if name and name.isidentifier():
            break
        print("  Nome non valido: usa solo lettere, cifre e underscore.")

    # --- Scelta connessione ---
    dbs = list(DbConnection)
    print("\nConnessioni disponibili:")
    for i, db in enumerate(dbs, 1):
        print(f"  {i}. {db.value}")
    while True:
        raw = _ask("Seleziona connessione [numero]: ").strip()
        try:
            db_conn = dbs[int(raw) - 1]
            break
        except (ValueError, IndexError):
            print("  Scelta non valida.")

    # --- Query SQL ---
    print("\nInserisci la query SQL.")
    print("Termina con una riga vuota (Invio su riga vuota = fine input):")
    query_lines: list[str] = []
    while True:
        line = _ask("  ")
        if not line:
            break
        query_lines.append(line)
    sql = " ".join(query_lines).strip()
    if not sql:
        print("Query vuota. Uscita.")
        sys.exit(1)

    # --- Esecuzione LIMIT 1 ---
    wrapped = _wrap_limit(sql, db_conn)
    params = {name: None for name in _extract_bind_params(sql)}
    print(f"\nEsecuzione su [{db_conn.value}] (una sola riga)...")
    if params:
        print(f"Parametri bind rilevati: {sorted(params)}")
    columns, row = _execute(wrapped, db_conn, params)

    if not columns:
        print("Impossibile recuperare i metadati. Controlla la connessione e la query.")
        sys.exit(1)

    # Riepilogo tipi rilevati
    print(f"\nColonne rilevate ({len(columns)}):")
    for col in columns:
        val = row.get(col) if row else None
        ptype, is_none = _pydantic_type(val)
        note = " (None → tipo inferito come Any)" if is_none else f" → {type(val).__name__}"
        print(f"  {col}: Optional[{ptype}] = None{note}")

    if row is None:
        print(
            "\nATTENZIONE: la query non ha restituito righe; "
            "tutti i tipi sono Optional[Any].\n"
            "Modifica manualmente models/models.py per raffinare i tipi."
        )

    # --- Anteprima codice ---
    code = _generate_class(name, columns, row)
    print(f"\nModello generato:\n{'─' * 40}{code}{'─' * 40}")

    # --- Conferma scrittura ---
    models_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "models", "models.py"
    )
    confirm = _ask(f"\nAggiungere in coda a models/models.py? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operazione annullata.")
        sys.exit(0)

    # Avvisa su import eventualmente mancanti
    missing = _missing_imports(columns, row, models_path)
    if missing:
        print("\nATTENZIONE: questi import potrebbero essere necessari in models.py:")
        for imp in missing:
            print(f"  {imp}")
        print("Aggiungili manualmente in cima al file se necessario.")

    # Scrittura
    with open(models_path, "a", encoding="utf-8") as f:
        f.write("\n" + code)

    print(f"\nClasse '{name}' aggiunta con successo a models/models.py.")

    # --- Creazione file repository ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_name = ""
    while True:
        repo_name = _ask("\nNome del repository (il file sarà repository/pst_<nome>.py): ").strip()
        if repo_name and repo_name.replace("_", "").isalnum():
            break
        print("  Nome non valido: usa solo lettere, cifre e underscore.")

    repo_path = os.path.join(base_dir, "repository", f"pst_{repo_name}.py")
    repo_content = _generate_repo_content(repo_name, sql)
    print(f"\nContenuto del file repository:\n{'─' * 40}\n{repo_content}{'─' * 40}")

    if os.path.exists(repo_path):
        confirm_repo = _ask(
            f"  Il file pst_{repo_name}.py esiste già. Sovrascrivere? (s/n): "
        ).strip().lower()
        write_repo = confirm_repo == "s"
    else:
        write_repo = True

    if write_repo:
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(repo_content)
        print(f"\nFile repository creato: repository/pst_{repo_name}.py")
    else:
        print("File repository non scritto.")

    # --- Guscio endpoint? ---
    gen_ep = _ask("\nVuoi generare anche il guscio di un endpoint? (s/n): ").strip().lower()
    if gen_ep != "s":
        print("Ok, operazione completata.")
        sys.exit(0)

    # Metodo HTTP
    while True:
        method_raw = _ask("Metodo HTTP [get/post]: ").strip().lower()
        if method_raw in ("get", "post"):
            break
        print("  Valore non valido. Inserisci 'get' o 'post'.")

    # Path dell'endpoint
    ep_path = _ask(f"Path dell'endpoint (es. miei_dati) [{name.lower()}]: ").strip().strip("/")
    if not ep_path:
        ep_path = name.lower()

    # Paginazione
    pag_raw = _ask("Endpoint paginato? (s/n): ").strip().lower()
    paginated = pag_raw == "s"

    # --- Query parameters ---
    query_params: list[dict] = []
    add_qp = _ask("Aggiungere query parameters all'endpoint? (s/n): ").strip().lower()
    if add_qp == "s":
        query_params = _ask_params_list("query parameters")

    # --- Body parameters (solo metodi con payload) ---
    body_fields: list[dict] = []
    body_model_name: str | None = None
    if method_raw == "post":
        add_body = _ask("Definire i campi del body? (s/n): ").strip().lower()
        if add_body == "s":
            body_fields = _ask_params_list("campi del body")

    if body_fields:
        body_model_name = f"{name}Request"
        body_model_code = _generate_request_body_model(body_model_name, body_fields)
        print(f"\nModello body generato:\n{'─' * 40}{body_model_code}{'─' * 40}")
        confirm_bm = _ask(
            f"Aggiungere '{body_model_name}' in coda a models/models.py? (s/n): "
        ).strip().lower()
        if confirm_bm == "s":
            with open(models_path, encoding="utf-8") as mf:
                models_content = mf.read()
            missing_bm_imports = []
            for t in set(field["type"] for field in body_fields):
                imp = _EXTRA_IMPORTS.get(t)
                if imp and imp not in models_content:
                    missing_bm_imports.append(imp)
            if missing_bm_imports:
                print("\nATTENZIONE: questi import potrebbero essere necessari in models.py:")
                for imp in missing_bm_imports:
                    print(f"  {imp}")
                print("Aggiungili manualmente in cima al file se necessario.")
            with open(models_path, "a", encoding="utf-8") as mf:
                mf.write("\n" + body_model_code)
            print(f"\nModello '{body_model_name}' aggiunto con successo a models/models.py.")
        else:
            print(
                f"\nATTENZIONE: il modello '{body_model_name}' non è stato scritto; "
                "aggiungilo manualmente a models/models.py prima di usare l'endpoint."
            )

    # Raccoglie i tipi custom per la risoluzione degli import nel router
    extra_types: list[str] = (
        [qp["type"] for qp in query_params] + [field["type"] for field in body_fields]
    )

    # Scelta file router
    router_files = sorted(
        f for f in os.listdir(base_dir)
        if f.endswith("_api.py") and f != "main.py"
    )
    print("\nFile router disponibili:")
    for i, rf in enumerate(router_files, 1):
        print(f"  {i}. {rf}")
    new_router_idx = len(router_files) + 1
    print(f"  {new_router_idx}. Crea nuovo router")
    create_new_router = False
    new_router_name = ""
    target_router = ""
    while True:
        raw = _ask("Seleziona il file router [numero]: ").strip()
        try:
            idx = int(raw) - 1
            if idx == len(router_files):
                create_new_router = True
                break
            elif 0 <= idx < len(router_files):
                target_router = router_files[idx]
                break
            else:
                print("  Scelta non valida.")
        except (ValueError, IndexError):
            print("  Scelta non valida.")

    if create_new_router:
        while True:
            new_router_name = _ask("Nome del nuovo router (es. nuovo → nuovo_api.py): ").strip()
            if new_router_name and new_router_name.replace("_", "").isalnum():
                break
            print("  Nome non valido: usa solo lettere, cifre e underscore.")
        target_router = f"{new_router_name}_api.py"

    ep_code = _generate_endpoint(
        name, ep_path, method_raw, paginated, db_conn, repo_name,
        query_params=query_params,
        body_model_name=body_model_name,
    )
    print(f"\nEndpoint generato:\n{'─' * 40}{ep_code}{'─' * 40}")

    confirm_ep = _ask(f"\nAggiungere in coda a {target_router}? (s/n): ").strip().lower()
    if confirm_ep == "s":
        target_path = os.path.join(base_dir, target_router)
        if create_new_router:
            router_header = _generate_router_header(
                name, repo_name, paginated,
                body_model_name=body_model_name,
                extra_types=extra_types or None,
            )
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(router_header + ep_code)
            print(f"\nNuovo router creato: {target_router}")

            prefix = _ask("Prefisso del router in main.py (es. /api): ").strip() or "/api"
            tag_label = _ask("Tag Swagger/OpenAPI per il router: ").strip() or "Nuovo router"
            prefix = _normalize_prefix(prefix, "/api")
            tag_label = _sanitize_tag(tag_label, "Nuovo router")
            try:
                _update_main_py_with_router(new_router_name, prefix, tag_label)
                print(f"\nRouter registrato automaticamente in main.py con prefix '{prefix}'.")
            except Exception as exc:
                print(f"\nATTENZIONE: non è stato possibile aggiornare automaticamente main.py: {exc}")
                print(
                    f"Aggiungi manualmente in main.py:\n"
                    f"  from {new_router_name}_api import router as {new_router_name}_router\n"
                    f"  app.include_router(prefix=\"{prefix}\", router={new_router_name}_router,tags=[\"{tag_label}\"])\n"
                    f"  # e aggiungi la voce a app.state.endpoint_local_paths"
                )
        else:
            with open(target_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            imports_code = _generate_endpoint_imports(
                name, repo_name, existing_content,
                body_model_name=body_model_name,
                has_query_params=bool(query_params),
                extra_types=extra_types or None,
            )
            with open(target_path, "a", encoding="utf-8") as f:
                if imports_code:
                    f.write(imports_code + "\n" + ep_code)
                else:
                    f.write(ep_code)
            print(f"\nEndpoint aggiunto con successo a {target_router}.")
            if imports_code:
                print(f"\nImport aggiunti automaticamente a {target_router}:{imports_code}")
    else:
        print("Endpoint non scritto.")


if __name__ == "__main__":
    main()
