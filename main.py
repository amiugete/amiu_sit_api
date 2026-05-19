from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


# importo i router dai vari moduli
from public_api import router as public_router
from mobile_api import router as mobile_router
from duale_api import router as duale_router
from utenze_api import router as utenze_router
from utenze_api_idea import router as utenze_idea_router
from bilaterale_api import router as bilaterale_router
from auth_api import router as auth_router
from tellus_api import router as tellus_router
from localizzazione_api import router as localizzazione_router




# Usa la data odierna per il nome del file log
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
today_str = datetime.now().strftime("%Y_%m_%d")
log_filename = f"{log_dir}/app_{today_str}.log"

log_handler = logging.FileHandler(log_filename, encoding="utf-8")
log_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, stream_handler],
    force=True
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Inizializza l'app FastAPI
app = FastAPI(title="API AMIU", version="1.0.0", description="API per l'accesso ai dati AMIU",root_path="/"+ os.getenv("ENVIRONMENT_CONTEXT_PATH"))


# 1. Definisci gli "origins" (chi può chiamare la tua API)
origins = [
    "http://localhost:8100",   # Il default di Ionic in sviluppo
    "http://localhost",         # Per i test da mobile
    "https://localhost",         # Per i test da mobile
    "capacitor://localhost",    # Necessario per iOS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],               # Permette GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],               # Permette tutti gli header (es. Authorization)
)


# Definizione del router per l'autenticazione
app.include_router(prefix="/auth", tags=["Servizi di autenticazione"], router=auth_router)


# Definizione dei router per i servizi ad con accesso autorizzato
app.include_router(prefix="", router=public_router)
app.include_router(prefix="/mobile", router=mobile_router)
app.include_router(prefix="/duale", router=duale_router)
app.include_router(prefix="/utenze", router=utenze_router)
app.include_router(prefix="/idea", router=utenze_idea_router)
app.include_router(prefix="/bilaterale", router=bilaterale_router)
app.include_router(prefix="/posteriori", router=tellus_router)
app.include_router(prefix="/locate", router=localizzazione_router)




