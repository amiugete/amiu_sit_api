# database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
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

################# Strnga di connessione base dati ##########################
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
DATABASE_URL_MAPPE = f"postgresql+psycopg2://{user_mappe}:{password_mappe}@{host_mappe}:{port_mappe}/{db_name_mappe}"

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
   

