from pydantic import BaseModel, HttpUrl


class FotoCreate(BaseModel):
    url: HttpUrl
    usuario_id: int


class FotoOut(BaseModel):
    id: int
    url: HttpUrl
    usuario_id: int

    model_config = {
        "from_attributes": True  # 🟢 Nueva sintaxis de Pydantic V2
    }
