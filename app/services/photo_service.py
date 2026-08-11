from sqlalchemy.orm import Session
from app import models
from app.schemas.photo import FotoCreate


def create_foto(db: Session, foto_in: FotoCreate):
    foto = models.Foto(url=str(foto_in.url), usuario_id=foto_in.usuario_id)
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def list_fotos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Foto).offset(skip).limit(limit).all()


def get_foto(db: Session, foto_id: int):
    return db.query(models.Foto).filter(models.Foto.id == foto_id).first()


def delete_foto(db: Session, foto: models.Foto):
    db.delete(foto)
    db.commit()
    return True
