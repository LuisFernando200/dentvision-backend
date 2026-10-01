from __future__ import annotations
import enum
from datetime import datetime
from typing import List

from sqlalchemy import Integer,String,Enum,DateTime,func
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.core.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .images import ImagesORM

class RolEnum(str, enum.Enum):
    admin = "admin"
    estudiante = "estudiante"

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key = True, index=True)
    name: Mapped[str] = mapped_column(String(100),nullable = False)
    email: Mapped[str] = mapped_column(String(100), unique= True,index = True)
    password: Mapped[str] = mapped_column(String(250))

    rol: Mapped[RolEnum] = mapped_column(
        Enum(RolEnum, name="rol_enum"),
        server_default=RolEnum.estudiante.value, # Protege la base de datos
        default=RolEnum.estudiante,
        nullable=False
    )
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    imagen_relacionados: Mapped[List["ImagesORM"]] = relationship("ImagesORM", back_populates="usuario", cascade="all, delete-orphan")