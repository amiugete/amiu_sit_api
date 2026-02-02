from datetime import datetime, timedelta, timezone
from jose import  jwt
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose.exceptions import JWTError

load_dotenv()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")

def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        raise e


# 2. La funzione "Tutto-in-uno" che automatizza la verifica
def check_jwt_token(token: str):
    """
    Questa funzione decodifica il token: estrae, decodifica e verifica.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise e