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

class AnalisisORM(Base):
    __tablename__ = "analisis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index =True)
    id_usuario: Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    fecha_de_analisis: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())
    resultado_general:Mapped[str] = mapped_column(String(250), nullable=False)
    nivel_de_confianza: Mapped[float] = mapped_column(Float, nullable = False)

    #conexion
    usuario: Mapped[UserORM] = relationship("UserORM", back_populates="analisis_relacionados")
