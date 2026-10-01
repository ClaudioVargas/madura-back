from sqlalchemy.orm import Session

from app import models


def create_foto(db: Session, url: str, usuario_id: int) -> models.Foto:
    foto = models.Foto(url=url, usuario_id=usuario_id)
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def list_fotos(db: Session, skip: int = 0, limit: int = 100) -> list[models.Foto]:
    return db.query(models.Foto).order_by(models.Foto.id).offset(skip).limit(limit).all()


def get_foto(db: Session, foto_id: int) -> models.Foto | None:
    return db.query(models.Foto).filter(models.Foto.id == foto_id).first()


def delete_foto(db: Session, foto: models.Foto) -> bool:
    db.delete(foto)
    db.commit()
    return True
