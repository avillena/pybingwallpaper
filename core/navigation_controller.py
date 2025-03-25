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
                return self.navigate_to_wallpaper(0, self.SOURCE_FAVORITE)
        else:  # En favoritos
            # Si podemos retroceder en la colección de favoritos
            if index < len(self.wallpaper_manager.favorites) - 1:
                return self.navigate_to_wallpaper(index + 1, source)
        
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
                return self.navigate_to_wallpaper(index - 1, source)
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