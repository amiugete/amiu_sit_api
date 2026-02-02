# database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

# Carica le variabili dal file .env
load_dotenv()

# Recupera i valori dalle variabili d'ambiente
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

################# Strnga di connessione base dati ##########################
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(DATABASE_URL)
logger = logging.getLogger(__name__)



#################### Funzione di esecuzione query ########################
def execute_query(sql, params=None):
   try:   
        with engine.connect() as connection:
            result = connection.execute(text(sql), params or {})
            connection.commit() # Necessario per INSERT/UPDATE
            return result
   except Exception as e:
        logger.error(f"Errore SQL o di connessione: {str(e)}")
        return result
   
