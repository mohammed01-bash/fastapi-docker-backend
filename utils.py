from passlib.context import CryptContext
import jwt 
from datetime import datetime,timedelta,timezone
from config import settings


pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto") #bycrypt est une fonction de hachage qui utilise algorithme eksblowfish(variante de blowfish)


def hash_password(password:str)->str:
    return pwd_context.hash(password)


def verify_password(plain_password:str,hashed_password:str) -> bool :
    return pwd_context.verify(plain_password,hashed_password)


SECRET_KEY = settings.secret_key
ALGORITHM=settings.algorithm    
ACCES_TOKEN_EXPIRE_MINUTES= settings.access_token_expire_minutes


def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt


