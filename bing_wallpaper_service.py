import os
import time
import ctypes
import winreg
import threading
import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QObject, pyqtSignal

from constants import Constants
from wallpaper_favorites import WallpaperFavorites
from logger import log_error, log_info
from file_utils import read_json, write_json, file_exists
from http_client import download_file, download_content, download_binary
from navigation_controller import NavigationController

class WallpaperManager(QObject):
    """Gestiona la descarga y actualización del fondo de pantalla."""
    
    # Señales Qt
    wallpaper_changed = pyqtSignal(dict)  # Emitida cuando cambia el fondo
    download_completed = pyqtSignal(dict)  # Emitida cuando se completa una descarga
    zoom_changed = pyqtSignal(float)  # Emitida cuando cambia el zoom
    
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
        self.current_source = self.SOURCE_BING  # Por defecto, fuente Bing
        
        # Crear controlador de navegación
        self.navigation_controller = NavigationController(self)
        
        # Conectar señales
        self.navigation_controller.wallpaper_changed.connect(
            lambda wallpaper: self.wallpaper_changed.emit(wallpaper)
        )
        
        # Carga inicialmente hasta 7 días de wallpapers en segundo plano
        threading.Thread(target=self.load_wallpaper_history, daemon=True).start()
        
        # Carga los favoritos
        self.load_favorites()
    
    def load_state(self):
        """Carga el estado desde el archivo."""
        state_file = Constants.get_state_file()
        state = read_json(state_file, None)
        
        if not state:
            # Estado por defecto
            state = {
                "picture_url": "",
                "picture_file_path": "",
                "copyright": "",
                "history": [],
                "current_source": self.SOURCE_BING,
                "current_index": 0,
                "zoom_factor": Constants.DEFAULT_ZOOM_FACTOR
            }
        
        return state
    
    def save_state(self):
        """Guarda el estado en un archivo."""
        try:
            self.state["history"] = self.wallpaper_history
            self.state["current_source"] = self.current_source
            self.state["current_index"] = self.current_wallpaper_index
            self.state["zoom_factor"] = self.zoom_factor
            write_json(Constants.get_state_file(), self.state)
        except Exception as e:
            log_error(f"Error al guardar el estado: {str(e)}")
    
    def get_zoom_factor(self):
        """Obtiene el factor de zoom actual."""
        return self.zoom_factor
    
    def set_zoom_factor(self, zoom_factor):
        """Establece un nuevo factor de zoom y notifica a los interesados."""
        if self.zoom_factor != zoom_factor:
            self.zoom_factor = zoom_factor
            self.save_state()
            
            # Emitir señal Qt
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
        """Ejecuta el bucle principal de actualización."""
        first_time = True
        
        while self.running:
            try:
                # Obtiene información de la imagen desde Bing
                xml_content = download_content(Constants.get_wallpaper_info_url())
                if xml_content:
                    info = self.parse_wallpaper_info(xml_content)
                    
                    # Si hay una nueva imagen o no hay imagen establecida, la descarga
                    if info and info["picture_url"] != self.state["picture_url"] or not file_exists(Path(self.state["picture_file_path"])):
                        self.download_wallpaper(info)
                    elif first_time:
                        # Si no hay imagen nueva pero es la primera ejecución, establece la imagen actual
                        self.set_wallpaper(self.state["picture_file_path"])
                    
                    first_time = False
                
                # Espera antes de comprobar de nuevo
                for _ in range(Constants.Network.CHECK_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                log_error(f"Error en el bucle principal: {str(e)}")
                time.sleep(Constants.Network.RETRY_INTERVAL)  # Espera antes de intentar de nuevo
    
    def parse_wallpaper_info(self, xml_content):
        """Analiza la respuesta XML de Bing para obtener información de la imagen."""
        try:
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
                    "source": self.SOURCE_BING
                })
            
            # Devuelve el primer wallpaper si solo estamos obteniendo uno
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
        """Carga el historial de fondos de pantalla de los últimos días."""
        if days is None:
            days = Constants.Files.HISTORY_DAYS
            
        try:
            # Intenta cargar el historial guardado primero
            if "history" in self.state and self.state["history"]:
                self.wallpaper_history = self.state["history"]
            
            # Obtiene información sobre varios días de wallpapers
            xml_content = download_content(Constants.get_wallpaper_info_url(0, days))
            if xml_content:
                wallpapers = self.parse_wallpaper_info(xml_content)
                
                # Actualiza o agrega al historial
                if wallpapers:
                    self.wallpaper_history = wallpapers
                    
                    # Descarga las miniaturas y wallpapers en segundo plano
                    for idx, wallpaper in enumerate(self.wallpaper_history):
                        thumb_file = Constants.get_thumbnail_file(idx)
                        wallpaper_file = Constants.get_wallpaper_file(idx)
                        
                        # Descarga la miniatura si no existe
                        if not file_exists(thumb_file) and "thumbnail_url" in wallpaper:
                            download_file(wallpaper["thumbnail_url"], thumb_file)
                        
                        # Descarga el wallpaper si no existe (solo los primeros N para ahorrar espacio)
                        if idx < Constants.Files.MAX_FULL_WALLPAPERS_TO_DOWNLOAD and not file_exists(wallpaper_file) and "picture_url" in wallpaper:
                            download_file(wallpaper["picture_url"], wallpaper_file)
                    
                    # Guarda el estado actualizado
                    self.save_state()
            
            # Carga también los favoritos
            self.load_favorites()
            
        except Exception as e:
            log_error(f"Error al cargar historial de wallpapers: {str(e)}")
    
    def download_wallpaper(self, info):
        """Descarga el fondo de pantalla y lo establece."""
        try:
            wallpaper_file = Constants.get_wallpaper_file(0)
            
            # Descarga la imagen
            if download_file(info["picture_url"], wallpaper_file):
                # Descarga la miniatura
                thumb_file = Constants.get_thumbnail_file(0)
                download_file(info["thumbnail_url"], thumb_file)
                
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
                
                # Emite señal Qt
                self.download_completed.emit(self.state)
                
        except Exception as e:
            log_error(f"Error al descargar el fondo de pantalla: {str(e)}")
    
    def set_wallpaper(self, wallpaper_path):
        """Establece la imagen como fondo de pantalla de Windows."""
        wallpaper_path = os.path.abspath(wallpaper_path)
        
        # Establece el estilo de ajuste del fondo de pantalla (ajustar a pantalla)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                "Control Panel\\Desktop", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, Constants.Windows.WALLPAPER_STYLE_FIT)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, Constants.Windows.WALLPAPER_TILE)
            winreg.CloseKey(key)
        except Exception as e:
            log_error(f"Error al configurar el estilo del fondo: {str(e)}")
        
        # Cambia el fondo de pantalla
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                Constants.Windows.SPI_SETDESKWALLPAPER, 0, wallpaper_path, 
                Constants.Windows.SPIF_UPDATEINIFILE | Constants.Windows.SPIF_SENDCHANGE
            )
            # Emite señal Qt
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
        """Obtiene la información del wallpaper actual."""
        # Recarga los favoritos para tener la lista actualizada
        self.load_favorites()  
        
        if self.current_source == self.SOURCE_BING:
            if not self.wallpaper_history or self.current_wallpaper_index >= len(self.wallpaper_history):
                return None
            # Creamos una copia para evitar modificaciones accidentales
            current = self.wallpaper_history[self.current_wallpaper_index].copy()
            # Añadimos metadatos adicionales
            current["current_index"] = self.current_wallpaper_index
            current["total_images"] = len(self.wallpaper_history)
            current["source_name"] = "Bing Wallpaper"
            # Añadimos ruta del archivo
            current["file_path"] = str(Constants.get_wallpaper_file(self.current_wallpaper_index))
            return current
        else:  # Favoritos
            if not self.favorites or self.current_wallpaper_index >= len(self.favorites):
                return None
            # Para favoritos, añadimos metadatos adicionales
            favorite = self.favorites[self.current_wallpaper_index].copy()
            favorite["total_images"] = len(self.favorites)
            favorite["current_index"] = self.current_wallpaper_index
            return favorite    
    
    def get_wallpaper_count(self):
        """Obtiene el número de wallpapers disponibles en la fuente actual."""
        if self.current_source == self.SOURCE_BING:
            return len(self.wallpaper_history)
        else:  # Favoritos
            return len(self.favorites)
    
    def get_total_wallpaper_count(self):
        """Obtiene el número total de wallpapers disponibles."""
        return len(self.wallpaper_history) + len(self.favorites)
    
    def add_current_to_favorites(self):
        """Agrega el wallpaper actual a favoritos."""
        current = self.get_current_wallpaper()
        if not current:
            return False
            
        # Si ya es un favorito, no es necesario agregarlo de nuevo
        if current.get("source") == self.SOURCE_FAVORITE:
            return True
            
        # Agregar a favoritos
        result = WallpaperFavorites.add_to_favorites(current)
        
        # Recargar la lista de favoritos
        if result:
            self.load_favorites()
            
        return result
    
    def remove_from_favorites(self, favorite_id):
        """Elimina un wallpaper de favoritos."""
        result = WallpaperFavorites.remove_from_favorites(favorite_id)
        
        # Si estamos viendo el favorito que acabamos de eliminar, navegamos al siguiente
        if result and self.current_source == self.SOURCE_FAVORITE:
            current = self.get_current_wallpaper()
            if current and current.get("id") == favorite_id:
                # Intentar navegar al siguiente, si no se puede, al anterior
                if not self.navigate_to_next_wallpaper():
                    if not self.navigate_to_previous_wallpaper():
                        # Si no hay más favoritos, volver a Bing
                        if self.wallpaper_history:
                            self.navigate_to_wallpaper(0, self.SOURCE_BING)
        
        # Recargar la lista de favoritos
        self.load_favorites()
        
        return result
    
    def is_current_favorite(self):
        """Verifica si el wallpaper actual está en favoritos."""
        current = self.get_current_wallpaper()
        
        # Si ya estamos viendo un favorito, devolver su ID
        if current and current.get("source") == self.SOURCE_FAVORITE:
            return current.get("id")
            
        # En caso contrario, verificar si existe en favoritos
        return WallpaperFavorites.is_favorite(current)
    
    def toggle_current_favorite(self):
        """Alterna el estado de favorito del wallpaper actual."""
        favorite_id = self.is_current_favorite()
        
        if favorite_id:
            return self.remove_from_favorites(favorite_id)
        else:
            return self.add_current_to_favorites()