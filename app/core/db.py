import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase,Session
from dotenv import load_dotenv

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("Error: La variable de entorno 'DATABASE_URL' no está configurada o el archivo .env no se leyó correctamente.")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo = True,#que consultas se estan haciendo 
    future=True,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush = False,
    autocommit=False, 
    class_ = Session
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
