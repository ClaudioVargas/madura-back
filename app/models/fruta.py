from sqlalchemy import Column, Float, Integer, String

from app.database.base import Base


class Fruta(Base):
    __tablename__ = "frutas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    color = Column(String, nullable=True)
    precio = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    creador_id = Column(Integer, nullable=True)
