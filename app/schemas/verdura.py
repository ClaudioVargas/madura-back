from pydantic import BaseModel, Field
from typing import Optional


class VerduraBase(BaseModel):
    nombre: str
    tipo: Optional[str]
    precio: float = Field(gt=0)
    stock: float = Field(gt=0)


class VerduraCreate(VerduraBase):
    pass


class VerduraOut(VerduraBase):
    id: int

    model_config = {
        "from_attributes": True  # 🟢 Nueva sintaxis de Pydantic V2
    }
