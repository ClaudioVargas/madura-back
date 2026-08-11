import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
print(f"BASE_DIR: {BASE_DIR}")  # Debugging line to check the base directory
DB_PATH = os.path.join(BASE_DIR, "database.db")
print(f"DB_PATH: {DB_PATH}")  # Debugging line to check the database path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")  # Debugging line to check the database URL

# For SQLite using SQLAlchemy 2.0, set future-style engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    # import models so they are registered with SQLAlchemy metadata
    from app.models import user, photo, fruta, verdura  # noqa: F401
    Base.metadata.create_all(bind=engine)
