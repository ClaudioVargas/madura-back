
from pydantic import BaseModel, HttpUrl


class FotoCreate(BaseModel):
    url: HttpUrl
    # Opcional: si no se envía, el backend usa el id del usuario autenticado.
    usuario_id: int | None = None


class FotoOut(BaseModel):
    id: int
    url: HttpUrl
    usuario_id: int

    model_config = {
        "from_attributes": True
    }
