from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.fruta import FrutaCreate, FrutaOut
from app.security.deps import get_db, require_role, get_current_user
from app.services.fruta_service import create_fruta, list_frutas, get_fruta, update_fruta, delete_fruta

router = APIRouter()


@router.get("/", response_model=List[FrutaOut])
def list_all(db: Session = Depends(get_db)):
    return list_frutas(db)


@router.post("/", response_model=FrutaOut)
def create(fruta_in: FrutaCreate, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    return create_fruta(db, fruta_in, creador_id=current.id)


@router.get("/{fruta_id}", response_model=FrutaOut)
def get_one(fruta_id: int, db: Session = Depends(get_db)):
    fruta = get_fruta(db, fruta_id)
    if not fruta:
        raise HTTPException(status_code=404, detail="Fruta not found")
    return fruta


@router.put("/{fruta_id}", response_model=FrutaOut)
def update(fruta_id: int, fruta_in: FrutaCreate, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    fruta = get_fruta(db, fruta_id)
    if not fruta:
        raise HTTPException(status_code=404, detail="Fruta not found")
    data = fruta_in.dict()
    return update_fruta(db, fruta, data)


@router.delete("/{fruta_id}")
def delete(fruta_id: int, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    fruta = get_fruta(db, fruta_id)
    if not fruta:
        raise HTTPException(status_code=404, detail="Fruta not found")
    delete_fruta(db, fruta)
    return {"ok": True}
