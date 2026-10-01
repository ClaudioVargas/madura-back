from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.base import SessionLocal
from app.security.jwt import decode_token
from app.services.user_service import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    """Dependencia de FastAPI: abre una sesión de BD y la cierra al terminar la petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Devuelve el usuario autenticado a partir de un token de tipo 'access'."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access" or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = get_user(db, int(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(role: str):
    """Devuelve una dependencia que exige un rol concreto (el admin siempre está permitido)."""

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.rol != role and current_user.rol != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
