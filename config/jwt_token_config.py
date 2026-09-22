from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv
from jose.exceptions import JWTError

# Carica le variabili d'ambiente dal file .env, se presente
load_dotenv()

# Numero di minuti di validità del token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Chiave segreta usata per firmare e verificare i token JWT
SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(data: dict):
    try:
        # Copia il payload in un nuovo dizionario per non alterare l'oggetto originale
        to_encode = data.copy()

        # Calcola la scadenza del token in UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Aggiunge la data di scadenza al payload secondo lo standard JWT
        to_encode.update({"exp": expire})

        # Crea e firma il token JWT con algoritmo HS256
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    except JWTError as e:
        # Propaga eventuali errori di encoding/firmatura JWT
        raise e


# La funzione che decodifica e verifica un token JWT
def check_jwt_token(token: str):
    """Decodifica e verifica un token JWT.

    Restituisce il payload se il token è valido.
    Solleva JWTError se il token è scaduto o la firma non è valida.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise e
    
    