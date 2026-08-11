from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import users, auth, frutas, verduras, fotos
from app.middleware.logging import RequestLoggingMiddleware
from app.database.base import init_db

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # run startup tasks
    init_db()
    yield
    # run shutdown tasks here if needed

app = FastAPI(title="madura_back", lifespan=lifespan)

# middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(frutas.router, prefix="/frutas", tags=["frutas"])
app.include_router(verduras.router, prefix="/verduras", tags=["verduras"])
app.include_router(fotos.router, prefix="/fotos", tags=["fotos"])