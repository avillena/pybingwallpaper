import os
import json
from pathlib import Path
from PyQt5.QtCore import QLocale

# Variable global para idioma actual
CURRENT_LANGUAGE = None

# Diccionarios de traducción
TRANSLATIONS = {
    'es': {},
    'en': {}
}

def get_system_language() -> str:
    """
    Detecta el idioma del sistema usando QLocale.
    Ejemplo: 'es_ES' o 'en_US'. Si empieza con "es", se retorna 'es'.
    """
    system_locale = QLocale.system().name()  # Ej: "es_ES", "en_US", etc.
    if system_locale.startswith("es"):
        return "es"
    return "en"

def get_data_path() -> Path:
    data_path = Path(os.environ['APPDATA']) / "PyBingWallpaper"
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

def get_translations_path() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__))) / "translations"

def get_current_language() -> str:
    global CURRENT_LANGUAGE
    
    if CURRENT_LANGUAGE is None:
        # Intentar leer la configuración guardada
        lang_file = get_data_path() / "language.json"
        if lang_file.exists():
            try:
                with open(lang_file, 'r') as f:
                    lang_data = json.load(f)
                    if "language" in lang_data:
                        CURRENT_LANGUAGE = lang_data["language"]
            except Exception:
                pass
        
        # Si no se estableció, usar el idioma del sistema
        if CURRENT_LANGUAGE is None:
            CURRENT_LANGUAGE = get_system_language()
    
    return CURRENT_LANGUAGE

def set_language(language_code: str) -> bool:
    global CURRENT_LANGUAGE
    
    if language_code in TRANSLATIONS:
        CURRENT_LANGUAGE = language_code
        lang_file = get_data_path() / "language.json"
        with open(lang_file, 'w') as f:
            json.dump({"language": language_code}, f)
        return True
    return False

def load_translations() -> None:
    base_path = get_translations_path()
    
    # Cargar traducciones españolas
    es_path = base_path / "translations_es.json"
    if es_path.exists():
        with open(es_path, 'r', encoding='utf-8') as f:
            TRANSLATIONS['es'] = json.load(f)
    
    # Cargar traducciones inglesas
    en_path = base_path / "translations_en.json"
    if en_path.exists():
        with open(en_path, 'r', encoding='utf-8') as f:
            TRANSLATIONS['en'] = json.load(f)

def tr(text: str, context: str = "Constants") -> str:
    """
    Función de traducción global. Construye la clave con el contexto y
    devuelve el texto traducido según el idioma actual.
    """
    key = f"{context}::{text}"
    language = get_current_language()
    if language in TRANSLATIONS and key in TRANSLATIONS[language]:
        return TRANSLATIONS[language][key]
    return text

# Definición de constantes dinámicas, evaluadas en tiempo de ejecución
class Constants:
    # Información de la aplicación
    APP_NAME = "PyBingWallpaper"
    APP_VERSION = "1.0.0"

    @staticmethod
    def get_app_copyright() -> str:
        return tr("Copyright © Python Version 2025", "Constants")
    
    # Constantes de UI agrupadas en una clase interna con getters dinámicos
    class UI:
        BACKGROUND_COLOR = "#1C1C1C"
        TEXT_COLOR = "#FFFFFF"
        HIGHLIGHT_COLOR = "#3B78FF"
        LINK_COLOR = "#0066cc"
        HOVER_COLOR = "rgba(255, 255, 255, 0.1)"
        DISABLED_COLOR = "rgba(255, 255, 255, 0.3)"
        MENU_BG_COLOR = "#2C2C2C"
        MENU_BORDER_COLOR = "#3C3C3C"
        THUMB_BG_COLOR = "#111111"
        FAVORITE_COLOR = "#FFD700"   # Dorado para favoritos
        FAVORITE_HOVER_COLOR = "#FFC125"
        
        BORDER_RADIUS = 10
        SHADOW_BLUR = 20
        SHADOW_OFFSET = 2
        SHADOW_COLOR = (0, 0, 0, 180)
        MAIN_WIDTH = 600
        MAIN_HEIGHT = 360
        NAV_BASE_WIDTH = 370
        NAV_BASE_HEIGHT = 200
        MARGIN = 8
        BUTTON_SIZE = 20
        
        TITLE_FONT_SIZE = 24
        VERSION_FONT_SIZE = 14
        COPYRIGHT_FONT_SIZE = 11
        BING_TITLE_FONT_SIZE = 13
        BUTTON_FONT_SIZE = 14
        NAV_TITLE_FONT_SIZE = 14
        NAV_COPYRIGHT_FONT_SIZE = 10
        NAV_BUTTON_FONT_SIZE = 12
        MENU_FONT_SIZE = 12
        
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
        ICON_BG_COLOR = (0, 120, 212, 255)
        ICON_FG_COLOR = (255, 255, 255, 255)
        
        MENU_BORDER_WIDTH = 1
        MENU_BORDER_RADIUS = 8
        MENU_PADDING = 5
        MENU_ITEM_PADDING_V = 5
        MENU_ITEM_PADDING_H = 20
        MENU_ITEM_BORDER_RADIUS = 4
        
        THUMB_WIDTH = 130
        THUMB_HEIGHT = 95
        
        TRAY_OFFSET_X = 20
        TRAY_OFFSET_Y = 60
        
        TITLE_CHAR_LIMIT_FACTOR = 70

        @staticmethod
        def get_main_window_title() -> str:
            return tr("Python Bing Wallpaper Client", "Constants")
        
        @staticmethod
        def get_minimize_button_text() -> str:
            return tr("−", "Constants")
        
        @staticmethod
        def get_share_button_text() -> str:
            return tr("⤴", "Constants")
        
        @staticmethod
        def get_settings_button_text() -> str:
            return tr("⚙", "Constants")
        
        @staticmethod
        def get_previous_button_text() -> str:
            return tr("⟨ Anterior", "Constants")
        
        @staticmethod
        def get_next_button_text() -> str:
            return tr("Siguiente ⟩", "Constants")
        
        @staticmethod
        def get_loading_text() -> str:
            return tr("Cargando...", "Constants")
        
        @staticmethod
        def get_downloading_image_text() -> str:
            return tr("Descargando imagen de Bing...", "Constants")
        
        @staticmethod
        def get_downloading_thumbnail_text() -> str:
            return tr("Descargando miniatura...", "Constants")
        
        @staticmethod
        def get_wait_message_text() -> str:
            return tr("Por favor espere mientras se obtienen los datos iniciales", "Constants")
        
        @staticmethod
        def get_image_not_available_text() -> str:
            return tr("Imagen no disponible", "Constants")
        
        @staticmethod
        def get_load_error_text() -> str:
            return tr("No se pudo cargar la imagen", "Constants")
        
        @staticmethod
        def get_download_error_text() -> str:
            return tr("Error al descargar", "Constants")
        
        @staticmethod
        def get_untitled_text() -> str:
            return tr("Sin título disponible", "Constants")
        
        @staticmethod
        def get_startup_menu_item_text() -> str:
            return tr("Iniciar con Windows", "Constants")
        
        @staticmethod
        def get_size_menu_title() -> str:
            return tr("Ajustar tamaño", "Constants")
        
        @staticmethod
        def get_language_menu_title() -> str:
            return tr("Idioma", "Constants")
        
        @staticmethod
        def get_open_favorites_menu_item_text() -> str:
            return tr("Abrir carpeta de favoritos", "Constants")
        
        @staticmethod
        def get_exit_menu_item_text() -> str:
            return tr("Salir de la aplicación", "Constants")
        
        @staticmethod
        def get_language_spanish_text() -> str:
            return tr("Español", "Constants")
        
        @staticmethod
        def get_language_english_text() -> str:
            return tr("Inglés", "Constants")
        
        @staticmethod
        def get_language_system_text() -> str:
            return tr("Usar idioma del sistema", "Constants")
        
        @staticmethod
        def get_language_change_title() -> str:
            return tr("Cambio de idioma", "Constants")
        
        @staticmethod
        def get_language_change_message() -> str:
            return tr("El cambio de idioma se aplicará al reiniciar la aplicación.", "Constants")
        
        @staticmethod
        def get_language_system_title() -> str:
            return tr("Idioma del sistema", "Constants")
        
        @staticmethod
        def get_language_system_message() -> str:
            return tr("Se usará el idioma del sistema al reiniciar la aplicación.", "Constants")
        
        @staticmethod
        def get_size_small_text() -> str:
            return tr("Pequeño", "Constants")
        
        @staticmethod
        def get_size_medium_text() -> str:
            return tr("Mediano", "Constants")
        
        @staticmethod
        def get_size_large_text() -> str:
            return tr("Grande", "Constants")
        
        @staticmethod
        def get_size_xlarge_text() -> str:
            return tr("Muy grande", "Constants")
        
        @staticmethod
        def get_error_load_wallpaper_text() -> str:
            return tr("No se pudo cargar el wallpaper", "Constants")
        
        @staticmethod
        def get_error_try_later_text() -> str:
            return tr("Intente más tarde o reinicie la aplicación", "Constants")
        
        @staticmethod
        def get_error_url_open_text() -> str:
            return tr("Fallo al abrir URL", "Constants")
        
        @staticmethod
        def get_error_url_open_detail_text() -> str:
            return tr("Error al abrir URL: {0}", "Constants")
        
        @staticmethod
        def get_no_url_available_text() -> str:
            return tr("No hay URL de imagen disponible", "Constants")
        
        @staticmethod
        def get_open_url_info_text() -> str:
            return tr("Abriendo URL de imagen: {0}", "Constants")
        
        @staticmethod
        def get_share_button_pressed_text() -> str:
            return tr("Botón compartir presionado", "Constants")
        
        ZOOM_OPTIONS = [
            (tr("Pequeño", "Constants"), 1.0),
            (tr("Mediano", "Constants"), 1.3),
            (tr("Grande", "Constants"), 1.6),
            (tr("Muy grande", "Constants"), 2.0)
        ]
        
        DEFAULT_ZOOM_FACTOR = 1.3
    
    class Network:
        DOWNLOAD_CHUNK_SIZE = 8192
        CHECK_INTERVAL = 3600
        SIGNAL_CHECK_INTERVAL = 1000
        RETRY_INTERVAL = 60
    
    class Files:
        HISTORY_DAYS = 7
        MAX_FULL_WALLPAPERS_TO_DOWNLOAD = 3
        LOG_SEPARATOR_LENGTH = 40
        LOG_SEPARATOR_CHAR = "="
    
    ZOOM_OPTIONS = [
        (tr("Pequeño", "Constants"), 1.0),
        (tr("Mediano", "Constants"), 1.3),
        (tr("Grande", "Constants"), 1.6),
        (tr("Muy grande", "Constants"), 2.0)
    ]
    
    DEFAULT_ZOOM_FACTOR = 1.3
    
    class Windows:
        SPI_SETDESKWALLPAPER = 0x0014
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        WALLPAPER_STYLE_FIT = "10"  # Ajustar a pantalla
        WALLPAPER_TILE = "0"
        REGISTRY_RUN_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    @classmethod
    def get_data_path(cls) -> Path:
        return get_data_path()
    
    @classmethod
    def get_wallpapers_path(cls) -> Path:
        wallpapers_path = cls.get_data_path() / "wallpapers"
        wallpapers_path.mkdir(exist_ok=True)
        return wallpapers_path
    
    @classmethod
    def get_favorites_path(cls) -> Path:
        favorites_path = cls.get_data_path() / "favorites"
        favorites_path.mkdir(exist_ok=True)
        return favorites_path
    
    @classmethod
    def get_state_file(cls) -> Path:
        return cls.get_data_path() / "state.json"
    
    @classmethod
    def get_wallpaper_file(cls, idx: int = 0) -> Path:
        if idx == 0:
            return cls.get_wallpapers_path() / "current.jpg"
        else:
            return cls.get_wallpapers_path() / f"wallpaper_{idx}.jpg"
    
    @classmethod
    def get_thumbnail_file(cls, idx: int = 0) -> Path:
        if idx == 0:
            return cls.get_wallpapers_path() / "current_thumb.jpg"
        else:
            return cls.get_wallpapers_path() / f"wallpaper_{idx}_thumb.jpg"
    
    @classmethod
    def get_log_file(cls) -> Path:
        return cls.get_data_path() / "log.txt"
    
    @classmethod
    def get_lock_file(cls) -> Path:
        return cls.get_data_path() / "app.lock"
    
    @classmethod
    def get_show_signal_file(cls) -> Path:
        return cls.get_data_path() / "show.signal"
    
    @classmethod
    def get_app_icon_file(cls) -> Path:
        return cls.get_data_path() / "app_icon.png"
    
    @staticmethod
    def get_wallpaper_info_url(idx: int = 0, count: int = 1) -> str:
        return f"https://www.bing.com/HPImageArchive.aspx?format=xml&idx={idx}&n={count}&mkt=en-US"
        
    @staticmethod
    def get_picture_url_format() -> str:
        return "https://www.bing.com{0}_UHD.jpg"
        
    @staticmethod
    def get_thumbnail_url_format() -> str:
        return "https://www.bing.com{0}_320x240.jpg"
    
    @staticmethod
    def get_bing_website_url() -> str:
        return "https://www.bing.com/wallpaper"
    
    @staticmethod
    def get_translations_path() -> Path:
        return get_translations_path()

# Cargar traducciones al importar el módulo
load_translations()
