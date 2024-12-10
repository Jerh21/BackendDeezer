from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Artistas(Base):
    __tablename__ = 'tbl_artistas'
    
    codigo_artista = Column(Integer, primary_key=True, autoincrement=True)
    nombre_artista = Column(String(200), nullable=False, index=True)  # Agregado el índice para optimizar las búsquedas
    biografia = Column(String(1000), nullable=True)  # Definí un límite para la biografía (opcional)
    url_foto = Column(String(300), nullable=True)  # El URL sigue siendo opcional
    
    # Relación con la tabla de canciones
    #canciones = relationship("Song", back_populates="artista")
    
class InsertArtistas(BaseModel):
    codigo_artista: int
    nombre_artista: str
    biografia: str | None = None  # Opcional
    url_foto: str | None = None  # Opcional