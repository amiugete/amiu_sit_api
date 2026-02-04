from fastapi import APIRouter, Query, Depends, HTTPException, status
from config.database import execute_query
from models.models import User
from repository.users_repo import check_user_db
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from config.ldap_amiu import verifica_utente_amiu_LDAP
from config.jwt_token_config import create_access_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

router = APIRouter()

@router.post("/token", description="Genera un token JWT per autenticare")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint per l'autenticazione e la generazione del token JWT"""
    username = form_data.username
    password = form_data.password
    logger.info(f"Ricevuta richiesta di login per l'utente {username}")
    is_authenticated, msg = verifica_utente_amiu_LDAP(username, password)
    if not is_authenticated:
        logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_query = check_user_db(username)
    user_record = execute_query(user_query, {"name": username})
    user_record = user_record.mappings().first() if user_record else None
    if not user_record:
        logger.warning(f"Utente {username} non trovato nel database.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = User(**user_record)
    try:
        access_token = create_access_token(data={"sub": username, "user_id": user.id_user, "email": user.email})
        logger.info(f"Utente {username} autenticato con successo.")
    except Exception as e:
        logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non autorizzato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}
