import ctypes
import os
from typing import Optional

# Constantes para Windows
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
WALLPAPER_STYLE_FILL = 10  # Valor para estilo de wallpaper "Fill" en Windows

class WallpaperService:
    """
    Servicio para establecer una imagen como fondo de pantalla del sistema.
    
    Implementación específica para Windows.
    """
    
    @staticmethod
    def set_as_wallpaper(image_path: str) -> bool:
        """
        Establece una imagen como fondo de pantalla del sistema.
        
        Args:
            image_path: Ruta absoluta a la imagen
            
        Returns:
            True si se pudo establecer, False en caso contrario
        """
        if not os.path.isfile(image_path):
            return False
            
        try:
            # Convertir a ruta absoluta
            abs_path = os.path.abspath(image_path)
            
            # Configurar el estilo de wallpaper para llenar la pantalla
            # Windows Registry: HKEY_CURRENT_USER\Control Panel\Desktop\WallpaperStyle
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 
                0, 
                abs_path, 
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            return True
        except Exception:
            return False
            
    @staticmethod
    def get_current_wallpaper() -> Optional[str]:
        """
        Obtiene la ruta del fondo de pantalla actual.
        
        Returns:
            Ruta del fondo de pantalla o None si no se pudo obtener
        """
        try:
            # Obtener la longitud necesaria para el buffer
            buffer_size = ctypes.c_int(260)  # MAX_PATH = 260
            path_buffer = ctypes.create_unicode_buffer(buffer_size.value)
            
            # Obtener la ruta del fondo de pantalla
            if ctypes.windll.user32.SystemParametersInfoW(0x0073, buffer_size, path_buffer, 0):
                return path_buffer.value
            return None
        except Exception:
            return None
