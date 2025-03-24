## File: wallpaper_favorites.py
import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from constants import Constants

class WallpaperFavorites:
    """Gestiona los fondos de pantalla favoritos."""
    
    @staticmethod
    def get_favorites_file():
        """Obtiene la ruta del archivo con metadatos de favoritos."""
        return Constants.get_data_path() / "favorites.json"
    
    @staticmethod
    def load_favorites_data():
        """Carga los datos de favoritos desde el archivo JSON."""
        favorites_file = WallpaperFavorites.get_favorites_file()
        if favorites_file.exists():
            try:
                with open(favorites_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar favoritos: {str(e)}")
        
        return {"favorites": []}
    
    @staticmethod
    def save_favorites_data(data):
        """Guarda los datos de favoritos en el archivo JSON."""
        try:
            favorites_file = WallpaperFavorites.get_favorites_file()
            with open(favorites_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar favoritos: {str(e)}")
            return False
    
    @staticmethod
    def add_to_favorites(wallpaper_info):
        """
        Agrega un wallpaper a favoritos.
        
        Args:
            wallpaper_info: Diccionario con información del wallpaper.
                Debe contener al menos 'picture_url', 'copyright' y el índice actual.
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario.
        """
        try:
            # Obtener la ruta del wallpaper original
            idx = wallpaper_info.get("current_index", 0)
            source_file = Constants.get_wallpaper_file(idx)
            
            if not source_file.exists():
                print(f"El archivo {source_file} no existe")
                return False
            
            # Generar un nombre único para el archivo favorito
            timestamp = int(datetime.now().timestamp())
            favorite_filename = f"favorite_{timestamp}{source_file.suffix}"
            target_path = Constants.get_favorites_path() / favorite_filename
            
            # Copiar el archivo
            shutil.copy2(source_file, target_path)
            
            # Crear registro de favorito con metadatos
            favorite_entry = {
                "id": str(timestamp),
                "picture_url": wallpaper_info.get("picture_url", ""),
                "thumbnail_url": wallpaper_info.get("thumbnail_url", ""),
                "copyright": wallpaper_info.get("copyright", "Sin título"),
                "date": wallpaper_info.get("date", datetime.now().strftime("%Y-%m-%d")),
                "file_path": str(target_path),
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "favorite"  # Marca para identificar que es un favorito
            }
            
            # Añadir a la lista de favoritos
            favorites_data = WallpaperFavorites.load_favorites_data()
            favorites_data["favorites"].append(favorite_entry)
            WallpaperFavorites.save_favorites_data(favorites_data)
            
            return True
        except Exception as e:
            print(f"Error al agregar a favoritos: {str(e)}")
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
            
            # Buscar el favorito por ID
            for i, favorite in enumerate(favorites_data["favorites"]):
                if favorite.get("id") == favorite_id:
                    # Eliminar el archivo
                    file_path = Path(favorite.get("file_path", ""))
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Eliminar de la lista
                    favorites_data["favorites"].pop(i)
                    WallpaperFavorites.save_favorites_data(favorites_data)
                    return True
            
            return False
        except Exception as e:
            print(f"Error al eliminar de favoritos: {str(e)}")
            return False
    
    @staticmethod
    def is_favorite(wallpaper_info):
        """
        Verifica si un wallpaper está en favoritos.
        
        Args:
            wallpaper_info: Diccionario con información del wallpaper.
                Debe contener al menos 'picture_url'.
            
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
            
            # Buscar por URL
            for favorite in favorites_data["favorites"]:
                if favorite.get("picture_url") == picture_url:
                    return favorite.get("id")
            
            return None
        except Exception as e:
            print(f"Error al verificar favorito: {str(e)}")
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
            print(f"Error al obtener lista de favoritos: {str(e)}")
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
            
            # En Windows
            if os.name == 'nt':
                os.startfile(fav_dir)
            # En MacOS
            elif os.name == 'posix' and hasattr(os, 'uname') and os.uname().sysname == 'Darwin':
                subprocess.call(['open', fav_dir])
            # En Linux
            elif os.name == 'posix':
                subprocess.call(['xdg-open', fav_dir])
            else:
                return False
                
            return True
        except Exception as e:
            print(f"Error al abrir carpeta de favoritos: {str(e)}")
            return False

