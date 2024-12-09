from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.config import DATABASE_URL
from models.Usuario import Base

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una función para obtener sesiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)