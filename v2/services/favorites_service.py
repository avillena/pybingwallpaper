import json
import os
import random
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from models.wallpaper import Wallpaper, Country, Language

# Constantes
DEFAULT_APP_DATA_DIR = "app_data"
FAVORITES_FILENAME = "favorites.json"
CACHE_DIR_NAME = "cache"
FAVORITES_DIR_NAME = "favorites"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DEFAULT_CACHE_DAYS = 30

class FavoritesService:
    """
    Servicio para gestionar los wallpapers favoritos.
    
    Utiliza almacenamiento JSON para la persistencia de datos.
    """
    
    def __init__(self, base_dir: str = DEFAULT_APP_DATA_DIR):
        """
        Inicializa el servicio de favoritos.
        
        Args:
            base_dir: Directorio base para almacenar datos
        """
        self.base_dir = os.path.abspath(base_dir)
        self.favorites_file = os.path.join(self.base_dir, FAVORITES_FILENAME)
        self.favorites_dir = os.path.join(self.base_dir, FAVORITES_DIR_NAME)
        self.cache_dir = os.path.join(self.base_dir, CACHE_DIR_NAME)
        
        # Asegurar que existan los directorios
        os.makedirs(self.favorites_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cargar favoritos desde JSON
        self._favorites = self._load_favorites()
        
    def _load_favorites(self) -> List[Dict[str, Any]]:
        """
        Carga los favoritos desde el archivo JSON.
        
        Returns:
            Lista de favoritos en formato diccionario
        """
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('favorites', [])
            return []
        except json.JSONDecodeError:
            # Archivo corrupto - crear backup y retornar lista vacía
            if os.path.exists(self.favorites_file):
                backup = f"{self.favorites_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy2(self.favorites_file, backup)
            return []
        
    def _save_favorites(self) -> bool:
        """
        Guarda los favoritos en el archivo JSON.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            data = {
                'favorites': self._favorites,
                'last_update': datetime.now().strftime(DATETIME_FORMAT)
            }
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_wallpaper_path(self, country: Country, language: Language, date: str, 
                          is_favorite: bool = False) -> str:
        """
        Construye la ruta a un archivo de wallpaper.
        
        Args:
            country: País del wallpaper
            language: Idioma del wallpaper
            date: Fecha del wallpaper en formato YYYY-MM-DD
            is_favorite: Si es True, usa el directorio de favoritos, sino el de caché
            
        Returns:
            Ruta completa al archivo
        """
        # Convertir YYYY-MM-DD a YYYYMMDD para el nombre de archivo
        date_parts = date.split('-')
        if len(date_parts) == 3:
            filename = f"{''.join(date_parts)}.jpg"
        else:
            filename = f"{date}.jpg"
            
        base = self.favorites_dir if is_favorite else self.cache_dir
        return os.path.join(base, country.value, language.value, filename)
    
    def add_favorite(self, wallpaper: Wallpaper) -> bool:
        """
        Añade un wallpaper a favoritos.
        
        Args:
            wallpaper: Objeto Wallpaper a añadir
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        # Verificar si ya existe
        country, language, date = wallpaper.country, wallpaper.language, wallpaper.date
        if self.is_favorite(country, language, date):
            return True  # Ya existe, no hacer nada
            
        # Preparar diccionario para JSON
        wallpaper_dict = wallpaper.to_dict()
        wallpaper_dict['added_date'] = datetime.now().strftime(DATETIME_FORMAT)
            
        # Asegurar que existe el directorio de destino
        dest_path = self.get_wallpaper_path(country, language, date, is_favorite=True)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Si está en caché, mover a favoritos; si no, debe descargarse
        cache_path = self.get_wallpaper_path(country, language, date, is_favorite=False)
        
        if os.path.exists(cache_path):
            # Copiar archivo (no mover, para mantener en caché también)
            shutil.copy2(cache_path, dest_path)
        elif os.path.exists(wallpaper.file_path):
            # Copiar desde la ubicación original
            shutil.copy2(wallpaper.file_path, dest_path)
        
        # Actualizar wallpaper_dict con la nueva ruta
        wallpaper_dict['file_path'] = dest_path
        
        # Agregar a favoritos y guardar
        self._favorites.append(wallpaper_dict)
        return self._save_favorites()
    
    def remove_favorite(self, country: Country, language: Language, date: str) -> bool:
        """
        Elimina un wallpaper de favoritos.
        
        Args:
            country: País del wallpaper
            language: Idioma del wallpaper
            date: Fecha del wallpaper
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # Filtrar favoritos
        initial_count = len(self._favorites)
        self._favorites = [
            f for f in self._favorites 
            if not (f['country'] == country.value and 
                   f['language'] == language.value and 
                   f['date'] == date)
        ]
        
        # Si se eliminó al menos uno, guardar
        if len(self._favorites) < initial_count:
            return self._save_favorites()
        return False
    
    def is_favorite(self, country: Country, language: Language, date: str) -> bool:
        """
        Verifica si un wallpaper está en favoritos.
        
        Args:
            country: País del wallpaper
            language: Idioma del wallpaper
            date: Fecha del wallpaper
            
        Returns:
            True si está en favoritos, False en caso contrario
        """
        return any(
            f['country'] == country.value and 
            f['language'] == language.value and 
            f['date'] == date 
            for f in self._favorites
        )
    
    def get_random_favorite(self) -> Optional[Wallpaper]:
        """
        Obtiene un wallpaper aleatorio de favoritos.
        
        Returns:
            Objeto Wallpaper aleatorio o None si no hay favoritos
        """
        if not self._favorites:
            return None
        
        fav = random.choice(self._favorites)
        
        # Verificar que el archivo existe
        file_path = fav['file_path']
        if not os.path.exists(file_path):
            # Si no existe, intentar la ruta construida
            file_path = self.get_wallpaper_path(
                Country(fav['country']),
                Language(fav['language']),
                fav['date'],
                is_favorite=True
            )
        
        # Convertir diccionario a objeto Wallpaper
        return Wallpaper(
            country=Country(fav['country']),
            language=Language(fav['language']),
            date=fav['date'],
            title=fav['title'],
            description=fav['description'],
            url=f"https://bing.npanuhin.me/{fav['country']}/{fav['language']}/{fav['date']}.jpg",
            file_path=file_path,
            added_date=fav.get('added_date'),
            custom_name=fav.get('custom_name')
        )
    
    def get_all_favorites(self) -> List[Wallpaper]:
        """
        Obtiene todos los wallpapers favoritos.
        
        Returns:
            Lista de objetos Wallpaper
        """
        return [
            Wallpaper(
                country=Country(f['country']),
                language=Language(f['language']),
                date=f['date'],
                title=f['title'],
                description=f['description'],
                url=f"https://bing.npanuhin.me/{f['country']}/{f['language']}/{f['date']}.jpg",
                file_path=f['file_path'],
                added_date=f.get('added_date'),
                custom_name=f.get('custom_name')
            ) for f in self._favorites
        ]
    
    def clean_cache(self, days_to_keep: int = DEFAULT_CACHE_DAYS) -> int:
        """
        Elimina archivos de caché más antiguos que days_to_keep.
        No elimina los que están en favoritos.
        
        Args:
            days_to_keep: Número de días a mantener en caché
            
        Returns:
            Número de archivos eliminados
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        count_removed = 0
        
        # Recorrer directorios de caché
        for country_dir in os.listdir(self.cache_dir):
            country_path = os.path.join(self.cache_dir, country_dir)
            if not os.path.isdir(country_path):
                continue
                
            for lang_dir in os.listdir(country_path):
                lang_path = os.path.join(country_path, lang_dir)
                if not os.path.isdir(lang_path):
                    continue
                    
                for file_name in os.listdir(lang_path):
                    if not file_name.endswith('.jpg'):
                        continue
                        
                    # Extraer fecha del nombre de archivo (formato yyyymmdd.jpg)
                    try:
                        date_str = os.path.splitext(file_name)[0]
                        # Convertir yyyymmdd a yyyy-mm-dd para comparar
                        if len(date_str) == 8:
                            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                            file_date = datetime.strptime(formatted_date, DATE_FORMAT)
                            
                            if file_date.date() < cutoff_date.date():
                                # Verificar si es favorito
                                is_fav = self.is_favorite(
                                    Country(country_dir), 
                                    Language(lang_dir), 
                                    formatted_date
                                )
                                
                                if not is_fav:
                                    # Eliminar archivo
                                    os.remove(os.path.join(lang_path, file_name))
                                    count_removed += 1
                    except (ValueError, IndexError):
                        # Formato de fecha inválido, ignorar
                        pass
        
        return count_removed
