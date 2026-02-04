from fastapi import FastAPI
import logging
from public_api import router as public_router
from utenze_api import router as utenze_router
from auth_api import router as auth_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"), # Scrive su file
        logging.StreamHandler()         # Scrive su console
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Inizializza l'app FastAPI##############################
app = FastAPI(title="API AMIU SIT", version="1.0.0", description="API per l'accesso ai dati geografici di AMIU")

# Definizione del router per l'autenticazione (accesso libero)
app.include_router(prefix="/auth",tags=["Servizi di autenticazione"], router=auth_router)
# Definizione del router per i servizi pubblici (accesso libero)
app.include_router(prefix="/ws_amiugis", tags=["Servizi ad accesso libero"], router=public_router)
app.include_router(prefix="/ws_amiugis", router=utenze_router)