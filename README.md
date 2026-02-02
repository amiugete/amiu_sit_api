# AMIU SIT API

API REST per la gestione dei dati geografici e amministrativi del sistema informativo AMIU (Azienda Mobilità e Igiene Urbana). L'applicazione fornisce accesso ai dati su piazzole e vie con supporto per paginazione e filtri avanzati.

## 📋 Descrizione

AMIU SIT API è un'applicazione FastAPI che espone endpoint per consultare:
- **Piazzole**: Punti di raccolta rifiuti con informazioni geografiche e amministrative
- **Vie**: Strade e percorsi del territorio servito
- **Comuni**: Comuni del territorio
- **Civici**: Indirizzi e numeri civici
- **Quartieri**: Suddivisioni territoriali per municipio
- **Ambiti**: Raggruppamenti amministrativi

L'API supporta:
- ✅ Paginazione personalizzabile per piazzole e civici
- ✅ Filtri avanzati per comune, municipio, via e PAP
- ✅ Risposte in formato JSON
- ✅ Logging dettagliato
- ✅ Connessione sicura a PostgreSQL
- ✅ Endpoint senza paginazione per dati di lookup (comuni, quartieri, ambiti)

## 🚀 Installazione

### Prerequisiti
- Python 3.8+
- PostgreSQL
- pip

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

Crea un file `.env` nella root del progetto:
```env
DB_USER=??
DB_PASSWORD=??
DB_HOST=??
DB_PORT=??
DB_NAME=??
```

5. **Avvia il server in sviluppo**
```bash
fastapi dev main.py
```

L'API sarà disponibile su `http://localhost:8000`


## 📚 API Endpoints

### GET /piazzole
Recupera l'elenco delle piazzole con paginazione opzionale.

**Query Parameters:**
- `page` (int, opzionale): Numero di pagina (default: nessuna paginazione)
- `size` (int, opzionale): Elementi per pagina, max 100
- `comune` (int, opzionale): Filtra per ID comune
- `municipio` (int, opzionale): Filtra per ID municipio
- `via` (int, opzionale): Filtra per ID via
- `pap` (int, opzionale): Filtra per PAP (0=No, 1=Sì)

**Response (con paginazione):**
```json
{
  "total": 1500,
  "page": 1,
  "size": 50,
  "pages": 30,
  "content": [
    {
      "id_piazzola": 1,
      "id_via": 10,
      "via": "Via Roma",
      "comune": "Roma",
      "municipio": "Municipio I",
      "quartiere": "Centro",
      "numero_civico": "42",
      "riferimento": "Presso chiesa",
      "note": "Accesso da retro",
      "elementi": "Carta,Vetro,Plastica",
      "pap": 1,
      "num_elementi": 3,
      "num_elementi_privati": 1,
      "lat": 41.8919,
      "lon": 12.4949
    }
  ]
}
```
### GET /vie
Recupera l'elenco delle vie con paginazione opzionale.

**Query Parameters:**
- `page` (int, opzionale): Numero di pagina
- `size` (int, opzionale): Elementi per pagina, max 100
- `comune` (int, opzionale): Filtra per ID comune

**Response (senza paginazione):**
```json
[
  {
    "id_via": 1,
    "nome": "Via Roma",
    "id_comune": 1
  }
]
```

### GET /comuni
Recupera l'elenco dei comuni.

**Query Parameters:**
- `id_ambito` (int, opzionale): Filtra per ID ambito
- `cod_istat` (string, opzionale): Filtra per codice ISTAT

**Response:**
```json
[
  {
    "id_comune": 1,
    "descr_comune": "Roma",
    "descr_provincia": "Roma",
    "prefisso_utenti": "06",
    "id_ambito": 1,
    "cod_istat": "058091"
  }
]
```

### GET /civici
Recupera l'elenco dei civici con paginazione opzionale.

**Query Parameters:**
- `page` (int, opzionale): Numero di pagina
- `size` (int, opzionale): Elementi per pagina, max 100
- `id_municipio` (int, opzionale): Filtra per municipio
- `id_via` (int, opzionale): Filtra per ID via

**Response:**
```json
{
  "total": 5000,
  "pages": 100,
  "content": [
    {
      "numero": 42,
      "lettera": "A",
      "colore": "rosso",
      "testo": "42A",
      "cod_strada": "STR001",
      "nome_via": "Via Roma",
      "id_comune": 1,
      "id_municipio": 1,
      "id_quartiere": 5,
      "lat": 41.8919,
      "lon": 12.4949,
      "insert_date": "2024-01-15T10:30:00",
      "update_date": "2024-01-20T14:22:00"
    }
  ]
}
```

### GET /quartieri
Recupera l'elenco dei quartieri.

**Query Parameters:**
- `id_municipio` (int, opzionale): Filtra per ID municipio

**Response:**
```json
[
  {
    "id_quartiere": 1,
    "id_municipio": 1,
    "id_comune": 1,
    "descrizione": "Quartiere Centro"
  }
]
```

### GET /ambiti
Recupera l'elenco degli ambiti.

**Query Parameters:** nessuno

**Response:**
```json
[
  {
    "id_ambito": 1,
    "descr_ambito": "Ambito Centro"
  }
] ]
}
```

### POST /token
Genera un token JWT per autenticare l'utente tramite credenziali LDAP.

**Request Body:**
- `username` (string): Nome utente per l'autenticazione
- `password` (string): Password associata all'utente

**Response:**
```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

**Errori Possibili:**
- **401 Unauthorized**: Credenziali non valide o utente non trovato

## 📁 Struttura del Progetto

```
amiu_sit_api/
├── main.py                      # Applicazione principale FastAPI
├── requirements.txt             # Dipendenze Python
├── README.md                    # Questo file
├── app.log                      # Log dell'applicazione
├── .env                         # Variabili di ambiente (non committare)
├── config/
│   ├── database.py             # Configurazione e connessione DB
│   └── __pycache__/
├── models/
│   ├── models.py               # Definizione modelli Pydantic
│   └── __pycache__/
└── repository/
    ├── piazzole_repo.py        # Query per piazzole
    ├── vie_repo.py             # Query per vie
    └── __pycache__/
```

## 🏗️ Architettura

### Modelli (models.py)
- **MyBaseModel**: Classe base con configurazione Pydantic
- **PaginatedResponse[T]**: Risposta generica paginata con total, page, size, pages, content
- **Piazzola**: Modello per i dati delle piazzole
- **Percorso/Via**: Modello per i dati delle vie

### Database (config/database.py)
- Connessione PostgreSQL tramite SQLAlchemy
- `execute_query()`: Funzione utility per eseguire query raw SQL
- Support per parametrizzazione delle query

### Repository (repository/)
- Contiene le query SQL preparate
- Funzioni dedicate per count e select
- Supporto per filtri dinamici

## 🔧 Configurazione

### Variabili di Ambiente
Tutte le configurazioni vengono caricate da `.env`:

| Variabile | Descrizione |
|-----------|------------|
| `DB_USER` | Utente PostgreSQL |
| `DB_PASSWORD` | Password PostgreSQL |
| `DB_HOST` | Host del server PostgreSQL |
| `DB_PORT` | Porta PostgreSQL (default: 5432) |
| `DB_NAME` | Nome del database |

### Logging
L'applicazione genera log in due destinazioni:
- **File**: `app.log` - Salva tutti i log
- **Console**: Output in tempo reale

Livello di log: INFO

## 📊 Esempi di Utilizzo

### Recuperare tutte le piazzole di una via
```bash
curl "http://localhost:8000/piazzole?via=10"
```

### Recuperare piazzole con paginazione
```bash
curl "http://localhost:8000/piazzole?page=1&size=50&comune=1"
```

### Filtrare per PAP e municipio
```bash
curl "http://localhost:8000/piazzole?pap=1&municipio=1"
```

### Recuperare le vie di un comune
```bash
curl "http://localhost:8000/vie?page=1&size=100&comune=1"
```

## 🐛 Gestione Errori

L'applicazione ritorna:
- **200 OK**: Richiesta riuscita
- **404 Not Found**: Endpoint non trovato
- **422 Unprocessable Entity**: Parametri non validi
- **500 Internal Server Error**: Errore del server (controllare i log)

Tutti gli errori sono loggati in `app.log`.

## 💡 Sviluppo

### Aggiungere un nuovo endpoint
1. Creare la query in `repository/`
2. Definire il modello in `models/models.py`
3. Aggiungere la rotta in `main.py`
4. Testare con curl o Swagger

### Documentazione Interattiva
Swagger UI disponibile a: `http://localhost:8000/docs`

## 📝 Licenza

Progetto AMIU

## 👤 Autore

Team AMIU Development
