# database.py

import sqlite3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import oracledb
from typing import List, Optional
from enum import Enum

# Carica le variabili dal file .env
load_dotenv()

# Recupera i valori dalle variabili d'ambiente di SIT
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Recupera i valori dalle variabili d'ambiente di DI CONFIGURAZIONE
user_config = os.getenv("DB_USER_CONFIG")
password_config = os.getenv("DB_PASSWORD_CONFIG")
host_config = os.getenv("DB_HOST_CONFIG")
port_config = os.getenv("DB_PORT_CONFIG")
db_name_config = os.getenv("DB_NAME_CONFIG")

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

################# Strnga di connessione base dati per la configurazione ##########################
DATABASE_URL_CONFIG = f"postgresql+psycopg2://{user_config}:{password_config}@{host_config}:{port_config}/{db_name_config}"

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
engine_config = create_engine(
     DATABASE_URL_CONFIG,
     echo=True,
     pool_pre_ping=True, # Verifica la connessione prima di usarla
     pool_recycle=900 # Ricicla le connessioni ogni 15 minuti
)
engine_mappe = create_engine(
     DATABASE_URL_MAPPE,
     echo=True,
     pool_pre_ping=True, # Verifica la connessione prima di usarla
     pool_recycle=900 # Ricicla le connessioni ogni 15 minuti
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

class DbConnection(Enum):
    SIT    = "SIT"
    CONFIG = "CONFIG"
    MAPPE  = "MAPPE"
    STRADE = "STRADE"

_ENGINE_MAP = {
    DbConnection.SIT:    lambda: engine,
    DbConnection.CONFIG: lambda: engine_config,
    DbConnection.MAPPE:  lambda: engine_mappe,
    DbConnection.STRADE: lambda: engine_oracle,
}

#################### Funzioni generiche con selezione engine tramite enum ########################
def fetch_list_by_engine(sql: str, db: DbConnection, params=None) -> Optional[List[dict]]:
   """Esegue una query di select all sul database specificato tramite DbConnection enum."""
   try:
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().all() if stream else []
   except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None

def fetch_one_by_engine(sql: str, db: DbConnection, params=None) -> Optional[dict]:
   """Esegue una query di select one sul database specificato tramite DbConnection enum."""
   try:
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().first() if stream else None
   except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None



def update_query_by_engine(sql: str, db: DbConnection, params=None) -> Optional[int]:
     """Esegue una query di aggiornamento sul database specificato tramite DbConnection enum."""
     try:
          with _ENGINE_MAP[db]().begin() as connection:
               stream = connection.execute(text(sql), params or {})
               return stream.rowcount if stream else None
     except Exception as e:
          logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
          return None
     
def insert_query_by_engine(sql: str, db: DbConnection, params=None) -> Optional[int]:
     """Esegue una query di inserimento sul database specificato tramite DbConnection enum."""
     try:
          with _ENGINE_MAP[db]().begin() as connection:
               stream = connection.execute(text(sql), params or {})
               return stream.rowcount if stream else None
     except Exception as e:
          logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
          return None
   
def fetch_count_by_engine(sql,  db: DbConnection, params=None) -> int:
   """Esegue una query sul database specificato e ritorna il conteggio dei risultati."""
   try:   
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.scalar() if stream else None
   except Exception as e:
        logger.error(f"Errore SQL o di connessione: {str(e)}")
        return None
   


