import contextlib
import os
import tempfile

import pytest

# La variable de entorno debe definirse ANTES de importar la app
with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as _tmp:
    _TMP_DB_NAME = _tmp.name
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB_NAME}"


def make_user(db, nombre: str, email: str, password: str, rol: str = "user"):
    """Crea un usuario directamente en la BD (permite fijar rol admin)."""
    from app.schemas.user import UsuarioCreate
    from app.services.user_service import create_user

    user = create_user(db, UsuarioCreate(nombre=nombre, email=email, password=password))
    if rol != "user":
        user.rol = rol
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as c:
        yield c
    # Libera las conexiones del pool antes de borrar el archivo (Windows)
    from app.database.base import engine

    engine.dispose()
    if os.path.exists(_TMP_DB_NAME):
        with contextlib.suppress(OSError):
            os.unlink(_TMP_DB_NAME)


@pytest.fixture
def db():
    from app.database.base import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def crear_usuario(db):
    def _crear(nombre: str, email: str, password: str, rol: str = "user"):
        return make_user(db, nombre, email, password, rol)

    return _crear


@pytest.fixture
def auth_headers(client):
    def _headers(email: str, password: str) -> dict:
        resp = client.post("/auth/token", data={"username": email, "password": password})
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture(autouse=True)
def _clean_state():
    """Limpia el rate limiter entre tests para no encadenar bloqueos."""
    from app.controllers.auth import login_limiter

    login_limiter.reset_all()
    yield
    login_limiter.reset_all()
