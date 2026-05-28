from fastapi import APIRouter, Form, HTTPException, status,Request #, Query, Depends
from pydantic import SecretStr

from business.email.email_engine import send_email_territorio
from config.database import fetch_list_by_engine, fetch_one_by_engine, update_query_by_engine, insert_query_by_engine, DbConnection
from models.models import SecurityLogUser, User, UserPermission,UserRoles,SecurityLog,Block
from repository.users_repo import pst_check_user_db, pst_user_roles, pst_user_roles
from repository.security_repo import pst_security_log_by_user, pst_insert_security_log_user, pst_reset_attempts_and_ban_count_user, pst_update_access_log, pst_update_access_log_user, pst_update_attempts0_block_24h_user, pst_update_attempts0_block_30min, pst_update_attempts0_block_24h, pst_update_attempts0_block_30min_user, pst_update_attempts0_block_permanent, pst_security_log_by_ip, pst_insert_security_log, pst_update_attempts0_block_permanent_user, pst_update_attempts_only, pst_reset_attempts_and_ban_count, pst_update_attempts_only_user
import logging
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
from config.ldap_amiu import verifica_utente_amiu_LDAP
from config.jwt_token_config import create_access_token
from datetime import datetime
from typing import Optional, Tuple


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

router = APIRouter()

############################################################################################################################################################################
#################################################################################################################################
###########################################      API        ################################################################
@router.post("/token", description="Genera un token JWT per autenticare")
async def login(request: Request,
                username: str = Form(..., description="Utente di dominio"),
                password: SecretStr = Form(..., description="Password dell'utente di dominio")):
    """Endpoint per l'autenticazione e la generazione del token JWT"""
    try:
        # 1. Recupera l'IP del client
        ip = get_client_ip(request)
        # Per forzare la valutazione della password e loggare eventuali errori di input

        # Recupera il record per questo IP dalla tabella security_logs se presente
        security_log : Optional[SecurityLog] = select_security_log_by_ip(ip)
        security_log_user : Optional[SecurityLogUser] = select_security_log_user_by_user(username)

        # Se non esiste un record per questo IP, viene creato con attempts=0, ban_count=0
        if not security_log:
            insert_security_log_for_ip(ip)
            logger.debug(f"Creato nuovo record di sicurezza per IP {ip}")
            # Dopo l'inserimento, recupera nuovamente il record per avere i valori aggiornati
            security_log = select_security_log_by_ip(ip)

        # Se non esiste un record per questo utente, viene creato con attempts=0, ban_count=0
        if not security_log_user:
            insert_security_log_for_user(username)
            logger.debug(f"Creato nuovo record di sicurezza per utente {username}")
            # Dopo l'inserimento, recupera nuovamente il record per avere i valori aggiornati
            security_log_user = select_security_log_user_by_user(username)

        ###### Registro l'accesso al server ############
        register_access_log(security_log.ip_address)
        register_access_log_user(security_log_user.user)
    except HTTPException as http_exc:
        # Loggo comunque le HTTPException per tracciabilità
        logger.error(f"HTTPException: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception(f"Errore imprevisto durante la login per utente {username}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Errore interno inatteso durante l'autenticazione. Contattare l'amministratore.",
        )

    ###### Calcolo la data di adesso per eventuali confronti con la data di blocco dell'indirizzo ##############
    datetime_now = datetime.now()
    ##########################################

    #### Prendo la data di eventuale blocco dell'indirizzo ip
    data_blocked = security_log.blocked_until
    ##########################################

    ######## Se ip è bloccato ti fermo subito ###################
    if data_blocked and datetime_now < data_blocked:
        time_remaining = data_blocked - datetime_now
        minutes_remaining = int(time_remaining.total_seconds() // 60)
        logger.warning(f"IP {ip} è attualmente bloccato fino alle {data_blocked} (restano {minutes_remaining} minuti)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"IP bloccato. Riprova tra {minutes_remaining} minuti."
        )
    #########################################################

    ######## Se user è bloccato ti fermo subito ###################
    data_blocked_user = security_log_user.blocked_until
    if data_blocked_user and datetime_now < data_blocked_user:
        time_remaining = data_blocked_user - datetime_now
        minutes_remaining = int(time_remaining.total_seconds() // 60)
        logger.warning(f"Utente {username} è attualmente bloccato fino alle {data_blocked_user} (restano {minutes_remaining} minuti)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Utente {username} bloccato. Riprova tra {minutes_remaining} minuti."
        )
    #########################################################

    ########### Prodeguo con Verifica LDAP se fallisce aggiorno attempts #####################
    is_authenticated, msg = verifica_utente_amiu_LDAP(username, password.get_secret_value())

    ##### Se LDAP fallisce inizia un sistema di blocco progressivo in base al numero di tentativi falliti per questo IP, con blocchi crescenti a 30 minuti, 24 ore e infine permanente dopo 3 tentativi falliti consecutivi. Se l'autenticazione ha successo, invece, si resetta il contatore dei tentativi e dei ban per questo IP. ######
    if not is_authenticated:
        # Gestione di blocchi progressivi in caso di fallimenti ripetuti, con log degli eventi di sicurezza
        is_blocked_ip, block_type_ip = manage_security_log_on_failure(security_log)
        is_blocked_user, block_type_user = manage_security_log_user_on_failure(security_log_user)

        #Se l'utente è stato bloccato a causa dei tentativi falliti, invia un'email di notifica al territorio
        if is_blocked_user:
            send_email_on_block(username, block_type_user)
        if is_blocked_ip:
            send_email_on_block(ip, block_type_ip)

        logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        # Se va a buon fine, resetta attempts e ban_count a 0 e la data di blocco
        reset_log_security(ip)
        reset_log_security_user(username)
        logger.info(f"Autenticazione riuscita per l'utente {username}")
        
    ############### VErifica presenza utente nel database #######################
    try:
        user_record = fetch_one_by_engine(pst_check_user_db, DbConnection.CONFIG, {"username": username})
        if not user_record:
            logger.warning(f"Utente {username} non trovato nel database.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non trovato",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Errore durante la verifica dell'utente {username} nel database: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Errore utente non trovato",
        )    
    
    user = User(**user_record)

    ######### Recupero i permessi associati all'utente per includerli nel token JWT, in modo da poterli utilizzare per l'autorizzazione a livello di endpoint. Se l'utente non ha permessi specifici, il token conterrà comunque un campo "permessi" vuoto, che potrà essere gestito dagli endpoint per negare l'accesso se necessario. #########
    rows_utente_permission = fetch_list_by_engine(pst_user_roles,
                                                  DbConnection.CONFIG, 
                                                  {"id_user": user.id})
    #### Creo la lista di permessi a partire dalle righe restituite dalla query, estraendo il campo "permesso" da ogni riga. Se l'utente non ha permessi specifici, questa lista sarà vuota. #####
    permessi = [row['permesso'] for row in rows_utente_permission]
    
    logger.info(f"Permessi per l'utente ID {user.id}: {permessi if permessi else 'Nessun permesso specifico trovato'}")
    
    try:
        access_token = create_access_token(data={"user_id": user.id, "sub": user.username , "permessi": permessi})
        logger.info(f"Utente {username} autenticato con successo.")
    except Exception as e:
        logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non autorizzato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}
################################################################## FINE API #########################################################################################################
###########################################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
############################################# FUNZIONI PER LA GESTIONE DEI LOG DI SICUREZZA #######################################################################################################################################################################################################################

def get_client_ip(request: Request):
    # Prova a prendere l'IP passatoci dal Proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]  # Prendi il primo IP della lista
    return request.client.host

def select_security_log_by_ip(ip: str) -> Optional[SecurityLog]:
    """Controlla se esiste un record di sicurezza per l'IP specificato e restituisce un oggetto SecurityLog o None."""
    row = fetch_one_by_engine(pst_security_log_by_ip, DbConnection.CONFIG, {"ip_address": ip})
    if row:
        return SecurityLog(**row)
    return None

def select_security_log_user_by_user(user: str) -> Optional[SecurityLogUser]:
    """Controlla se esiste un record di sicurezza per l'utente specificato e restituisce un oggetto SecurityLogUser o None."""
    row = fetch_one_by_engine(pst_security_log_by_user, DbConnection.CONFIG, {"user": user})
    if row:
        return SecurityLogUser(**row)
    return None


def insert_security_log_for_ip(ip: str):
    """Inserisce un nuovo record di sicurezza per l'IP specificato con attempts=0 e ban_count=0."""
    insert_query_by_engine(pst_insert_security_log, DbConnection.CONFIG, {"ip_address": ip})

def insert_security_log_for_user(user: str):
    """Inserisce un nuovo record di sicurezza per l'utente specificato con attempts=0 e ban_count=0."""
    insert_query_by_engine(pst_insert_security_log_user, DbConnection.CONFIG, {"user": user})

def reset_log_security(ip: str):
    update_query_by_engine(pst_reset_attempts_and_ban_count, DbConnection.CONFIG, {"ip_address": ip})

def reset_log_security_user(user: str):
    update_query_by_engine(pst_reset_attempts_and_ban_count_user, DbConnection.CONFIG, {"user": user})

def manage_security_log_on_failure(securityLog_record: SecurityLog) -> Tuple[bool, Block]:
    """
    Gestisce il log di sicurezza in caso di fallimento dell'autenticazione, implementando un sistema di blocco progressivo:
    - Se attempts < 3: incrementa solo il contatore dei tentativi falliti (attempts).
    - Se attempts == 3 e ban_count == 0: blocca l'IP per 30 minuti (primo blocco temporaneo).
    - Se attempts == 3 e ban_count == 1: blocca l'IP per 24 ore (secondo blocco temporaneo).
    - Se attempts == 3 e ban_count >= 2: blocco permanente (imposta una data molto lontana).
    Dopo ogni blocco, il contatore attempts viene azzerato e ban_count incrementato.<br>
    Ritorna una tupla (is_blocked: bool, block_type: Block) per indicare se l'IP è stato bloccato e il tipo di blocco applicato.
    """
    if securityLog_record:
        # Caso: meno di 3 tentativi falliti, solo incremento del contatore
        if securityLog_record.attempts < 3:
            new_attempts = securityLog_record.attempts + 1
            update_query_by_engine(pst_update_attempts_only, DbConnection.CONFIG, {"attempts": new_attempts, "ip_address": securityLog_record.ip_address})
            return False, None
        # Caso: 3 tentativi falliti, primo blocco temporaneo di 30 minuti
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 0:
            update_query_by_engine(pst_update_attempts0_block_30min, DbConnection.CONFIG, {"ip_address": securityLog_record.ip_address})
            return True, Block.MIN_30
        # Caso: 3 tentativi falliti, secondo blocco temporaneo di 24 ore
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 1:
            update_query_by_engine(pst_update_attempts0_block_24h, DbConnection.CONFIG, {"ip_address": securityLog_record.ip_address})
            return True, Block.H_24
        # Caso: 3 tentativi falliti, blocco permanente
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count >= 2:
            update_query_by_engine(pst_update_attempts0_block_permanent, DbConnection.CONFIG, {"ip_address": securityLog_record.ip_address})
            return True, Block.PERMANENT
        
        return False, None

def manage_security_log_user_on_failure(securityLog_record: SecurityLogUser) -> Tuple[bool, Block]:
    """
    Gestisce il log di sicurezza in caso di fallimento dell'autenticazione, implementando un sistema di blocco progressivo:
    - Se attempts < 3: incrementa solo il contatore dei tentativi falliti (attempts).
    - Se attempts == 3 e ban_count == 0: blocca l'IP per 30 minuti (primo blocco temporaneo).
    - Se attempts == 3 e ban_count == 1: blocca l'IP per 24 ore (secondo blocco temporaneo).
    - Se attempts == 3 e ban_count >= 2: blocco permanente (imposta una data molto lontana).
    Dopo ogni blocco, il contatore attempts viene azzerato e ban_count incrementato.<br>
    Ritorna una tupla (is_blocked: bool, block_type: Block) per indicare se l'utente è stato bloccato e di che tipo di blocco si tratta, in modo da poter eventualmente inviare notifiche o loggare l'evento.
    """
    if securityLog_record:
        # Caso: meno di 3 tentativi falliti, solo incremento del contatore
        if securityLog_record.attempts < 3:
            new_attempts = securityLog_record.attempts + 1
            update_query_by_engine(pst_update_attempts_only_user, DbConnection.CONFIG, {"attempts": new_attempts, "user": securityLog_record.user})
            return False, None
        # Caso: 3 tentativi falliti, primo blocco temporaneo di 30 minuti
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 0:
            update_query_by_engine(pst_update_attempts0_block_30min_user, DbConnection.CONFIG, {"user": securityLog_record.user})
            return True, Block.MIN_30
        # Caso: 3 tentativi falliti, secondo blocco temporaneo di 24 ore
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 1:
            update_query_by_engine(pst_update_attempts0_block_24h_user, DbConnection.CONFIG, {"user": securityLog_record.user})
            return True, Block.H_24
        # Caso: 3 tentativi falliti, blocco permanente
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count >= 2:
            update_query_by_engine(pst_update_attempts0_block_permanent_user, DbConnection.CONFIG, {"user": securityLog_record.user})
            return True, Block.PERMANENT
        
        return False, None
    

def send_email_on_block(block_ref:str, block_type: Block):
    """Invia un'email di notifica al territorio quando un utente o un IP viene bloccato a causa di tentativi di accesso falliti."""
    subject = f"{block_type.value} per {block_ref}"
    body = f"{block_ref} è stato bloccato con {block_type.value} a causa di tentativi di accesso falliti."
    send_email_territorio(subject, body)    


def register_access_log(ip: str):
    """Aggiorna last_access e incrementa count_access dopo un login riuscito."""
    update_query_by_engine(pst_update_access_log, DbConnection.CONFIG, {"ip_address": ip})

def register_access_log_user(user: str):
    """Aggiorna last_access e incrementa count_access dopo un login riuscito."""
    update_query_by_engine(pst_update_access_log_user, DbConnection.CONFIG, {"user": user})





