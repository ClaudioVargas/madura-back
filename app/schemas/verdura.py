
from pydantic import BaseModel, Field


class VerduraBase(BaseModel):
    nombre: str
    tipo: str | None = None
    precio: float = Field(gt=0)
    stock: int = Field(gt=0)


class VerduraCreate(VerduraBase):
    pass


class VerduraOut(VerduraBase):
    id: int

    model_config = {
        "from_attributes": True
    }
