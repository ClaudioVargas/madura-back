from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.token import RefreshRequest, Token
from app.schemas.user import UsuarioCreate, UsuarioOut
from app.security.deps import get_db
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.rate_limit import LoginRateLimiter
from app.services.user_service import create_user, get_user, get_user_by_email, verify_password

router = APIRouter()

# Limita intentos fallidos de login por IP (en memoria).
login_limiter = LoginRateLimiter(
    max_attempts=settings.RATE_LIMIT_MAX_ATTEMPTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)


@router.post("/token", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login OAuth2 (username = email). Devuelve token de acceso + refresh."""
    client_ip = request.client.host if request.client else "unknown"

    if login_limiter.is_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intenta de nuevo más tarde.",
        )

    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        login_limiter.record_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    login_limiter.reset(client_ip)
    return Token(
        access_token=create_access_token({"user_id": user.id, "rol": user.rol}),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=create_refresh_token({"user_id": user.id}),
    )


@router.post("/register", response_model=UsuarioOut)
def register(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario con el rol 'user' por defecto."""
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return create_user(db, user_in)


@router.post("/refresh", response_model=Token)
def refresh_access_token(body: RefreshRequest, db: Session = Depends(get_db)):
    """Renueva el token de acceso usando un refresh token válido."""
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh" or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = get_user(db, int(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return Token(
        access_token=create_access_token({"user_id": user.id, "rol": user.rol}),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=body.refresh_token,
    )
