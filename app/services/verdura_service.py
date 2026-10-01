from sqlalchemy.orm import Session

from app import models


def create_verdura(db: Session, verdura_in, creador_id: int | None = None) -> models.Verdura:
    verdura = models.Verdura(
        nombre=verdura_in.nombre,
        tipo=verdura_in.tipo,
        precio=verdura_in.precio,
        stock=verdura_in.stock,
        creador_id=creador_id,
    )
    db.add(verdura)
    db.commit()
    db.refresh(verdura)
    return verdura


def list_verduras(db: Session, skip: int = 0, limit: int = 100) -> list[models.Verdura]:
    return db.query(models.Verdura).order_by(models.Verdura.id).offset(skip).limit(limit).all()


def get_verdura(db: Session, verdura_id: int) -> models.Verdura | None:
    return db.query(models.Verdura).filter(models.Verdura.id == verdura_id).first()


def update_verdura(db: Session, verdura: models.Verdura, data: dict) -> models.Verdura:
    for key, value in data.items():
        setattr(verdura, key, value)
    db.add(verdura)
    db.commit()
    db.refresh(verdura)
    return verdura


def delete_verdura(db: Session, verdura: models.Verdura) -> bool:
    db.delete(verdura)
    db.commit()
    return True
