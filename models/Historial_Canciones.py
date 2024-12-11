from sqlalchemy import Column, Integer, Date, ForeignKey
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HistorialCanciones(Base):
    __tablename__ = 'tbl_historial_canciones'

    codigo_historial = Column(Integer, primary_key=True, autoincrement=True)
    codigo_usuario = Column(Integer, nullable=False)
    codigo_cancion = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)


class InsertHistorialCanciones(BaseModel):
    codigo_historial: int
    codigo_usuario: int
    codigo_cancion: int
    fecha: date  # Corregido para que coincida con el campo en el modelo de SQLAlchemy