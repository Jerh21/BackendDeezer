from sqlalchemy import Column, Integer, String
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Relación con la tabla 
class Ambient(Base):
    __tablename__ = 'tbl_ambientes'

    codigo_ambiente = Column(Integer, primary_key=True, autoincrement=True)
    nombre_ambiente = Column(String(100), nullable=False)
