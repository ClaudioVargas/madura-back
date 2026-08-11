from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.photo import FotoCreate, FotoOut
from app.security.deps import get_db, require_role
from app.services.photo_service import create_foto, list_fotos, get_foto, delete_foto

router = APIRouter()


@router.get("/", response_model=List[FotoOut])
def list_all(db: Session = Depends(get_db)):
    return list_fotos(db)


@router.post("/", response_model=FotoOut)
def create(foto_in: FotoCreate, db: Session = Depends(get_db), current=Depends(require_role("user"))):
    # any authenticated user can upload a foto
    return create_foto(db, foto_in)


@router.get("/{foto_id}", response_model=FotoOut)
def get_one(foto_id: int, db: Session = Depends(get_db)):
    foto = get_foto(db, foto_id)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto not found")
    return foto


@router.delete("/{foto_id}")
def delete(foto_id: int, db: Session = Depends(get_db), current=Depends(require_role("user"))):
    foto = get_foto(db, foto_id)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto not found")
    delete_foto(db, foto)
    return {"ok": True}
