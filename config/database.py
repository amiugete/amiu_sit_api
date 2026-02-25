# database.py

import sqlite3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import oracledb
from typing import List, Optional

# Carica le variabili dal file .env
load_dotenv()

# Recupera i valori dalle variabili d'ambiente di SIT
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Recupera i valori dalle variabili d'ambiente delle MAPPE
user_mappe = os.getenv("DB_USER_MAPPE")
password_mappe = os.getenv("DB_PASSWORD_MAPPE")
host_mappe = os.getenv("DB_HOST_MAPPE")
port_mappe = os.getenv("DB_PORT_MAPPE")
db_name_mappe = os.getenv("DB_NAME_MAPPE")

# Recupera i valori dalle variabili d'ambiente delle per STRADE DB ORACLE
path_client_oracle = os.getenv("ORACLE_CLIENT_PATH")
user_oracle = os.getenv("DB_USER_STRADE")
password_oracle = os.getenv("DB_PASSWORD_STRADE")
host_oracle = os.getenv("DB_HOST_STRADE")
port_oracle = os.getenv("DB_PORT_STRADE")
db_name_oracle = os.getenv("DB_NAME_STRADE")

# Inizializza il client Oracle
oracledb.init_oracle_client(lib_dir=path_client_oracle)

################# Strnga di connessione base dati ##########################
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

################# Strnga di connessione base dati Mappe ##########################
DATABASE_URL_MAPPE = f"postgresql+psycopg2://{user_mappe}:{password_mappe}@{host_mappe}:{port_mappe}/{db_name_mappe}"

################# Strnga di connessione base dati Strade ##########################

DATABASE_URL_STRADE = f"oracle+oracledb://{user_oracle}:{password_oracle}@{host_oracle}:{port_oracle}/{db_name_oracle}"


################################                  ############################
################################ SINGLETON ENGINE ####################################
################################                  ##########################
engine = create_engine(
     DATABASE_URL,
     echo=True,
     pool_pre_ping=True,  # Verifica la connessione prima di usarla
     pool_recycle=900    # Ricicla le connessioni ogni 15 minuti
)
engine_mappe = create_engine(
     DATABASE_URL_MAPPE,
     echo=True,
     pool_pre_ping=True,
     pool_recycle=900
)
engine_oracle = create_engine(
     DATABASE_URL_STRADE,
     echo=True
)
####################################################################################
####################################################################################
####################################################################################

#### Inizializza il logger ########
logger = logging.getLogger(__name__)

#################### Funzione di esecuzione query ########################
def fetch_list_by_query(sql: str, params=None) -> Optional[List[dict]]:
     """Esegue una query sul database SIT e ritorna una lista di risultati."""
     try:
          with engine.connect() as connection:
               stream = connection.execute(text(sql), params or {})
               return stream.mappings().all() if stream else []
     except Exception as e:
          logger.error(f"Errore SQL o di connessione: {str(e)}")
          return None
   
#################### Funzione di esecuzione query ########################
def fetch_one_by_query(sql: str, params=None) -> Optional[dict]:
     """Esegue una query sul database SIT e ritorna un singolo risultato come dict."""
     try:
          with engine.connect() as connection:
               stream = connection.execute(text(sql), params or {})
               return stream.mappings().first() if stream else None
     except Exception as e:
          logger.error(f"Errore SQL o di connessione: {str(e)}")
          return None
   
#################### Funzione di esecuzione query  Mappe ########################
def fetch_list_by_query_mappe(sql, params=None) -> Optional[List[dict]]:
   """Esegue una query sul database Mappe e ritorna una lista di risultati."""
   try:   
        with engine_mappe.connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().all() if stream else []
   except Exception as e:
        logger.error(f"Errore SQL o di connessione: {str(e)}")
        return None
   
#################### Funzione di esecuzione query  Strade ########################
def fetch_list_by_query_strade(sql, params=None) -> Optional[List[dict]]:
   """Esegue una query sul database Strade e ritorna una lista di risultati."""
   try:   
        with engine_oracle.connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().all() if stream else []
   except Exception as e:
        logger.error(f"Errore SQL o di connessione: {str(e)}")
        return None
   

def init_security_log_db():
    """Inizializza la tabella per i log di sicurezza se non esiste già; il database sqlite dovrebbe trovarsi in un percorso definito nella variabile d'ambiente SQL_LITE_PATH,
      che dovrebbe essere configurata correttamente per evitare problemi di accesso al database."""
    conn = get_security_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_logs
   (
    ip_address VARCHAR(45) PRIMARY KEY,
    attempts INT DEFAULT 0, -- Fallimenti attuali
    ban_count INT DEFAULT 0, -- Quante volte è stato già bannato
    last_failure TIMESTAMP NULL,
    blocked_until TIMESTAMP NULL,
    last_access TIMESTAMP NULL,
    count_access INT DEFAULT 0 -- Numero di accessi riusciti
   )
    """)
    conn.commit()
    conn.close()

def init_security_log_user_db():
    """Inizializza la tabella per i log di sicurezza se non esiste già; il database sqlite dovrebbe trovarsi in un percorso definito nella variabile d'ambiente SQL_LITE_PATH,
      che dovrebbe essere configurata correttamente per evitare problemi di accesso al database."""
    conn = get_security_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_logs_user
   (
    user VARCHAR(45) PRIMARY KEY,
    attempts INT DEFAULT 0, -- Fallimenti attuali
    ban_count INT DEFAULT 0, -- Quante volte è stato già bannato
    last_failure TIMESTAMP NULL,
    blocked_until TIMESTAMP NULL,
    last_access TIMESTAMP NULL,
    count_access INT DEFAULT 0 -- Numero di accessi riusciti
   )
    """)
    conn.commit()
    conn.close()


def get_security_connection() -> sqlite3.Connection:
    """Restituisce una connessione al database di sicurezza, creando cartella e db se necessario."""
    db_path = os.getenv("SQL_LITE_PATH")
    dir_path = os.path.dirname(db_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
    return sqlite3.connect(db_path)
