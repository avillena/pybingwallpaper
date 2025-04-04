#!/usr/bin/env python3
"""
Python Bing Wallpaper App

Una aplicación para descargar y aplicar fondos de pantalla de Bing.
"""
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow

# Constantes
APP_NAME = "BingWallpaperApp"
DEFAULT_APP_DATA_DIR = "app_data"

def get_app_data_dir() -> str:
    """
    Obtiene el directorio de datos de la aplicación según el sistema operativo.
    
    Returns:
        Ruta completa al directorio de datos
    """
    home = Path.home()
    
    if sys.platform == "win32":
        # Windows: %APPDATA%\BingWallpaperApp
        app_data = os.getenv("APPDATA")
        if app_data:
            base_dir = Path(app_data) / APP_NAME
        else:
            base_dir = home / "AppData" / "Roaming" / APP_NAME
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/BingWallpaperApp
        base_dir = home / "Library" / "Application Support" / APP_NAME
    else:
        # Linux/Unix: ~/.config/BingWallpaperApp
        base_dir = home / ".config" / APP_NAME
    
    # Crear directorio si no existe
    os.makedirs(base_dir, exist_ok=True)
    
    # Devolver subdirectorio app_data
    app_data_dir = base_dir / DEFAULT_APP_DATA_DIR
    os.makedirs(app_data_dir, exist_ok=True)
    
    return str(app_data_dir)

def main():
    """Función principal de la aplicación."""
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("PythonBingWallpaper")
    
    # Obtener directorio de datos
    app_data_dir = get_app_data_dir()
    
    try:
        # Crear ventana principal
        window = MainWindow(app_data_dir)
        window.show()
        
        # Ejecutar loop principal
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
