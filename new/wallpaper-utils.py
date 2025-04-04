import os
from pathlib import Path
from typing import Callable, Optional

from constants import Constants
from utils.http_client import download_file
from utils.file_utils import file_exists
from utils.logger import log_info, log_error

def reformat_date(date_str: str) -> str:
    """
    Convierte un string de fecha en formato 'YYYYMMDD' a 'YYYY-MM-DD' si es necesario.
    Si la fecha ya contiene guiones, la retorna tal cual.
    """
    if '-' not in date_str and len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str

def construct_picture_url(date_str: str) -> str:
    """
    Construye la URL del wallpaper en alta resolución usando el date_str.
    Se basa en el formato definido en Constants y utiliza país, idioma y la fecha en formato 'YYYY-MM-DD'.
    """
    formatted_date = reformat_date(date_str)
    return Constants.get_picture_url_format().format(
        Constants.BING_ARCHIVE_COUNTRY, Constants.BING_ARCHIVE_LANGUAGE, formatted_date
    )

def construct_thumbnail_url(date_str: str) -> str:
    """
    Construye la URL de la miniatura usando el date_str.
    Se basa en el formato definido en Constants y utiliza país, idioma y la fecha en formato 'YYYY-MM-DD'.
    """
    formatted_date = reformat_date(date_str)
    return Constants.get_thumbnail_url_format().format(
        Constants.BING_ARCHIVE_COUNTRY, Constants.BING_ARCHIVE_LANGUAGE, formatted_date
    )

def _ensure_file_downloaded(date_str: str, file_suffix: str, url_constructor: Callable[[str], str]) -> Optional[Path]:
    """
    Función genérica para asegurar que un archivo (wallpaper o miniatura) esté descargado.

    Args:
        date_str: La fecha en formato 'YYYYMMDD' o 'YYYY-MM-DD'.
        file_suffix: Sufijo para el nombre del archivo (por ejemplo, ".jpg" o "_thumb.jpg").
        url_constructor: Función que, a partir de date_str, construye la URL correspondiente.

    Returns:
        El Path del archivo descargado o existente; o None si falla la descarga.
    """
    # Usamos la fecha sin guiones para el nombre del archivo
    file_date = date_str.replace("-", "")
    wallpapers_dir: Path = Constants.get_wallpapers_path()
    local_file: Path = wallpapers_dir / f"{file_date}{file_suffix}"
    
    if not file_exists(local_file):
        url = url_constructor(date_str)
        if file_suffix.startswith("_thumb"):
            log_info(f"Descargando miniatura {date_str} desde {url}...")
        else:
            log_info(f"Descargando wallpaper {date_str} desde {url}...")
        
        if download_file(url, local_file):
            return local_file
        else:
            if file_suffix.startswith("_thumb"):
                log_error(f"Error al descargar miniatura {date_str}.")
            else:
                log_error(f"Error al descargar wallpaper {date_str}.")
            return None
    else:
        if file_suffix.startswith("_thumb"):
            log_info(f"Miniatura {date_str} ya existe.")
        else:
            log_info(f"Wallpaper {date_str} ya existe.")
    return local_file

def ensure_wallpaper_downloaded(date_str: str) -> Optional[Path]:
    """
    Asegura que el wallpaper identificado por date_str esté descargado.
    
    Returns:
        El Path del wallpaper o None si falla la descarga.
    """
    return _ensure_file_downloaded(date_str, ".jpg", construct_picture_url)

def ensure_thumbnail_downloaded(date_str: str) -> Optional[Path]:
    """
    Asegura que la miniatura del wallpaper identificado por date_str esté descargado.
    
    Returns:
        El Path de la miniatura o None si falla la descarga.
    """
    return _ensure_file_downloaded(date_str, "_thumb.jpg", construct_thumbnail_url)

def build_wallpaper_info_by_date(date_str: str) -> Optional[dict]:
    """
    Construye y retorna el diccionario de información del wallpaper basado en date_str.
    Se asegura de que el wallpaper (y la miniatura) estén descargados.
    
    Returns:
        Diccionario con los datos del wallpaper o None si falla la descarga.
    """
    local_file = ensure_wallpaper_downloaded(date_str)
    if local_file is None:
        return None
    
    # Intentar descargar la miniatura; su ausencia no impide la construcción de la info.
    ensure_thumbnail_downloaded(date_str)
    
    wallpaper_info = {
        "picture_url": construct_picture_url(date_str),
        "thumbnail_url": construct_thumbnail_url(date_str),
        "copyright": f"Wallpaper {date_str}",
        "date": date_str,
        "file_path": str(local_file),
        "current_index": 0  # Este valor no es relevante en este contexto
    }
    return wallpaper_info
