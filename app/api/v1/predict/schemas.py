from pydantic import BaseModel

class PredictionResponse(BaseModel):
    diagnostico:str
    porcentaje:float
    imagen:str