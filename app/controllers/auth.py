from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.security.jwt import create_access_token
from app.database.base import SessionLocal
from app.services.user_service import get_user_by_email, verify_password, create_user
from app.schemas.token import Token
from app.schemas.user import UsuarioCreate, UsuarioOut

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db: Session = SessionLocal()
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token({"user_id": user.id, "rol": user.rol})
    return {"access_token": token,
            "token_type": "bearer", 
            "expires_in":  ACCESS_TOKEN_EXPIRE_MINUTES * 60}  # Ajusta el tiempo de expiración según tu configuración


@router.post("/register", response_model=UsuarioOut)
def register(user_in: UsuarioCreate):
    db: Session = SessionLocal()
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, user_in)
    return user
