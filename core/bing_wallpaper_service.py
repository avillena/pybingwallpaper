import os
import time
import ctypes
import winreg
import threading
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QObject, pyqtSignal

from constants import Constants
from core.wallpaper_favorites import WallpaperFavorites
from utils.logger import log_error, log_info
from utils.file_utils import read_json, write_json, file_exists
from utils.http_client import download_file, download_content, download_binary
from core.navigation_controller import NavigationController

class WallpaperManager(QObject):
    """Gestiona la descarga y actualización del fondo de pantalla usando nombres basados en la fecha
       y un enlace simbólico para el wallpaper actual.
    """
    # Señales Qt
    wallpaper_changed = pyqtSignal(dict)   # Emitida cuando cambia el fondo
    download_completed = pyqtSignal(dict)    # Emitida cuando se completa una descarga
    zoom_changed = pyqtSignal(float)         # Emitida cuando cambia el zoom

    # Constantes para fuentes de wallpapers
    SOURCE_BING = "bing"
    SOURCE_FAVORITE = "favorite"

    def __init__(self):
        """Inicializa el gestor de fondos de pantalla."""
        super().__init__()

        self.state = self.load_state()
        self.zoom_factor = self.state.get("zoom_factor", Constants.DEFAULT_ZOOM_FACTOR)
        self.running = False
        self.thread = None
        self.wallpaper_history = []
        self.favorites = []
        self.current_wallpaper_index = 0
        self.current_source = self.SOURCE_BING  # Fuente predeterminada

        # Crear controlador de navegación
        self.navigation_controller = NavigationController(self)
        self.navigation_controller.wallpaper_changed.connect(
            lambda wallpaper: self.wallpaper_changed.emit(wallpaper)
        )

        # Cargar historial y favoritos en segundo plano
        threading.Thread(target=self.load_wallpaper_history, daemon=True).start()
        self.load_favorites()

    def load_state(self):
        """Carga el estado desde el archivo JSON."""
        state_file = Constants.get_state_file()
        state = read_json(state_file, None)
        if not state:
            # Estado por defecto con un campo para la fecha del wallpaper
            state = {
                "picture_url": "",
                "picture_date": "",
                "picture_file_path": "",
                "copyright": "",
                "history": [],
                "current_source": self.SOURCE_BING,
                "current_index": 0,
                "zoom_factor": Constants.DEFAULT_ZOOM_FACTOR
            }
        return state

    def save_state(self):
        """Guarda el estado actual en el archivo JSON."""
        try:
            self.state["history"] = self.wallpaper_history
            self.state["current_source"] = self.current_source
            self.state["current_index"] = self.current_wallpaper_index
            self.state["zoom_factor"] = self.zoom_factor
            write_json(Constants.get_state_file(), self.state)
        except Exception as e:
            log_error(f"Error al guardar el estado: {str(e)}")

    def get_zoom_factor(self):
        """Retorna el factor de zoom actual."""
        return self.zoom_factor

    def set_zoom_factor(self, zoom_factor):
        """Establece un nuevo factor de zoom y emite la señal correspondiente."""
        if self.zoom_factor != zoom_factor:
            self.zoom_factor = zoom_factor
            self.save_state()
            self.zoom_changed.emit(zoom_factor)
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
        """Bucle principal que consulta Bing y actualiza el wallpaper según corresponda."""
        first_time = True
        while self.running:
            try:
                xml_content = download_content(Constants.get_wallpaper_info_url())
                if xml_content:
                    info = self.parse_wallpaper_info(xml_content)
                    # Si se detecta un nuevo wallpaper o la copia local no existe
                    if info and (info["picture_url"] != self.state.get("picture_url") or
                                 not file_exists(Path(self.state.get("picture_file_path", "")))):
                        self.download_wallpaper(info)
                    elif first_time:
                        # En la primera ejecución, se usa el enlace simbólico actual
                        current_link = Constants.get_wallpapers_path() / "current.jpg"
                        self.set_wallpaper(str(current_link))
                    first_time = False

                # Espera el intervalo configurado antes de volver a consultar
                for _ in range(Constants.Network.CHECK_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                log_error(f"Error en el bucle principal: {str(e)}")
                time.sleep(Constants.Network.RETRY_INTERVAL)

    def parse_wallpaper_info(self, xml_content):
        """Analiza el XML de Bing y extrae la información relevante del wallpaper."""
        try:
            root = ET.fromstring(xml_content)
            images = root.findall(".//image")
            wallpapers = []
            for image in images:
                url_base = image.find("urlBase").text
                copyright_text = image.find("copyright").text
                start_date = image.find("startdate").text  # Formato: YYYYMMDD
                # Usamos directamente start_date para nombrar los archivos
                picture_url = Constants.get_picture_url_format().format(url_base)
                thumbnail_url = Constants.get_thumbnail_url_format().format(url_base)
                wallpapers.append({
                    "picture_url": picture_url,
                    "thumbnail_url": thumbnail_url,
                    "copyright": copyright_text,
                    "date": start_date,  # Ej: "20250409"
                    "source": self.SOURCE_BING
                })
            if len(wallpapers) == 1:
                return wallpapers[0]
            return wallpapers
        except Exception as e:
            log_error(f"Error al analizar información de wallpaper: {str(e)}")
            return None

    def load_favorites(self):
        """Carga la lista de wallpapers favoritos."""
        self.favorites = WallpaperFavorites.get_favorites_list()

    def load_wallpaper_history(self, days=None):
        """Carga el historial de wallpapers de los últimos 'days' días."""
        if days is None:
            days = Constants.Files.HISTORY_DAYS
        try:
            if "history" in self.state and self.state["history"]:
                self.wallpaper_history = self.state["history"]

            xml_content = download_content(Constants.get_wallpaper_info_url(0, days))
            if xml_content:
                wallpapers = self.parse_wallpaper_info(xml_content)
                if wallpapers:
                    self.wallpaper_history = wallpapers
                    for wallpaper in self.wallpaper_history:
                        date_str = wallpaper["date"]
                        thumb_file = Constants.get_wallpapers_path() / f"{date_str}_thumb.jpg"
                        wallpaper_file = Constants.get_wallpapers_path() / f"{date_str}.jpg"
                        if not file_exists(thumb_file) and "thumbnail_url" in wallpaper:
                            download_file(wallpaper["thumbnail_url"], thumb_file)
                        if not file_exists(wallpaper_file) and "picture_url" in wallpaper:
                            download_file(wallpaper["picture_url"], wallpaper_file)
                    self.save_state()
            self.load_favorites()
        except Exception as e:
            log_error(f"Error al cargar historial de wallpapers: {str(e)}")

    def download_wallpaper(self, info):
        """
        Descarga el wallpaper y su miniatura usando la fecha como parte del nombre.
        Luego, actualiza el enlace simbólico 'current.jpg' para apuntar al nuevo wallpaper.
        """
        try:
            date_str = info["date"]  # Ejemplo: "20250409"
            wallpaper_file = Constants.get_wallpapers_path() / f"{date_str}.jpg"
            if download_file(info["picture_url"], wallpaper_file):
                thumb_file = Constants.get_wallpapers_path() / f"{date_str}_thumb.jpg"
                download_file(info["thumbnail_url"], thumb_file)
                # Actualizar el enlace simbólico "current.jpg"
                current_link = Constants.get_wallpapers_path() / "current.jpg"
                if os.path.exists(current_link) or os.path.islink(current_link):
                    os.remove(current_link)
                os.symlink(wallpaper_file, current_link)
                # Establecer el wallpaper utilizando el enlace simbólico
                self.set_wallpaper(str(current_link))
                # Actualizar el estado
                self.state["picture_url"] = info["picture_url"]
                self.state["picture_date"] = date_str
                self.state["picture_file_path"] = str(wallpaper_file)
                self.state["copyright"] = info["copyright"]
                if not self.wallpaper_history or self.wallpaper_history[0]["picture_url"] != info["picture_url"]:
                    self.load_wallpaper_history()
                self.save_state()
                self.download_completed.emit(self.state)
        except Exception as e:
            log_error(f"Error al descargar el fondo de pantalla: {str(e)}")

    def set_wallpaper(self, wallpaper_path):
        """Establece la imagen como fondo de pantalla en Windows utilizando la API del sistema."""
        wallpaper_path = os.path.abspath(wallpaper_path)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, Constants.Windows.WALLPAPER_STYLE_FIT)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, Constants.Windows.WALLPAPER_TILE)
            winreg.CloseKey(key)
        except Exception as e:
            log_error(f"Error al configurar el estilo del fondo: {str(e)}")
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                Constants.Windows.SPI_SETDESKWALLPAPER, 0, wallpaper_path,
                Constants.Windows.SPIF_UPDATEINIFILE | Constants.Windows.SPIF_SENDCHANGE
            )
            self.wallpaper_changed.emit(self.get_current_wallpaper())
        except Exception as e:
            log_error(f"Error al establecer el fondo de pantalla: {str(e)}")

    def navigate_to_wallpaper(self, index, source=None):
        """Navega a un wallpaper específico por índice."""
        return self.navigation_controller.navigate_to_wallpaper(index, source)

    def navigate_to_previous_wallpaper(self):
        """Navega al wallpaper anterior (más antiguo)."""
        return self.navigation_controller.navigate_to_previous()

    def navigate_to_next_wallpaper(self):
        """Navega al wallpaper siguiente (más reciente)."""
        return self.navigation_controller.navigate_to_next()

    def get_current_wallpaper(self):
        """Obtiene la información del wallpaper actual, usando el enlace simbólico 'current.jpg'."""
        self.load_favorites()  # Actualiza la lista de favoritos
        if self.current_source == self.SOURCE_BING:
            if not self.wallpaper_history or self.current_wallpaper_index >= len(self.wallpaper_history):
                return None
            current = self.wallpaper_history[self.current_wallpaper_index].copy()
            current["current_index"] = self.current_wallpaper_index
            current["total_images"] = len(self.wallpaper_history)
            current["source_name"] = "Bing Wallpaper"
            # Siempre se usa el enlace simbólico para el wallpaper actual
            current["file_path"] = str(Constants.get_wallpapers_path() / "current.jpg")
            return current
        else:
            if not self.favorites or self.current_wallpaper_index >= len(self.favorites):
                return None
            favorite = self.favorites[self.current_wallpaper_index].copy()
            favorite["total_images"] = len(self.favorites)
            favorite["current_index"] = self.current_wallpaper_index
            return favorite

    def get_wallpaper_count(self):
        """Retorna el número de wallpapers disponibles según la fuente actual."""
        if self.current_source == self.SOURCE_BING:
            return len(self.wallpaper_history)
        else:
            return len(self.favorites)

    def get_total_wallpaper_count(self):
        """Retorna el número total de wallpapers disponibles (Bing + Favoritos)."""
        return len(self.wallpaper_history) + len(self.favorites)

    def add_current_to_favorites(self):
        """Agrega el wallpaper actual a la lista de favoritos."""
        current = self.get_current_wallpaper()
        if not current:
            return False
        if current.get("source") == self.SOURCE_FAVORITE:
            return True
        result = WallpaperFavorites.add_to_favorites(current)
        if result:
            self.load_favorites()
        return result

    def remove_from_favorites(self, favorite_id):
        """Elimina un wallpaper de favoritos."""
        result = WallpaperFavorites.remove_from_favorites(favorite_id)
        if result and self.current_source == self.SOURCE_FAVORITE:
            current = self.get_current_wallpaper()
            if current and current.get("id") == favorite_id:
                if not self.navigate_to_next_wallpaper():
                    if not self.navigate_to_previous_wallpaper():
                        if self.wallpaper_history:
                            self.navigate_to_wallpaper(0, self.SOURCE_BING)
        self.load_favorites()
        return result

    def is_current_favorite(self):
        """Verifica si el wallpaper actual está marcado como favorito."""
        current = self.get_current_wallpaper()
        if current and current.get("source") == self.SOURCE_FAVORITE:
            return current.get("id")
        return WallpaperFavorites.is_favorite(current)

    def toggle_current_favorite(self):
        """Alterna el estado de favorito del wallpaper actual."""
        favorite_id = self.is_current_favorite()
        if favorite_id:
            return self.remove_from_favorites(favorite_id)
        else:
            return self.add_current_to_favorites()
