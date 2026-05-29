from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import time


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
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


_RES_BODY_MAX_BYTES = 500  # caratteri loggati dalla response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        body = await request.body()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000

        # Legge il body della response senza consumarlo
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        res_size = len(response_body)
        is_json = "application/json" in (response.media_type or "")

        if is_json and res_size <= _RES_BODY_MAX_BYTES:
            res_log = response_body.decode("utf-8", errors="replace")
        elif is_json:
            res_log = response_body[:_RES_BODY_MAX_BYTES].decode("utf-8", errors="replace") + f"... [troncato, totale {res_size} bytes]"
        else:
            res_log = f"[{response.media_type}, {res_size} bytes]"

        logger.info(
            "method=%s path=%s status=%s duration_ms=%.1f | req_body=%s | res_body=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            body.decode("utf-8", errors="replace") or "-",
            res_log,
        )

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

# Inizializza l'app FastAPI
app = FastAPI(title="API AMIU", version="1.0.0", description="API per l'accesso ai dati AMIU",root_path="/"+ os.getenv("ENVIRONMENT_CONTEXT_PATH"))

app.add_middleware(RequestLoggingMiddleware)

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

# Mappa endpoint → path locale (senza prefisso del router), usata da check_permissions
app.state.endpoint_local_paths = {
    route.endpoint: route.path
    for sub_router, prefix in [
        (auth_router,          "/auth"),
        (public_router,        ""),
        (mobile_router,        "/mobile"),
        (duale_router,         "/duale"),
        (utenze_router,        "/utenze"),
        (utenze_idea_router,   "/idea"),
        (bilaterale_router,    "/bilaterale"),
        (tellus_router,        "/posteriori"),
        (localizzazione_router,"/locate"),
    ]
    for route in sub_router.routes
    if hasattr(route, "endpoint")
}




