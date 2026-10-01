import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from PIL import UnidentifiedImageError
from sqlalchemy.orm import Session

from app.schemas.photo import FotoCreate, FotoOut
from app.security.deps import get_db, require_role
from app.services.fruta_service import evaluate_fruit
from app.services.photo_service import create_foto, delete_foto, get_foto, list_fotos
from app.utils.image_utils import ImageTooLargeError

logger = logging.getLogger("madura_back")

router = APIRouter()


@router.post("/evaluate")
def evaluate_fruit_endpoint(
    file: UploadFile = File(...),
    current=Depends(require_role("user")),
):
    """Clasifica el estado de madurez de la imagen subida (verde/madura/pasada).

    Requiere autenticación (token JWT). La función es síncrona a propósito:
    Starlette la ejecuta en un threadpool para no bloquear el event loop durante
    la inferencia con TensorFlow.
    """
    try:
        result = evaluate_fruit(file.file)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida") from None
    except ImageTooLargeError:
        raise HTTPException(status_code=413, detail="La imagen supera el tamaño máximo permitido") from None
    except Exception:
        logger.exception("Error inesperado al evaluar la fruta")
        raise HTTPException(status_code=500, detail="Error al procesar la imagen") from None
    finally:
        file.file.close()
    return {"estado": result}


@router.get("/", response_model=list[FotoOut])
def list_all(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    return list_fotos(db, skip=skip, limit=limit)


@router.post("/", response_model=FotoOut)
def create(
    foto_in: FotoCreate,
    db: Session = Depends(get_db),
    current=Depends(require_role("user")),
):
    # Un usuario normal solo puede registrar fotos a su nombre (se ignora el
    # usuario_id del payload); el admin puede asignarlas a otros usuarios.
    usuario_id = current.id if current.rol != "admin" else (foto_in.usuario_id or current.id)
    return create_foto(db, url=str(foto_in.url), usuario_id=usuario_id)


@router.get("/{foto_id}", response_model=FotoOut)
def get_one(foto_id: int, db: Session = Depends(get_db)):
    foto = get_foto(db, foto_id)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto not found")
    return foto


@router.delete("/{foto_id}")
def delete(
    foto_id: int,
    db: Session = Depends(get_db),
    current=Depends(require_role("user")),
):
    foto = get_foto(db, foto_id)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto not found")
    # Solo el dueño de la foto o un admin pueden eliminarla
    if current.rol != "admin" and foto.usuario_id != current.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    delete_foto(db, foto)
    return {"ok": True}
