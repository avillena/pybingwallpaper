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
from ui import MainWindow, WallpaperNavigatorWindow
from run_windows_startup import StartupManager

# Constantes locales para la aplicación principal
class AppConstants:
    """Constantes específicas para la aplicación principal."""
    # Tamaño del icono de la aplicación
    ICON_SIZE = 64
    
    # Valores para dibujar el icono
    ICON_B_LEFT = 15
    ICON_B_TOP = 10
    ICON_B_WIDTH = 10
    ICON_B_HEIGHT = 44
    ICON_BOW_WIDTH = 20
    ICON_BOW_HEIGHT = 10
    ICON_BOW_TOP1 = 10
    ICON_BOW_TOP2 = 22
    ICON_BOW_TOP3 = 34
    
    # Colores para el icono
    ICON_BG_COLOR = (0, 120, 212, 255)  # Azul de Bing
    ICON_FG_COLOR = (255, 255, 255, 255)  # Blanco
    
    # Posición del icono en bandeja
    TRAY_OFFSET = 20
    
    # Tiempo de espera para join de threads
    THREAD_JOIN_TIMEOUT = 1.0

class BingWallpaperApp:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Permite ejecutar en segundo plano
        
        self.wallpaper_manager = WallpaperManager()
        self.main_window = None
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
        
        # Agrega método para acceso a la ventana principal
        self.app.access_app_window = self.show_main_window
        
        # Registra un callback para recrear las ventanas cuando cambie el zoom
        self.wallpaper_manager.add_zoom_changed_callback(self.handle_zoom_change)
    
    def handle_zoom_change(self, new_zoom_factor):
        """Maneja el cambio en el factor de zoom."""
        # Si las ventanas existen, las recreamos con el nuevo zoom
        if hasattr(self, 'navigator_window') and self.navigator_window:
            # La ventana de navegación se actualiza automáticamente a través de su propio callback
            pass
            
        if hasattr(self, 'main_window') and self.main_window:
            # Guardamos el estado de visibilidad de la ventana principal
            was_visible = self.main_window.isVisible()
            
            # Cerramos la ventana actual
            self.main_window.close()
            
            # Creamos una nueva ventana con el zoom actualizado
            self.main_window = MainWindow(self.wallpaper_manager)
            
            # Restauramos la visibilidad
            if was_visible:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
    
    def setup_app_icon(self):
        """Configura el icono de la aplicación."""
        # Intenta cargar un icono si existe, o crea uno básico
        icon_path = Constants.get_app_icon_file()
        
        # Si no existe el icono, crea uno básico usando Pillow
        if not icon_path.exists():
            try:
                # Crea una imagen cuadrada con fondo azul de Bing
                img = Image.new('RGBA', (AppConstants.ICON_SIZE, AppConstants.ICON_SIZE), AppConstants.ICON_BG_COLOR)
                draw = ImageDraw.Draw(img)
                
                # Dibuja una forma de 'B' simplificada
                b_left = AppConstants.ICON_B_LEFT
                b_right = b_left + AppConstants.ICON_B_WIDTH
                b_top = AppConstants.ICON_B_TOP
                b_bottom = b_top + AppConstants.ICON_B_HEIGHT
                
                # Línea vertical
                draw.rectangle((b_left, b_top, b_right, b_bottom), fill=AppConstants.ICON_FG_COLOR)
                
                # Líneas horizontales (tres arcos)
                bow_left = b_right
                bow_right = bow_left + AppConstants.ICON_BOW_WIDTH
                
                # Arco superior
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP1, 
                              bow_right, AppConstants.ICON_BOW_TOP1 + AppConstants.ICON_BOW_HEIGHT), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Arco medio
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP2, 
                              bow_right, AppConstants.ICON_BOW_TOP2 + AppConstants.ICON_BOW_HEIGHT), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Arco inferior
                draw.rectangle((bow_left, AppConstants.ICON_BOW_TOP3, 
                              bow_right + 4, AppConstants.ICON_BOW_TOP3 + AppConstants.ICON_BOW_HEIGHT * 2), 
                              fill=AppConstants.ICON_FG_COLOR)
                
                # Guarda la imagen
                img.save(str(icon_path))
            except Exception:
                # Si falla la creación, simplemente continuamos
                pass
        
        # Establece el icono de la aplicación
        self.app_icon = QIcon(str(icon_path) if icon_path.exists() else "")
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
        
        if lock_file.exists():
            # Comprueba si el proceso sigue en ejecución
            try:
                with open(lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Intenta obtener el proceso con ese PID
                if psutil.pid_exists(pid):
                    return False  # La aplicación ya está en ejecución
            except Exception:
                pass  # Si hay error, asumimos que el archivo está obsoleto
        
        # Crea el archivo de bloqueo con nuestro PID
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception:
            return True  # Si no podemos crear el archivo, continuamos de todos modos
    
    def send_show_message(self):
        """Envía un mensaje a la instancia en ejecución para mostrar la ventana."""
        try:
            show_signal = Constants.get_show_signal_file()
            with open(show_signal, 'w') as f:
                f.write("SHOW")
        except Exception:
            pass
    
    def check_show_signals(self):
        """Comprueba si hay señales para mostrar la ventana."""
        show_signal = Constants.get_show_signal_file()
        
        if show_signal.exists():
            try:
                show_signal.unlink()  # Elimina el archivo
                self.show_navigator_window()
            except Exception:
                pass
            
        # Programa la próxima comprobación
        QApplication.instance().processEvents()
        QTimer.singleShot(Constants.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
    
    def show_main_window(self):
        """Muestra la ventana principal."""
        if not self.main_window:
            self.main_window = MainWindow(self.wallpaper_manager)
        
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
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
        
        # Crea la ventana principal pero no la muestra automáticamente
        self.main_window = MainWindow(self.wallpaper_manager)
        
        # Crea la ventana de navegación
        self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager)
        
        # Si no se especifica /background, muestra la ventana
        if not self.running_in_background:
            self.show_navigator_window()
        
        # Inicia la comprobación de señales para mostrar la ventana
        QTimer.singleShot(Constants.SIGNAL_CHECK_INTERVAL, self.check_show_signals)
        
        # Ejecuta el bucle de eventos
        return self.app.exec_()
    
    def cleanup(self):
        """Limpia los recursos antes de salir."""
        # Detiene el gestor de fondos de pantalla
        self.wallpaper_manager.stop()
        
        # Elimina el archivo de bloqueo
        try:
            lock_file = Constants.get_lock_file()
            if lock_file.exists():
                lock_file.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    app = BingWallpaperApp()
    
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    
    sys.exit(exit_code)