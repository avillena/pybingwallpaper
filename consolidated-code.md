## File: constants.py
```python
import os
from pathlib import Path

class Constants:
    """Centraliza las constantes de la aplicación."""
    APP_NAME = "PyBingWallpaper"
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
```

## File: run_windows_startup.py
```python
import os
import sys
import winreg
from constants import Constants

class StartupManager:
    """Gestiona la configuración de inicio con Windows."""
    
    @staticmethod
    def get_run_on_startup():
        """Comprueba si la aplicación está configurada para iniciarse con Windows."""
        try:
            # Abre la clave del registro
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Constants.REGISTRY_RUN_PATH,
                0, winreg.KEY_READ
            )
            
            # Intenta leer el valor
            try:
                value, _ = winreg.QueryValueEx(key, Constants.APP_NAME)
                winreg.CloseKey(key)
                
                # Verifica que el comando coincida con el comando esperado
                expected_cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" /background'
                return value == expected_cmd
            except Exception:
                winreg.CloseKey(key)
                return False
                
        except Exception:
            return False
    
    @staticmethod
    def set_run_on_startup(enable):
        """Configura si la aplicación debe iniciarse con Windows."""
        try:
            # Abre la clave del registro con permisos de escritura
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Constants.REGISTRY_RUN_PATH,
                0, winreg.KEY_WRITE
            )
            
            if enable:
                # Define el comando para ejecutar al inicio
                # Usa sys.executable para obtener la ruta del intérprete de Python
                # y sys.argv[0] para obtener la ruta del script actual
                cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" /background'
                winreg.SetValueEx(key, Constants.APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                # Elimina la entrada del registro
                try:
                    winreg.DeleteValue(key, Constants.APP_NAME)
                except Exception:
                    pass  # Si no existe, simplemente ignoramos el error
                    
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error al configurar el inicio automático: {str(e)}")
            return False
```

## File: wallpaper_favorites.py
```python
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
```

## File: bing_wallpaper_service.py
```python
import os
import json
import time
import ctypes
import winreg
import threading
import requests
import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from constants import Constants
from wallpaper_favorites import WallpaperFavorites

# Constantes locales del servicio
class WallpaperServiceConstants:
    """Constantes específicas para el servicio de wallpaper."""
    # Tamaño de chunk para descargar archivos (8KB)
    DOWNLOAD_CHUNK_SIZE = 8192
    
    # Número de días anteriores para descargar wallpapers completos
    MAX_FULL_WALLPAPERS_TO_DOWNLOAD = 3
    
    # Número de separadores para el log
    LOG_SEPARATOR_LENGTH = 40
    
    # Separador para el log
    LOG_SEPARATOR_CHAR = "="
    
    # Fuentes de wallpapers
    SOURCE_BING = "bing"
    SOURCE_FAVORITE = "favorite"

class WallpaperManager:
    """Gestiona la descarga y actualización del fondo de pantalla."""
    
    def __init__(self):
        """Inicializa el gestor de fondos de pantalla."""
        self.state = self.load_state()
        self.zoom_factor = self.state.get("zoom_factor", Constants.DEFAULT_ZOOM_FACTOR)
        self.download_completed_callbacks = []
        self.wallpaper_changed_callbacks = []
        self.zoom_changed_callbacks = []
        self.running = False
        self.thread = None
        self.wallpaper_history = []
        self.favorites = []
        self.current_wallpaper_index = 0
        self.current_source = WallpaperServiceConstants.SOURCE_BING  # Por defecto, fuente Bing
        
        # Carga inicialmente hasta 7 días de wallpapers en segundo plano
        threading.Thread(target=self.load_wallpaper_history, daemon=True).start()
        
        # Carga los favoritos
        self.load_favorites()
    
    def add_download_completed_callback(self, callback):
        """Agrega un callback para cuando se completa la descarga."""
        self.download_completed_callbacks.append(callback)
    
    def add_wallpaper_changed_callback(self, callback):
        """Agrega un callback para cuando cambia el fondo de pantalla."""
        self.wallpaper_changed_callbacks.append(callback)
    
    def add_zoom_changed_callback(self, callback):
        """Agrega un callback para cuando cambia el zoom."""
        self.zoom_changed_callbacks.append(callback)
    
    def load_state(self):
        """Carga el estado desde el archivo."""
        state_file = Constants.get_state_file()
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                self.log_error("Error al cargar el archivo de estado")
        
        # Estado por defecto
        return {
            "picture_url": "",
            "picture_file_path": "",
            "copyright": "",
            "history": [],
            "current_source": WallpaperServiceConstants.SOURCE_BING,
            "current_index": 0,
            "zoom_factor": Constants.DEFAULT_ZOOM_FACTOR
        }
    
    def save_state(self):
        """Guarda el estado en un archivo."""
        try:
            self.state["history"] = self.wallpaper_history
            self.state["current_source"] = self.current_source
            self.state["current_index"] = self.current_wallpaper_index
            self.state["zoom_factor"] = self.zoom_factor
            with open(Constants.get_state_file(), 'w') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            self.log_error(f"Error al guardar el estado: {str(e)}")
    
    def log_error(self, message):
        """Registra un error en el archivo de log."""
        try:
            with open(Constants.get_log_file(), 'a') as f:
                f.write(WallpaperServiceConstants.LOG_SEPARATOR_CHAR * WallpaperServiceConstants.LOG_SEPARATOR_LENGTH + "\n")
                f.write(f"{datetime.datetime.now()}\n")
                f.write(WallpaperServiceConstants.LOG_SEPARATOR_CHAR * WallpaperServiceConstants.LOG_SEPARATOR_LENGTH + "\n")
                f.write(message + "\n\n")
        except Exception:
            pass  # Si no podemos escribir en el log, simplemente continuamos
    
    def get_zoom_factor(self):
        """Obtiene el factor de zoom actual."""
        return self.zoom_factor
    
    def set_zoom_factor(self, zoom_factor):
        """Establece un nuevo factor de zoom y notifica a los interesados."""
        if self.zoom_factor != zoom_factor:
            self.zoom_factor = zoom_factor
            self.save_state()
            
            # Notificar a los callbacks sobre el cambio de zoom
            for callback in self.zoom_changed_callbacks:
                callback(zoom_factor)
            
            return True
        return False
        
    def start(self):
        """Inicia el proceso de actualización del fondo de pantalla."""
        if self.thread and self.thread.is_alive():
            return  # Ya está en ejecución
        
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Detiene el proceso de actualización."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def run(self):
        """Ejecuta el bucle principal de actualización."""
        first_time = True
        
        while self.running:
            try:
                # Obtiene información de la imagen desde Bing
                xml_content = requests.get(Constants.get_wallpaper_info_url()).text
                info = self.parse_wallpaper_info(xml_content)
                
                # Si hay una nueva imagen o no hay imagen establecida, la descarga
                if info["picture_url"] != self.state["picture_url"] or not Path(self.state["picture_file_path"]).exists():
                    self.download_wallpaper(info)
                elif first_time:
                    # Si no hay imagen nueva pero es la primera ejecución, establece la imagen actual
                    self.set_wallpaper(self.state["picture_file_path"])
                
                first_time = False
                
                # Espera antes de comprobar de nuevo
                for _ in range(Constants.CHECK_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_error(f"Error en el bucle principal: {str(e)}")
                time.sleep(Constants.RETRY_INTERVAL)  # Espera antes de intentar de nuevo
    
    def parse_wallpaper_info(self, xml_content):
        """Analiza la respuesta XML de Bing para obtener información de la imagen."""
        root = ET.fromstring(xml_content)
        images = root.findall(".//image")
        
        wallpapers = []
        for image in images:
            url_base = image.find("urlBase").text
            copyright_text = image.find("copyright").text
            start_date = image.find("startdate").text
            
            # Parsear la fecha (formato: YYYYMMDD)
            year = int(start_date[:4])
            month = int(start_date[4:6])
            day = int(start_date[6:8])
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            picture_url = Constants.get_picture_url_format().format(url_base)
            thumbnail_url = Constants.get_thumbnail_url_format().format(url_base)
            
            wallpapers.append({
                "picture_url": picture_url,
                "thumbnail_url": thumbnail_url,
                "copyright": copyright_text,
                "date": date_str,
                "source": WallpaperServiceConstants.SOURCE_BING
            })
        
        # Devuelve el primer wallpaper si solo estamos obteniendo uno
        if len(wallpapers) == 1:
            return wallpapers[0]
        return wallpapers
    
    def load_favorites(self):
        """Carga la lista de wallpapers favoritos."""
        self.favorites = WallpaperFavorites.get_favorites_list()
    
    def load_wallpaper_history(self, days=None):
        """Carga el historial de fondos de pantalla de los últimos días."""
        if days is None:
            days = Constants.HISTORY_DAYS
            
        try:
            # Intenta cargar el historial guardado primero
            if "history" in self.state and self.state["history"]:
                self.wallpaper_history = self.state["history"]
            
            # Obtiene información sobre varios días de wallpapers
            xml_content = requests.get(Constants.get_wallpaper_info_url(0, days)).text
            wallpapers = self.parse_wallpaper_info(xml_content)
            
            # Actualiza o agrega al historial
            self.wallpaper_history = wallpapers
            
            # Descarga las miniaturas y wallpapers en segundo plano
            for idx, wallpaper in enumerate(self.wallpaper_history):
                thumb_file = Constants.get_thumbnail_file(idx)
                wallpaper_file = Constants.get_wallpaper_file(idx)
                
                # Descarga la miniatura si no existe
                if not thumb_file.exists():
                    try:
                        response = requests.get(wallpaper["thumbnail_url"])
                        response.raise_for_status()
                        with open(thumb_file, 'wb') as f:
                            f.write(response.content)
                    except Exception as e:
                        self.log_error(f"Error al descargar miniatura {idx}: {str(e)}")
                
                # Descarga el wallpaper si no existe (solo los primeros N para ahorrar espacio)
                if idx < WallpaperServiceConstants.MAX_FULL_WALLPAPERS_TO_DOWNLOAD and not wallpaper_file.exists():
                    try:
                        response = requests.get(wallpaper["picture_url"])
                        response.raise_for_status()
                        with open(wallpaper_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=WallpaperServiceConstants.DOWNLOAD_CHUNK_SIZE):
                                f.write(chunk)
                    except Exception as e:
                        self.log_error(f"Error al descargar wallpaper {idx}: {str(e)}")
            
            # Guarda el estado actualizado
            self.save_state()
            
            # Carga también los favoritos
            self.load_favorites()
            
        except Exception as e:
            self.log_error(f"Error al cargar historial de wallpapers: {str(e)}")
    
    def download_wallpaper(self, info):
        """Descarga el fondo de pantalla y lo establece."""
        try:
            # Descarga la imagen
            response = requests.get(info["picture_url"], stream=True)
            response.raise_for_status()
            
            wallpaper_file = Constants.get_wallpaper_file(0)
            
            # Guarda la imagen
            with open(wallpaper_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=WallpaperServiceConstants.DOWNLOAD_CHUNK_SIZE):
                    f.write(chunk)
            
            # Descarga la miniatura
            thumb_file = Constants.get_thumbnail_file(0)
            thumb_response = requests.get(info["thumbnail_url"])
            thumb_response.raise_for_status()
            with open(thumb_file, 'wb') as f:
                f.write(thumb_response.content)
            
            # Establece la imagen como fondo de pantalla
            self.set_wallpaper(str(wallpaper_file))
            
            # Actualiza el estado
            self.state["picture_url"] = info["picture_url"]
            self.state["picture_file_path"] = str(wallpaper_file)
            self.state["copyright"] = info["copyright"]
            
            # Asegúrate de que el historial esté actualizado
            if not self.wallpaper_history or self.wallpaper_history[0]["picture_url"] != info["picture_url"]:
                self.load_wallpaper_history()
            
            self.save_state()
            
            # Notifica a los callbacks
            for callback in self.download_completed_callbacks:
                callback(self.state)
                
        except Exception as e:
            self.log_error(f"Error al descargar el fondo de pantalla: {str(e)}")
    
    def set_wallpaper(self, wallpaper_path):
        """Establece la imagen como fondo de pantalla de Windows."""
        wallpaper_path = os.path.abspath(wallpaper_path)
        
        # Establece el estilo de ajuste del fondo de pantalla (ajustar a pantalla)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                "Control Panel\\Desktop", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, Constants.WIN_WALLPAPER_STYLE_FIT)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, Constants.WIN_WALLPAPER_TILE)
            winreg.CloseKey(key)
        except Exception as e:
            self.log_error(f"Error al configurar el estilo del fondo: {str(e)}")
        
        # Cambia el fondo de pantalla
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                Constants.WIN_SPI_SETDESKWALLPAPER, 0, wallpaper_path, 
                Constants.WIN_SPIF_UPDATEINIFILE | Constants.WIN_SPIF_SENDCHANGE
            )
            # Notifica a los callbacks
            for callback in self.wallpaper_changed_callbacks:
                callback(wallpaper_path)
        except Exception as e:
            self.log_error(f"Error al establecer el fondo de pantalla: {str(e)}")
    
    def get_current_wallpaper(self):
        """Obtiene la información del wallpaper actual."""
        self.load_favorites()  # Recarga los favoritos para tener la lista actualizada
        
        if self.current_source == WallpaperServiceConstants.SOURCE_BING:
            if not self.wallpaper_history:
                return None
            current = self.wallpaper_history[self.current_wallpaper_index].copy()
            current["current_index"] = self.current_wallpaper_index
            return current
        else:  # Favoritos
            if not self.favorites or self.current_wallpaper_index >= len(self.favorites):
                return None
            return self.favorites[self.current_wallpaper_index]
    
    def get_wallpaper_count(self):
        """Obtiene el número de wallpapers disponibles en la fuente actual."""
        if self.current_source == WallpaperServiceConstants.SOURCE_BING:
            return len(self.wallpaper_history)
        else:  # Favoritos
            return len(self.favorites)
    
    def get_total_wallpaper_count(self):
        """Obtiene el número total de wallpapers disponibles."""
        return len(self.wallpaper_history) + len(self.favorites)
    
    def navigate_to_wallpaper(self, index, source=None):
        """
        Navega a un wallpaper específico por índice.
        
        Args:
            index: Índice dentro de la colección (Bing o favoritos)
            source: Fuente del wallpaper (Bing o favorito). Si es None, usa la fuente actual.
            
        Returns:
            bool: True si se navegó correctamente, False en caso contrario.
        """
        if source is None:
            source = self.current_source
            
        # Validar límites
        if source == WallpaperServiceConstants.SOURCE_BING:
            if not self.wallpaper_history or index < 0 or index >= len(self.wallpaper_history):
                return False
                
            wallpaper = self.wallpaper_history[index]
            wallpaper_file = Constants.get_wallpaper_file(index)
        else:  # Favoritos
            if not self.favorites or index < 0 or index >= len(self.favorites):
                return False
                
            wallpaper = self.favorites[index]
            wallpaper_file = Path(wallpaper.get("file_path", ""))
        
        # Si el wallpaper no existe, intentamos descargarlo (solo para Bing)
        if not wallpaper_file.exists() and source == WallpaperServiceConstants.SOURCE_BING:
            try:
                response = requests.get(wallpaper["picture_url"])
                response.raise_for_status()
                with open(wallpaper_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=WallpaperServiceConstants.DOWNLOAD_CHUNK_SIZE):
                        f.write(chunk)
            except Exception as e:
                self.log_error(f"Error al descargar wallpaper {index}: {str(e)}")
                return False
        
        # Si el wallpaper sigue sin existir, no podemos navegar a él
        if not wallpaper_file.exists():
            return False
        
        # Establece el wallpaper
        self.set_wallpaper(str(wallpaper_file))
        self.current_wallpaper_index = index
        self.current_source = source
        self.save_state()
        return True
    
    def navigate_to_previous_wallpaper(self):
        """
        Navega al wallpaper anterior.
        Primero dentro de la colección actual, luego a la otra colección si es necesario.
        """
        # Primero intenta navegar dentro de la colección actual
        if self.current_source == WallpaperServiceConstants.SOURCE_BING:
            # Si hay más wallpapers de Bing, navega a ellos
            if self.current_wallpaper_index < len(self.wallpaper_history) - 1:
                return self.navigate_to_wallpaper(self.current_wallpaper_index + 1)
            # Si no hay más wallpapers de Bing pero hay favoritos, cambia a favoritos
            elif self.favorites:
                return self.navigate_to_wallpaper(0, WallpaperServiceConstants.SOURCE_FAVORITE)
        else:  # Estamos en favoritos
            # Si hay más favoritos, navega a ellos
            if self.current_wallpaper_index < len(self.favorites) - 1:
                return self.navigate_to_wallpaper(self.current_wallpaper_index + 1)
        
        # Si llegamos aquí, no pudimos navegar a un wallpaper anterior
        return False
    
    def navigate_to_next_wallpaper(self):
        """
        Navega al wallpaper siguiente.
        Primero dentro de la colección actual, luego a la otra colección si es necesario.
        """
        # Primero intenta navegar dentro de la colección actual
        if self.current_source == WallpaperServiceConstants.SOURCE_FAVORITE:
            # Si estamos en favoritos y podemos retroceder, lo hacemos
            if self.current_wallpaper_index > 0:
                return self.navigate_to_wallpaper(self.current_wallpaper_index - 1)
            # Si estamos al principio de favoritos y hay wallpapers de Bing, cambiamos a Bing
            elif self.wallpaper_history:
                return self.navigate_to_wallpaper(len(self.wallpaper_history) - 1, WallpaperServiceConstants.SOURCE_BING)
        else:  # Estamos en Bing
            # Si podemos navegar hacia atrás en Bing, lo hacemos
            if self.current_wallpaper_index > 0:
                return self.navigate_to_wallpaper(self.current_wallpaper_index - 1)
        
        # Si llegamos aquí, no pudimos navegar a un wallpaper siguiente
        return False
    
    def add_current_to_favorites(self):
        """
        Agrega el wallpaper actual a favoritos.
        
        Returns:
            bool: True si se agregó correctamente, False en caso contrario.
        """
        # Obtener el wallpaper actual
        current = self.get_current_wallpaper()
        if not current:
            return False
            
        # Si ya es un favorito, no es necesario agregarlo de nuevo
        if current.get("source") == WallpaperServiceConstants.SOURCE_FAVORITE:
            return True
            
        # Agregar a favoritos
        result = WallpaperFavorites.add_to_favorites(current)
        
        # Recargar la lista de favoritos
        if result:
            self.load_favorites()
            
        return result
    
    def remove_from_favorites(self, favorite_id):
        """
        Elimina un wallpaper de favoritos.
        
        Args:
            favorite_id: ID del favorito a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        result = WallpaperFavorites.remove_from_favorites(favorite_id)
        
        # Si estamos viendo el favorito que acabamos de eliminar, navegamos al siguiente
        if result and self.current_source == WallpaperServiceConstants.SOURCE_FAVORITE:
            current = self.get_current_wallpaper()
            if current and current.get("id") == favorite_id:
                # Intentar navegar al siguiente, si no se puede, al anterior
                if not self.navigate_to_next_wallpaper():
                    if not self.navigate_to_previous_wallpaper():
                        # Si no hay más favoritos, volver a Bing
                        if self.wallpaper_history:
                            self.navigate_to_wallpaper(0, WallpaperServiceConstants.SOURCE_BING)
        
        # Recargar la lista de favoritos
        self.load_favorites()
        
        return result
    
    def is_current_favorite(self):
        """
        Verifica si el wallpaper actual está en favoritos.
        
        Returns:
            str or None: ID del favorito si está en favoritos, None en caso contrario.
        """
        current = self.get_current_wallpaper()
        
        # Si ya estamos viendo un favorito, devolver su ID
        if current and current.get("source") == WallpaperServiceConstants.SOURCE_FAVORITE:
            return current.get("id")
            
        # En caso contrario, verificar si existe en favoritos
        return WallpaperFavorites.is_favorite(current)
    
    def toggle_current_favorite(self):
        """
        Alterna el estado de favorito del wallpaper actual.
        
        Returns:
            bool: True si se cambió el estado correctamente, False en caso contrario.
        """
        favorite_id = self.is_current_favorite()
        
        if favorite_id:
            return self.remove_from_favorites(favorite_id)
        else:
            return self.add_current_to_favorites()
```

## File: ui.py
```python
import os
import subprocess
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QPalette, QColor
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QCheckBox, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMenu, 
                             QAction, QDialog, QFrame, QGraphicsDropShadowEffect,
                             QMessageBox)

from constants import Constants
from run_windows_startup import StartupManager
from wallpaper_favorites import WallpaperFavorites

# Constantes locales para la interfaz de usuario
class UIConstants:
    """Constantes específicas para la interfaz de usuario."""
    # Márgenes y espaciados
    MAIN_MARGIN_H = 15
    MAIN_MARGIN_V = 20
    CONTENT_MARGIN = 4
    CONTENT_PADDING_V = 8
    CONTENT_SPACING = 12
    HEADER_SPACING = 4
    LAYOUT_SPACING = 6
    NAV_MARGIN = 8
    BUTTON_PADDING_H = 8
    BUTTON_PADDING_V = 4
    
    # Estilos de texto
    TITLE_FONT_SIZE = 24
    VERSION_FONT_SIZE = 14
    COPYRIGHT_FONT_SIZE = 11
    BING_TITLE_FONT_SIZE = 13
    BUTTON_FONT_SIZE = 14
    NAV_TITLE_FONT_SIZE = 14
    NAV_COPYRIGHT_FONT_SIZE = 10
    NAV_BUTTON_FONT_SIZE = 12
    MENU_FONT_SIZE = 12
    
    # Colores
    LINK_COLOR = "#0066cc"
    HOVER_COLOR = "rgba(255, 255, 255, 0.1)"
    DISABLED_COLOR = "rgba(255, 255, 255, 0.3)"
    MENU_BG_COLOR = "#2C2C2C"
    MENU_BORDER_COLOR = "#3C3C3C"
    THUMB_BG_COLOR = "#111111"
    FAVORITE_COLOR = "#FFD700"  # Color dorado para favoritos
    FAVORITE_HOVER_COLOR = "#FFC125"  # Color cuando se pasa el cursor
    
    # Tamaño de la miniatura en navegador
    THUMB_WIDTH = 130
    THUMB_HEIGHT = 95
    
    # Posicionamiento del navegador
    TRAY_OFFSET_X = 20
    TRAY_OFFSET_Y = 60
    
    # Límite de caracteres para título
    TITLE_CHAR_LIMIT_FACTOR = 70
    
    # Borde de menú
    MENU_BORDER_WIDTH = 1
    MENU_BORDER_RADIUS = 8
    MENU_PADDING = 5
    MENU_ITEM_PADDING_V = 5
    MENU_ITEM_PADDING_H = 20
    MENU_ITEM_BORDER_RADIUS = 4
    
    # Iconos y símbolos
    FAVORITE_ICON_ACTIVE = "★"   # Estrella llena
    FAVORITE_ICON_INACTIVE = "☆"  # Estrella vacía

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self, wallpaper_manager):
        super().__init__()
        
        self.wallpaper_manager = wallpaper_manager
        self.wallpaper_manager.add_download_completed_callback(self.update_state)
        
        self.init_ui()
        self.update_state(self.wallpaper_manager.state)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle(Constants.APP_NAME)
        self.setFixedSize(Constants.UI_MAIN_WIDTH, Constants.UI_MAIN_HEIGHT)
        
        # Widget principal y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(UIConstants.MAIN_MARGIN_H, 
                                      UIConstants.MAIN_MARGIN_V, 
                                      UIConstants.MAIN_MARGIN_H, 
                                      UIConstants.MAIN_MARGIN_V)
        
        # Título y versión
        title_label = QLabel(Constants.APP_NAME)
        title_label.setStyleSheet(f"font-size: {UIConstants.TITLE_FONT_SIZE}px; font-weight: bold;")
        
        version_label = QLabel(f"Version {Constants.APP_VERSION}")
        version_label.setStyleSheet(f"font-size: {UIConstants.VERSION_FONT_SIZE}px;")
        
        # Copyright y enlace
        self.copyright_label = QLabel(Constants.APP_COPYRIGHT)
        self.copyright_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px; color: {UIConstants.LINK_COLOR};")
        self.copyright_label.setOpenExternalLinks(True)
        self.copyright_label.setCursor(Qt.PointingHandCursor)
        self.copyright_label.mousePressEvent = self.open_website
        
        # Checkbox para iniciar con Windows
        self.startup_checkbox = QCheckBox(f"Iniciar {Constants.APP_NAME} con Windows")
        self.startup_checkbox.setChecked(StartupManager.get_run_on_startup())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        
        # Información de la imagen actual
        self.image_title_label = QLabel("Cargando información de la imagen...")
        self.image_title_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px; color: {UIConstants.LINK_COLOR};")
        self.image_title_label.setCursor(Qt.PointingHandCursor)
        self.image_title_label.mousePressEvent = self.open_image_link
        
        # Estado de la aplicación
        self.status_label = QLabel(f"{Constants.APP_NAME} está en funcionamiento.")
        self.status_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px;")
        
        # Botón de salir
        exit_button = QPushButton(f"Salir de {Constants.APP_NAME}")
        exit_button.clicked.connect(self.exit_app)
        
        # Añadir widgets al layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(version_label)
        main_layout.addWidget(self.copyright_label)
        main_layout.addStretch(1)
        main_layout.addWidget(self.startup_checkbox)
        main_layout.addStretch(1)
        main_layout.addWidget(self.image_title_label)
        main_layout.addWidget(self.status_label)
        
        # Layout para botón inferior
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(exit_button)
        main_layout.addLayout(button_layout)
    
    def update_state(self, state):
        """Actualiza la interfaz con el estado actual."""
        if not state["copyright"]:
            self.image_title_label.setText("Esperando información de la imagen...")
        else:
            self.image_title_label.setText(state["copyright"])
            # Guarda la URL para cuando el usuario haga clic
            self.image_title_label.setProperty("url", state["picture_url"])
    
    def toggle_startup(self, state):
        """Cambia la configuración de inicio con Windows."""
        StartupManager.set_run_on_startup(state == Qt.Checked)
    
    def open_website(self, event):
        """Abre el sitio web del proyecto."""
        self.open_url(Constants.get_bing_website_url())
    
    def open_image_link(self, event):
        """Abre la URL de la imagen actual."""
        url = self.image_title_label.property("url")
        if url:
            self.open_url(url)
    
    def open_url(self, url):
        """Abre una URL en el navegador predeterminado."""
        try:
            # En Windows, esto abrirá la URL en el navegador predeterminado
            os.startfile(url)
        except Exception:
            try:
                # Intenta con subprocess como alternativa
                subprocess.run(['start', url], shell=True, check=True)
            except Exception:
                pass  # Si falla, simplemente ignoramos el error
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        # Oculta la ventana en lugar de cerrar la aplicación
        self.hide()
        event.ignore()
    
    def exit_app(self):
        """Cierra la aplicación completamente."""
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()


class WallpaperNavigatorWindow(QDialog):
    """Ventana para navegar por los fondos de pantalla."""
    
    def __init__(self, wallpaper_manager):
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
        self.setWindowTitle("Bing Wallpaper")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Guardamos una referencia al factor de zoom
        self.zoom_factor = self.wallpaper_manager.get_zoom_factor()
        
        # Registramos el callback para cuando cambie el zoom
        self.wallpaper_manager.add_zoom_changed_callback(self.on_zoom_changed)
        
        # Inicializamos la interfaz
        self.init_ui()
        self.update_content()
        self.update_window_size()
    
    def update_window_size(self):
        """Actualiza el tamaño de la ventana según el factor de zoom."""
        # Aplicar el factor de zoom a las dimensiones base
        base_width, base_height = Constants.UI_NAV_BASE_WIDTH, Constants.UI_NAV_BASE_HEIGHT
        scaled_width = int(base_width * self.zoom_factor)
        scaled_height = int(base_height * self.zoom_factor)
        self.setFixedSize(scaled_width, scaled_height)
        
        # Reposiciona la ventana
        self.position_window()
    
    def on_zoom_changed(self, new_zoom_factor):
        """Manejador para cuando cambia el factor de zoom."""
        self.zoom_factor = new_zoom_factor
        
        # Recreamos la interfaz con el nuevo factor de zoom
        self.recreate_ui()
    
    def recreate_ui(self):
        """Recrea la interfaz de usuario con el nuevo factor de zoom."""
        # Limpiamos cualquier widget existente
        if self.layout():
            # Eliminar todos los widgets del layout
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Eliminar el layout
            QWidget().setLayout(self.layout())
        
        # Actualizamos el tamaño de la ventana
        self.update_window_size()
        
        # Recreamos la interfaz
        self.init_ui()
        self.update_content()
    
    def position_window(self):
        """Posiciona la ventana sobre el system tray."""
        from PyQt5.QtWidgets import QApplication
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        
        # En Windows, el system tray suele estar en la esquina inferior derecha
        self.move(screen_rect.width() - self.width() - UIConstants.TRAY_OFFSET_X, 
                  screen_rect.height() - self.height() - UIConstants.TRAY_OFFSET_Y)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Factor de zoom para escalar elementos
        zoom = self.zoom_factor
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor principal con borde redondeado y sombra
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet(f"""
            #container {{
                background-color: {Constants.BACKGROUND_COLOR};
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                color: {Constants.TEXT_COLOR};
            }}
        """)
        
        # Aplicamos efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(Constants.UI_SHADOW_BLUR * zoom)
        shadow_color = QColor(*Constants.UI_SHADOW_COLOR)
        shadow.setColor(shadow_color)
        shadow.setOffset(0, Constants.UI_SHADOW_OFFSET * zoom)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        margin = int(Constants.UI_MARGIN * zoom)
        container_layout.setContentsMargins(margin, margin, margin, margin)
        container_layout.setSpacing(int(UIConstants.LAYOUT_SPACING * zoom))
        
        # Barra superior con título y botones
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        # Logo de Bing
        bing_label = QLabel("Microsoft Bing")
        bing_label.setStyleSheet(f"""
            font-size: {int(UIConstants.BING_TITLE_FONT_SIZE * zoom)}px;
            font-weight: bold;
            color: white;
        """)
        
        # Botones de la barra superior
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        btn_size = int(Constants.UI_BUTTON_SIZE * zoom)
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(btn_size, btn_size)
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        minimize_btn.clicked.connect(self.hide)
        
        share_btn = QPushButton("⤴")
        share_btn.setFixedSize(btn_size, btn_size)
        share_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        
        # Botón de favorito
        self.favorite_btn = QPushButton(UIConstants.FAVORITE_ICON_INACTIVE)
        self.favorite_btn.setFixedSize(btn_size, btn_size)
        self.favorite_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                color: {UIConstants.FAVORITE_HOVER_COLOR};
            }}
        """)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        
        # Botón de configuración con menú
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(btn_size, btn_size)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings_menu)
        
        buttons_layout.addWidget(minimize_btn)
        buttons_layout.addWidget(share_btn)
        buttons_layout.addWidget(self.favorite_btn)
        buttons_layout.addWidget(settings_btn)
        
        header_layout.addWidget(bing_label)
        header_layout.addStretch(1)
        header_layout.addLayout(buttons_layout)
        
        # Contenido principal con la imagen y la descripción
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(
            int(UIConstants.CONTENT_MARGIN * zoom), 
            int(UIConstants.CONTENT_PADDING_V * zoom), 
            int(UIConstants.CONTENT_MARGIN * zoom), 
            int(UIConstants.CONTENT_MARGIN * zoom))
        content_layout.setSpacing(int(UIConstants.CONTENT_SPACING * zoom))
        
        # Imagen miniatura - Escalada con el factor de zoom
        self.thumbnail_label = QLabel()
        thumb_width = int(UIConstants.THUMB_WIDTH * zoom)
        thumb_height = int(UIConstants.THUMB_HEIGHT * zoom)
        self.thumbnail_label.setFixedSize(thumb_width, thumb_height)
        self.thumbnail_label.setStyleSheet(f"""
            border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            background-color: {UIConstants.THUMB_BG_COLOR};
        """)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        # Información del wallpaper
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"""
            font-size: {int(UIConstants.NAV_TITLE_FONT_SIZE * zoom)}px;
            font-weight: bold;
            color: white;
            margin-right: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
        """)
        
        self.copyright_label = QLabel()
        self.copyright_label.setStyleSheet(f"""
            font-size: {int(UIConstants.NAV_COPYRIGHT_FONT_SIZE * zoom)}px;
            color: rgba(255, 255, 255, 0.7);
        """)
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.copyright_label)
        info_layout.addStretch(1)
        
        content_layout.addWidget(self.thumbnail_label)
        content_layout.addLayout(info_layout, 1)
        
        # Barra de navegación
        nav_layout = QHBoxLayout()
        nav_margin = int(UIConstants.NAV_MARGIN * zoom)
        nav_layout.setContentsMargins(nav_margin, 0, nav_margin, nav_margin)
        nav_layout.setSpacing(0)
        
        self.prev_button = QPushButton("⟨ Anterior")
        self.prev_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: {int(UIConstants.BUTTON_PADDING_V * zoom)}px {int(UIConstants.BUTTON_PADDING_H * zoom)}px;
                font-size: {int(UIConstants.NAV_BUTTON_FONT_SIZE * zoom)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            }}
            QPushButton:disabled {{
                color: {UIConstants.DISABLED_COLOR};
            }}
        """)
        self.prev_button.clicked.connect(self.navigate_to_previous)
        
        self.next_button = QPushButton("Siguiente ⟩")
        self.next_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: {int(UIConstants.BUTTON_PADDING_V * zoom)}px {int(UIConstants.BUTTON_PADDING_H * zoom)}px;
                font-size: {int(UIConstants.NAV_BUTTON_FONT_SIZE * zoom)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            }}
            QPushButton:disabled {{
                color: {UIConstants.DISABLED_COLOR};
            }}
        """)
        self.next_button.clicked.connect(self.navigate_to_next)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.next_button)
        
        # Agregamos todos los layouts al contenedor principal
        container_layout.addLayout(header_layout)
        container_layout.addLayout(content_layout, 1)
        container_layout.addLayout(nav_layout)
        
        # Agregamos el contenedor al layout principal
        main_layout.addWidget(container)
    
    def show_settings_menu(self):
        """Muestra el menú de configuración."""
        zoom = self.zoom_factor
        
        settings_menu = QMenu(self)
        settings_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {UIConstants.MENU_BG_COLOR};
                color: white;
                border: {UIConstants.MENU_BORDER_WIDTH}px solid {UIConstants.MENU_BORDER_COLOR};
                border-radius: {int(UIConstants.MENU_BORDER_RADIUS * zoom)}px;
                padding: {int(UIConstants.MENU_PADDING * zoom)}px;
                font-size: {int(UIConstants.MENU_FONT_SIZE * zoom)}px;
            }}
            QMenu::item {{
                padding: {int(UIConstants.MENU_ITEM_PADDING_V * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_H * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_V * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_H * zoom)}px;
                border-radius: {int(UIConstants.MENU_ITEM_BORDER_RADIUS * zoom)}px;
            }}
            QMenu::item:selected {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        
        # Opciones del menú
        run_startup_action = settings_menu.addAction("Iniciar con Windows")
        run_startup_action.setCheckable(True)
        run_startup_action.setChecked(StartupManager.get_run_on_startup())
        run_startup_action.triggered.connect(lambda checked: StartupManager.set_run_on_startup(checked))
        
        # Opción para ajustar zoom
        zoom_menu = settings_menu.addMenu("Ajustar tamaño")
        
        for name, factor in Constants.ZOOM_OPTIONS:
            zoom_action = zoom_menu.addAction(name)
            zoom_action.setCheckable(True)
            zoom_action.setChecked(abs(self.zoom_factor - factor) < 0.1)
            
            # Función para aplicar el cambio de zoom
            def apply_zoom(checked, new_factor=factor):
                if checked:
                    self.wallpaper_manager.set_zoom_factor(new_factor)
            
            zoom_action.triggered.connect(apply_zoom)
        
        settings_menu.addSeparator()
        
        # Opción para abrir la carpeta de favoritos
        favorites_action = settings_menu.addAction("Abrir carpeta de favoritos")
        favorites_action.triggered.connect(WallpaperFavorites.open_favorites_folder)
        
        settings_menu.addSeparator()
        
        exit_action = settings_menu.addAction("Salir de la aplicación")
        from PyQt5.QtWidgets import QApplication
        exit_action.triggered.connect(QApplication.instance().quit)
        
        # Muestra el menú en la posición del cursor
        settings_menu.exec_(QCursor.pos())
    
    def open_main_window(self):
        """Abre la ventana principal."""
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().postEvent(self, QEvent(QEvent.Type.Hide))
        # Luego llamamos a la función que muestra la ventana principal usando QTimer
        # para evitar problemas de temporización con el cierre del menú
        QTimer.singleShot(100, lambda: QApplication.instance().access_app_window())
    
    def toggle_favorite(self):
        """Alterna el estado de favorito del wallpaper actual."""
        if self.wallpaper_manager.toggle_current_favorite():
            self.update_favorite_button()
    
    def update_favorite_button(self):
        """Actualiza el estado visual del botón de favorito."""
        is_favorite = self.wallpaper_manager.is_current_favorite() is not None
        
        # Actualizar el estilo y texto del botón
        zoom = self.zoom_factor
        if is_favorite:
            self.favorite_btn.setText(UIConstants.FAVORITE_ICON_ACTIVE)
            self.favorite_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {UIConstants.FAVORITE_COLOR};
                    font-weight: bold;
                    border: none;
                    border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                    font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
                }}
                QPushButton:hover {{
                    background-color: {UIConstants.HOVER_COLOR};
                    color: {UIConstants.FAVORITE_HOVER_COLOR};
                }}
            """)
        else:
            self.favorite_btn.setText(UIConstants.FAVORITE_ICON_INACTIVE)
            self.favorite_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                    font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
                }}
                QPushButton:hover {{
                    background-color: {UIConstants.HOVER_COLOR};
                    color: {UIConstants.FAVORITE_HOVER_COLOR};
                }}
            """)
    
    def update_content(self):
        """Actualiza el contenido de la ventana con el wallpaper actual."""
        current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
        if not current_wallpaper:
            return
        
        # Aplicar factor de zoom
        zoom = self.zoom_factor
        
        # Actualiza la miniatura
        idx = self.wallpaper_manager.current_wallpaper_index
        
        # Obtener la ruta de la miniatura según la fuente
        if self.wallpaper_manager.current_source == "bing":
            thumb_file = Constants.get_thumbnail_file(idx)
        else:  # Favorito
            # Usar el archivo original para los favoritos
            thumb_file = Path(current_wallpaper.get("file_path", ""))
        
        if thumb_file.exists():
            pixmap = QPixmap(str(thumb_file))
            # Usamos una escala óptima para la imagen con el factor de zoom
            thumb_width = int(UIConstants.THUMB_WIDTH * zoom)
            thumb_height = int(UIConstants.THUMB_HEIGHT * zoom)
            self.thumbnail_label.setPixmap(pixmap.scaled(
                thumb_width, thumb_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Parsea y formatea mejor el título y copyright
        if "copyright" in current_wallpaper:
            title_parts = current_wallpaper["copyright"].split("(©")
            title = title_parts[0].strip()
            # Limita el título a dos líneas basado en el tamaño y zoom
            max_length = int(UIConstants.TITLE_CHAR_LIMIT_FACTOR / zoom)  # Menos caracteres si es más grande
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
            
            copyright_text = "©" + title_parts[1] if len(title_parts) > 1 else ""
            
            self.title_label.setText(title)
            self.copyright_label.setText(copyright_text)
        
        # Actualiza los botones de navegación
        wallpaper_count = self.wallpaper_manager.get_wallpaper_count()
        current_idx = self.wallpaper_manager.current_wallpaper_index
        
        # Lógica avanzada para los botones de navegación
        can_go_previous = (
            # Hay más wallpapers en la colección actual
            (current_idx < wallpaper_count - 1) or 
            # O estamos en Bing y hay favoritos disponibles
            (self.wallpaper_manager.current_source == "bing" and len(self.wallpaper_manager.favorites) > 0)
        )
        
        can_go_next = (
            # Hay wallpapers anteriores en la colección actual
            (current_idx > 0) or 
            # O estamos en favoritos y hay wallpapers Bing disponibles
            (self.wallpaper_manager.current_source == "favorite" and len(self.wallpaper_manager.wallpaper_history) > 0)
        )
        
        self.prev_button.setEnabled(can_go_previous)
        self.next_button.setEnabled(can_go_next)
        
        # Muestra la fuente actual en la interfaz
        if self.wallpaper_manager.current_source == "favorite":
            self.title_label.setText(f"⭐ {self.title_label.text()}")
        
        # Actualiza el estado del botón de favorito
        self.update_favorite_button()
    
    def navigate_to_previous(self):
        """Navega al wallpaper anterior."""
        if self.wallpaper_manager.navigate_to_previous_wallpaper():
            self.update_content()
    
    def navigate_to_next(self):
        """Navega al wallpaper siguiente."""
        if self.wallpaper_manager.navigate_to_next_wallpaper():
            self.update_content()
    
    def mousePressEvent(self, event):
        """Gestiona el evento de pulsación del ratón para mover la ventana."""
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Gestiona el evento de movimiento del ratón para mover la ventana."""
        if hasattr(self, 'offset'):
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Gestiona el evento de liberación del ratón."""
        if hasattr(self, 'offset'):
            del self.offset
        else:
            super().mouseReleaseEvent(event)
    
    # Cierra la ventana si se presiona Escape
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
    
    # Asegura que la ventana se cierra al perder el foco
    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)
```

## File: app.py
```python
import os
import sys
import psutil
from pathlib import Path
from PIL import Image, ImageDraw
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction

from constants import Constants
from bing_wallpaper_service import WallpaperManager
from ui import MainWindow, WallpaperNavigatorWindow
from run_windows_startup import StartupManager

# Constantes locales para la aplicación principal
class AppConstants:
    """Constantes específicas para la aplicación principal."""
    # Tamaño del icono de la aplicación
    ICON_SIZE = 64
    
    # Valores para dibujar el icono
    ICON_B_LEFT = 15
    ICON_B_TOP = 10
    ICON_B_WIDTH = 10
    ICON_B_HEIGHT = 44
    ICON_BOW_WIDTH = 20
    ICON_BOW_HEIGHT = 10
    ICON_BOW_TOP1 = 10
    ICON_BOW_TOP2 = 22
    ICON_BOW_TOP3 = 34
    
    # Colores para el icono
    ICON_BG_COLOR = (0, 120, 212, 255)  # Azul de Bing
    ICON_FG_COLOR = (255, 255, 255, 255)  # Blanco
    
    # Posición del icono en bandeja
    TRAY_OFFSET = 20
    
    # Tiempo de espera para join de threads
    THREAD_JOIN_TIMEOUT = 1.0

class BingWallpaperApp:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Permite ejecutar en segundo plano
        
        self.wallpaper_manager = WallpaperManager()
        self.main_window = None
        self.navigator_window = None
        self.tray_icon = None
        
        # Carga los iconos
        self.setup_app_icon()
        
        # Verifica si hay una instancia en ejecución
        self.running_in_background = "/background" in sys.argv
        self.is_first_instance = self.check_single_instance()
        
        if not self.is_first_instance:
            # Si ya hay una instancia, envía un mensaje para mostrar la ventana
            if not self.running_in_background:
                self.send_show_message()
            sys.exit(0)
        
        # Agrega método para acceso a la ventana principal
        self.app.access_app_window = self.show_main_window
        
        # Registra un callback para recrear las ventanas cuando cambie el zoom
        self.wallpaper_manager.add_zoom_changed_callback(self.handle_zoom_change)
    
    def handle_zoom_change(self, new_zoom_factor):
        """Maneja el cambio en el factor de zoom."""
        # Si las ventanas existen, las recreamos con el nuevo zoom
        if hasattr(self, 'navigator_window') and self.navigator_window:
            # La ventana de navegación se actualiza automáticamente a través de su propio callback
            pass
            
        if hasattr(self, 'main_window') and self.main_window:
            # Guardamos el estado de visibilidad de la ventana principal
            was_visible = self.main_window.isVisible()
            
            # Cerramos la ventana actual
            self.main_window.close()
            
            # Creamos una nueva ventana con el zoom actualizado
            self.main_window = MainWindow(self.wallpaper_manager)
            
            # Restauramos la visibilidad
            if was_visible:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
    
    def setup_app_icon(self):
        """Configura el icono de la aplicación."""
        # Intenta cargar un icono si existe, o crea uno básico
        icon_path = Constants.get_app_icon_file()
        
        # Si no existe el icono, crea uno básico usando Pillow
        if not icon_path.exists():
            try:
                # Crea una imagen cuadrada con fondo azul de Bing
                img = Image.new('RGBA', (AppConstants.ICON_SIZE, AppConstants.ICON_SIZE), AppConstants.ICON_BG_COLOR)
                draw = ImageDraw.Draw(img)
                
                # Dibuja una forma de 'B' simplificada
                b_left = AppConstants.ICON_B_LEFT
                b_right = b_left + AppConstants.ICON_B_WIDTH
                b_top = AppConstants.ICON_B_TOP
                b_bottom = b_top + AppConstants.ICON_B_HEIGHT
                
                # Línea vertical
                draw.rectangle((b_left, b_top, b_right, b_bottom), fill=AppConstants.ICON_FG_COLOR)
                
                # Líneas horizontales (tres arcos)
                bow_left = b_right
                bow_right = bow_left + AppConstants.ICON_BOW_WIDTH
                
                # Arco superior
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP1, 
                              bow_right, AppConstants.ICON_BOW_TOP1 + AppConstants.ICON_BOW_HEIGHT), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Arco medio
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP2, 
                              bow_right, AppConstants.ICON_BOW_TOP2 + AppConstants.ICON_BOW_HEIGHT), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Arco inferior
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP3, 
                              bow_right + 4, AppConstants.ICON_BOW_TOP3 + AppConstants.ICON_BOW_HEIGHT * 2), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Guarda la imagen
                img.save(str(icon_path))
            except Exception:
                # Si falla la creación, simplemente continuamos
                pass
        
        # Establece el icono de la aplicación
        self.app_icon = QIcon(str(icon_path) if icon_path.exists() else "")
        if not self.app_icon.isNull():
            self.app.setWindowIcon(self.app_icon)
    
    def setup_tray_icon(self):
        """Configura el icono de la bandeja del sistema."""
        # Si no hay icono de aplicación válido, intenta usar uno del sistema
        if self.app_icon.isNull():
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("image", QIcon()))
        else:
            self.tray_icon = QSystemTrayIcon(self.app_icon)
        
        # Crea el menú contextual
        tray_menu = QMenu()
        
        # Acción para abrir el navegador de wallpapers
        navigator_action = QAction("Explorar fondos de pantalla", self.app)
        navigator_action.triggered.connect(self.show_navigator_window)
        tray_menu.addAction(navigator_action)
        
        # Opción para iniciar con Windows
        startup_action = QAction("Iniciar con Windows", self.app)
        startup_action.setCheckable(True)
        startup_action.setChecked(StartupManager.get_run_on_startup())
        startup_action.triggered.connect(lambda checked: StartupManager.set_run_on_startup(checked))
        tray_menu.addAction(startup_action)
        
        tray_menu.addSeparator()
        
        # Acción para salir
        exit_action = QAction("Salir", self.app)
        exit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(exit_action)
        
        # Asigna el menú al icono
        self.tray_icon.setContextMenu(tray_menu)
        
        # Conecta el evento de clic del icono para mostrar/ocultar el navegador
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Tooltip para el icono
        self.tray_icon.setToolTip(Constants.APP_NAME)
        
        # Muestra el icono
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        """Maneja los eventos de activación del icono de la bandeja."""
        # Al hacer clic en el icono, alterna la visibilidad de la ventana de navegación
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.navigator_window and self.navigator_window.isVisible():
                self.navigator_window.hide()
            else:
                self.show_navigator_window()
    
    def check_single_instance(self):
        """Verifica si ya hay una instancia en ejecución."""
        lock_file = Constants.get_lock_file()
        
        if lock_file.exists():
            # Comprueba si el proceso sigue en ejecución
            try:
                with open(lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Intenta obtener el proceso con ese PID
                if psutil.pid_exists(pid):
                    return False  # La aplicación ya está en ejecución
            except Exception:
                pass  # Si hay error, asumimos que el archivo está obsoleto
        
        # Crea el archivo de bloqueo con nuestro PID
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception:
            return True  # Si no podemos crear el archivo, continuamos de todos modos
    
    def send_show_message(self):
        """Envía un mensaje a la instancia en ejecución para mostrar la ventana."""
        try:
            show_signal = Constants.get_show_signal_file()
            with open(show_signal, 'w') as f:
                f.write("SHOW")
        except Exception:
            pass
    
    def check_show_signals(self):
        """Comprueba si hay señales para mostrar la ventana."""
        show_signal = Constants.get_show_signal_file()
        
        if show_signal.exists():
            try:
                show_signal.unlink()  # Elimina el archivo
                self.show_navigator_window()
            except Exception:
                pass
            
        # Programa la próxima comprobación
        QApplication.instance().processEvents()
        QTimer.singleShot(Constants.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
    
    def show_main_window(self):
        """Muestra la ventana principal."""
        if not self.main_window:
            self.main_window = MainWindow(self.wallpaper_manager)
        
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def show_navigator_window(self):
        """Muestra la ventana de navegación de wallpapers."""
        if not self.navigator_window:
            self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager)
        else:
            self.navigator_window.update_content()
        
        self.navigator_window.show()
        self.navigator_window.raise_()
        self.navigator_window.activateWindow()
    
    def run(self):
        """Ejecuta la aplicación."""
        # Inicia el gestor de fondos de pantalla
        self.wallpaper_manager.start()
        
        # Configura el icono de la bandeja del sistema
        self.setup_tray_icon()
        
        # Crea la ventana principal pero no la muestra automáticamente
        self.main_window = MainWindow(self.wallpaper_manager)
        
        # Crea la ventana de navegación
        self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager)
        
        # Si no se especifica /background, muestra la ventana
        if not self.running_in_background:
            self.show_navigator_window()
        
        # Inicia la comprobación de señales para mostrar la ventana
        QTimer.singleShot(Constants.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
        
        # Ejecuta el bucle de eventos
        return self.app.exec_()
    
    def cleanup(self):
        """Limpia los recursos antes de salir."""
        # Detiene el gestor de fondos de pantalla
        self.wallpaper_manager.stop()
        
        # Elimina el archivo de bloqueo
        try:
            lock_file = Constants.get_lock_file()
            if lock_file.exists():
                lock_file.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    app = BingWallpaperApp()
    
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    
    sys.exit(exit_code)
```

## File: requirements.txt
```
PyQt5>=5.15.0
requests>=2.25.0
Pillow>=8.0.0
psutil>=5.8.0
```
