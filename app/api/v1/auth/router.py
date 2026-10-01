from fastapi import APIRouter
from .schemas import Token, UserPublic
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from datetime import timedelta
from app.core.security import create_access_token, get_current_user,verify_password
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.v1.users.repository import UserRepository
from .schemas import Token, UserLogin


router = APIRouter(prefix="/auth" , tags = ["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me", response_model=UserPublic)
async def read_me(current = Depends(get_current_user)):
    return {"id": current["id"], "email": current["email"], "name": current["name"], "rol": current["rol"]}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)
    
    # OAuth2PasswordRequestForm SIEMPRE usa "username" como atributo fijo,
    # sin importar que aquí mandes el email
    user = repository.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas"
        )
    
    token = create_access_token(
        data={"sub": user.email, "name": user.name, "rol": user.rol.value, "user_id": user.id},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}
