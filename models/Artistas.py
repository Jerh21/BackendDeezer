from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Artistas(Base):
    __tablename__ = 'tbl_artistas'
    
    codigo_artista = Column(Integer, primary_key=True, autoincrement=True)
    nombre_artista = Column(String(200), nullable=False)
    biografia = Column(String)
    url_foto = Column(String(300)) 
    
class InsertArtistas(BaseModel):
    codigo_artista: int
    nombre_artista: str
    biografia: str | None = None  # Opcional
    url_foto: str | None = None  # Opcional