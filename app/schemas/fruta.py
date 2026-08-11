from pydantic import BaseModel, confloat, conint
from typing import Optional


class FrutaBase(BaseModel):
    nombre: str
    color: Optional[str]
    precio: confloat(gt=0)
    stock: conint(ge=0)


class FrutaCreate(FrutaBase):
    pass


class FrutaOut(FrutaBase):
    id: int

    class Config:
        orm_mode = True
