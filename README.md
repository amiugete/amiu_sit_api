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


   Crea un file `.env` nella root del progetto e inserisci le seguenti variabili (vedi esempio):

   **Variabili generali:**
   ```env
   # root path della URL
   ENVIRONMENT_CONTEXT_PATH=test
   ```

   **Database SIT:**
   ```env
   DB_USER=webgis
   DB_PASSWORD=qgisisN1ce
   DB_HOST=172.24.4.39
   DB_PORT=5432
   DB_NAME=sit_test
   ```

   **Database Mappe (per WS mappe duale):**
   ```env
   DB_HOST_MAPPE=amiugis
   DB_PORT_MAPPE=5432
   DB_NAME_MAPPE=api_db
   DB_USER_MAPPE=api
   DB_PASSWORD_MAPPE=4pi1sN1ce
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
   HOST_AMIU_LDAP=172.24.4.1
   DOMAIN_NAME_AMIU=amiu.genova.it
   ```

   > ⚠️ Ricordati di aggiornare le variabili secondo il tuo ambiente. Tutte le connessioni ai database e servizi usano queste variabili tramite il file `.env`.

5. **Avvia il server in sviluppo**
   ```bash
   fastapi dev main.py
   ```

L'API sarà disponibile su `http://localhost:8000` e la documentazione interattiva su `http://localhost:8000/docs`.

## 📚 API Endpoints

### Servizi di Autenticazione (`/auth`)

#### `POST /token`
Genera un token JWT per autenticare un utente tramite credenziali LDAP.
- **Request Body**: `application/x-www-form-urlencoded` con `username` e `password`.
- **Autorizzazione**: Nessuna.

---

### Servizi Pubblici (`/`)
Questi endpoint richiedono autenticazione tramite Bearer Token (JWT).

#### `GET /mappe`
Recupera le mappe disponibili.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /piazzole`
Recupera la lista delle piazzole con filtri e paginazione.
- **Parametri**: `page`, `size`, `comune`, `municipio`, `via`, `pap`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /vie`
Recupera la lista delle vie con filtri e paginazione.
- **Parametri**: `page`, `size`, `comune`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /comuni`
Recupera la lista dei comuni.
- **Parametri**: `id_ambito`, `cod_istat`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /civici`
Recupera la lista dei civici con filtri e paginazione.

- **Parametri**:
  - `page`: Numero della pagina (opzionale, per paginazione)
  - `size`: Dimensione della pagina (opzionale, per paginazione, max 100)
  - `id_municipio`: Filtra per municipio (opzionale)
  - `id_via`: Filtra per via (opzionale)
  - `last_update`: Filtra per data di inserimento/aggiornamento civico, formato stringa `YYYYMMDD` (opzionale)
    - Esempio: `last_update=20260101` filtra i civici inseriti/modificati dal 1 gennaio 2026 in poi
- **Autorizzazione**: Richiesto token JWT

Risposta:
- Se vengono indicati `page` e `size`, la risposta è paginata e include il totale.
- Se non vengono indicati, restituisce la lista completa (max 10.000 record).

Esempio di richiesta:
```
GET /civici?page=1&size=50&id_municipio=2&id_via=123&last_update=20260101
Authorization: Bearer <token>
```

#### `GET /quartieri`
Recupera la lista dei quartieri.
- **Parametri**: `id_municipio`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /ambiti`
Recupera la lista degli ambiti.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /municipi`
Recupera la lista dei municipi di Genova.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /POI`
Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari).
- **Autorizzazione**: Richiesto token JWT.

#### `GET /layer_filter`
Recupera i layer filtrati in base a titolo mappa, livello e nome.
- **Parametri**: `t` (titolo), `l` ('ambito', 'comune', 'municipio'), `n` (nome).
- **Autorizzazione**: Richiesto token JWT.

---

### Servizi di Localizzazione (`/`)

#### `GET /point2area`
Restituisce le informazioni sull'area (comune, municipio, quartiere, etc.) a partire da coordinate geografiche.
- **Parametri**: `lat` (latitudine), `lon` (longitudine).
- **Autorizzazione**: Richiesto token JWT.

---

### Servizi TELLUS (`/`)
Questi endpoint forniscono dati operativi dal sistema TELLUS e richiedono autenticazione tramite Bearer Token (JWT).

#### `GET /percorsi_p`
Restituisce la lista dei percorsi posteriori con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /piazzole_amiu`
Restituisce la lista delle piazzole AMIU con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /elementi_p`
Restituisce la lista degli elementi con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.
- **Autorizzazione**: Richiesto token JWT.


#### `GET /mezzi_ekovision`
Restituisce la lista dei mezzi ekovision con paginazione e filtro per data di esecuzione prevista.
- **Parametri**: 
   - `check_date` (obbligatorio, formato `YYYYMMDD`): data di esecuzione prevista
   - `page`, `size` (opzionali, per paginazione)
- **Autorizzazione**: Richiesto token JWT.

#### `GET /itinerari_p`
Restituisce la lista degli itinerari dei percorsi posteriori con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /depositi`
Restituisce la lista di Unità Territoriali e Rimesse con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.
- **Autorizzazione**: Richiesto token JWT.

---

### Servizi IDEA (`/`)
Questi endpoint richiedono un token di autenticazione Bearer.

#### `GET /utenze_tari`
Recupera la lista delle utenze TARI (Domestiche o Non Domestiche) con paginazione.
- **Parametri**: `tipo` ('UD' o 'UND'), `page`, `size`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /elenco_percorsi_bilaterali_tree`
Recupera la lista dei percorsi bilaterali strutturata ad albero.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /elenco_percorsi_bilaterali`
Recupera la lista flat dei percorsi bilaterali.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /dettagli_percorso`
Recupera i dettagli di uno specifico percorso bilaterale.
- **Parametri**: `id` del percorso.
- **Autorizzazione**: Richiesto token JWT.

## 🐛 Gestione Errori

L'applicazione ritorna:
- **200 OK**: Richiesta riuscita.
- **400 Bad Request**: Parametri non validi (es. `livello` errato per `/layer_filter`).
- **401 Unauthorized**: Token mancante, invalido o scaduto.
- **403 Forbidden**: L'utente non ha i permessi per accedere alla risorsa.
- **404 Not Found**: Risorsa o endpoint non trovato.
- **422 Unprocessable Entity**: Dati della richiesta non validi o mancanti.
- **500 Internal Server Error**: Errore generico del server (controllare i log).

Tutti gli errori sono loggati in `app.log`.

## 📝 Licenza

Progetto AMIU

## 👤 Autore

Team AMIU Development