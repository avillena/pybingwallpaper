import os
import sys
import psutil
from pathlib import Path
from PIL import Image, ImageDraw
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction

from constants import Constants
from bing_wallpaper_service import WallpaperManager
from ui import WallpaperNavigatorWindow
from run_windows_startup import StartupManager
from logger import log_info, log_error
from file_utils import file_exists, write_json, delete_file

class BingWallpaperApp:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Permite ejecutar en segundo plano
        
        self.wallpaper_manager = WallpaperManager()
        self.navigator_window = None
        self.tray_icon = None
        
        # Carga los iconos
        self.setup_app_icon()
        
        # Verifica si hay una instancia en ejecución
        self.running_in_background = "/background" in sys.argv
        self.is_first_instance = self.check_single_instance()
        
        if not self.is_first_instance:
            # Si ya hay una instancia, envía un mensaje para mostrar la ventana
            if not self.running_in_background:
                self.send_show_message()
            sys.exit(0)
        
        # Registra un callback para recrear las ventanas cuando cambie el zoom
        self.wallpaper_manager.zoom_changed.connect(self.handle_zoom_change)
    
    def handle_zoom_change(self, new_zoom_factor):
        """Maneja el cambio en el factor de zoom."""
        # Si la ventana existe, la recreamos con el nuevo zoom
        if hasattr(self, 'navigator_window') and self.navigator_window:
            # La ventana de navegación se actualiza automáticamente a través de su propio callback
            pass
    
    def setup_app_icon(self):
        """Configura el icono de la aplicación."""
        # Intenta cargar un icono si existe, o crea uno básico
        icon_path = Constants.get_app_icon_file()
        
        # Si no existe el icono, crea uno básico usando Pillow
        if not file_exists(icon_path):
            try:
                # Crea una imagen cuadrada con fondo azul de Bing
                img = Image.new('RGBA', (Constants.UI.ICON_SIZE, Constants.UI.ICON_SIZE), 
                               (0, 120, 212, 255))  # Azul de Bing
                draw = ImageDraw.Draw(img)
                
                # Dibuja una forma de 'B' simplificada
                b_left = 15
                b_right = b_left + 10
                b_top = 10
                b_bottom = b_top + 44
                
                # Línea vertical
                draw.rectangle((b_left, b_top, b_right, b_bottom), fill=(255, 255, 255, 255))
                
                # Líneas horizontales (tres arcos)
                bow_left = b_right
                bow_right = bow_left + 20
                
                # Arco superior
                draw.rectangle((bow_left, 10, bow_right, 10 + 10), fill=(255, 255, 255, 255))
                
                # Arco medio
                draw.rectangle((bow_left, 22, bow_right, 22 + 10), fill=(255, 255, 255, 255))
                
                # Arco inferior
                draw.rectangle((bow_left, 34, bow_right + 4, 34 + 10 * 2), fill=(255, 255, 255, 255))
                
                # Guarda la imagen
                img.save(str(icon_path))
            except Exception as e:
                log_error(f"Error al crear icono: {str(e)}")
        
        # Establece el icono de la aplicación
        self.app_icon = QIcon(str(icon_path) if file_exists(icon_path) else "")
        if not self.app_icon.isNull():
            self.app.setWindowIcon(self.app_icon)
    
    def setup_tray_icon(self):
        """Configura el icono de la bandeja del sistema."""
        # Si no hay icono de aplicación válido, intenta usar uno del sistema
        if self.app_icon.isNull():
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("image", QIcon()))
        else:
            self.tray_icon = QSystemTrayIcon(self.app_icon)
        
        # Crea el menú contextual
        tray_menu = QMenu()
        
        # Acción para abrir el navegador de wallpapers
        navigator_action = QAction("Explorar fondos de pantalla", self.app)
        navigator_action.triggered.connect(self.show_navigator_window)
        tray_menu.addAction(navigator_action)
        
        # Opción para iniciar con Windows
        startup_action = QAction("Iniciar con Windows", self.app)
        startup_action.setCheckable(True)
        startup_action.setChecked(StartupManager.get_run_on_startup())
        startup_action.triggered.connect(lambda checked: StartupManager.set_run_on_startup(checked))
        tray_menu.addAction(startup_action)
        
        tray_menu.addSeparator()
        
        # Acción para salir
        exit_action = QAction("Salir", self.app)
        exit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(exit_action)
        
        # Asigna el menú al icono
        self.tray_icon.setContextMenu(tray_menu)
        
        # Conecta el evento de clic del icono para mostrar/ocultar el navegador
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Tooltip para el icono
        self.tray_icon.setToolTip(Constants.APP_NAME)
        
        # Muestra el icono
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        """Maneja los eventos de activación del icono de la bandeja."""
        # Al hacer clic en el icono, alterna la visibilidad de la ventana de navegación
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.navigator_window and self.navigator_window.isVisible():
                self.navigator_window.hide()
            else:
                self.show_navigator_window()
    
    def check_single_instance(self):
        """Verifica si ya hay una instancia en ejecución."""
        lock_file = Constants.get_lock_file()
        
        if file_exists(lock_file):
            # Comprueba si el proceso sigue en ejecución
            try:
                with open(lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Intenta obtener el proceso con ese PID
                if psutil.pid_exists(pid):
                    return False  # La aplicación ya está en ejecución
            except Exception as e:
                log_error(f"Error al verificar instancia: {str(e)}")
        
        # Crea el archivo de bloqueo con nuestro PID
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception as e:
            log_error(f"Error al crear archivo de bloqueo: {str(e)}")
            return True  # Si no podemos crear el archivo, continuamos de todos modos
    
    def send_show_message(self):
        """Envía un mensaje a la instancia en ejecución para mostrar la ventana."""
        try:
            show_signal = Constants.get_show_signal_file()
            write_json(show_signal, {"action": "SHOW"})
        except Exception as e:
            log_error(f"Error al enviar señal de mostrar: {str(e)}")
    
    def check_show_signals(self):
        """Comprueba si hay señales para mostrar la ventana."""
        show_signal = Constants.get_show_signal_file()
        
        if file_exists(show_signal):
            try:
                delete_file(show_signal)  # Elimina el archivo
                self.show_navigator_window()
            except Exception as e:
                log_error(f"Error al procesar señal de mostrar: {str(e)}")
            
        # Programa la próxima comprobación
        QApplication.instance().processEvents()
        QTimer.singleShot(Constants.Network.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
    
    def show_navigator_window(self):
        """Muestra la ventana de navegación de wallpapers."""
        if not self.navigator_window:
            self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager)
        else:
            self.navigator_window.update_content()
        
        self.navigator_window.show()
        self.navigator_window.raise_()
        self.navigator_window.activateWindow()
    
    def run(self):
        """Ejecuta la aplicación."""
        # Inicia el gestor de fondos de pantalla
        self.wallpaper_manager.start()
        
        # Configura el icono de la bandeja del sistema
        self.setup_tray_icon()
        
        # Crea la ventana de navegación
        self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager)
        
        # Si no se especifica /background, muestra la ventana
        if not self.running_in_background:
            self.show_navigator_window()
        
        # Inicia la comprobación de señales para mostrar la ventana
        QTimer.singleShot(Constants.Network.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
        
        # Ejecuta el bucle de eventos
        return self.app.exec_()
    
    def cleanup(self):
        """Limpia los recursos antes de salir."""
        # Detiene el gestor de fondos de pantalla
        self.wallpaper_manager.stop()
        
        # Elimina el archivo de bloqueo
        try:
            delete_file(Constants.get_lock_file())
        except Exception as e:
            log_error(f"Error al eliminar archivo de bloqueo: {str(e)}")


if __name__ == "__main__":
    app = BingWallpaperApp()
    
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    
    sys.exit(exit_code)