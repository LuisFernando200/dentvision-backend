from math import ceil
from fastapi import APIRouter,Query,Depends,Path,status,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from typing import List,Optional,Union,Literal
from app.core.db import get_db
from .schemas import UserCreate,UserPublic,UserUpdate,PaginatedPost
from .repository import UserRepository
from app.core.security import get_current_user
from app.core.security import hash_password
from app.core.security import require_admin
from .schemas import UserUpdateMe
from app.core.security import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["users"])
 
@router.post("", response_model=UserPublic,status_code= status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    hashed_password = hash_password(payload.password)
    new_user = repository.create(name = payload.name,
                                 email= payload.email,
                                 password=hashed_password
                                 )
    db.commit()          # Le dice a Postgres: "Guarda esto permanentemente"
    db.refresh(new_user)
    return new_user


@router.get("",response_model=PaginatedPost)
def list_user(
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar por nombre o correo",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"
    ),
    per_page: int = Query(
        10, ge=1, le=50,
        description="Número de resultados (1-50)"
    ),
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)"
    ),
    order_by: Literal["name", "email"] = Query(
        "name", description="Campo de orden"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden"
    ),
    db: Session = Depends(get_db),
    current = Depends(require_admin)
):
    repository = UserRepository(db)
    

    total, items = repository.search(query,order_by,direction,page,per_page)
    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page,total_pages)
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )

@router.put("/me", response_model=UserPublic)
def update_me(
    data: UserUpdateMe,
    db: Session = Depends(get_db),
    current = Depends(get_current_user),
):
    repository = UserRepository(db)
    user = repository.get(current["id"])

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update = {}

    if data.name is not None:
        update["name"] = data.name

    if data.email is not None:
        update["email"] = data.email

    if data.new_password is not None:
        # Verificamos la contraseña actual antes de permitir el cambio
        if not verify_password(data.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        update["password"] = hash_password(data.new_password)

    if not update:
        raise HTTPException(status_code=400, detail="No hay cambios para aplicar")

    try:
        user = repository.update_user(user, update)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el usuario")


@router.put("/{user_id}" , response_model=UserUpdate,response_description="Post acutalizado", response_model_exclude_none= True )
def update_user(user_id:int ,data:UserUpdate, db = Depends(get_db),current = Depends(get_current_user,)):
    repository = UserRepository(db)

    user = repository.get(user_id)

    if not user:
        raise HTTPException(status_code = 404, detail="no encontrado")
    try:
        update = data.model_dump(exclude_unset=True) #trandorma la data en un diccionario
        user = repository.update_user(user,update)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail= "Error al actualizar el user")
