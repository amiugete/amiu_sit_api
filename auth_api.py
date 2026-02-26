from fastapi import APIRouter, Form, HTTPException, status,Request #, Query, Depends

from pydantic import SecretStr

from config.database import fetch_one_by_query,init_security_log_db,get_security_connection, init_security_log_user_db
from models.models import SecurityLogUser, User,UserRoles,SecurityLog
from repository.users_repo import check_user_db, get_user_roles
from repository.security_repo import get_security_log_by_user, insert_security_log_user, reset_attempts_and_ban_count_user, update_access_log, update_access_log_user, update_attempts0_block_24h_user, update_attempts0_block_30min,update_attempts0_block_24h, update_attempts0_block_30min_user, update_attempts0_block_30min_user, update_attempts0_block_permanent, get_security_log_by_ip,insert_security_log, update_attempts0_block_permanent_user,update_attempts_only,reset_attempts_and_ban_count, update_attempts_only_user
import logging
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
from config.ldap_amiu import verifica_utente_amiu_LDAP
from config.jwt_token_config import create_access_token
import sqlite3
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

router = APIRouter()



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

        # tabella security_logs inizializzata se non esiste già
        init_security_log_db()
        init_security_log_user_db()

        connection = get_security_connection()
        connection.row_factory = sqlite3.Row

        # Recupera il record per questo IP dalla tabella security_logs se presente
        security_log : Optional[SecurityLog] = select_security_log_by_ip(connection, ip)
        security_log_user : Optional[SecurityLogUser] = select_security_log_user_by_user(connection, username)

        # Se non esiste un record per questo IP, viene creato con attempts=0, ban_count=0
        if not security_log:
            insert_security_log_for_ip(connection, ip)
            logger.debug(f"Creato nuovo record di sicurezza per IP {ip}")
            # Dopo l'inserimento, recupera nuovamente il record per avere i valori aggiornati
            security_log = select_security_log_by_ip(connection, ip)

        # Se non esiste un record per questo utente, viene creato con attempts=0, ban_count=0
        if not security_log_user:
            insert_security_log_for_user(connection, username)
            logger.debug(f"Creato nuovo record di sicurezza per utente {username}")
            # Dopo l'inserimento, recupera nuovamente il record per avere i valori aggiornati
            security_log_user = select_security_log_user_by_user(connection, username)

        ###### Registro l'accesso al server ############
        register_access_log(connection, security_log.ip_address)
        register_access_log_user(connection, security_log_user.user)
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
        manage_security_log_on_failure(security_log, connection)
        manage_security_log_user_on_failure(security_log_user, connection)
        logger.warning(f"Autenticazione fallita per l'utente {username}: {msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        # Se va a buon fine, resetta attempts e ban_count a 0 e la data di blocco
        reset_log_security(connection, ip)
        reset_log_security_user(connection, username)
        logger.info(f"Autenticazione riuscita per l'utente {username}")
        
    ############### VErifica presenza utente nel database #######################
    user_query = check_user_db(username)

    try:
        user_record = fetch_one_by_query(user_query, {"name": username})
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
    
    # Creazione dell'oggetto User con i dati recuperati dal database per inserimento parametri nel token JWT
    user = User(**user_record)

    # Una volta ottenuto l'utente verifico se ha il permesso per l'utenze e lo aggiungo al token come parametro per poterlo utilizzare nei servizi che richiedono questo permesso specifico####
    # Per eventuali futuri permessi, si potrebbe implementare una logica simile per aggiungere altri parametri al token in base ai permessi dell'utente, in modo da avere un token più ricco di informazioni sui privilegi dell'utente.
    user_roles_query = get_user_roles()
    utente_role = fetch_one_by_query(user_roles_query, {"id_user": user.id_user})
    utente_role = UserRoles(**utente_role) if utente_role else None
    utenze_param = {"utenze": utente_role.utenze if utente_role is not None and utente_role.utenze else False}
    ################################################################################################################
    try:
        access_token = create_access_token(data={"sub": username, "user_id": user.id_user, "email": user.email, "role": user.role_name,**utenze_param})
        logger.info(f"Utente {username} autenticato con successo.")
    except Exception as e:
        logger.error(f"Errore durante la creazione del token per l'utente {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non autorizzato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}
###########################################################################################################################################################################


############################################# Funzioni per la gestione dei log di sicurezza #######################################################################################################################################################################################################################

def get_client_ip(request: Request):
    # Prova a prendere l'IP passatoci dal Proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]  # Prendi il primo IP della lista
    return request.client.host

def select_security_log_by_ip(conn: sqlite3.Connection, ip: str) -> Optional[SecurityLog]:
    """Controlla se esiste un record di sicurezza per l'IP specificato e restituisce un oggetto SecurityLog o None."""
    cursor = conn.cursor()
    cursor.execute(get_security_log_by_ip(), {"ip_address": ip})
    row = cursor.fetchone()
    if row:
        return SecurityLog(**row)
    return None

def select_security_log_user_by_user(conn: sqlite3.Connection, user: str) -> Optional[SecurityLogUser]:
    """Controlla se esiste un record di sicurezza per l'utente specificato e restituisce un oggetto SecurityLogUser o None."""
    cursor = conn.cursor()
    cursor.execute(get_security_log_by_user(), {"user": user})
    row = cursor.fetchone()
    if row:
        return SecurityLogUser(**row)
    return None


def insert_security_log_for_ip(conn: sqlite3.Connection, ip: str):
    """Inserisce un nuovo record di sicurezza per l'IP specificato con attempts=0 e ban_count=0."""
    cursor = conn.cursor()
    cursor.execute(insert_security_log(), {"ip_address": ip})
    conn.commit()

def insert_security_log_for_user(conn: sqlite3.Connection, user: str):
    """Inserisce un nuovo record di sicurezza per l'utente specificato con attempts=0 e ban_count=0."""
    cursor = conn.cursor()
    cursor.execute(insert_security_log_user(), {"user": user})
    conn.commit()

def reset_log_security(conn: sqlite3.Connection, ip: str):
        cursor = conn.cursor()
        cursor.execute(reset_attempts_and_ban_count(), {"ip_address": ip})
        conn.commit()

def reset_log_security_user(conn: sqlite3.Connection, user: str):
        cursor = conn.cursor()
        cursor.execute(reset_attempts_and_ban_count_user(), {"user": user})
        conn.commit()

def manage_security_log_on_failure(securityLog_record: SecurityLog, conn: sqlite3.Connection):
    """
    Gestisce il log di sicurezza in caso di fallimento dell'autenticazione, implementando un sistema di blocco progressivo:
    - Se attempts < 3: incrementa solo il contatore dei tentativi falliti (attempts).
    - Se attempts == 3 e ban_count == 0: blocca l'IP per 30 minuti (primo blocco temporaneo).
    - Se attempts == 3 e ban_count == 1: blocca l'IP per 24 ore (secondo blocco temporaneo).
    - Se attempts == 3 e ban_count >= 2: blocco permanente (imposta una data molto lontana).
    Dopo ogni blocco, il contatore attempts viene azzerato e ban_count incrementato.
    """
    cursor = conn.cursor()
    if securityLog_record:
        # Caso: meno di 3 tentativi falliti, solo incremento del contatore
        if securityLog_record.attempts < 3:
            new_attempts = securityLog_record.attempts + 1
            cursor.execute(update_attempts_only(), {"attempts": new_attempts, "ip_address": securityLog_record.ip_address})
            conn.commit()
        # Caso: 3 tentativi falliti, primo blocco temporaneo di 30 minuti
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 0:
            cursor.execute(update_attempts0_block_30min(), { "ip_address": securityLog_record.ip_address})
            conn.commit()
        # Caso: 3 tentativi falliti, secondo blocco temporaneo di 24 ore
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 1:
            cursor.execute(update_attempts0_block_24h(), {"ip_address": securityLog_record.ip_address})
            conn.commit()
        # Caso: 3 tentativi falliti, blocco permanente
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count >= 2:
            cursor.execute(update_attempts0_block_permanent(), {"ip_address": securityLog_record.ip_address})
            conn.commit()

def manage_security_log_user_on_failure(securityLog_record: SecurityLogUser, conn: sqlite3.Connection):
    """
    Gestisce il log di sicurezza in caso di fallimento dell'autenticazione, implementando un sistema di blocco progressivo:
    - Se attempts < 3: incrementa solo il contatore dei tentativi falliti (attempts).
    - Se attempts == 3 e ban_count == 0: blocca l'IP per 30 minuti (primo blocco temporaneo).
    - Se attempts == 3 e ban_count == 1: blocca l'IP per 24 ore (secondo blocco temporaneo).
    - Se attempts == 3 e ban_count >= 2: blocco permanente (imposta una data molto lontana).
    Dopo ogni blocco, il contatore attempts viene azzerato e ban_count incrementato.
    """
    cursor = conn.cursor()
    if securityLog_record:
        # Caso: meno di 3 tentativi falliti, solo incremento del contatore
        if securityLog_record.attempts < 3:
            new_attempts = securityLog_record.attempts + 1
            cursor.execute(update_attempts_only_user(), {"attempts": new_attempts, "user": securityLog_record.user})
            conn.commit()
        # Caso: 3 tentativi falliti, primo blocco temporaneo di 30 minuti
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 0:
            cursor.execute(update_attempts0_block_30min_user(), { "user": securityLog_record.user})
            conn.commit()
        # Caso: 3 tentativi falliti, secondo blocco temporaneo di 24 ore
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count == 1:
            cursor.execute(update_attempts0_block_24h_user(), {"user": securityLog_record.user})
            conn.commit()
        # Caso: 3 tentativi falliti, blocco permanente
        elif securityLog_record.attempts == 3 and securityLog_record.ban_count >= 2:
            cursor.execute(update_attempts0_block_permanent_user(), {"user": securityLog_record.user})
            conn.commit()


def register_access_log(conn: sqlite3.Connection, ip: str):
    """Aggiorna last_access e incrementa count_access dopo un login riuscito."""
    cursor = conn.cursor()
    cursor.execute(update_access_log(), {"ip_address": ip})
    conn.commit()

def register_access_log_user(conn: sqlite3.Connection, user: str):
    """Aggiorna last_access e incrementa count_access dopo un login riuscito."""
    cursor = conn.cursor()
    cursor.execute(update_access_log_user(), {"user": user})
    conn.commit()

#######################################################################################################################################################################################################################





