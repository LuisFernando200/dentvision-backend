import os
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from typing import Optional
import jwt
from jwt.exceptions import ExpiredSignatureError,InvalidTokenError
from passlib.context import CryptContext

SECRET_KEY =  os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticadi",
    headers={"WWW-Authenticate":"Bearer"}
)

def raise_expired_token():
    return HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token expirado",
    headers={"WWW-Authenticate":"Bearer"}
    )

def raise_forbidden():
    return HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="no tienes permisos suficientes"
    )

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(data: dict,expires_delta:Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(tz = timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(payload=to_encode, key= SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token:str) -> dict:
    payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    
#en esta parte van las ecepciones
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        name: Optional[str] = payload.get("name")
        rol: Optional[str] = payload.get("rol")
        user_id: Optional[int] = payload.get("user_id")  # <-- faltaba esto
        if not sub or not name or not rol or user_id is None:
            raise credentials_exc
        return {"id": user_id, "email": sub, "name": name, "rol": rol}  # <-- y esto
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exc

def require_admin(current: dict = Depends(get_current_user)):
    if current["rol"] != "admin":
        raise raise_forbidden()
    return current