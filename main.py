from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models.Usuario import User, UserCreate
from utils.database import get_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Esquema para la solicitud de inicio de sesión
class LoginRequest(BaseModel):
    correo: str
    contrasenna: str
    
# Configuración de CORS
origins = [
    "http://localhost:3000",  # URL de tu frontend React
    "http://127.0.0.1:3000",  # También puedes agregar esta por si usas 127.0.0.1
]

# Añadir middleware para permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.get("/users")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Crear un nuevo usuario con la contraseña cifrada
    db_user = User(
        codigo_usuario=user.codigo_usuario,
        codigo_suscripcion_actual=user.codigo_suscripcion_actual,
        codigo_identidad=user.codigo_identidad,
        nombre_usuario=user.nombre_usuario,
        edad=user.edad,
        correo=user.correo,
        contrasenna=user.contrasenna,  # Almacenar la contraseña cifrada
        fecha_registro=user.fecha_registro,
        url_foto_perfil=user.url_foto_perfil,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Buscar usuario por correo
    user = db.query(User).filter(User.correo == request.correo).first()
    
    # Validar si el correo existe
    if not user:
        raise HTTPException(status_code=404, detail="Correo no encontrado")
    
    # Validar contraseña simple (comparación directa de cadenas)
    if user.contrasenna != request.contrasenna:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    # Responder con los datos del usuario en caso de éxito
    return {"id": user.codigo_usuario, "nombre": user.nombre_usuario, "url_foto_perfil": user.url_foto_perfil}

@app.get("/users/email/{email}")
def check_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.correo == email).first()
    if user:
        return {"exists": True}  # El correo está registrado
    return {"exists": False}  # El correo no está registrado

@app.get("/users/last")
def get_last_user(db: Session = Depends(get_db)):
    last_user = db.query(User).order_by(User.codigo_usuario.desc()).first()
    return last_user