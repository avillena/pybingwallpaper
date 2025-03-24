## File: bing_wallpaper_service.py

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
        self.download_completed_callbacks = []
        self.wallpaper_changed_callbacks = []
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
            "current_index": 0
        }
    
    def save_state(self):
        """Guarda el estado en un archivo."""
        try:
            self.state["history"] = self.wallpaper_history
            self.state["current_source"] = self.current_source
            self.state["current_index"] = self.current_wallpaper_index
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

