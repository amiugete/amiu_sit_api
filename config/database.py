# database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import oracledb
from typing import List, Optional
from enum import Enum

# Carica le variabili d'ambiente dal file .env, se presente.
load_dotenv()

# Parametri di connessione al database principale SIT (PostgreSQL)
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Parametri di connessione al database di configurazione (PostgreSQL)
user_config = os.getenv("DB_USER_CONFIG")
password_config = os.getenv("DB_PASSWORD_CONFIG")
host_config = os.getenv("DB_HOST_CONFIG")
port_config = os.getenv("DB_PORT_CONFIG")
db_name_config = os.getenv("DB_NAME_CONFIG")

# Parametri di connessione al database delle mappe (PostgreSQL)
user_mappe = os.getenv("DB_USER_MAPPE")
password_mappe = os.getenv("DB_PASSWORD_MAPPE")
host_mappe = os.getenv("DB_HOST_MAPPE")
port_mappe = os.getenv("DB_PORT_MAPPE")
db_name_mappe = os.getenv("DB_NAME_MAPPE")

# Parametri di connessione al database Strade (Oracle)
path_client_oracle = os.getenv("ORACLE_CLIENT_PATH")
user_oracle = os.getenv("DB_USER_STRADE")
password_oracle = os.getenv("DB_PASSWORD_STRADE")
host_oracle = os.getenv("DB_HOST_STRADE")
port_oracle = os.getenv("DB_PORT_STRADE")
db_name_oracle = os.getenv("DB_NAME_STRADE")

# Inizializza il client Oracle con il percorso specificato.
oracledb.init_oracle_client(lib_dir=path_client_oracle)

# Stringhe di connessione per i diversi database.
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
DATABASE_URL_CONFIG = f"postgresql+psycopg2://{user_config}:{password_config}@{host_config}:{port_config}/{db_name_config}"
DATABASE_URL_MAPPE = f"postgresql+psycopg2://{user_mappe}:{password_mappe}@{host_mappe}:{port_mappe}/{db_name_mappe}"
DATABASE_URL_STRADE = f"oracle+oracledb://{user_oracle}:{password_oracle}@{host_oracle}:{port_oracle}/{db_name_oracle}"

# Singleton SQLAlchemy engines per database.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Controlla la connessione prima di usarla.
    pool_recycle=900,    # Ricicla le connessioni aperte ogni 15 minuti.
)
engine_config = create_engine(
    DATABASE_URL_CONFIG,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=900,
)
engine_mappe = create_engine(
    DATABASE_URL_MAPPE,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=900,
)
engine_oracle = create_engine(
    DATABASE_URL_STRADE,
    echo=False,
)

# Logger del modulo.
logger = logging.getLogger(__name__)

class DbConnection(Enum):
    SIT = "SIT"
    CONFIG = "CONFIG"
    MAPPE = "MAPPE"
    STRADE = "STRADE"

# Mappa enum -> engine. Usata per selezionare dinamicamente l'engine corretto.
_ENGINE_MAP = {
    DbConnection.SIT: lambda: engine,
    DbConnection.CONFIG: lambda: engine_config,
    DbConnection.MAPPE: lambda: engine_mappe,
    DbConnection.STRADE: lambda: engine_oracle,
}

def fetch_list_by_engine(sql: str, db: DbConnection, params=None) -> Optional[List[dict]]:
    """Esegue una query SELECT e restituisce tutti i risultati come lista di dizionari."""
    try:
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().all() if stream else []
    except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None


def fetch_one_by_engine(sql: str, db: DbConnection, params=None) -> Optional[dict]:
    """Esegue una query SELECT e restituisce il primo risultato come dizionario."""
    try:
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.mappings().first() if stream else None
    except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None


def update_query_by_engine(sql: str, db: DbConnection, params=None) -> Optional[int]:
    """Esegue una query di aggiornamento (UPDATE/DELETE) e restituisce il numero di righe modificate."""
    try:
        with _ENGINE_MAP[db]().begin() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.rowcount if stream else None
    except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None


def insert_query_by_engine(sql: str, db: DbConnection, params=None) -> Optional[int]:
    """Esegue una query di inserimento e restituisce il numero di righe inserite."""
    try:
        with _ENGINE_MAP[db]().begin() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.rowcount if stream else None
    except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None


def fetch_count_by_engine(sql: str, db: DbConnection, params=None) -> Optional[int]:
    """Esegue una query e restituisce un singolo valore di conteggio (scalar)."""
    try:
        with _ENGINE_MAP[db]().connect() as connection:
            stream = connection.execute(text(sql), params or {})
            return stream.scalar() if stream else None
    except Exception as e:
        logger.error(f"Errore SQL o di connessione [{db.value}]: {str(e)}")
        return None



