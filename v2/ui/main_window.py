import os
import logging
from enum import Enum, auto
from datetime import datetime
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QMessageBox, QMenu
)
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSlot

from models.wallpaper import Wallpaper, Country, Language
from services.bing_service import BingService
from services.wallpaper_service import WallpaperService
from services.favorites_service import FavoritesService

# Constantes
WINDOW_TITLE = "Python Bing Wallpaper"
WINDOW_WIDTH = 550
WINDOW_HEIGHT = 480
DEFAULT_APP_DATA_DIR = "app_data"
DEFAULT_ICON_SIZE = QSize(24, 24)
MISSING_IMAGE_TEXT = "No se pudo cargar la imagen"
COPYRIGHT_TEMPLATE = "© {year} Bing - {date}"
NO_FAVORITES_MESSAGE = "No tienes wallpapers favoritos guardados.\nUsa el botón de corazón para añadir el wallpaper actual a favoritos."
APPLY_SUCCESS_MESSAGE = "¡Wallpaper aplicado correctamente!"
APPLY_ERROR_MESSAGE = "Error al aplicar el wallpaper"
FAVORITE_ADDED_MESSAGE = "Wallpaper añadido a favoritos"
FAVORITE_REMOVED_MESSAGE = "Wallpaper eliminado de favoritos"

class ApplicationState(Enum):
    """Estados posibles de la aplicación."""
    CURRENT = auto()    # S0: Wallpaper del día actual
    NAVIGATION = auto() # S1: Navegando por fechas anteriores
    SPECIFIC = auto()   # S2: Visualizando un wallpaper específico
    FAVORITE = auto()   # S3: Visualizando un favorito aleatorio
    APPLYING = auto()   # S4: Aplicando un wallpaper (estado temporal)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self, app_data_dir: str = DEFAULT_APP_DATA_DIR):
        super().__init__()
        
        # Servicios
        self.app_data_dir = os.path.abspath(app_data_dir)
        self.bing_service = BingService(Country.US, Language.EN)
        self.favorites_service = FavoritesService(self.app_data_dir)
        self.wallpaper_service = WallpaperService()
        
        # Estado actual
        self.current_state = ApplicationState.CURRENT
        self.current_wallpaper = None
        self.today_date = self.bing_service.get_today_date()
        
        # Inicializar UI
        self.init_ui()
        
        # Limpiar caché y cargar wallpaper actual
        self.favorites_service.clean_cache()
        self.load_current_wallpaper()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Configuración de la ventana principal
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear componentes
        self.create_header()
        self.create_wallpaper_container()
        self.create_action_bar()
        
        # Agregar componentes al layout principal
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.wallpaper_container, 1)  # 1 = stretch factor
        main_layout.addWidget(self.action_bar)
        
        # Crear menú
        self.create_menu()
        
        # Aplicar estilos
        self.apply_styles()
    
    def create_header(self):
        """Crea la barra de encabezado."""
        self.header = QFrame()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Título de la aplicación
        title_label = QLabel(WINDOW_TITLE)
        title_label.setObjectName("app-title")
        
        # Controles de la derecha
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        # Botón de favoritos
        self.favorite_button = QPushButton("♥")
        self.favorite_button.setToolTip("Añadir a Favoritos")
        self.favorite_button.setFixedSize(30, 30)
        self.favorite_button.setObjectName("icon-button")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        
        # Botón de configuración
        settings_button = QPushButton("⚙")
        settings_button.setToolTip("Configuración")
        settings_button.setFixedSize(30, 30)
        settings_button.setObjectName("icon-button")
        settings_button.clicked.connect(self.show_settings_menu)
        
        # Agregar botones al layout de controles
        controls_layout.addWidget(self.favorite_button)
        controls_layout.addWidget(settings_button)
        
        # Agregar componentes al layout del encabezado
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)  # Espacio flexible
        header_layout.addLayout(controls_layout)
        
    def create_wallpaper_container(self):
        """Crea el contenedor principal para la imagen del wallpaper."""
        self.wallpaper_container = QFrame()
        self.wallpaper_container.setObjectName("wallpaper-container")
        wallpaper_layout = QVBoxLayout(self.wallpaper_container)
        wallpaper_layout.setContentsMargins(0, 0, 0, 0)
        
        # Contenedor para la imagen
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setObjectName("wallpaper-image")
        
        # Información del wallpaper (overlay)
        self.info_overlay = QFrame()
        self.info_overlay.setObjectName("info-overlay")
        info_layout = QVBoxLayout(self.info_overlay)
        
        # Título del wallpaper
        self.title_label = QLabel()
        self.title_label.setObjectName("wallpaper-title")
        self.title_label.setWordWrap(True)
        
        # Descripción del wallpaper
        self.description_label = QLabel()
        self.description_label.setObjectName("wallpaper-description")
        self.description_label.setWordWrap(True)
        
        # Copyright
        self.copyright_label = QLabel()
        self.copyright_label.setObjectName("copyright")
        
        # Agregar labels al layout de información
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.description_label)
        info_layout.addWidget(self.copyright_label)
        
        # Agregar componentes al layout principal
        wallpaper_layout.addWidget(self.image_label, 1)  # 1 = stretch factor
        wallpaper_layout.addWidget(self.info_overlay)
        
    def create_action_bar(self):
        """Crea la barra de acciones inferior."""
        self.action_bar = QFrame()
        self.action_bar.setObjectName("action-bar")
        action_layout = QHBoxLayout(self.action_bar)
        action_layout.setContentsMargins(15, 15, 15, 15)
        
        # Botón para aplicar wallpaper
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.setObjectName("btn-primary")
        self.apply_button.clicked.connect(self.apply_wallpaper)
        
        # Controles de navegación
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)
        
        # Botón Anterior
        self.prev_button = QPushButton("⟨")
        self.prev_button.setToolTip("Anterior")
        self.prev_button.setFixedSize(36, 36)
        self.prev_button.setObjectName("nav-btn")
        self.prev_button.clicked.connect(self.load_previous_wallpaper)
        
        # Botón Aleatorio
        self.random_button = QPushButton("🍀")
        self.random_button.setToolTip("Aleatorio")
        self.random_button.setFixedSize(36, 36)
        self.random_button.setObjectName("nav-btn")
        self.random_button.clicked.connect(self.load_random_favorite)
        
        # Botón Siguiente
        self.next_button = QPushButton("⟩")
        self.next_button.setToolTip("Siguiente")
        self.next_button.setFixedSize(36, 36)
        self.next_button.setObjectName("nav-btn")
        self.next_button.clicked.connect(self.load_next_wallpaper)
        
        # Agregar botones al layout de navegación
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.random_button)
        nav_layout.addWidget(self.next_button)
        
        # Agregar componentes al layout de acciones
        action_layout.addWidget(self.apply_button)
        action_layout.addStretch(1)  # Espacio flexible
        action_layout.addLayout(nav_layout)
        
    def create_menu(self):
        """Crea el menú de la aplicación."""
        # Menú de configuración (se mostrará al hacer clic en el botón de configuración)
        self.settings_menu = QMenu(self)
        
        # Acción para abrir carpeta de favoritos
        open_favorites_action = QAction("Abrir carpeta de favoritos", self)
        open_favorites_action.triggered.connect(self.open_favorites_folder)
        self.settings_menu.addAction(open_favorites_action)
        
    def apply_styles(self):
        """Aplica estilos CSS a la interfaz desde el archivo externo."""
        try:
            # Buscar archivo de estilos en la ruta relativa al módulo
            style_file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "resources",
                "styles",
                "dark_theme.qss"
            )
            
            # Si el archivo existe, cargarlo
            if os.path.exists(style_file_path):
                with open(style_file_path, "r", encoding="utf-8") as styles_file:
                    self.setStyleSheet(styles_file.read())
                logging.info(f"Estilos cargados desde: {style_file_path}")
            else:
                # Si no se encuentra, registrar advertencia
                logging.warning(f"Archivo de estilos no encontrado: {style_file_path}")
        except Exception as e:
            # En caso de error, registrarlo
            logging.error(f"Error al cargar los estilos: {e}")
    
    def load_current_wallpaper(self):
        """Carga el wallpaper del día actual."""
        wallpaper = self.bing_service.get_wallpaper_by_date(self.today_date)
        if wallpaper:
            self.current_wallpaper = wallpaper
            self.current_state = ApplicationState.CURRENT
            self.display_wallpaper(wallpaper)
            self.update_ui_controls()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el wallpaper del día")
    
    def load_previous_wallpaper(self):
        """Carga el wallpaper del día anterior."""
        if not self.current_wallpaper:
            return
            
        prev_date = self.bing_service.get_previous_date(self.current_wallpaper.date)
        wallpaper = self.bing_service.get_wallpaper_by_date(prev_date)
        
        if wallpaper:
            self.current_wallpaper = wallpaper
            # Si estamos en estado inicial, cambiar a navegación
            if self.current_state == ApplicationState.CURRENT:
                self.current_state = ApplicationState.NAVIGATION
            self.display_wallpaper(wallpaper)
            self.update_ui_controls()
    
    def load_next_wallpaper(self):
        """Carga el wallpaper del día siguiente."""
        if not self.current_wallpaper or self.current_state == ApplicationState.CURRENT:
            return
            
        next_date = self.bing_service.get_next_date(self.current_wallpaper.date)
        
        # Si la siguiente fecha es hoy, volver al estado actual
        if next_date == self.today_date:
            self.current_state = ApplicationState.CURRENT
            self.load_current_wallpaper()
            return
            
        wallpaper = self.bing_service.get_wallpaper_by_date(next_date)
        if wallpaper:
            self.current_wallpaper = wallpaper
            self.display_wallpaper(wallpaper)
            self.update_ui_controls()
    
    def load_random_favorite(self):
        """Carga un wallpaper aleatorio de favoritos."""
        random_wallpaper = self.favorites_service.get_random_favorite()
        
        if not random_wallpaper:
            QMessageBox.information(
                self, 
                "Sin favoritos", 
                NO_FAVORITES_MESSAGE
            )
            return
        
        self.current_wallpaper = random_wallpaper
        self.current_state = ApplicationState.FAVORITE
        self.display_wallpaper(random_wallpaper)
        self.update_ui_controls()
    
    def display_wallpaper(self, wallpaper: Wallpaper):
        """
        Muestra un wallpaper en la interfaz.
        
        Args:
            wallpaper: Objeto Wallpaper a mostrar
        """
        # Descargar si es necesario
        cache_path = self.favorites_service.get_wallpaper_path(
            wallpaper.country, 
            wallpaper.language, 
            wallpaper.date,
            is_favorite=False
        )
        
        file_path = wallpaper.file_path
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            # Verificar si existe en caché o favoritos
            if os.path.exists(cache_path):
                file_path = cache_path
            else:
                fav_path = self.favorites_service.get_wallpaper_path(
                    wallpaper.country, 
                    wallpaper.language, 
                    wallpaper.date,
                    is_favorite=True
                )
                if os.path.exists(fav_path):
                    file_path = fav_path
                else:
                    # Descargar si no existe
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    self.bing_service.download(wallpaper, os.path.dirname(cache_path))
                    file_path = cache_path
        
        # Cargar imagen
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Escalar imagen manteniendo relación de aspecto
            pixmap = pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(MISSING_IMAGE_TEXT)
        
        # Actualizar información
        self.title_label.setText(wallpaper.title)
        self.description_label.setText(wallpaper.description)
        
        # Fecha para copyright
        try:
            date_obj = datetime.strptime(wallpaper.date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d de %B, %Y")
        except ValueError:
            formatted_date = wallpaper.date
            
        # Actualizar copyright
        self.copyright_label.setText(
            COPYRIGHT_TEMPLATE.format(
                year=date_obj.year, 
                date=formatted_date
            )
        )
        
        # Actualizar estado del botón de favoritos
        is_favorite = self.favorites_service.is_favorite(
            wallpaper.country,
            wallpaper.language,
            wallpaper.date
        )
        self.favorite_button.setProperty("favorite", "true" if is_favorite else "false")
        self.favorite_button.setStyleSheet("") # Forzar actualización de estilo
    
    def update_ui_controls(self):
        """Actualiza el estado de los controles según el estado actual de la aplicación."""
        if not self.current_wallpaper:
            return
            
        # Botón siguiente habilitado solo si no estamos en el día actual
        is_current = self.bing_service.is_current_date(self.current_wallpaper.date)
        self.next_button.setEnabled(not is_current and self.current_state != ApplicationState.CURRENT)
        
        # Actualizar estilo del botón de favoritos
        is_favorite = self.favorites_service.is_favorite(
            self.current_wallpaper.country,
            self.current_wallpaper.language,
            self.current_wallpaper.date
        )
        self.favorite_button.setProperty("favorite", "true" if is_favorite else "false")
        self.favorite_button.style().unpolish(self.favorite_button)
        self.favorite_button.style().polish(self.favorite_button)
    
    def apply_wallpaper(self):
        """Aplica el wallpaper actual como fondo de pantalla del sistema."""
        if not self.current_wallpaper:
            return
            
        # Transición a estado APPLYING
        previous_state = self.current_state
        self.current_state = ApplicationState.APPLYING
        
        # Verificar que el archivo existe
        file_path = self.current_wallpaper.file_path
        if not os.path.exists(file_path):
            # Intentar encontrarlo en caché o favoritos
            cache_path = self.favorites_service.get_wallpaper_path(
                self.current_wallpaper.country,
                self.current_wallpaper.language,
                self.current_wallpaper.date,
                is_favorite=False
            )
            if os.path.exists(cache_path):
                file_path = cache_path
            else:
                fav_path = self.favorites_service.get_wallpaper_path(
                    self.current_wallpaper.country,
                    self.current_wallpaper.language,
                    self.current_wallpaper.date,
                    is_favorite=True
                )
                if os.path.exists(fav_path):
                    file_path = fav_path
        
        # Aplicar wallpaper
        if os.path.exists(file_path):
            success = self.wallpaper_service.set_as_wallpaper(file_path)
            
            if success:
                # Añadir a favoritos automáticamente
                self.favorites_service.add_favorite(self.current_wallpaper)
                QMessageBox.information(self, "Éxito", APPLY_SUCCESS_MESSAGE)
            else:
                QMessageBox.warning(self, "Error", APPLY_ERROR_MESSAGE)
        else:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el archivo del wallpaper")
        
        # Volver al estado anterior
        self.current_state = previous_state
        self.update_ui_controls()
    
    def toggle_favorite(self):
        """Añade o elimina el wallpaper actual de favoritos."""
        if not self.current_wallpaper:
            return
            
        is_favorite = self.favorites_service.is_favorite(
            self.current_wallpaper.country,
            self.current_wallpaper.language,
            self.current_wallpaper.date
        )
        
        if is_favorite:
            # Eliminar de favoritos
            self.favorites_service.remove_favorite(
                self.current_wallpaper.country,
                self.current_wallpaper.language,
                self.current_wallpaper.date
            )
            # Si estábamos viendo un favorito, cargar otro
            if self.current_state == ApplicationState.FAVORITE:
                self.load_random_favorite()
            else:
                # Solo actualizar controles
                self.update_ui_controls()
                QMessageBox.information(self, "Favoritos", FAVORITE_REMOVED_MESSAGE)
        else:
            # Añadir a favoritos
            self.favorites_service.add_favorite(self.current_wallpaper)
            self.update_ui_controls()
            QMessageBox.information(self, "Favoritos", FAVORITE_ADDED_MESSAGE)
    
    def open_favorites_folder(self):
        """Abre la carpeta de favoritos en el explorador de archivos."""
        favorites_dir = self.favorites_service.favorites_dir
        
        try:
            # Abrir carpeta usando el método apropiado para Windows
            os.startfile(favorites_dir)
        except Exception as e:
            logging.error(f"Error al abrir carpeta de favoritos: {e}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudo abrir la carpeta: {favorites_dir}"
            )
    
    def show_settings_menu(self):
        """Muestra el menú de configuración."""
        # Posicionar el menú bajo el botón de configuración
        button = self.sender()
        if button:
            self.settings_menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    def resizeEvent(self, event):
        """Maneja el evento de redimensionamiento de la ventana."""
        super().resizeEvent(event)
        
        # Reescalar imagen si hay un wallpaper cargado
        if self.current_wallpaper and hasattr(self, 'image_label'):
            file_path = self.current_wallpaper.file_path
            if os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        self.image_label.width(), 
                        self.image_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(pixmap)