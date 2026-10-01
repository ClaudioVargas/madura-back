import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# check_same_thread solo aplica a SQLite (SQLAlchemy 2.x)
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Activa el chequeo de claves foráneas en SQLite (PRAGMA foreign_keys=ON)."""
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    # Se importan los modelos para que queden registrados en el metadata de SQLAlchemy
    from app.models import fruta, photo, user, verdura  # noqa: F401

    Base.metadata.create_all(bind=engine)
