import os
from pathlib import Path

class Constants:
    """Centraliza las constantes de la aplicación."""
    APP_NAME = "BingWallpaper"
    APP_VERSION = "1.0.0"
    APP_COPYRIGHT = "Copyright © Python Version 2025"
    
    # Colores y estilos
    BACKGROUND_COLOR = "#1C1C1C"
    TEXT_COLOR = "#FFFFFF"
    HIGHLIGHT_COLOR = "#3B78FF"
    
    # Opciones de tamaño de zoom
    ZOOM_OPTIONS = [
        ("Pequeño", 1.0),
        ("Mediano", 1.3),
        ("Grande", 1.6),
        ("Muy grande", 2.0)
    ]
    
    # Factor de zoom predeterminado para la interfaz
    DEFAULT_ZOOM_FACTOR = 1.3
    
    # Tiempo de espera entre comprobaciones (segundos)
    CHECK_INTERVAL = 3600  # 1 hora
    SIGNAL_CHECK_INTERVAL = 1000  # 1 segundo (en milisegundos para QTimer)
    RETRY_INTERVAL = 60  # 1 minuto
    
    # Número de días de historial a mantener
    HISTORY_DAYS = 7
    
    # Parámetros de UI
    UI_BORDER_RADIUS = 10
    UI_SHADOW_BLUR = 20
    UI_SHADOW_OFFSET = 2
    UI_SHADOW_COLOR = (0, 0, 0, 180)  # RGBA
    UI_MAIN_WIDTH = 600
    UI_MAIN_HEIGHT = 360
    UI_NAV_BASE_WIDTH = 370
    UI_NAV_BASE_HEIGHT = 200
    UI_MARGIN = 8
    UI_BUTTON_SIZE = 20
    
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
        """Obtiene la ruta del archivo de fondo de pantalla.
        
        Args:
            idx: Índice del día (0 = hoy, 1 = ayer, etc.)
        """
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
        """Obtiene la URL de la información del fondo de pantalla.
        
        Args:
            idx: Índice del día (0 = hoy, 1 = ayer, etc.)
            count: Número de imágenes a obtener
        """
        # Parámetros: idx=0 (último día), n=1 (1 imagen), mkt=en-US (mercado en inglés)
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
    
    # Constantes para configuración del registro de Windows
    REGISTRY_RUN_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    # Parámetros de Windows API
    WIN_SPI_SETDESKWALLPAPER = 0x0014
    WIN_SPIF_UPDATEINIFILE = 0x01
    WIN_SPIF_SENDCHANGE = 0x02
    WIN_WALLPAPER_STYLE_FIT = "10"  # 10 = Ajustar a pantalla
    WIN_WALLPAPER_TILE = "0"