from models.Artistas import Artistas
from models.Canciones import Song
from models.Historial_Canciones import HistorialCanciones
from models.Usuario import User

from sqlalchemy.orm import configure_mappers

try:
    configure_mappers()
    print("Todos los mapeadores configurados correctamente.")
except Exception as e:
    print(f"Error al configurar mapeadores: {e}")