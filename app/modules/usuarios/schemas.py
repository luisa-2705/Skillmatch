from datetime import datetime
from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nombre :str
    apellido : str
    email : EmailStr
    password : str
    tipo_usuario: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    tipo_usuario: str
    fecha_registro: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str