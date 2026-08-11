from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.verdura import VerduraCreate, VerduraOut
from app.security.deps import get_db, require_role
from app.services.verdura_service import create_verdura, list_verduras, get_verdura, update_verdura, delete_verdura

router = APIRouter()


@router.get("/", response_model=List[VerduraOut])
def list_all(db: Session = Depends(get_db)):
    return list_verduras(db)


@router.post("/", response_model=VerduraOut)
def create(verdura_in: VerduraCreate, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    return create_verdura(db, verdura_in)


@router.get("/{verdura_id}", response_model=VerduraOut)
def get_one(verdura_id: int, db: Session = Depends(get_db)):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    return verdura


@router.put("/{verdura_id}", response_model=VerduraOut)
def update(verdura_id: int, verdura_in: VerduraCreate, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    data = verdura_in.dict()
    return update_verdura(db, verdura, data)


@router.delete("/{verdura_id}")
def delete(verdura_id: int, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    delete_verdura(db, verdura)
    return {"ok": True}
