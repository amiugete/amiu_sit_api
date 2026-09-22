# AMIU SIT API

API REST per la gestione dei dati geografici e amministrativi del sistema informativo AMIU (Azienda Mobilità e Igiene Urbana). L'applicazione fornisce accesso a dati su piazzole, vie, utenze, percorsi e altro, con supporto per paginazione, filtri avanzati e autenticazione.

## 📋 Descrizione

AMIU SIT API è un'applicazione FastAPI che espone una serie di endpoint per consultare:
- **Dati Geografici Pubblici**: Vie, piazze, comuni, municipi, quartieri, ambiti.
- **Dati Operativi TELLUS**: Percorsi, piazzole, elementi e itinerari specifici.
- **Dati Protetti IDEA**: Utenze TARI e percorsi bilaterali (richiede autenticazione).
- **Servizi di Localizzazione**: Endpoint per risolvere coordinate geografiche in aree amministrative.
- **Autenticazione**: Sistema basato su token JWT per l'accesso alle risorse protette.

L'API supporta:
- ✅ Autenticazione sicura tramite JWT.
- ✅ Paginazione personalizzabile sulla maggior parte degli endpoint di lista.
- ✅ Filtri avanzati su molteplici parametri.
- ✅ Risposte in formato JSON standard.
- ✅ Logging dettagliato su file (`app.log`) e console.
- ✅ Connessione sicura a PostgreSQL.
- ✅ Documentazione interattiva tramite Swagger UI.

## 🚀 Installazione e Configurazione


### Prerequisiti
- Python 3.8+
- PostgreSQL
- pip
- [WinSW (Windows Service Wrapper)](https://github.com/winsw/winsw) per installare l'app come servizio Windows
## 🖥️ Installazione come Servizio Windows (WinSW)

Per eseguire l'applicazione come servizio di sistema su Windows, puoi utilizzare [WinSW](https://github.com/winsw/winsw). Questo consente di avviare automaticamente l'API all'avvio del sistema e gestirla come un normale servizio Windows.

### 1. Scarica WinSW
Scarica l'eseguibile WinSW (ad esempio `WinSW-x64.exe`) dalla [pagina dei rilasci](https://github.com/winsw/winsw/releases) e rinominalo in `fastapi-service.exe`.

### 2. Configura il file XML del servizio
Nella root del progetto è già presente il file `fastapi-service.xml` di esempio. Ecco i punti principali:

- **Percorso Python**: Il servizio usa l'eseguibile Python dell'ambiente virtuale (`.venv\Scripts\python.exe`).
- **Variabile di ambiente**: `APP_ROOT` viene impostata come root del progetto.
- **Comando di avvio**: Avvia Uvicorn con 4 worker sulla porta 8000.
- **Log**: I log vengono salvati nella cartella `logs`.

Puoi personalizzare il file XML secondo le tue esigenze. Esempio:

```xml
<service>
   <id>fastapi-service</id>
   <name>FastAPI Service</name>
   <description>Servizio FastAPI con WinSW</description>
   <env name="APP_ROOT" value="C:\Sviluppo\amiu_sit_api" />
   <executable>%APP_ROOT%\.venv\Scripts\python.exe</executable>
   <arguments>-m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4</arguments>
   <workingdirectory>%APP_ROOT%</workingdirectory>
   <priority>Normal</priority>
   <stoptimeout>15 sec</stoptimeout>
   <stopparentprocessfirst>true</stopparentprocessfirst>
   <startmode>Automatic</startmode>
   <waithint>15 sec</waithint>
   <sleeptime>1 sec</sleeptime>
   <log mode="roll-by-time">
      <logpath>%APP_ROOT%\logs</logpath>
      <workingdirectory>%APP_ROOT%</workingdirectory>
      <period>1</period>
      <pattern>yyyyMMdd</pattern>
      <keepFiles>10</keepFiles>
   </log>
</service>
```

### 3. Installa il servizio
Apri un terminale come **amministratore** nella cartella del progetto e lancia:

```powershell
./fastapi-service.exe install
```

### 4. Avvia/ferma il servizio
Per avviare:
```powershell
./fastapi-service.exe start
```
Per fermare:
```powershell
./fastapi-service.exe stop
```
Per disinstallare (necessario in caso di modifiche al file XML, altrimenti è sufficiente stop e start):
```powershell
./fastapi-service.exe uninstall
```

### 5. Log
I log del servizio sono disponibili nella cartella `logs`.

---

### Setup

1. **Clone il repository**
   ```bash
   git clone <repository-url>
   cd amiu_sit_api
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili di ambiente**

   Il file `config/database.py` utilizza SQLAlchemy per creare i motori di connessione (`engine`) e seleziona il database corretto tramite l'enum `DbConnection`.
   Le connessioni PostgreSQL impostano `pool_pre_ping=True` e `pool_recycle=900` per mantenere i pool di connessione stabili.

   - `DbConnection.SIT` → database PostgreSQL principale (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`)
   - `DbConnection.CONFIG` → database PostgreSQL di configurazione (`DB_USER_CONFIG`, `DB_PASSWORD_CONFIG`, `DB_HOST_CONFIG`, `DB_PORT_CONFIG`, `DB_NAME_CONFIG`)
   - `DbConnection.MAPPE` → database PostgreSQL mappe (`DB_USER_MAPPE`, `DB_PASSWORD_MAPPE`, `DB_HOST_MAPPE`, `DB_PORT_MAPPE`, `DB_NAME_MAPPE`)
   - `DbConnection.STRADE` → database Oracle per le strade (`ORACLE_CLIENT_PATH`, `DB_USER_STRADE`, `DB_PASSWORD_STRADE`, `DB_HOST_STRADE`, `DB_PORT_STRADE`, `DB_NAME_STRADE`)

   Crea un file `.env` nella root del progetto e inserisci le seguenti variabili (vedi esempio):

   **Variabili generali:**
   ```env
   # root path della URL
   ENVIRONMENT_CONTEXT_PATH=test
   ```

   **Database SIT:**
   ```env
   DB_USER=user
   DB_PASSWORD=pwdsicura
   DB_HOST=111.111.1.11
   DB_PORT=5432
   DB_NAME=SIT
   ```

   **Database Configurazione:**
   ```env
   DB_USER_CONFIG=user
   DB_PASSWORD_CONFIG=pwdsicura_config
   DB_HOST_CONFIG=111.111.1.11
   DB_PORT_CONFIG=5432
   DB_NAME_CONFIG=webservice_test
   ```

   **Database Mappe (per WS mappe duale):**
   ```env
   DB_USER_MAPPE=user
   DB_PASSWORD_MAPPE=pwdsicura_mappe
   DB_HOST_MAPPE=111.111.1.11
   DB_PORT_MAPPE=5432
   DB_NAME_MAPPE=jj
   ```

   **Database Oracle Strade:**
   ```env
   ORACLE_CLIENT_PATH=C:\oracle\instantclient_19_29
   DB_USER_STRADE=ws_readonly
   DB_PASSWORD_STRADE=strade_pwd
   DB_HOST_STRADE=111.111.1.11
   DB_PORT_STRADE=1526
   DB_NAME_STRADE=PEOR
   ```

   **Autenticazione JWT:**
   ```env
   SECRET_KEY=passwordsicura
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   - `SECRET_KEY`: Stringa lunga e casuale usata per firmare i token.
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: Durata di validità del token in minuti.

   **LDAP AMIU:**
   ```env
   HOST_AMIU_LDAP=host.amiu
   DOMAIN_NAME_AMIU=amiu.genova.it
   ```

   > ⚠️ Ricordati di aggiornare le variabili secondo il tuo ambiente. Tutte le connessioni ai database e servizi usano queste variabili tramite il file `.env`.

5. **Avvia il server in sviluppo**
   ```bash
   fastapi dev main.py
   ```

L'API sarà disponibile su `http://localhost:8000` e la documentazione interattiva su `http://localhost:8000/docs`.


Tutti gli errori sono loggati in `app.log`.

## 🧩 Pattern consigliato per creare un nuovo endpoint

Il progetto usa un pattern molto uniforme per tutte le API: la query SQL è separata dal router, il modello Pydantic definisce la risposta, e i router usano sempre le stesse helper per eseguire le query.

### 1. Query SQL in repository

Le query sono definite in file `repository/*.py`.

```python
# repository/utenti_repo.py
pst_ricerca_utenti = """
    SELECT
        id_utente,
        nome,
        cognome,
        codice_fiscale,
        id_comune
    FROM utenti
    WHERE
        (:id_comune IS NULL OR id_comune = :id_comune)
        AND (:codice_fiscale IS NULL OR codice_fiscale = :codice_fiscale)
    ORDER BY nome, cognome
"""
```

### 2. Modello Pydantic

Il risultato viene mappato su una classe nel file `models/models.py`.

```python
from typing import Optional
from pydantic import BaseModel

class Utente(BaseModel):
    id_utente: Optional[int] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    codice_fiscale: Optional[str] = None
    id_comune: Optional[int] = None
```

### 3. Endpoint semplice senza paginazione

Per liste non paginate si usa `execute_simple_query(...)`.

```python
from fastapi import APIRouter, Request, Query, Depends
from typing import Any, Optional, List

from business.permission import check_permissions
from business.query_helpers import execute_simple_query
from config.database import DbConnection
from models.models import Utente
from repository.utenti_repo import pst_ricerca_utenti

router = APIRouter()

@router.get(
    "/ricerca-utenti",
    response_model=List[Utente],
    description="Recupera la lista degli utenti con filtri opzionali. Richiede autenticazione."
)
def ricerca_utenti(
    request: Request,
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    codice_fiscale: Optional[str] = Query(None, description="Filtra per codice fiscale"),
    payload: dict[str, Any] = Depends(check_permissions),
):
    params = {
        "id_comune": id_comune,
        "codice_fiscale": codice_fiscale,
    }

    return execute_simple_query(
        request,
        pst_ricerca_utenti,
        Utente,
        DbConnection.SIT,
        params,
    )
```

In questo pattern:
- `request: Request` viene usato dal logger
- `payload: dict[str, Any] = Depends(check_permissions)` fa il controllo JWT + permessi
- `Query(...)` definisce i filtri opzionali
- `execute_simple_query(...)` esegue la query e mappa i risultati

### 4. Endpoint paginato

Per liste potenzialmente grandi si usa `execute_paginated_query(...)` con `page` e `size`.

```python
from fastapi import APIRouter, Request, Query, Depends
from typing import Any, Optional, List, Union

from business.permission import check_permissions
from business.query_helpers import execute_paginated_query
from config.database import DbConnection
from models.models import Documento, PaginatedResponse
from repository.documenti_repo import pst_documenti

router = APIRouter()

@router.get(
    "/documenti",
    response_model=Union[List[Documento], PaginatedResponse[Documento]],
    description="Recupera i documenti con filtri opzionali e paginazione. Richiede autenticazione."
)
def lista_documenti(
    request: Request,
    page: Optional[int] = Query(None, ge=1, description="Numero della pagina"),
    size: Optional[int] = Query(None, ge=1, le=100, description="Dimensione della pagina"),
    id_comune: Optional[int] = Query(None, description="Filtra per comune"),
    id_stato: Optional[int] = Query(None, description="Filtra per stato documento"),
    payload: dict[str, Any] = Depends(check_permissions),
):
    params = {
        "id_comune": id_comune,
        "id_stato": id_stato,
    }

    return execute_paginated_query(
        request,
        pst_documenti,
        Documento,
        DbConnection.SIT,
        params,
        page,
        size,
    )
```

In questo caso la helper si occupa di:
- calcolare `OFFSET` e `LIMIT`
- determinare il totale righe
- costruire la risposta `PaginatedResponse` con `total`, `page`, `size`, `pages`, `content`

### 5. Funzioni base da usare

In questo progetto la chiamata corretta è sempre una di queste due:

```python
execute_simple_query(request, query, model_class, db_conn, params)
execute_paginated_query(request, query, model_class, db_conn, params, page, size)
```

Non è consigliato scrivere direttamente la query SQL nel router. Il pattern corretto è:
1. definire la query in `repository/*.py`
2. definire il modello in `models/models.py`
3. chiamare la helper corretta
4. aggiungere `Depends(check_permissions)` a ogni endpoint protetto

### 6. Autenticazione e permessi

Tutti gli endpoint sensibili devono avere il dependency di sicurezza:

```python
payload: dict[str, Any] = Depends(check_permissions)
```

Questo dipende da `business/permission.py` e fa tre cose:
- legge il token JWT dalla request
- valida il payload del token
- verifica che l'utente abbia i permessi richiesti per l'endpoint

Se l'utente non è autorizzato, la richiesta viene impedita con `401 Unauthorized`.

Questo pattern è il medesimo usato in `public_api.py` e va rispettato per tutte le nuove API del progetto.

## 📝 Licenza

Progetto AMIU

## 👤 Autore

Team AMIU Development - TEST