from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Song(Base):
    __tablename__ = 'tbl_canciones'

    codigo_cancion = Column(Integer, primary_key=True, autoincrement=True)
    codigo_artista = Column(Integer, ForeignKey('tbl_artistas.codigo_artista'), nullable=False)
    codigo_genero = Column(Integer, ForeignKey('tbl_generos.codigo_genero'), nullable=False)
    codigo_ambiente = Column(Integer, ForeignKey('tbl_ambientes.codigo_ambiente'), nullable=False)
    codigo_album = Column(Integer, ForeignKey('tbl_albums.codigo_album'), nullable=False)
    titulo = Column(String(100), nullable=False)
    duracion = Column(Float, nullable=False)
    fecha_subida = Column(Date, nullable=False)
    url_foto_portada = Column(String(300), nullable=True)
    numero_reproducciones = Column(Integer, default=0)



    # Relación con el historial de canciones
    #historial_canciones = relationship('HistorialCanciones', back_populates="cancion")
    #artista = relationship("Artistas", back_populates="canciones")

class InsertSong(BaseModel):
    codigo_cancion: int
    codigo_artista: int
    codigo_genero: int
    codigo_ambiente: int
    codigo_album: int
    titulo: str
    duracion: float
    fecha_subida: date
    url_foto_portada: str | None = None  # Opcional
    numero_reproducciones: int = 0  # Valor predeterminado