from pydantic import BaseModel, Field
from typing import Optional


class FrutaBase(BaseModel):
    nombre: str
    color: Optional[str]
    precio: float = Field(gt=0)
    stock: float = Field(gt=0)


class FrutaCreate(FrutaBase):
    pass


class FrutaOut(FrutaBase):
    id: int

    model_config = {
        "from_attributes": True  # 🟢 Nueva sintaxis de Pydantic V2
    }
