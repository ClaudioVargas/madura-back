from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UsuarioCreate
import bcrypt



def get_password_hash(password: str) -> str:
    try:
        # Bcrypt requiere que el texto sea convertido a bytes (.encode)
        password_bytes = password.encode("utf-8")
        
        # Genera la sal y crea el hash
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        
        # Retorna el hash como un string normal para guardarlo en la Base de Datos
        return hashed_bytes.decode("utf-8")
        
    except Exception as error:
        print(f"Error al encriptar la contraseña: {error}")
        raise error


def verify_password(plain: str, hashed: str) -> bool:
    """Compara una contraseña del login con el hash guardado en la BD."""
    try:
        password_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
        print(f"Verifying password. password_bytes: {password_bytes}, hashed_bytes: {hashed_bytes}")  # Debugging line to check the values
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as error:
        # Esto te mostrará la línea exacta y la razón del fallo en la consola
        print(f"❌ ERROR CRÍTICO EN VERIFY_PASSWORD: {error}")
        import traceback
        traceback.print_exc()
        return False


def create_user(db: Session, user_in: UsuarioCreate):
    user = models.Usuario(
        nombre=user_in.nombre,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    print(f"Querying for user with email: {email}")  # Debugging line to check the email being queried
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()
