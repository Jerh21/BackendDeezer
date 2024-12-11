from sqlalchemy import Column, Integer, String, Date
from datetime import date
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



class User(Base):
    __tablename__ = 'tbl_usuarios'

    codigo_usuario = Column(Integer, primary_key=True, autoincrement=True)
    codigo_suscripcion_actual = Column(Integer, nullable=False)
    codigo_identidad = Column(Integer, nullable=False)
    nombre_usuario = Column(String(200))
    edad = Column(Integer)
    correo = Column(String(200), nullable=False, unique=True)
    contrasenna = Column(String(100), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    url_foto_perfil = Column(String(300))

    
class UserCreate(BaseModel):
    codigo_usuario: int
    codigo_suscripcion_actual: int = 1
    codigo_identidad: int
    nombre_usuario: str | None = None
    edad: int | None = None
    correo: EmailStr
    contrasenna: str
    fecha_registro: date
    url_foto_perfil: str | None = None