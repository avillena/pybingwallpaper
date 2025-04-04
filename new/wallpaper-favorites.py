import json
from datetime import datetime
from pathlib import Path
from constants import Constants
from utils.file_utils import read_json, write_json, copy_file, delete_file, file_exists
from utils.logger import log_error, log_info
from utils.resource_utils import open_folder

class WallpaperFavorites:
    """Gestiona los fondos de pantalla favoritos."""
    
    # Fuente de wallpapers
    SOURCE_FAVORITE = "favorite"
    
    @staticmethod
    def get_favorites_file():
        """Obtiene la ruta del archivo con metadatos de favoritos."""
        return Constants.get_data_path() / "favorites.json"
    
    @staticmethod
    def load_favorites_data():
        """Carga los datos de favoritos desde el archivo JSON."""
        favorites_file = WallpaperFavorites.get_favorites_file()
        favorites_data = read_json(favorites_file, {"favorites": []})
        return favorites_data
    
    @staticmethod
    def save_favorites_data(data):
        """Guarda los datos de favoritos en el archivo JSON."""
        favorites_file = WallpaperFavorites.get_favorites_file()
        return write_json(favorites_file, data)
    
    @staticmethod
    def add_to_favorites(wallpaper_info):
        """
        Agrega un wallpaper a favoritos.
        Se utiliza el campo "file_path" de wallpaper_info, si existe, para obtener
        la ruta del archivo descargado.
        """
        try:
            source_file_path = wallpaper_info.get("file_path")
            if source_file_path:
                source_file = Path(source_file_path)
            else:
                idx = wallpaper_info.get("current_index", 0)
                source_file = Constants.get_wallpaper_file(idx)
            
            if not file_exists(source_file):
                log_error(f"El archivo {source_file} no existe")
                return False
            
            timestamp = int(datetime.now().timestamp())
            favorite_filename = f"favorite_{timestamp}{source_file.suffix}"
            target_path = Constants.get_favorites_path() / favorite_filename
            
            if not copy_file(source_file, target_path):
                return False
            
            favorite_entry = {
                "id": str(timestamp),
                "picture_url": wallpaper_info.get("picture_url", ""),
                "thumbnail_url": wallpaper_info.get("thumbnail_url", ""),
                "copyright": wallpaper_info.get("copyright", "Sin título"),
                "date": wallpaper_info.get("date", datetime.now().strftime("%Y-%m-%d")),
                "file_path": str(target_path),
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": WallpaperFavorites.SOURCE_FAVORITE
            }
            
            favorites_data = WallpaperFavorites.load_favorites_data()
            favorites_data["favorites"].append(favorite_entry)
            WallpaperFavorites.save_favorites_data(favorites_data)
            
            log_info(f"Wallpaper agregado a favoritos: {favorite_entry.get('copyright')}")
            return True
        except Exception as e:
            log_error(f"Error al agregar a favoritos: {str(e)}")
            return False
    
    @staticmethod
    def remove_from_favorites(favorite_id):
        """
        Elimina un wallpaper de favoritos por su ID.
        
        Args:
            favorite_id: ID único del favorito.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        try:
            favorites_data = WallpaperFavorites.load_favorites_data()
            for i, favorite in enumerate(favorites_data["favorites"]):
                if favorite.get("id") == favorite_id:
                    file_path = favorite.get("file_path", "")
                    if file_path and file_exists(file_path):
                        delete_file(file_path)
                    
                    favorites_data["favorites"].pop(i)
                    WallpaperFavorites.save_favorites_data(favorites_data)
                    log_info(f"Wallpaper eliminado de favoritos: {favorite.get('copyright', 'Sin título')}")
                    return True
            return False
        except Exception as e:
            log_error(f"Error al eliminar de favoritos: {str(e)}")
            return False
    
    @staticmethod
    def is_favorite(wallpaper_info):
        """
        Verifica si un wallpaper está en favoritos.
        
        Args:
            wallpaper_info: Diccionario con información del wallpaper.
            
        Returns:
            str or None: ID del favorito si existe, None si no está en favoritos.
        """
        try:
            if not wallpaper_info:
                return None
            picture_url = wallpaper_info.get("picture_url", "")
            if not picture_url:
                return None
            favorites_data = WallpaperFavorites.load_favorites_data()
            for favorite in favorites_data["favorites"]:
                if favorite.get("picture_url") == picture_url:
                    return favorite.get("id")
            return None
        except Exception as e:
            log_error(f"Error al verificar favorito: {str(e)}")
            return None
    
    @staticmethod
    def get_favorites_list():
        """
        Obtiene la lista de wallpapers favoritos.
        
        Returns:
            list: Lista de diccionarios con información de los wallpapers favoritos.
        """
        try:
            favorites_data = WallpaperFavorites.load_favorites_data()
            return favorites_data["favorites"]
        except Exception as e:
            log_error(f"Error al obtener lista de favoritos: {str(e)}")
            return []
    
    @staticmethod
    def open_favorites_folder():
        """
        Abre la carpeta de favoritos en el explorador de archivos.
        
        Returns:
            bool: True si se abrió correctamente, False en caso contrario.
        """
        try:
            fav_dir = Constants.get_favorites_path()
            return open_folder(fav_dir)
        except Exception as e:
            log_error(f"Error al abrir carpeta de favoritos: {str(e)}")
            return False

def add_favorite_by_date(date_str: str) -> bool:
    """
    Agrega un wallpaper a favoritos utilizando la fecha (date_str).
    Reutiliza la lógica de descarga y armado de información desde utils.wallpaper_utils.
    Retorna True si se agregó correctamente, False en caso contrario.
    """
    from utils.wallpaper_utils import build_wallpaper_info_by_date
    wallpaper_info = build_wallpaper_info_by_date(date_str)
    if wallpaper_info is None:
        return False
    if WallpaperFavorites.is_favorite(wallpaper_info):
        log_info(f"El wallpaper {date_str} ya está en favoritos.")
        return True
    return WallpaperFavorites.add_to_favorites(wallpaper_info)
