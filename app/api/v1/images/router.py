from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.model.images import ImagesORM
from app.core.security import get_current_user
from .schemas import ImageResponse
from app.core.security import require_admin
import uuid
import shutil

router = APIRouter(prefix="/images", tags=["images"])


MEDIA_DIR = Path("app/media/feedback")
MEDIA_DIR.mkdir(parents = True, exist_ok = True)

@router.post("", status_code= status.HTTP_201_CREATED)
async def crear_feedback_imagen(
    imagen: UploadFile = File(...),
    comentario: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    extensiones_permitidas = ["image/png", "image/jpeg", "image/jpg"]

    if imagen.content_type not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen"
        )

    # Crear nombre único
    extension = imagen.filename.split(".")[-1]
    nombre_archivo = f"{uuid.uuid4()}.{extension}"

    ruta_archivo = MEDIA_DIR / nombre_archivo

    # Guardar imagen físicamente
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)


    # Ruta que guardarás en la BD
    url_imagen = f"/media/feedback/{nombre_archivo}"

    # Crear registro
    nueva_imagen = ImagesORM(
        id_usuario=current_user["id"], 
        url_img=url_imagen,
        comentario=comentario
    )


    db.add(nueva_imagen)
    db.commit()
    db.refresh(nueva_imagen)


    return {
        "mensaje": "Imagen guardada correctamente",
        "id": nueva_imagen.id,
        "url": nueva_imagen.url_img
    }

@router.get("", response_model=list[ImageResponse])
def listar_imagenes(
    db: Session = Depends(get_db),
    current = Depends(require_admin)
):
    
    return db.query(ImagesORM).all()