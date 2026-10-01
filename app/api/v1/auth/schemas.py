from pydantic import BaseModel,ConfigDict

class Token(BaseModel):
    access_token:str
    token_type: str = "bearer"

class TokednData(BaseModel):
    sub: str 
    username: str

class UserPublic(BaseModel):
    email:str
    name:str
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str