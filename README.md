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
Per disinstallare:
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

   Crea un file `.env` nella root del progetto e inserisci le seguenti variabili.

   **Database:**
   ```env
   DB_USER=postgres
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=amiu
   ```

   **Autenticazione JWT:**
   Aggiungi queste variabili al tuo file `.env` per configurare la generazione dei token.
   ```env
   SECRET_KEY=la_tua_chiave_segreta_super_difficile
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   - `SECRET_KEY`: Una stringa lunga e casuale usata per firmare i token.
   - `ALGORITHM`: L'algoritmo di hashing (es. HS256).
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: La durata di validità del token in minuti.

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
Questi endpoint sono ad accesso libero e non richiedono autenticazione.

#### `GET /mappe`
Recupera le mappe disponibili.

#### `GET /piazzole`
Recupera la lista delle piazzole con filtri e paginazione.
- **Parametri**: `page`, `size`, `comune`, `municipio`, `via`, `pap`.

#### `GET /vie`
Recupera la lista delle vie con filtri e paginazione.
- **Parametri**: `page`, `size`, `comune`.

#### `GET /comuni`
Recupera la lista dei comuni.
- **Parametri**: `id_ambito`, `cod_istat`.

#### `GET /civici`
Recupera la lista dei civici con filtri e paginazione.
- **Parametri**: `page`, `size`, `id_municipio`, `id_via`.

#### `GET /quartieri`
Recupera la lista dei quartieri.
- **Parametri**: `id_municipio`.

#### `GET /ambiti`
Recupera la lista degli ambiti.

#### `GET /municipi`
Recupera la lista dei municipi di Genova.

#### `GET /pointofinterest`
Recupera i dettagli dei Punti di Interesse (Rimesse, UT e Scarichi vari).

#### `GET /layer_filter`
Recupera i layer filtrati in base a titolo mappa, livello e nome.
- **Parametri**: `t` (titolo), `l` ('ambito', 'comune', 'municipio'), `n` (nome).

---

### Servizi di Localizzazione (`/`)

#### `GET /point2area`
Restituisce le informazioni sull'area (comune, municipio, quartiere, etc.) a partire da coordinate geografiche.
- **Parametri**: `lat` (latitudine), `lon` (longitudine).
- **Autorizzazione**: Nessuna.

---

### Servizi TELLUS (`/`)
Questi endpoint forniscono dati operativi dal sistema TELLUS e non richiedono autenticazione.

#### `GET /percorsi_p`
Restituisce la lista dei percorsi posteriori con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.

#### `GET /piazzole_amiu`
Restituisce la lista delle piazzole AMIU con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.

#### `GET /elementi_p`
Restituisce la lista degli elementi con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.

#### `GET /itinerari_p`
Restituisce la lista degli itinerari dei percorsi posteriori con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.

#### `GET /depositi`
Restituisce la lista di Unità Territoriali e Rimesse con paginazione e filtro data.
- **Parametri**: `page`, `size`, `last_update`.

---

### Servizi IDEA (`/`)
Questi endpoint richiedono un token di autenticazione Bearer.

#### `GET /utenze_tari`
Recupera la lista delle utenze TARI (Domestiche o Non Domestiche) con paginazione.
- **Parametri**: `tipo` ('UD' o 'UND'), `page`, `size`.
- **Autorizzazione**: Richiesto token JWT.

#### `GET /elenco_percorsi_bilaterali_tree`
Recupera la lista dei percorsi bilaterali strutturata ad albero.
- **Autorizzazione**: Nessuna (potrebbe essere un errore, da verificare).

#### `GET /elenco_percorsi_bilaterali`
Recupera la lista flat dei percorsi bilaterali.
- **Autorizzazione**: Nessuna (potrebbe essere un errore, da verificare).

#### `GET /dettagli_percorso`
Recupera i dettagli di uno specifico percorso bilaterale.
- **Parametri**: `id` del percorso.
- **Autorizzazione**: Nessuna (potrebbe essere un errore, da verificare).

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