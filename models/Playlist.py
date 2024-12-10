from sqlalchemy import Column, Integer, String, Date
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Playlist(Base):
    __tablename__ = 'tbl_playlist'

    codigo_playlist = Column(Integer, primary_key=True, autoincrement=True)
    codigo_usuario_creador = Column(Integer, nullable=False)
    nombre_playlist = Column(String(200), nullable=True)
    fecha_creacion = Column(Date, nullable=False)
    descripcion = Column(String, nullable=True)
    url_foto_portada = Column(String(300), nullable=True)

class InsertPlaylist(BaseModel):
    codigo_playlist: int
    codigo_usuario_creador: int
    nombre_playlist: str
    fecha_creacion: date
    descripcion: str
    url_foto_portada: str | None = None