from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=6)


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str

    model_config = {
        "from_attributes": True  # 🟢 Nueva sintaxis de Pydantic V2
    }


class UsuarioUpdate(BaseModel):
    nombre: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str] = Field(min_length=6)
    rol: Optional[str]
