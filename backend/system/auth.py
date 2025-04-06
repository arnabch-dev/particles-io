from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime,timedelta
from typing import Optional
import jwt

SECRET_KEY = "supersecretarnabkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

pwd_context = CryptContext(schemes=["bcrypt"])
endpoint_for_getting_token = "token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=endpoint_for_getting_token)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id:str = payload.get("sub")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

def authenticate_user():
    pass

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)