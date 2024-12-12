from sqlalchemy import func, desc
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from models.Usuario import User, UserCreate
from models.Historial_Canciones import HistorialCanciones
from models.Artistas import Artistas
from models.Canciones import Song, InsertSong
from models.Fans import FansArtista
from models.Albumes import Album
from models.Ambientes import Ambient
from utils.database import get_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from fastapi import Body

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
        url_foto_perfil="/images/default-profile.png",
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
        "nombre_artista": last_song.nombre_artista,  # Nombre del artista
        "duracion": last_song.duracion,  # Duración en segundos
        "url_foto_portada": last_song.url_foto_portada or "/images/default-song.png",  # URL de la portada
    }


@app.get("/song/{song_id}")
def obtener_cancion(song_id: int, db: Session = Depends(get_db)):
    cancion = obtener_cancion_por_id(db, song_id)
    if cancion:
        return cancion
    return {"error": "Canción no encontrada"}


# Función para obtener la canción y su artista
def obtener_cancion_por_id(db: Session, song_id: int):
    # Hacemos la consulta con un LEFT JOIN entre tbl_canciones y tbl_artistas
    query = (
        db.query(
            Song.codigo_cancion,
            Song.titulo,
            Song.codigo_artista,
            Artistas.nombre_artista,
            Song.duracion,
            Song.url_foto_portada
        )
        .join(Artistas, Song.codigo_artista == Artistas.codigo_artista, isouter=True)  # LEFT JOIN
        .filter(Song.codigo_cancion == song_id)  # Filtrar por el ID de la canción
    )

    result = query.first()  # Obtenemos solo el primer (y único) resultado

    if result:
        return {
            "codigo_cancion": result.codigo_cancion,
            "titulo": result.titulo,
            "codigo_artista": result.codigo_artista,
            "nombre_artista": result.nombre_artista,
            "duracion": result.duracion,
            "url_foto_portada": result.url_foto_portada or "/images/default-song.png",  # Si no tiene portada, usar la portada por defecto
        }
    return None
    
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
        .limit(5)  # Limitar a los primeros 5 resultados
    )

    result = query.all()

    # Serializar los resultados para retornarlos como JSON
    return [
        {
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "url_foto": row.url_foto or "/images/default-artist.jpg",  # Foto predeterminada si no hay URL
            "fans": row.fans,
            "cantidad_cancion": row.cantidad_cancion or 0  # Asumir 0 si es NULL
        }
        for row in result
    ]
    
    
@app.get("/albumes-detalles")
def obtener_albumes_con_detalles(db: Session = Depends(get_db)):
    albumes = obtener_albumes_con_detalles(db)
    return albumes


def obtener_albumes_con_detalles(db: Session):
    # Subconsulta para obtener cantidad de canciones y duración total por álbum
    subquery_canciones_album = (
        db.query(
            Song.codigo_album.label("codigo_album"),
            func.count(Song.codigo_album).label("cantidad_canciones_album"),
            func.sum(Song.duracion).label("duracion_album")
        )
        .group_by(Song.codigo_album)
        .subquery()
    )

    # Consulta principal
    query = (
        db.query(
            Album.codigo_album,
            Album.titulo,
            Album.codigo_artista,
            Artistas.nombre_artista,
            subquery_canciones_album.c.cantidad_canciones_album,
            subquery_canciones_album.c.duracion_album,
            Album.fecha_lanzamiento
        )
        .join(Artistas, Album.codigo_artista == Artistas.codigo_artista)
        .outerjoin(subquery_canciones_album, Album.codigo_album == subquery_canciones_album.c.codigo_album)
        .group_by(
            Album.codigo_album,
            Album.titulo,
            Album.codigo_artista,
            Artistas.nombre_artista,
            subquery_canciones_album.c.cantidad_canciones_album,
            subquery_canciones_album.c.duracion_album,
            Album.fecha_lanzamiento
        )
    )

    # Ejecutar la consulta y obtener los resultados
    result = query.all()

    # Serializar los resultados
    return [
        {
            "codigo_album": row.codigo_album,
            "titulo": row.titulo,
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "cantidad_canciones_album": row.cantidad_canciones_album or 0,
            "duracion_album": row.duracion_album or 0,
            "fecha_lanzamiento": row.fecha_lanzamiento,
        }
        for row in result
    ]
    
@app.get("/top-albumes-reproducidos")
def obtener_top_albumes_reproducidos_endpoint(db: Session = Depends(get_db)):
    top_albumes = obtener_top_albumes_reproducidos(db)
    return top_albumes

    
def obtener_top_albumes_reproducidos(db: Session):
    # Subconsulta para obtener el total de reproducciones por álbum
    subquery_reproducciones_total = (
        db.query(
            Song.codigo_album.label("codigo_album"),
            func.sum(Song.numero_reproducciones).label("reproducciones_album")
        )
        .group_by(Song.codigo_album)
        .subquery()
    )

    # Consulta principal
    query = (
        db.query(
            Album.codigo_album,
            Album.titulo,
            Album.codigo_artista,
            Artistas.nombre_artista,
            Album.fecha_lanzamiento,
            Album.url_portada,
            subquery_reproducciones_total.c.reproducciones_album
        )
        .join(Artistas, Album.codigo_artista == Artistas.codigo_artista)
        .outerjoin(subquery_reproducciones_total, Album.codigo_album == subquery_reproducciones_total.c.codigo_album)
        .group_by(
            Album.codigo_album,
            Album.titulo,
            Album.codigo_artista,
            Artistas.nombre_artista,
            Album.fecha_lanzamiento,
            Album.url_portada,
            subquery_reproducciones_total.c.reproducciones_album
        )
        .order_by(desc(subquery_reproducciones_total.c.reproducciones_album))  # Ordenar por reproducciones, descendente
        .limit(5)  # Limitar a los 5 álbumes más reproducidos
    )

    # Ejecutar la consulta y obtener los resultados
    result = query.all()

    # Serializar los resultados
    return [
        {
            "codigo_album": row.codigo_album,
            "titulo": row.titulo,
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "fecha_lanzamiento": row.fecha_lanzamiento,
            "url_portada": row.url_portada or "/images/default-cover.jpg",
            "reproducciones_album": row.reproducciones_album or 0,  # Asumir 0 si es NULL
        }
        for row in result
    ]
    

@app.get("/top-5-albumes-recientes")
def obtener_top_5_albumes_recientes(db: Session = Depends(get_db)):
    albumes_recientes = obtener_5_albumes_mas_recientes(db)
    return albumes_recientes

def obtener_5_albumes_mas_recientes(db: Session):
    # Consulta principal para obtener los 5 álbumes más recientes
    query = (
        db.query(
            Album.codigo_album,
            Album.titulo,
            Album.codigo_artista,
            Artistas.nombre_artista,
            Album.fecha_lanzamiento,
            Album.url_portada
        )
        .join(Artistas, Album.codigo_artista == Artistas.codigo_artista)
        .order_by(desc(Album.fecha_lanzamiento))  # Ordenar por fecha de lanzamiento, descendente
        .limit(5)  # Limitar a los 5 álbumes más recientes
    )

    # Ejecutar la consulta y obtener los resultados
    result = query.all()

    # Serializar los resultados
    return [
        {
            "codigo_album": row.codigo_album,
            "titulo": row.titulo,
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "fecha_lanzamiento": row.fecha_lanzamiento,
            "url_portada": row.url_portada or "/images/default-cover.jpg",  # Si no tiene portada, usar la portada por defecto
        }
        for row in result
    ]


@app.get("/album-songs/{album_id}")
def obtener_canciones_album(album_id: int, db: Session = Depends(get_db)):
    canciones = db.query(
        Song.codigo_cancion,
        Song.titulo,
        Song.codigo_artista,
        Artistas.nombre_artista,
        Song.duracion,
        Song.url_foto_portada
    ).join(Artistas, Song.codigo_artista == Artistas.codigo_artista, isouter=True)  \
    .filter(Song.codigo_album == album_id)  \
    .all()
    
    return [
        {
            "codigo_cancion": row.codigo_cancion,
            "titulo": row.titulo,
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "duracion": row.duracion,
            "url_foto_portada": row.url_foto_portada or "/images/default-song.png",
        }
        for row in canciones
    ]
    
@app.get("/artist-songs/{artist_id}")
def obtener_canciones_artista(artist_id: int, db: Session = Depends(get_db)):
    canciones = db.query(
        Song.codigo_cancion,
        Song.titulo,
        Song.codigo_artista,
        Artistas.nombre_artista,
        Song.duracion,
        Song.url_foto_portada
    ).join(Artistas, Song.codigo_artista == Artistas.codigo_artista, isouter=True)  \
    .filter(Song.codigo_artista == artist_id)  \
    .all()
    
    return [
        {
            "codigo_cancion": row.codigo_cancion,
            "titulo": row.titulo,
            "codigo_artista": row.codigo_artista,
            "nombre_artista": row.nombre_artista,
            "duracion": row.duracion,
            "url_foto_portada": row.url_foto_portada or "/images/default-song.png",
        }
        for row in canciones
    ]

class InsertHistorialCanciones(BaseModel):
    codigo_usuario: int
    codigo_cancion: int
    fecha: datetime

@app.post("/insertar_historial/")
def insertar_historial(historial: InsertHistorialCanciones, db: Session = Depends(get_db)):

    # 3. Obtener el último CODIGO_HISTORIAL y aumentarlo en 1
    last_historial = db.query(HistorialCanciones).order_by(HistorialCanciones.codigo_historial.desc()).first()
    if last_historial:
        nuevo_codigo_historial = last_historial.codigo_historial + 1
    else:
        nuevo_codigo_historial = 1  # Si no hay registros previos, iniciar con 1

    # 4. Crear el nuevo historial
    nuevo_historial = HistorialCanciones(
        codigo_historial=nuevo_codigo_historial,
        codigo_usuario=historial.codigo_usuario,
        codigo_cancion=historial.codigo_cancion,
        fecha=historial.fecha,
    )

    # 5. Insertar el nuevo historial en la base de datos
    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)

    return {"message": "Historial insertado correctamente", "codigo_historial": nuevo_historial.codigo_historial}

@app.post("/historial")
def add_to_historial(user_id: int, song_id: int, db: Session = Depends(get_db)):
    try:
        # Verificar si el usuario y la canción existen
        user = db.query(User).filter(User.codigo_usuario == user_id).first()
        song = db.query(Song).filter(Song.codigo_cancion == song_id).first()

        if not user or not song:
            raise HTTPException(status_code=404, detail="Usuario o Canción no encontrados")

        # Obtener el último codigo_historial y sumarle 1 para el nuevo valor
        last_historial = db.query(HistorialCanciones).order_by(HistorialCanciones.codigo_historial.desc()).first()
        if last_historial:
            new_codigo_historial = last_historial.codigo_historial + 1
        else:
            new_codigo_historial = 1  # Si no existe historial previo, empezar desde 1

        # Crear nueva entrada en el historial
        new_entry = HistorialCanciones(
            codigo_historial=new_codigo_historial,
            codigo_usuario=user_id,
            codigo_cancion=song_id,
            fecha=datetime.today(),
        )

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {"message": "Historial actualizado correctamente.", "entry": new_entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en el historial: {str(e)}")
    
@app.get("/ambientes")
def get_ambientes(db: Session = Depends(get_db)):
    try:
        # Obtener todos los ambientes
        ambientes = db.query(Ambient).all()
        return ambientes
    except SQLAlchemyError as e:
        print(f"Error al obtener los ambientes: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los ambientes.")


@app.get("/canciones/ambiente/{codigo_ambiente}")
def get_songs_by_ambient(codigo_ambiente: int, db: Session = Depends(get_db)):
    # Realizamos la consulta a la base de datos para obtener las canciones de ese ambiente
    songs = db.query(Song, Artistas.nombre_artista).join(Artistas, Song.codigo_artista == Artistas.codigo_artista).filter(Song.codigo_ambiente == codigo_ambiente).all()
    
    # Devolver los resultados de la consulta
    result = []
    for song, artist_name in songs:
        result.append({
            "codigo_cancion": song.codigo_cancion,
            "codigo_artista": song.codigo_artista,
            "codigo_genero": song.codigo_genero,
            "codigo_ambiente": song.codigo_ambiente,
            "codigo_album": song.codigo_album,
            "titulo": song.titulo,
            "duracion": song.duracion,
            "fecha_subida": song.fecha_subida,
            "url_foto_portada": song.url_foto_portada,
            "numero_reproducciones": song.numero_reproducciones,
            "nombre_artista": artist_name  # Incluimos el nombre del artista
        })
    
    return result

@app.get("/searching")
def searching(search: str = Query(None), db: Session = Depends(get_db)):
    try:
        # Crear la consulta base
        query = db.query(
            Song.codigo_cancion,
            Song.titulo.label("song_title"),
            Song.duracion,
            Song.url_foto_portada,
            Artistas.nombre_artista,
            Album.titulo.label("album_title")
        ).join(
            Artistas, Song.codigo_artista == Artistas.codigo_artista
        ).join(
            Album, Song.codigo_album == Album.codigo_album
        )

        # Filtrar por el término de búsqueda
        if search:
            search = f"%{search.lower()}%"
            query = query.filter(
                (Song.titulo.ilike(search)) |
                (Artistas.nombre_artista.ilike(search)) |
                (Album.titulo.ilike(search))
            )

        # Ejecutar la consulta
        results = query.all()

        # Formatear los resultados para enviarlos como JSON
        songs = [
            {
                "id": song.codigo_cancion,
                "title": song.song_title,
                "artist": song.nombre_artista,
                "album": song.album_title,
                "duration": song.duracion,
                "cover_url": song.url_foto_portada,
            }
            for song in results
        ]

        return {"songs": songs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar canciones: {str(e)}")