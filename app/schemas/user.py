from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: constr(min_length=6)


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str

    class Config:
        orm_mode = True


class UsuarioUpdate(BaseModel):
    nombre: Optional[str]
    email: Optional[EmailStr]
    password: Optional[constr(min_length=6)]
    rol: Optional[str]
