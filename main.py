import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.controllers import auth, fotos, frutas, users, verduras
from app.core.config import settings
from app.database.base import engine, init_db
from app.middleware.logging import RequestLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("madura_back")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # tareas de arranque: crear tablas si no existen
    init_db()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


@app.get("/")
def read_root():
    """Health check básico (evita el 404 en Render)."""
    return {"status": "ok", "message": "Backend running successfully"}


@app.get("/health")
def health():
    """Health check con verificación real de la base de datos."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        logger.exception("Health check falló")
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "error"})


# --- Manejadores globales de excepciones ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "Validación fallida en %s %s: %s", request.method, request.url.path, exc.errors()
    )
    # Mantiene el formato estándar de FastAPI: {"detail": [errores]}
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error("IntegrityError en %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=409, content={"detail": "Conflict: resource already exists"}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# --- Middleware ---
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(frutas.router, prefix="/frutas", tags=["frutas"])
app.include_router(verduras.router, prefix="/verduras", tags=["verduras"])
app.include_router(fotos.router, prefix="/fotos", tags=["fotos"])
