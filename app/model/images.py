from __future__ import annotations
import enum
from datetime import datetime
from typing import List

from sqlalchemy import Integer,String,Enum,DateTime,ForeignKey,Float,func
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.core.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserORM


class ImagesORM(Base):
    __tablename__ = "imagenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index =True)
    id_usuario: Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    url_img: Mapped[str] = mapped_column(String(250), nullable=False)
    comentario : Mapped[str] = mapped_column(String(500), nullable=False)
    usuario: Mapped[UserORM] = relationship("UserORM", back_populates="imagen_relacionados")
