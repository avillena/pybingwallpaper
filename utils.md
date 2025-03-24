# logger.py
import logging
from pathlib import Path
from constants import Constants

class AppLogger:
    """Centraliza el logging de la aplicación."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Patrón singleton para obtener la instancia del logger."""
        if cls._instance is None:
            cls._instance = AppLogger()
        return cls._instance
    
    def __init__(self):
        """Inicializa el logger."""
        self.logger = logging.getLogger('PyBingWallpaper')
        self.logger.setLevel(logging.INFO)
        
        # Asegura que exista el directorio de logs
        log_file = Constants.get_log_file()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler(str(log_file))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Registra un mensaje informativo."""
        self.logger.info(message)
    
    def warning(self, message):
        """Registra una advertencia."""
        self.logger.warning(message)
    
    def error(self, message):
        """Registra un error."""
        self.logger.error(message)
    
    def debug(self, message):
        """Registra un mensaje de depuración."""
        self.logger.debug(message)

# Funciones de conveniencia
def get_logger():
    """Obtiene la instancia del logger."""
    return AppLogger.get_instance()

def log_info(message):
    """Registra un mensaje informativo."""
    get_logger().info(message)

def log_warning(message):
    """Registra una advertencia."""
    get_logger().warning(message)

def log_error(message):
    """Registra un error."""
    get_logger().error(message)

def log_debug(message):
    """Registra un mensaje de depuración."""
    get_logger().debug(message)


# file_utils.py
import json
import os
import shutil
from pathlib import Path
from logger import log_error, log_info

def ensure_directory(directory_path):
    """Asegura que un directorio exista, creándolo si es necesario."""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        log_error(f"Error al crear directorio {directory_path}: {str(e)}")
        return False

def read_json(file_path, default=None):
    """Lee y parsea un archivo JSON con manejo de errores."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_info(f"Archivo no encontrado: {file_path}, retornando valor por defecto")
        return default if default is not None else {}
    except json.JSONDecodeError:
        log_error(f"JSON inválido en archivo {file_path}, retornando valor por defecto")
        return default if default is not None else {}
    except Exception as e:
        log_error(f"Error al leer archivo JSON {file_path}: {str(e)}")
        return default if default is not None else {}

def write_json(file_path, data, indent=4):
    """Escribe datos en un archivo JSON con manejo de errores."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        log_error(f"Error al escribir archivo JSON {file_path}: {str(e)}")
        return False

def copy_file(source, destination):
    """Copia un archivo con manejo de errores."""
    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        log_error(f"Error al copiar archivo de {source} a {destination}: {str(e)}")
        return False

def delete_file(file_path):
    """Elimina un archivo con manejo de errores."""
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception as e:
        log_error(f"Error al eliminar archivo {file_path}: {str(e)}")
        return False

def file_exists(file_path):
    """Comprueba si un archivo existe."""
    return Path(file_path).exists()


# http_client.py
import requests
from pathlib import Path
from logger import log_error

def download_file(url, destination_path, chunk_size=8192):
    """
    Descarga un archivo desde una URL a una ruta local.
    
    Args:
        url: URL desde donde descargar
        destination_path: Ruta donde guardar el archivo
        chunk_size: Tamaño de los chunks para descarga en streaming
        
    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        return True
    except Exception as e:
        log_error(f"Error al descargar {url} a {destination_path}: {str(e)}")
        return False

def download_content(url):
    """
    Descarga contenido desde una URL.
    
    Args:
        url: URL desde donde descargar
        
    Returns:
        str o None: Contenido si la descarga fue exitosa, None en caso contrario
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log_error(f"Error al descargar contenido de {url}: {str(e)}")
        return None

def download_binary(url):
    """
    Descarga contenido binario desde una URL.
    
    Args:
        url: URL desde donde descargar
        
    Returns:
        bytes o None: Contenido binario si la descarga fue exitosa, None en caso contrario
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        log_error(f"Error al descargar binario de {url}: {str(e)}")
        return None


# ui_components.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import (QLabel, QPushButton, QCheckBox, 
                            QFrame, QGraphicsDropShadowEffect)
from constants import Constants

def apply_zoom(size, zoom_factor):
    """Aplica factor de zoom a un valor de tamaño."""
    return int(size * zoom_factor)

def create_label(text, font_size, bold=False, color=None, zoom_factor=1.0):
    """Crea un QLabel con estilo."""
    label = QLabel(text)
    
    # Aplicar estilo
    style = []
    
    # Tamaño de fuente con zoom
    zoomed_size = apply_zoom(font_size, zoom_factor)
    style.append(f"font-size: {zoomed_size}px")
    
    # Peso de fuente
    if bold:
        style.append("font-weight: bold")
    
    # Color del texto
    if color:
        style.append(f"color: {color}")
    
    # Aplicar estilo
    label.setStyleSheet("; ".join(style))
    
    return label

def create_button(text, font_size=None, icon=None, background=None, 
                 color="white", padding=None, border_radius=None, 
                 zoom_factor=1.0, hover_color=None):
    """Crea un QPushButton con estilo."""
    button = QPushButton(text)
    
    # Aplicar estilo
    style = []
    
    # Fondo
    if background:
        style.append(f"background-color: {background}")
    else:
        style.append("background-color: transparent")
    
    # Color del texto
    style.append(f"color: {color}")
    
    # Tamaño de fuente con zoom
    if font_size:
        zoomed_size = apply_zoom(font_size, zoom_factor)
        style.append(f"font-size: {zoomed_size}px")
    
    # Borde
    style.append("border: none")
    
    # Radio del borde
    if border_radius:
        zoomed_radius = apply_zoom(border_radius, zoom_factor)
        style.append(f"border-radius: {zoomed_radius}px")
    
    # Padding
    if padding:
        if isinstance(padding, tuple) and len(padding) == 2:
            # Padding vertical y horizontal
            v_padding = apply_zoom(padding[0], zoom_factor)
            h_padding = apply_zoom(padding[1], zoom_factor)
            style.append(f"padding: {v_padding}px {h_padding}px")
        else:
            # Padding uniforme
            p = apply_zoom(padding, zoom_factor)
            style.append(f"padding: {p}px")
    
    # Estado hover
    hover_style = []
    if hover_color:
        hover_style.append(f"background-color: {hover_color}")
    
    # Combinar estilos
    button_style = "; ".join(style)
    if hover_style:
        button_style += f"; QPushButton:hover {{ {'; '.join(hover_style)} }}"
    
    button.setStyleSheet(button_style)
    
    # Aplicar icono si se proporciona
    if icon:
        button.setIcon(QIcon(icon))
    
    return button

def create_container(border_radius=None, background=None, shadow=None, zoom_factor=1.0):
    """Crea un contenedor con estilo y sombra opcional."""
    container = QFrame()
    
    # Aplicar estilo
    style = []
    
    # Fondo
    if background:
        style.append(f"background-color: {background}")
    
    # Radio del borde
    if border_radius:
        zoomed_radius = apply_zoom(border_radius, zoom_factor)
        style.append(f"border-radius: {zoomed_radius}px")
    
    container.setStyleSheet("; ".join(style))
    
    # Aplicar sombra si se solicita
    if shadow and isinstance(shadow, dict):
        shadow_effect = QGraphicsDropShadowEffect()
        
        # Aplicar propiedades de sombra
        if 'blur' in shadow:
            shadow_effect.setBlurRadius(apply_zoom(shadow['blur'], zoom_factor))
        
        if 'color' in shadow:
            shadow_effect.setColor(shadow['color'])
        
        if 'offset' in shadow:
            offset = apply_zoom(shadow['offset'], zoom_factor)
            shadow_effect.setOffset(0, offset)
        
        container.setGraphicsEffect(shadow_effect)
    
    return container

def load_pixmap(image_path, width=None, height=None, keep_aspect_ratio=True, zoom_factor=1.0):
    """Carga y escala un pixmap."""
    pixmap = QPixmap(str(image_path))
    
    # Escalar si se proporcionan dimensiones
    if width or height:
        # Aplicar zoom
        if width:
            width = apply_zoom(width, zoom_factor)
        if height:
            height = apply_zoom(height, zoom_factor)
        
        # Escalar el pixmap
        if width and height:
            if keep_aspect_ratio:
                pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                pixmap = pixmap.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif width:
            pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
        elif height:
            pixmap = pixmap.scaledToHeight(height, Qt.SmoothTransformation)
    
    return pixmap


# navigation_controller.py
from PyQt5.QtCore import QObject, pyqtSignal
from constants import Constants
from logger import log_error, log_info
import http_client
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
        if not wallpaper_file.exists():
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
        if not file_path.exists() and source == self.SOURCE_BING:
            # Solo descarga para la fuente Bing
            if "picture_url" in wallpaper:
                log_info(f"Descargando wallpaper para índice {index}...")
                http_client.download_file(
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
                
                if not thumb_file.exists() and "thumbnail_url" in wallpaper:
                    log_info(f"Pre-descargando miniatura para índice {index}...")
                    http_client.download_file(
                        wallpaper["thumbnail_url"], 
                        thumb_file
                    )


# resource_utils.py
import os
import subprocess
import platform
from pathlib import Path
from logger import log_error

def open_url(url):
    """
    Abre una URL en el navegador web predeterminado.
    
    Args:
        url: URL a abrir
        
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        # Diferentes métodos según la plataforma
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(url)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', url], check=True)
        else:  # Linux y otros
            subprocess.run(['xdg-open', url], check=True)
        return True
    except Exception as e:
        log_error(f"Error al abrir URL {url}: {str(e)}")
        return False

def open_folder(folder_path):
    """
    Abre una carpeta en el explorador de archivos.
    
    Args:
        folder_path: Ruta a la carpeta
        
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        folder_path = Path(folder_path)
        if not folder_path.exists():
            return False
            
        # Diferentes métodos según la plataforma
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(folder_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux y otros
            subprocess.run(['xdg-open', folder_path], check=True)
        return True
    except Exception as e:
        log_error(f"Error al abrir carpeta {folder_path}: {str(e)}")
        return False