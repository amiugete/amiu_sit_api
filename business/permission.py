from typing import List
import logging
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from business.utility import get_route_path_from_request
from config.database import fetch_list_by_engine, DbConnection
from config.jwt_token_config import check_jwt_token
from repository.users_repo import pst_endpoint_permissions


logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()


        

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


def check_permissions(
    request: Request,
    payload: dict[str, any] = Depends(get_current_user)
) -> dict[str, any]:
    """Dependency che verifica autenticazione e permessi in un unico step."""
    route_path = get_route_path_from_request(request)
    verifica_permessi_endpoint_utente(payload, route_path)
    return payload

def verifica_permessi_endpoint_utente(payload: dict[str, any], indirizzo_ws) -> None:
    """
    Verifica se l'utente ha i permessi necessari per accedere a un endpoint specifico.
    Prende in input il payload dell'utente (ottenuto dal token JWT) e restituisce una tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione.
    Returns:
    Restituisce una tupla (is_authorized: bool, message: str) dove is_authorized indica se l'utente è autorizzato e message fornisce dettagli in caso di mancata autorizzazione.
    """
    # Recupera i ruoli dell'utente dal database considerando la nattura deterministica dei ruoli presenti in base dati es (utenze = True/False)
    permessi_utente :List[str] = payload.get("permessi", [])
    
    permessi_dict = fetch_list_by_engine(pst_endpoint_permissions,
                                         DbConnection.CONFIG, 
                                         {"endpoint": indirizzo_ws})
    
    permessi_necessari = [row['permesso'] for row in permessi_dict]
    
    if permessi_necessari == []:
        logger.info(f"Nessun permesso specifico richiesto per l'endpoint {indirizzo_ws}. Accesso consentito.")
        return  # Nessun permesso specifico richiesto per l'endpoint, accesso consentito
    
    for permesso in permessi_necessari:
        if permesso in permessi_utente:
            logger.info(f"Utente ID {payload.get('user_id')} autorizzato per l'endpoint {indirizzo_ws} con permesso {permesso}.")
            return
        else:
            continue
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Utente non autorizzato per questo endpoint",
        headers={"WWW-Authenticate": "Bearer"},
    )