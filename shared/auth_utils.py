from datetime import datetime, timedelta
from pathlib import Path
from jose import jwt
from . import logger
import os
from dotenv import load_dotenv

SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000
def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_token_payload(token: str):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.JWTError:
        logger.error("Token is invalid")
        return None
