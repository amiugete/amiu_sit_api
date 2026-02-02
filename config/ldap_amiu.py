from ldap3 import Server, Connection, ALL, SIMPLE
import logging
import os
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()
logger = logging.getLogger(__name__)
SERVER_ADRTESS = os.getenv("HOST_AMIU_LDAP")
PORT_AMIU_LDAP = os.getenv("PORT_AMIU_LDAP")
DOMAIN_NAME_AMIU = os.getenv("DOMAIN_NAME_AMIU")

def verifica_utente_amiu_LDAP(username, password)-> tuple[bool, str]:
    # Usiamo l'indirizzo IP direttamente sulla porta standard configurata
    user_principal = f"{username}@{DOMAIN_NAME_AMIU}"
    try:
        # Ci connettiamo alla porta 389 
        server = Server(SERVER_ADRTESS, port=PORT_AMIU_LDAP, get_info=ALL)
        # Creiamo la connessione
        conn = Connection(server, user=user_principal, password=password, authentication=SIMPLE)

        # Eseguiamo il bind (login)
        if conn.bind():
            msg = f"✅ Autenticazione riuscita per {username}"
            logger.info(msg)
            conn.unbind()
            return True, msg
        else:
            msg =f"❌ Credenziali errate per {username}"
            logger.warning(msg)
            return False, msg

    except Exception as e:
        logger.error(f"⚠️ Errore critico: {e}")
        return False, "Errore critico durante l'autenticazione LDAP"
