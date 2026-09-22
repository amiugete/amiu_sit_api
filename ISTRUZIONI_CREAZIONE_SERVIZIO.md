# Istruzioni per la generazione di endpoint con `genera_servizio.py`

Questo documento spiega come usare lo script `genera_servizio.py` per generare:
- un modello Pydantic in `models/models.py`
- un file repository SQL in `repository/pst_<nome>.py`
- il guscio di un endpoint FastAPI in un router esistente o nuovo
- l’eventuale registrazione del router in `main.py`

---

## 1. Preparazione

Lo script `genera_servizio.py` lavora con:
- `config/database.py` per le connessioni DB
- `models/models.py` per i modelli Pydantic
- `repository/` per le query SQL
- file router `*_api.py` per gli endpoint
- `main.py` per la registrazione del router

È pensato per progetti dove:
- le query DB sono centralizzate in repository
- le risposte sono tipizzate con modelli Pydantic
- gli endpoint usano i helper in `business.query_helpers`
- l’autenticazione è gestita con `check_permissions`

---

## 2. Flusso principale dello script

1. Inserisci il nome del modello Pydantic.
2. Seleziona la connessione DB (`DbConnection`).
3. Inserisci la query SQL e termina con una riga vuota.
4. Lo script esegue la query in forma limitata (`LIMIT 1` o equivalente).
5. In base ai tipi delle colonne, genera una classe Pydantic in `models/models.py`.
6. Crea o sovrascrive il repository `repository/pst_<nome>.py`.
7. Eventualmente genera anche il guscio dell’endpoint.
8. Se crei un nuovo router, prova ad aggiornare `main.py` automaticamente.

---

## 3. Modello Pydantic generato

Lo script genera una classe con campi `Optional[...] = None`, per compatibilità con il pattern del progetto.

Esempio generato:

```python
class MioRisultato(BaseModel):
    id: Optional[int] = None
    nome: Optional[str] = None
    data: Optional[datetime] = None
```

Attenzione:
- `time` viene mappato a `str`
- `Decimal` viene mappato a `float`
- se la query non restituisce righe, tutti i campi diventano `Optional[Any]`
- se il tipo non è riconosciuto, viene usato `Any`

Se serve, aggiungi manualmente in `models/models.py` gli import:

```python
from datetime import date
from datetime import datetime
```

---

## 4. Repository SQL generato

Lo script crea un file `repository/pst_<nome>.py` con questa struttura:

```python
# Preparazione della query per il recupero di <nome>
pst_<nome>: str = """
        <SQL>
        """
```

Nel router il repository viene importato come:

```python
from repository.pst_<nome> import pst_<nome>
```

La query può usare bind parameter `:nome` per i filtri.

---

## 5. Endpoint generato

Lo script genera endpoint `GET` o `POST` seguendo il pattern del progetto:
- `request: Request`
- `payload: dict[str, Any] = Depends(check_permissions)`
- utilizzo di `execute_simple_query(...)` o `execute_paginated_query(...)`
- `response_model=List[Modello]` per endpoint non paginati
- `response_model=Union[List[Modello], PaginatedResponse[Modello]]` per endpoint paginati

### Endpoint `GET` semplice

Esempio:

```python
@router.get(
    "/mio_servizio",
    response_model=List[MioModello],
    description="TODO: descrizione endpoint. Richiede autenticazione (Bearer Token)."
)
def mio_servizio(
    request: Request,
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_simple_query(
        request,
        pst_mio_servizio,
        MioModello,
        DbConnection.SIT,
        {"id_comune": id_comune},
    )
```

### Endpoint paginato

Esempio:

```python
@router.get(
    "/miei_elementi",
    response_model=Union[List[Elemento], PaginatedResponse[Elemento]],
    description="Recupera la lista degli elementi con filtri opzionali."
)
def lista_elementi(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_piazzola: Optional[int] = Query(None, description="Filtra per ID piazzola"),
    payload: dict[str, Any] = Depends(check_permissions)
):
    return execute_paginated_query(
        request,
        pst_elementi,
        Elemento,
        DbConnection.SIT,
        {"id_piazzola": id_piazzola},
        page,
        size,
    )
```

Note:
- `page` e `size` sono usati per la paginazione
- se omessi, il comportamento dipende da `execute_paginated_query`

---

## 6. Come scegliere il router

Lo script ti chiede se usare un router esistente o crearne uno nuovo.

### Router esistente

Inserisci il file `*_api.py` esistente.
Lo script aggiunge automaticamente gli import mancanti:
- modello Pydantic
- repository
- `Query` se sono presenti query params
- `date`/`datetime` se necessari

### Nuovo router

Se crei un nuovo router, lo script genera anche l’header iniziale con:
- import FastAPI (`APIRouter`, `Query`, `Depends`, `Request`)
- tipi di Python (`Any`, `List`, `Optional`, `Union`)
- `check_permissions`
- `execute_simple_query` e `execute_paginated_query`
- `DbConnection`
- modello e repository
- `logger = logging.getLogger(__name__)`
- `router = APIRouter()`

---

## 7. Registrazione del router in `main.py`

Se viene creato un nuovo router, lo script tenta di aggiornare automaticamente `main.py` con:
- `from <router> import router as <router>_router`
- `app.include_router(prefix="...", router=<router>_router, tags=["..."])`
- l’aggiunta alla mappa `app.state.endpoint_local_paths`

Se l’aggiornamento automatico fallisce, lo script mostra il codice da inserire manualmente.

---

## 8. Dettagli utili

### Parametri SQL

Lo script estrae i bind parameter `:nome` dalla query SQL e li usa per l’esecuzione di prova con valore `None`.

### Import aggiuntivi

Se il modello o il body usa `date` o `datetime`, aggiungi questi import dove serve:

```python
from datetime import date
from datetime import datetime
```

### Endpoint `POST`

Se definisci campi body, lo script può creare un modello `NomeRequest` in `models/models.py`.
Se non scrivi il modello, aggiungilo manualmente prima di usare l’endpoint.

---

## 9. Cosa controllare dopo la generazione

Dopo l’esecuzione di `genera_servizio.py`:
- verifica il modello in `models/models.py`
- controlla il repository `repository/pst_<nome>.py`
- verifica il codice nel router selezionato
- verifica `main.py` se è stato creato un nuovo router
- completa le `description` e i commenti TODO
- testa manualmente il servizio in FastAPI

---

## 10. Esempio rapido di uso

1. Esegui:

```bash
python genera_servizio.py
```

2. Rispondi alle domande:
- nome del modello
- connessione DB
- query SQL
- nome repository
- metodo HTTP
- path dell’endpoint
- paginazione
- query params
- campi body (per POST)

3. Controlla i file generati:
- `models/models.py`
- `repository/pst_<nome>.py`
- `*_api.py`
- `main.py`

---

## 11. Consigli pratici

- usa nomi coerenti: `pst_<nome>` e `<nome>_api.py`
- scegli path endpoint chiari e senza slash iniziale
- mantieni i nomi dei query params uguali ai bind SQL
- aggiungi una `description` per OpenAPI
- allinea i tipi del modello ai campi restituiti dalla query
- verifica che `models/models.py` importi `BaseModel` e `Optional`
