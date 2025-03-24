# file_utils.py
import json
import os
import shutil
from pathlib import Path
from logger import log_error, log_info

def ensure_directory(directory_path):
    """Asegura que un directorio exista, creándolo si es necesario."""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        log_error(f"Error al crear directorio {directory_path}: {str(e)}")
        return False

def read_json(file_path, default=None):
    """Lee y parsea un archivo JSON con manejo de errores."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_info(f"Archivo no encontrado: {file_path}, retornando valor por defecto")
        return default if default is not None else {}
    except json.JSONDecodeError:
        log_error(f"JSON inválido en archivo {file_path}, retornando valor por defecto")
        return default if default is not None else {}
    except Exception as e:
        log_error(f"Error al leer archivo JSON {file_path}: {str(e)}")
        return default if default is not None else {}

def write_json(file_path, data, indent=4):
    """Escribe datos en un archivo JSON con manejo de errores."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        log_error(f"Error al escribir archivo JSON {file_path}: {str(e)}")
        return False

def copy_file(source, destination):
    """Copia un archivo con manejo de errores."""
    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        log_error(f"Error al copiar archivo de {source} a {destination}: {str(e)}")
        return False

def delete_file(file_path):
    """Elimina un archivo con manejo de errores."""
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception as e:
        log_error(f"Error al eliminar archivo {file_path}: {str(e)}")
        return False

def file_exists(file_path):
    """Comprueba si un archivo existe."""
    return Path(file_path).exists()

