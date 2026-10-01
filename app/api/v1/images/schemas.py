from pydantic import BaseModel, ConfigDict, Field

class ImageCreate(BaseModel):
    comentario: str = Field(max_length=500)

class UsuarioBasico(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class ImageResponse(BaseModel):
    id: int
    id_usuario: int
    url_img: str
    comentario: str
    usuario: UsuarioBasico  # <-- datos anidados del usuario que subió la imagen

    model_config = ConfigDict(from_attributes=True)