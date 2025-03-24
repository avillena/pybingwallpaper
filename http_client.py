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

