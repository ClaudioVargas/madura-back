
from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=8, description="Mínimo 8 caracteres")


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str

    model_config = {
        "from_attributes": True
    }


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, description="Mínimo 8 caracteres")
    rol: str | None = None
