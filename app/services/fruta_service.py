import numpy as np
from sqlalchemy.orm import Session

from app import models
from app.models.fruit_model import FruitModel
from app.schemas.fruta import FrutaCreate
from app.utils.image_utils import preprocess_image

_STATES = {0: "verde", 1: "madura", 2: "pasada"}

# Instanciar el objeto es barato; el modelo Keras se carga con pereza en la primera
# llamada a predict (ver FruitModel).
fruit_model = FruitModel()


def evaluate_fruit(image_file):
    """Clasifica el estado de madurez de un plátano a partir de un archivo de imagen."""
    img_array = preprocess_image(image_file)
    prediction = fruit_model.predict(img_array)
    label = int(np.argmax(prediction))
    return _STATES.get(label, "desconocido")


def create_fruta(db: Session, fruta_in: FrutaCreate, creador_id: int | None = None) -> models.Fruta:
    fruta = models.Fruta(
        nombre=fruta_in.nombre,
        color=fruta_in.color,
        precio=fruta_in.precio,
        stock=fruta_in.stock,
        creador_id=creador_id,
    )
    db.add(fruta)
    db.commit()
    db.refresh(fruta)
    return fruta


def list_frutas(db: Session, skip: int = 0, limit: int = 100) -> list[models.Fruta]:
    return db.query(models.Fruta).order_by(models.Fruta.id).offset(skip).limit(limit).all()


def get_fruta(db: Session, fruta_id: int) -> models.Fruta | None:
    return db.query(models.Fruta).filter(models.Fruta.id == fruta_id).first()


def update_fruta(db: Session, fruta: models.Fruta, data: dict) -> models.Fruta:
    for key, value in data.items():
        setattr(fruta, key, value)
    db.add(fruta)
    db.commit()
    db.refresh(fruta)
    return fruta


def delete_fruta(db: Session, fruta: models.Fruta) -> bool:
    db.delete(fruta)
    db.commit()
    return True
