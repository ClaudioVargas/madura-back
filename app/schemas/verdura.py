from pydantic import BaseModel, confloat, conint
from typing import Optional


class VerduraBase(BaseModel):
    nombre: str
    tipo: Optional[str]
    precio: confloat(gt=0)
    stock: conint(ge=0)


class VerduraCreate(VerduraBase):
    pass


class VerduraOut(VerduraBase):
    id: int

    class Config:
        orm_mode = True
