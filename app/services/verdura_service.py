from sqlalchemy.orm import Session
from app import models


def create_verdura(db: Session, verdura_in):
    verdura = models.Verdura(
        nombre=verdura_in.nombre,
        tipo=verdura_in.tipo,
        precio=verdura_in.precio,
        stock=verdura_in.stock,
        creador_id=None,
    )
    db.add(verdura)
    db.commit()
    db.refresh(verdura)
    return verdura


def list_verduras(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Verdura).offset(skip).limit(limit).all()


def get_verdura(db: Session, verdura_id: int):
    return db.query(models.Verdura).filter(models.Verdura.id == verdura_id).first()


def update_verdura(db: Session, verdura: models.Verdura, data: dict):
    for k, v in data.items():
        setattr(verdura, k, v)
    db.add(verdura)
    db.commit()
    db.refresh(verdura)
    return verdura


def delete_verdura(db: Session, verdura: models.Verdura):
    db.delete(verdura)
    db.commit()
    return True
