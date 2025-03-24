# resource_utils.py
import os
import subprocess
import platform
from pathlib import Path
from logger import log_error

def open_url(url):
    """
    Abre una URL en el navegador web predeterminado.
    
    Args:
        url: URL a abrir
        
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        # Diferentes métodos según la plataforma
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(url)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', url], check=True)
        else:  # Linux y otros
            subprocess.run(['xdg-open', url], check=True)
        return True
    except Exception as e:
        log_error(f"Error al abrir URL {url}: {str(e)}")
        return False

def open_folder(folder_path):
    """
    Abre una carpeta en el explorador de archivos.
    
    Args:
        folder_path: Ruta a la carpeta
        
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        folder_path = Path(folder_path)
        if not folder_path.exists():
            return False
            
        # Diferentes métodos según la plataforma
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(folder_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux y otros
            subprocess.run(['xdg-open', folder_path], check=True)
        return True
    except Exception as e:
        log_error(f"Error al abrir carpeta {folder_path}: {str(e)}")
        return False