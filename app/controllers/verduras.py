from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.verdura import VerduraCreate, VerduraOut
from app.security.deps import get_db, require_role
from app.services.verdura_service import (
    create_verdura,
    delete_verdura,
    get_verdura,
    list_verduras,
    update_verdura,
)

router = APIRouter()


@router.get("/", response_model=list[VerduraOut])
def list_all(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    return list_verduras(db, skip=skip, limit=limit)


@router.post("/", response_model=VerduraOut)
def create(
    verdura_in: VerduraCreate,
    db: Session = Depends(get_db),
    current=Depends(require_role("admin")),
):
    return create_verdura(db, verdura_in, creador_id=current.id)


@router.get("/{verdura_id}", response_model=VerduraOut)
def get_one(verdura_id: int, db: Session = Depends(get_db)):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    return verdura


@router.put("/{verdura_id}", response_model=VerduraOut)
def update(
    verdura_id: int,
    verdura_in: VerduraCreate,
    db: Session = Depends(get_db),
    current=Depends(require_role("admin")),
):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    return update_verdura(db, verdura, verdura_in.model_dump())


@router.delete("/{verdura_id}")
def delete(
    verdura_id: int,
    db: Session = Depends(get_db),
    current=Depends(require_role("admin")),
):
    verdura = get_verdura(db, verdura_id)
    if not verdura:
        raise HTTPException(status_code=404, detail="Verdura not found")
    delete_verdura(db, verdura)
    return {"ok": True}
