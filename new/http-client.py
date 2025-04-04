# http_client.py
import os
import requests
from pathlib import Path
from utils.logger import log_error, log_info

def download_file(url, destination_path, chunk_size=8192, max_retries=3):
    """
    Descarga un archivo desde una URL a una ruta local con validación y reintentos.
    
    Args:
        url: URL desde donde descargar
        destination_path: Ruta donde guardar el archivo
        chunk_size: Tamaño de los chunks para descarga en streaming
        max_retries: Número máximo de reintentos en caso de error
        
    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario
    """
    # Asegurarse de que destination_path es un objeto Path
    destination_path = Path(destination_path)
    temp_file = destination_path.with_suffix('.temp')
    
    for attempt in range(max_retries):
        try:
            # Usar un archivo temporal para evitar archivos parciales
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # Verificar que el contenido es una imagen
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    log_error(f"El contenido no es una imagen: {content_type} para URL {url}")
                    return False
                
                # Obtener el tamaño esperado del archivo
                expected_size = int(response.headers.get('Content-Length', 0))
                log_info(f"Descargando {url} - Tamaño esperado: {expected_size} bytes")
                
                # Descargar a un archivo temporal
                actual_size = 0
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:  # filtrar keep-alive chunks
                            f.write(chunk)
                            actual_size += len(chunk)
            
            # Verificar el tamaño del archivo descargado
            if expected_size > 0 and actual_size != expected_size:
                log_error(f"Tamaño de archivo incorrecto: esperado {expected_size}, obtenido {actual_size}")
                if attempt < max_retries - 1:
                    log_info(f"Reintentando descarga ({attempt + 1}/{max_retries})...")
                    continue
                return False
            
            # Si todo está correcto, mover el archivo temporal al destino final
            if temp_file.exists():
                # Verificar integridad básica de imagen JPEG
                if verify_jpeg_integrity(temp_file):
                    # Renombrar al destino final
                    if destination_path.exists():
                        os.remove(destination_path)
                    os.rename(temp_file, destination_path)
                    log_info(f"Descarga completada: {url} -> {destination_path}")
                    return True
                else:
                    log_error(f"El archivo descargado no es un JPEG válido: {url}")
                    if attempt < max_retries - 1:
                        log_info(f"Reintentando descarga ({attempt + 1}/{max_retries})...")
                        continue
                    return False
            
        except requests.RequestException as e:
            log_error(f"Error en la petición HTTP al descargar {url}: {str(e)}")
            if attempt < max_retries - 1:
                log_info(f"Reintentando descarga ({attempt + 1}/{max_retries})...")
                continue
        except Exception as e:
            log_error(f"Error al descargar {url} a {destination_path}: {str(e)}")
            if attempt < max_retries - 1:
                log_info(f"Reintentando descarga ({attempt + 1}/{max_retries})...")
                continue
        finally:
            # Limpiar archivo temporal en caso de error
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    return False

def verify_jpeg_integrity(file_path):
    """
    Verifica que un archivo sea un JPEG válido comprobando sus marcadores.
    
    Args:
        file_path: Ruta al archivo a verificar
        
    Returns:
        bool: True si el archivo parece ser un JPEG válido
    """
    try:
        with open(file_path, 'rb') as f:
            # Verificar la firma JPEG (SOI marker): FF D8
            header = f.read(2)
            if header != b'\xFF\xD8':
                return False
            
            # Buscar el marcador EOI (End of Image): FF D9
            f.seek(-2, os.SEEK_END)
            footer = f.read(2)
            return footer == b'\xFF\xD9'
    except Exception as e:
        log_error(f"Error al verificar integridad JPEG de {file_path}: {str(e)}")
        return False

def download_content(url):
    """
    Descarga contenido desde una URL.
    
    Args:
        url: URL desde donde descargar
        
    Returns:
        Response o None: Objeto de respuesta si la descarga fue exitosa, None en caso contrario
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response
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
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        log_error(f"Error al descargar binario de {url}: {str(e)}")
        return None
