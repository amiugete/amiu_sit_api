from typing import List
import logging
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config.database import execute_query
from config.jwt_token_config import check_jwt_token
from models.models import UserRoles
from repository.users_repo import get_lista_permessi_endpoint, get_user_roles

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

bearer_scheme = HTTPBearer()

def verifica_permesso_utente_endpoint(endpoint: str, id_user: int) -> tuple[bool, str]:
    """
       Recupera la lista dei permessi associati all'utente per un endpoint specifico:
       Verifica a fronte dei permessi dell'utente ricavati sulla tabella sys_users_ws
       di avere i permessi per l'accesso all'endpoint richiesto.
       Ritorna una tupla[bool, str] la quale True per utente abilitato False e messaggio
       se non ci sono le abilitazioni o configurazioni.
    """
    # Recupera i ruoli dell'utente dal database considerando la nattura deterministica dei ruoli presenti in base dati es (utenze = True/False)
    permessi :List[str] = []
    active_roles_user :List[str] = []
   
    query_roles = get_user_roles()
    roles_result = execute_query(query_roles, {"id_user": id_user})
    roles = roles_result.mappings().first() if roles_result else None

    # Se l'utente ha ruoli assegnati, li elabora la classe UserRoles
    if roles:
        user_roles = UserRoles(**roles)
        active_roles_user = user_roles.get_active_roles()
    else:
        return False, "Utente senza ruoli assegnati"

    # Recupera i permessi associati ai ruoli per l'endpoint specificato
    query_perms = get_lista_permessi_endpoint()
    perms_result = execute_query(query_perms, {"endpoint": endpoint})

    
    if perms_result:
       permessi = [row['permesso'] for row in perms_result.mappings()]
       if permessi is None or len(permessi) == 0:
           logger.info(f"Nessun permesso trovato per l'endpoint {endpoint}")
           return True,""  # Nessun permesso richiesto per l'endpoint
       for permesso in permessi:
           if permesso in active_roles_user:
               logger.info(f"Utente ID {id_user} autorizzato per l'endpoint {endpoint} con permesso {permesso}")
               return True, ""
           else:
            continue         
    else:
       logger.info(f"Nessun permesso trovato per l'endpoint {endpoint}")
       return True,""  # Nessun permesso richiesto per l'endpoint  


    return False,'Utente non autorizzato'


# Dipendenza per ottenere l'utente corrente dal token JWT
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    # Verifica il token JWT
    token = credentials.credentials
    logger.info("Verifica del token JWT in corso...")
    logger.info(token)
    try:
        payload = check_jwt_token(token)
        logger.info(f"Token valido per l'utente {payload.get('sub')}")
    except Exception as e:
        logger.warning(f"Token non valido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
