from sqlalchemy.orm import Session
from app import models
from app.schemas.fruta import FrutaCreate


def create_fruta(db: Session, fruta_in: FrutaCreate, creador_id: int | None = None):
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


def list_frutas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Fruta).offset(skip).limit(limit).all()


def get_fruta(db: Session, fruta_id: int):
    return db.query(models.Fruta).filter(models.Fruta.id == fruta_id).first()


def update_fruta(db: Session, fruta: models.Fruta, data: dict):
    for k, v in data.items():
        setattr(fruta, k, v)
    db.add(fruta)
    db.commit()
    db.refresh(fruta)
    return fruta


def delete_fruta(db: Session, fruta: models.Fruta):
    db.delete(fruta)
    db.commit()
    return True
