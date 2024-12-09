from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models.Usuario import UserCreate
from utils.database import get_db
from models.Usuario import User

app = FastAPI()


@app.get("/users")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Convertir el esquema de entrada (Pydantic) en un modelo SQLAlchemy
    db_user = User(
        codigo_usuario=user.codigo_usuario,
        codigo_suscripcion_actual=user.codigo_suscripcion_actual,
        codigo_identidad=user.codigo_identidad,
        nombre_usuario=user.nombre_usuario,
        edad=user.edad,
        correo=user.correo,
        contrasenna=user.contrasenna,
        fecha_registro=user.fecha_registro,
        url_foto_perfil=user.url_foto_perfil
    )
    # Agregar el usuario a la base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user