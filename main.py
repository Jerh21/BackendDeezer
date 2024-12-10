from sqlalchemy import func, desc
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models.Usuario import User, UserCreate
from models.Historial_Canciones import HistorialCanciones
from models.Artistas import Artistas
from models.Canciones import Song
from models.Fans import FansArtista
from utils.database import get_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select


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



@app.get("/last-song/{user_id}")
def get_last_song(user_id: int, db: Session = Depends(get_db)):
    # Consulta para obtener la última canción del historial
    query = (
        db.query(
            HistorialCanciones.codigo_usuario,
            HistorialCanciones.codigo_cancion,
            Song.titulo,
            Song.codigo_artista,
            Artistas.nombre_artista,
            Song.duracion,
            Song.url_foto_portada
        )
        .join(Song, HistorialCanciones.codigo_cancion == Song.codigo_cancion)
        .join(Artistas, Song.codigo_artista == Artistas.codigo_artista)
        .filter(HistorialCanciones.codigo_usuario == user_id)
        .order_by(desc(HistorialCanciones.fecha))  # Ordenar por fecha, de la más reciente
    )

    # Usamos `first()` para obtener solo el primer resultado
    last_song = query.first()

    if not last_song:
        raise HTTPException(status_code=404, detail="No se encontró historial de canciones para este usuario.")
    
    # Devolver los datos de la última canción reproducida
    return {
        "titulo": last_song.titulo,
        "artista": last_song.nombre_artista,  # Nombre del artista
        "duracion": last_song.duracion,  # Duración en segundos
        "url_foto_portada": last_song.url_foto_portada or "/images/default-song.png",  # URL de la portada
    }
    
# Ruta para obtener los detalles de una canción específica por ID
@app.get("/api/song/{song_id}")
def get_song(song_id: int, db: Session = Depends(get_db)):
    # Buscar la canción por ID
    song = db.query(Song).filter(Song.codigo_cancion == song_id).first()

    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada.")
    
    # Devolver los detalles de la canción
    return {
        "codigo_cancion": song.codigo_cancion,
        "titulo": song.titulo,
        "artista": song.artista.nombre,  # Asumiendo que tienes una relación con 'Artistas'
        "album": song.album.nombre,  # Asumiendo que tienes una relación con 'Albums'
        "duracion": song.duracion,
        "fecha_subida": song.fecha_subida,
        "url_foto_portada": song.url_foto_portada or "images/default-song.png",
    }

# Ruta para obtener los detalles de un artista específico por ID
@app.get("/api/artist/{artist_id}")
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    # Buscar el artista por ID
    artist = db.query(Artistas).filter(Artistas.codigo_artista == artist_id).first()

    if not artist:
        raise HTTPException(status_code=404, detail="Artista no encontrado.")
    
    # Devolver los detalles del artista
    return {
        "codigo_artista": artist.codigo_artista,
        "nombre": artist.nombre,  # Asumiendo que el artista tiene un campo 'nombre'
        "biografia": artist.biografia or "Biografía no disponible",  # Suponiendo que tiene un campo 'biografia'
        "url_foto": artist.url_foto or "images/default-profile.png",  # URL de la foto del artista
    }
    
    
@app.get("/artist-stats")
def get_artist_stats(db: Session = Depends(get_db)):
    # Subconsulta para contar la cantidad de canciones por artista
    subquery_canciones_artistas = (
        db.query(
            Song.codigo_artista.label("codigo_artista"),
            func.count(Song.codigo_artista).label("cantidad_cancion")
        )
        .group_by(Song.codigo_artista)
        .subquery()
    )

    # Consulta principal
    query = (
        db.query(
            FansArtista.codigo_artista,
            Artistas.nombre_artista,
            Artistas.url_foto,
            func.count(FansArtista.codigo_artista).label("fans"),
            subquery_canciones_artistas.c.cantidad_cancion
        )
        .join(Artistas, FansArtista.codigo_artista == Artistas.codigo_artista)
        .outerjoin(subquery_canciones_artistas, FansArtista.codigo_artista == subquery_canciones_artistas.c.codigo_artista)
        .group_by(
            FansArtista.codigo_artista,
            Artistas.nombre_artista,
            Artistas.url_foto,
            subquery_canciones_artistas.c.cantidad_cancion
        )
        .order_by(desc(func.count(FansArtista.codigo_artista)))  # Ordenar por cantidad de fans, descendente
    )

    result = query.all()

    # Serializar los resultados para retornarlos como JSON
    return [
        {
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "url_foto": row.url_foto or "/images/default-profile.png",  # Foto predeterminada si no hay URL
            "fans": row.fans,
            "cantidad_cancion": row.cantidad_cancion or 0  # Asumir 0 si es NULL
        }
        for row in result
    ]