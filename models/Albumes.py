from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Album(Base):
    __tablename__ = 'tbl_albumes'

    codigo_album = Column(Integer, primary_key=True, autoincrement=True)
    codigo_artista = Column(Integer, ForeignKey('tbl_artistas.codigo_artista'), nullable=False)
    titulo = Column(String(300), nullable=False)
    fecha_lanzamiento = Column(Date, nullable=False)
    url_foto_portada = Column(String(300), nullable=True)



    # Relación con el historial de canciones
    #historial_canciones = relationship('HistorialCanciones', back_populates="cancion")
    #artista = relationship("Artistas", back_populates="canciones")

class InsertAlbum(BaseModel):
    codigo_album: int
    codigo_artista: int
    titulo: str
    fecha_lanzamiento: date
    url_foto_portada: str | None = None  # Opcional