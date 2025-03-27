from PyQt5.QtCore import QObject, pyqtSignal
from constants import Constants
from utils.logger import log_error, log_info
from utils.http_client import download_file
from utils.file_utils import file_exists
from pathlib import Path

class NavigationController(QObject):
    """Controlador para navegar entre fondos de pantalla."""
    
    # Señales Qt para eventos
    wallpaper_changed = pyqtSignal(dict)  # Emitida cuando cambia el fondo
    
    # Constantes para fuentes de wallpapers
    SOURCE_BING = "bing"
    SOURCE_FAVORITE = "favorite"
    
    def __init__(self, wallpaper_manager):
        """Inicializa el controlador de navegación."""
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
    
    def navigate_to_wallpaper(self, index, source=None):
        """
        Navega a un wallpaper específico por índice y fuente.
        
        Args:
            index: Índice dentro de la colección (Bing o favoritos)
            source: Fuente del wallpaper (Bing o favorito)
            
        Returns:
            bool: True si la navegación fue exitosa, False en caso contrario
        """
        # Usa la fuente actual si no se proporciona
        if source is None:
            source = self.wallpaper_manager.current_source
        
        # Obtiene la colección apropiada
        if source == self.SOURCE_BING:
            collection = self.wallpaper_manager.wallpaper_history
            if not collection or index < 0 or index >= len(collection):
                return False
            
            wallpaper = collection[index]
            wallpaper_file = Constants.get_wallpaper_file(index)
        else:  # SOURCE_FAVORITE
            collection = self.wallpaper_manager.favorites
            if not collection or index < 0 or index >= len(collection):
                return False
            
            wallpaper = collection[index]
            wallpaper_file = Path(wallpaper.get("file_path", ""))
        
        # Verifica si el archivo existe o lo descarga si es necesario
        self._ensure_wallpaper_file(wallpaper_file, wallpaper, index, source)
        
        # Si el archivo aún no existe, la navegación falló
        if not file_exists(wallpaper_file):
            return False
        
        # Actualiza el estado
        self.wallpaper_manager.current_wallpaper_index = index
        self.wallpaper_manager.current_source = source
        self.wallpaper_manager.save_state()
        
        # Establece el fondo de pantalla
        self.wallpaper_manager.set_wallpaper(str(wallpaper_file))
        
        # Emite señal con info del wallpaper actual
        self.wallpaper_changed.emit(self.wallpaper_manager.get_current_wallpaper())
        
        return True
    
    def _is_favorite_duplicate(self, favorite_index):
        """
        Verifica si un favorito ya existe en la colección de Bing.
        
        Args:
            favorite_index: Índice del favorito a verificar
            
        Returns:
            bool: True si el favorito es un duplicado, False en caso contrario
        """
        # Validar que existe la colección y el índice
        if (not self.wallpaper_manager.favorites or 
            favorite_index < 0 or 
            favorite_index >= len(self.wallpaper_manager.favorites)):
            return False
            
        # Obtener el favorito a verificar
        favorite = self.wallpaper_manager.favorites[favorite_index]
        favorite_url = favorite.get("picture_url", "")
        
        if not favorite_url:
            return False
            
        # Buscar si existe la misma URL en la colección de Bing
        for bing_wallpaper in self.wallpaper_manager.wallpaper_history:
            if bing_wallpaper.get("picture_url", "") == favorite_url:
                return True
                
        return False
    
    def _find_next_non_duplicate_favorite(self, start_index, direction=1):
        """
        Encuentra el siguiente favorito que no sea duplicado de Bing.
        
        Args:
            start_index: Índice inicial para buscar
            direction: 1 para buscar hacia adelante, -1 para buscar hacia atrás
            
        Returns:
            int or None: Índice del siguiente favorito no duplicado, o None si no hay más
        """
        favorites = self.wallpaper_manager.favorites
        
        if not favorites:
            return None
            
        # Calcular límites
        end_index = len(favorites) if direction > 0 else -1
        
        # Buscar el siguiente favorito no duplicado
        current_index = start_index
        while current_index != end_index:
            if not self._is_favorite_duplicate(current_index):
                return current_index
            current_index += direction
            
        return None
    
    def navigate_to_previous(self):
        """
        Navega al wallpaper anterior (más antiguo).
        
        Returns:
            bool: True si la navegación fue exitosa, False en caso contrario
        """
        source = self.wallpaper_manager.current_source
        index = self.wallpaper_manager.current_wallpaper_index
        
        # Pre-descarga miniaturas para navegación más fluida
        self._preload_thumbnail(index + 1, source)
        
        # Intenta navegar primero dentro de la colección actual
        if source == self.SOURCE_BING:
            # Si podemos retroceder en la colección de Bing
            if index < len(self.wallpaper_manager.wallpaper_history) - 1:
                return self.navigate_to_wallpaper(index + 1, source)
            # Si estamos al final de la colección de Bing pero existen favoritos
            elif self.wallpaper_manager.favorites:
                # Buscar el primer favorito que no sea duplicado de Bing
                next_favorite_index = self._find_next_non_duplicate_favorite(0)
                if next_favorite_index is not None:
                    return self.navigate_to_wallpaper(next_favorite_index, self.SOURCE_FAVORITE)
        else:  # En favoritos
            # Si podemos retroceder en la colección de favoritos
            if index < len(self.wallpaper_manager.favorites) - 1:
                # Buscar el siguiente favorito que no sea duplicado
                next_favorite_index = self._find_next_non_duplicate_favorite(index + 1)
                if next_favorite_index is not None:
                    return self.navigate_to_wallpaper(next_favorite_index, source)
        
        # No se puede navegar más allá
        return False
    
    def navigate_to_next(self):
        """
        Navega al wallpaper siguiente (más reciente).
        
        Returns:
            bool: True si la navegación fue exitosa, False en caso contrario
        """
        source = self.wallpaper_manager.current_source
        index = self.wallpaper_manager.current_wallpaper_index
        
        # Pre-descarga miniaturas para navegación más fluida
        self._preload_thumbnail(index - 1, source)
        
        # Intenta navegar primero dentro de la colección actual
        if source == self.SOURCE_FAVORITE:
            # Si podemos avanzar en la colección de favoritos
            if index > 0:
                # Buscar el favorito anterior que no sea duplicado
                next_favorite_index = self._find_next_non_duplicate_favorite(index - 1, -1)
                if next_favorite_index is not None:
                    return self.navigate_to_wallpaper(next_favorite_index, source)
            # Si estamos al inicio de favoritos pero existe colección de Bing
            elif self.wallpaper_manager.wallpaper_history:
                return self.navigate_to_wallpaper(
                    len(self.wallpaper_manager.wallpaper_history) - 1, 
                    self.SOURCE_BING
                )
        else:  # En Bing
            # Si podemos avanzar en la colección de Bing
            if index > 0:
                return self.navigate_to_wallpaper(index - 1, source)
        
        # No se puede navegar más allá
        return False
    
    def _ensure_wallpaper_file(self, file_path, wallpaper, index, source):
        """Asegura que exista el archivo de wallpaper, descargándolo si es necesario."""
        if not file_exists(file_path) and source == self.SOURCE_BING:
            # Solo descarga para la fuente Bing
            if "picture_url" in wallpaper:
                log_info(f"Descargando wallpaper para índice {index}...")
                download_file(
                    wallpaper["picture_url"], 
                    file_path
                )
    
    def _preload_thumbnail(self, index, source):
        """Pre-descarga miniatura para navegación más fluida."""
        if source == self.SOURCE_BING and index >= 0:
            collection = self.wallpaper_manager.wallpaper_history
            if index < len(collection):
                wallpaper = collection[index]
                thumb_file = Constants.get_thumbnail_file(index)
                
                if not file_exists(thumb_file) and "thumbnail_url" in wallpaper:
                    log_info(f"Pre-descargando miniatura para índice {index}...")
                    download_file(
                        wallpaper["thumbnail_url"], 
                        thumb_file
                    )