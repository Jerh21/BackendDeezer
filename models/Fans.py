from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Modelo de SQLAlchemy para la tabla tbl_artistas_favoritos
class FansArtista(Base):
    __tablename__ = 'tbl_artistas_favoritos'

    # Atributos de la tabla
    codigo_usuario = Column(Integer, ForeignKey('tbl_usuarios.codigo_usuario'), primary_key=True, nullable=False)
    codigo_artista = Column(Integer, ForeignKey('tbl_artistas.codigo_artista'), primary_key=True, nullable=False)

# Modelo Pydantic para validación de datos
class InsertFan(BaseModel):
    codigo_usuario: int
    codigo_artista: int