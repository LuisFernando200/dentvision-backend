import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import Base, engine
# from app.model import UserORM
from app.model.user import UserORM
from app.model.images import ImagesORM
from app.api.v1.users.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.predict.router import router as predict_router
from app.api.v1.images.router import router as images_router
from fastapi.staticfiles import StaticFiles

def create_app() -> FastAPI:
    app = FastAPI(title="Datasentinel")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # ajusta si usas :3000
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["diagnostico", "porcentaje"],  # para tu endpoint /predict
    )

    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(post_router)
    app.include_router(auth_router)
    app.include_router(predict_router)
    app.include_router(images_router)
    app.mount("/media", StaticFiles(directory="app/media"), name="media")
    return app


app = create_app()