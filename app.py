import os
import sys
import psutil
from pathlib import Path
from PIL import Image, ImageDraw
from PyQt5.QtCore import QTimer, QLocale, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction

from constants import Constants, tr
from core.bing_wallpaper_service import WallpaperManager
from ui import WallpaperNavigatorWindow
from sys_platform.windows.startup import StartupManager
from utils.logger import log_info, log_error
from utils.file_utils import file_exists, write_json, delete_file, read_json

class BingWallpaperApp:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Permite ejecutar en segundo plano
        
        # Inicializa la variable del idioma actual
        self.current_language = None
        
        # Configurar internacionalización
        self.setup_translation()
        
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
    
    def setup_translation(self):
        """Configura el sistema de traducción según el idioma del sistema o preferencia del usuario."""
        self.translator = QTranslator()
        
        # Verificar si existe una preferencia de idioma guardada
        language_file = Constants.get_data_path() / "language.json"
        language_settings = read_json(language_file, None)
        
        # Obtiene el idioma del sistema por defecto
        system_locale = QLocale.system().name()
        system_language = system_locale.split('_')[0]  # Por ejemplo, "es" de "es_ES"
        
        # Determinar qué idioma usar
        preferred_language = None
        if language_settings and "language" in language_settings:
            preferred_language = language_settings["language"]
            log_info(f"Usando idioma preferido por el usuario: {preferred_language}")
        else:
            preferred_language = system_language
            log_info(f"Idioma del sistema detectado: {system_locale}")
        
        # Guarda el idioma actual para que la UI pueda consultarlo
        self.current_language = preferred_language
        
        # Intentamos cargar el archivo de traducción correspondiente
        translations_path = Constants.get_translations_path()
        
        # Creamos el directorio de traducciones si no existe
        translations_path.mkdir(parents=True, exist_ok=True)
        
        # Intentamos cargar la traducción
        translation_loaded = False
        
        # Primero intentamos la traducción específica para el idioma preferido
        if translations_path.exists():
            # Intentar con locale completo primero (es_ES)
            if preferred_language == system_language:
                translation_file = translations_path / f"pybingwallpaper_{system_locale}.qm"
                if file_exists(translation_file):
                    if self.translator.load(str(translation_file)):
                        translation_loaded = True
                        log_info(f"Traducción cargada: {translation_file}")
            
            # Si no se cargó o se usa un idioma personalizado, intentar con el código de idioma genérico
            if not translation_loaded:
                translation_file = translations_path / f"pybingwallpaper_{preferred_language}.qm"
                if file_exists(translation_file):
                    if self.translator.load(str(translation_file)):
                        translation_loaded = True
                        log_info(f"Traducción cargada: {translation_file}")
        
        # Si se cargó alguna traducción, la instalamos en la aplicación
        if translation_loaded:
            self.app.installTranslator(self.translator)
            log_info("Traductor instalado en la aplicación")
        else:
            log_info("No se encontró archivo de traducción, usando textos predeterminados")
    
    def get_current_language(self):
        """Devuelve el idioma actual de la aplicación."""
        return self.current_language
    
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
        navigator_action = QAction(tr("Explorar fondos de pantalla"), self.app)
        navigator_action.triggered.connect(self.show_navigator_window)
        tray_menu.addAction(navigator_action)
        
        # Opción para iniciar con Windows
        startup_action = QAction(tr("Iniciar con Windows"), self.app)
        startup_action.setCheckable(True)
        startup_action.setChecked(StartupManager.get_run_on_startup())
        startup_action.triggered.connect(lambda checked: StartupManager.set_run_on_startup(checked))
        tray_menu.addAction(startup_action)
        
        tray_menu.addSeparator()
        
        # Acción para salir
        exit_action = QAction(tr("Salir"), self.app)
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
            self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager, self)
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
        self.navigator_window = WallpaperNavigatorWindow(self.wallpaper_manager, self)
        
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