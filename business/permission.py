from typing import List
import logging
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config.database import fetch_list_by_query,fetch_one_by_query
from config.jwt_token_config import check_jwt_token
from models.models import UserRoles
from repository.users_repo import get_lista_permessi_endpoint, get_user_roles


logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

def verifica_permesso_utenze(payload: dict[str, any], indirizzo_ws) -> tuple[bool, str]:
    """
    Verifica se l'utente ha i permessi necessari per accedere a un endpoint specifico.
    Prende in input il payload dell'utente (ottenuto dal token JWT) e restituisce una tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione.
    Returns:
    Restituisce una tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione.
    """
    # Recupera i ruoli dell'utente dal database considerando la nattura deterministica dei ruoli presenti in base dati es (utenze = True/False)
    #UTENZE_ENDPOINT = "/utenze_tari"
    permessi :List[str] = []
    active_roles_user :List[str] = []

    # Se l'utente ha ruoli assegnati, li elabora la classe UserRoles in concreto gli passo il valore boleano nel campo utenze e lui se True me lo aggiunge in un array 
    # di stringhe con il metodo di classe get_active_roles() che restituisce un array di stringhe 
    # con i ruoli attivi per l'utente in base al valore boleano passato, 
    # se False non aggiunge nulla all'array dei ruoli attivi. Se l'utente non ha ruoli assegnati restituisco False e un messaggio di errore.
    if payload.get("user_id") is not None :
        
    
    ### ATTENZIONE: se l'utente ha più ruoli assegnati (es. utenze = True e idea = True)
    # bisognerebbe renderlo dinamico 
    
    
    # if payload.get("user_id") and payload.get("utenze") is not None:
        user_roles = UserRoles(id_user=payload.get("user_id"), 
                               utenze=payload.get("utenze"), 
                               idea=payload.get("idea"))
        active_roles_user = user_roles.get_active_roles()
        
    else:
        return False, "Utente senza ruoli assegnati"
    
    logger.info(f'user_roles: {user_roles}')
    logger.info(f"active_roles_user: {active_roles_user}")
    
    
    
    return verifica_permesso_endpoint_utente( id_user=payload.get("user_id"),
                                              endpoint=indirizzo_ws,
                                              active_permiss_user=active_roles_user)


def verifica_permesso_endpoint_utente(id_user: int, endpoint: str, active_permiss_user: List[str],) -> tuple[bool, str]:
   # Recupera i permessi associati ai ruoli per l'endpoint specificato e li confrona con i permessi attivi all'utente
    """
    Verifica se l'utente ha i permessi necessari per accedere a un endpoint specifico.
    prende in input id_user, endpoint e active_permiss_user e restituisce una tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione.

    :param id_user: ID dell'utente per cui verificare i permessi
    :type id_user: int
    :param endpoint: Endpoint per cui verificare i permessi
    :type endpoint: str
    :param active_permiss_user: Lista dei permessi attivi dell'utente
    :type active_permiss_user: List[str]
    :return: Tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione
    :rtype: tuple[bool, str]
    """
    if id_user is None:
        logger.warning("ID utente non presente nel payload")
        return False, "utente non presente nel payload"

    query_perms = get_lista_permessi_endpoint()
    perms_result = fetch_list_by_query(query_perms, {"endpoint": endpoint})
    
    logger.info(f"Permessi richiesti per l'endpoint {endpoint}: {[row['permesso'] for row in perms_result]}")
    
    logger.info(f'active_permiss_user: {active_permiss_user}')
    if perms_result:
       permessi = [row['permesso'] for row in perms_result]
       if permessi is None or len(permessi) == 0:
           logger.info(f"Nessun permesso trovato per l'endpoint {endpoint}")
           return True,""  # Nessun permesso richiesto per l'endpoint
       for permesso in permessi:
           if permesso in active_permiss_user:
               logger.info(f"Utente {id_user} autorizzato per l'endpoint {endpoint} con permesso {permesso}")
               return True, ""# Utente autorizzato per l'endpoint
           else:
            continue
    else:
       logger.info(f"Nessun permesso trovato per l'endpoint {endpoint}")
       return False,""  # Nessun permesso richiesto per l'endpoint


    return False,f'Utente {id_user} non autorizzato'


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
