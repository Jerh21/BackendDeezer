from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Playlist(Base):
    __tablename__ = 'tbl_playlist'

    codigo_playlist = Column(Integer, primary_key=True, autoincrement=True)
    codigo_usuario = Column(Integer, ForeignKey('tbl_usuario.codigo_usuario'), nullable=False)  # Clave foránea hacia tbl_usuario
    nombre_playlist = Column(String(200), nullable=True)
    fecha_creacion = Column(Date, nullable=False)
    descripcion = Column(String, nullable=True)
    url_foto_portada = Column(String(300), nullable=True)

    # Relación con el modelo de Usuario
    #usuario = relationship('Usuario', backref='playlists')  # Esto te permitirá acceder a las playlists del usuario

class InsertPlaylist(BaseModel):
    codigo_playlist: int
    codigo_usuario: int
    nombre_playlist: str
    fecha_creacion: date
    descripcion: str
    url_foto_portada: str | None = None