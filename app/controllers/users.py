from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.security.deps import get_db, require_role, get_current_user
from app.services.user_service import create_user, list_users, get_user
from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter()


@router.post("/", response_model=UsuarioOut)
def create_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in)


@router.get("/", response_model=List[UsuarioOut])
def read_users(db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    return list_users(db)


@router.get("/me", response_model=UsuarioOut)
def read_me(current_user = Depends(get_current_user)):
    return current_user


@router.put("/{user_id}", response_model=UsuarioOut)
def update_user(user_id: int, user_in: UsuarioUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # only allow self or admin
    if current.id != user.id and current.rol != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    data = user_in.dict(exclude_unset=True)
    if "password" in data:
        from app.services.user_service import get_password_hash
        data["hashed_password"] = get_password_hash(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
