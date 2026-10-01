
from pydantic import BaseModel, Field


class FrutaBase(BaseModel):
    nombre: str
    color: str | None = None
    precio: float = Field(gt=0)
    stock: int = Field(gt=0)


class FrutaCreate(FrutaBase):
    pass


class FrutaOut(FrutaBase):
    id: int

    model_config = {
        "from_attributes": True
    }
