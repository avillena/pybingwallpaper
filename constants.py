import os
from pathlib import Path

class Constants:
    """Centraliza las constantes de la aplicación."""
    
    # Información de la aplicación
    APP_NAME = "PyBingWallpaper"
    APP_VERSION = "1.0.0"
    APP_COPYRIGHT = "Copyright © Python Version 2025"
    
    # Constantes de UI
    class UI:
        # Colores y estilos
        BACKGROUND_COLOR = "#1C1C1C"
        TEXT_COLOR = "#FFFFFF"
        HIGHLIGHT_COLOR = "#3B78FF"
        LINK_COLOR = "#0066cc"
        HOVER_COLOR = "rgba(255, 255, 255, 0.1)"
        DISABLED_COLOR = "rgba(255, 255, 255, 0.3)"
        MENU_BG_COLOR = "#2C2C2C"
        MENU_BORDER_COLOR = "#3C3C3C"
        THUMB_BG_COLOR = "#111111"
        FAVORITE_COLOR = "#FFD700"  # Color dorado para favoritos
        FAVORITE_HOVER_COLOR = "#FFC125"  # Color cuando se pasa el cursor
        
        # Dimensiones y espaciado
        BORDER_RADIUS = 10
        SHADOW_BLUR = 20
        SHADOW_OFFSET = 2
        SHADOW_COLOR = (0, 0, 0, 180)  # RGBA
        MAIN_WIDTH = 600
        MAIN_HEIGHT = 360
        NAV_BASE_WIDTH = 370
        NAV_BASE_HEIGHT = 200
        MARGIN = 8
        BUTTON_SIZE = 20
        
        # Tamaños de fuente
        TITLE_FONT_SIZE = 24
        VERSION_FONT_SIZE = 14
        COPYRIGHT_FONT_SIZE = 11
        BING_TITLE_FONT_SIZE = 13
        BUTTON_FONT_SIZE = 14
        NAV_TITLE_FONT_SIZE = 14
        NAV_COPYRIGHT_FONT_SIZE = 10
        NAV_BUTTON_FONT_SIZE = 12
        MENU_FONT_SIZE = 12
        
        # Configuración de iconos y menús
        ICON_SIZE = 64
        ICON_B_LEFT = 15
        ICON_B_TOP = 10
        ICON_B_WIDTH = 10
        ICON_B_HEIGHT = 44
        ICON_BOW_WIDTH = 20
        ICON_BOW_HEIGHT = 10
        ICON_BOW_TOP1 = 10
        ICON_BOW_TOP2 = 22
        ICON_BOW_TOP3 = 34
        ICON_BG_COLOR = (0, 120, 212, 255)  # Azul de Bing
        ICON_FG_COLOR = (255, 255, 255, 255)  # Blanco
        
        MENU_BORDER_WIDTH = 1
        MENU_BORDER_RADIUS = 8
        MENU_PADDING = 5
        MENU_ITEM_PADDING_V = 5
        MENU_ITEM_PADDING_H = 20
        MENU_ITEM_BORDER_RADIUS = 4
        
        # Iconos y símbolos
        FAVORITE_ICON_ACTIVE = "★"   # Estrella llena
        FAVORITE_ICON_INACTIVE = "☆"  # Estrella vacía
        
        # Configuración de miniatura en navegador
        THUMB_WIDTH = 130
        THUMB_HEIGHT = 95
        
        # Posicionamiento del navegador
        TRAY_OFFSET_X = 20
        TRAY_OFFSET_Y = 60
        
        # Límite de caracteres para título
        TITLE_CHAR_LIMIT_FACTOR = 70
    
    # Constantes de red
    class Network:
        # Tamaño de chunk para descargar archivos (8KB)
        DOWNLOAD_CHUNK_SIZE = 8192
        
        # Tiempo de espera entre comprobaciones (segundos)
        CHECK_INTERVAL = 3600  # 1 hora
        SIGNAL_CHECK_INTERVAL = 1000  # 1 segundo (en milisegundos para QTimer)
        RETRY_INTERVAL = 60  # 1 minuto
        
        # Tiempo de espera para join de threads
        THREAD_JOIN_TIMEOUT = 1.0
    
    # Constantes de sistema de archivos
    class Files:
        # Número de días de historial a mantener
        HISTORY_DAYS = 7
        
        # Número de wallpapers completos a descargar
        MAX_FULL_WALLPAPERS_TO_DOWNLOAD = 3
        
        # Número de separadores para el log
        LOG_SEPARATOR_LENGTH = 40
        
        # Separador para el log
        LOG_SEPARATOR_CHAR = "="
    
    # Opciones de tamaño de zoom
    ZOOM_OPTIONS = [
        ("Pequeño", 1.0),
        ("Mediano", 1.3),
        ("Grande", 1.6),
        ("Muy grande", 2.0)
    ]
    
    # Factor de zoom predeterminado para la interfaz
    DEFAULT_ZOOM_FACTOR = 1.3
    
    # Constantes para Windows API
    class Windows:
        SPI_SETDESKWALLPAPER = 0x0014
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        WALLPAPER_STYLE_FIT = "10"  # 10 = Ajustar a pantalla
        WALLPAPER_TILE = "0"
        
        # Constantes para configuración del registro de Windows
        REGISTRY_RUN_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    @classmethod
    def get_data_path(cls):
        """Obtiene la ruta de datos de la aplicación."""
        data_path = Path(os.environ['APPDATA']) / cls.APP_NAME
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path
    
    @classmethod
    def get_wallpapers_path(cls):
        """Obtiene la ruta para almacenar los wallpapers."""
        wallpapers_path = cls.get_data_path() / "wallpapers"
        wallpapers_path.mkdir(exist_ok=True)
        return wallpapers_path
    
    @classmethod
    def get_favorites_path(cls):
        """Obtiene la ruta para almacenar los wallpapers favoritos."""
        favorites_path = cls.get_data_path() / "favorites"
        favorites_path.mkdir(exist_ok=True)
        return favorites_path
    
    @classmethod
    def get_state_file(cls):
        """Obtiene la ruta del archivo de estado."""
        return cls.get_data_path() / "state.json"
    
    @classmethod
    def get_wallpaper_file(cls, idx=0):
        """Obtiene la ruta del archivo de fondo de pantalla."""
        if idx == 0:
            return cls.get_wallpapers_path() / "current.jpg"
        else:
            return cls.get_wallpapers_path() / f"wallpaper_{idx}.jpg"
    
    @classmethod
    def get_thumbnail_file(cls, idx=0):
        """Obtiene la ruta del archivo de miniatura."""
        if idx == 0:
            return cls.get_wallpapers_path() / "current_thumb.jpg"
        else:
            return cls.get_wallpapers_path() / f"wallpaper_{idx}_thumb.jpg"
    
    @classmethod
    def get_log_file(cls):
        """Obtiene la ruta del archivo de log."""
        return cls.get_data_path() / "log.txt"
    
    @classmethod
    def get_lock_file(cls):
        """Obtiene la ruta del archivo de bloqueo para instancia única."""
        return cls.get_data_path() / "app.lock"
    
    @classmethod
    def get_show_signal_file(cls):
        """Obtiene la ruta del archivo de señal para mostrar la ventana."""
        return cls.get_data_path() / "show.signal"
    
    @classmethod
    def get_app_icon_file(cls):
        """Obtiene la ruta del archivo de icono de la aplicación."""
        return cls.get_data_path() / "app_icon.png"
    
    @staticmethod
    def get_wallpaper_info_url(idx=0, count=1):
        """Obtiene la URL de la información del fondo de pantalla."""
        return f"https://www.bing.com/HPImageArchive.aspx?format=xml&idx={idx}&n={count}&mkt=en-US"
    
    @staticmethod
    def get_picture_url_format():
        """Obtiene el formato de la URL de la imagen."""
        return "https://www.bing.com{0}_UHD.jpg"
        
    @staticmethod
    def get_thumbnail_url_format():
        """Obtiene el formato de la URL de la miniatura."""
        return "https://www.bing.com{0}_320x240.jpg"
    
    @staticmethod
    def get_bing_website_url():
        """Obtiene la URL del sitio web de Bing Wallpaper."""
        return "https://www.bing.com/wallpaper"