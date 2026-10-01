from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.security.deps import get_current_user, get_db, require_role
from app.services.user_service import (
    create_user,
    get_user,
    get_user_by_email,
    list_users,
    update_user,
)

router = APIRouter()


@router.post("/", response_model=UsuarioOut)
def create_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un usuario (mismo comportamiento que /auth/register con validación de email)."""
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_in)


@router.get("/", response_model=list[UsuarioOut])
def read_users(
    db: Session = Depends(get_db),
    current=Depends(require_role("admin")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    return list_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UsuarioOut)
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/{user_id}", response_model=UsuarioOut)
def update_usuario(
    user_id: int,
    user_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    """Actualiza un usuario. Solo el propio usuario o un admin pueden hacerlo."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Solo el propio usuario o un admin
    if current.id != user.id and current.rol != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    data = user_in.model_dump(exclude_unset=True)
    return update_user(db, user, data)
