from typing import Optional,List, Literal
from pydantic import BaseModel,Field,field_validator, EmailStr,ConfigDict
from app.model.user import RolEnum


class UserBase(BaseModel):
    name:str
    email: EmailStr

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class UserUpdateAdmin(UserUpdate):
    rol: Optional[RolEnum] = Field(default=None)

# class UserPublic(UserBase):
#     id: int
#     rol: RolEnum
#     model_config = ConfigDict(from_attributes=True)

class UserPublic(BaseModel):
    id:int
    email: str
    name: str
    rol: str
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PaginatedPost(BaseModel):
    page: int
    per_page: int 
    total: int
    total_pages: int
    has_prev: bool
    has_next:bool
    order_by: Literal["name", "email"]
    direction: Literal["asc","desc"]
    items: List[UserPublic]

class UserUpdateMe(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

    @field_validator("new_password")
    @classmethod
    def validar_password_juntas(cls, v, info):
        # Si mandan new_password, deben mandar current_password también
        if v and not info.data.get("current_password"):
            raise ValueError("Debes proporcionar tu contraseña actual para cambiarla")
        return v

