from fastapi import FastAPI
import logging
from public_api import router as public_router
from idea_api import router as idea_router
from auth_api import router as auth_router
from tellus_api import router as tellus_router
from localizzazione_api import router as localizzazione_router
from logging.handlers import TimedRotatingFileHandler
# Usa la data odierna per il nome del file log
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
today_str = datetime.now().strftime("%Y%m%d")
log_filename = f"{log_dir}/app_{today_str}.log"

log_handler = logging.FileHandler(log_filename, encoding="utf-8")
log_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, stream_handler]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Inizializza l'app FastAPI
app = FastAPI(title="API AMIU SIT", version="1.0.0", description="API per l'accesso ai dati geografici di AMIU",root_path="/"+ os.getenv("ENVIRONMENT_CONTEXT_PATH"))

# Definizione del router per l'autenticazione (accesso libero)
app.include_router(prefix="/auth", tags=["Servizi di autenticazione"], router=auth_router)
# Definizione del router per i servizi pubblici (accesso libero)
app.include_router(prefix="", tags=["Servizi ad accesso libero"], router=public_router)
app.include_router(prefix="", router=idea_router)
app.include_router(prefix="", router=tellus_router)
app.include_router(prefix="", router=localizzazione_router)


