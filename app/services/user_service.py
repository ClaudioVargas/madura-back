import traceback

import bcrypt
from sqlalchemy.orm import Session

from app import models
from app.schemas.user import UsuarioCreate


def get_password_hash(password: str) -> str:
    """Hashea una contraseña con bcrypt y la devuelve como string."""
    try:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")
    except Exception:
        traceback.print_exc()
        raise


def verify_password(plain: str, hashed: str) -> bool:
    """Compara una contraseña en claro con el hash almacenado en la BD."""
    try:
        password_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        traceback.print_exc()
        return False


def create_user(db: Session, user_in: UsuarioCreate) -> models.Usuario:
    """Crea un usuario con el rol 'user' por defecto."""
    user = models.Usuario(
        nombre=user_in.nombre,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: models.Usuario, data: dict) -> models.Usuario:
    """Aplica cambios parciales a un usuario (re-hashea 'password' si viene en los datos)."""
    data = data.copy()
    password = data.pop("password", None)
    if password:
        data["hashed_password"] = get_password_hash(password)
    for key, value in data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> models.Usuario | None:
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def get_user(db: Session, user_id: int) -> models.Usuario | None:
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.Usuario]:
    return db.query(models.Usuario).order_by(models.Usuario.id).offset(skip).limit(limit).all()
