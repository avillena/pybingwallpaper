import os
import subprocess
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QPalette, QColor
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QCheckBox, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMenu, 
                             QAction, QDialog, QFrame, QGraphicsDropShadowEffect,
                             QMessageBox)

from constants import Constants
from run_windows_startup import StartupManager
from wallpaper_favorites import WallpaperFavorites
from pathlib import Path

# Constantes locales para la interfaz de usuario
class UIConstants:
    """Constantes específicas para la interfaz de usuario."""
    # Márgenes y espaciados
    MAIN_MARGIN_H = 15
    MAIN_MARGIN_V = 20
    CONTENT_MARGIN = 4
    CONTENT_PADDING_V = 8
    CONTENT_SPACING = 12
    HEADER_SPACING = 4
    LAYOUT_SPACING = 6
    NAV_MARGIN = 8
    BUTTON_PADDING_H = 8
    BUTTON_PADDING_V = 4
    
    # Estilos de texto
    TITLE_FONT_SIZE = 24
    VERSION_FONT_SIZE = 14
    COPYRIGHT_FONT_SIZE = 11
    BING_TITLE_FONT_SIZE = 13
    BUTTON_FONT_SIZE = 14
    NAV_TITLE_FONT_SIZE = 14
    NAV_COPYRIGHT_FONT_SIZE = 10
    NAV_BUTTON_FONT_SIZE = 12
    MENU_FONT_SIZE = 12
    
    # Colores
    LINK_COLOR = "#0066cc"
    HOVER_COLOR = "rgba(255, 255, 255, 0.1)"
    DISABLED_COLOR = "rgba(255, 255, 255, 0.3)"
    MENU_BG_COLOR = "#2C2C2C"
    MENU_BORDER_COLOR = "#3C3C3C"
    THUMB_BG_COLOR = "#111111"
    FAVORITE_COLOR = "#FFD700"  # Color dorado para favoritos
    FAVORITE_HOVER_COLOR = "#FFC125"  # Color cuando se pasa el cursor
    
    # Tamaño de la miniatura en navegador
    THUMB_WIDTH = 130
    THUMB_HEIGHT = 95
    
    # Posicionamiento del navegador
    TRAY_OFFSET_X = 20
    TRAY_OFFSET_Y = 60
    
    # Límite de caracteres para título
    TITLE_CHAR_LIMIT_FACTOR = 70
    
    # Borde de menú
    MENU_BORDER_WIDTH = 1
    MENU_BORDER_RADIUS = 8
    MENU_PADDING = 5
    MENU_ITEM_PADDING_V = 5
    MENU_ITEM_PADDING_H = 20
    MENU_ITEM_BORDER_RADIUS = 4
    
    # Iconos y símbolos
    FAVORITE_ICON_ACTIVE = "★"   # Estrella llena
    FAVORITE_ICON_INACTIVE = "☆"  # Estrella vacía

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self, wallpaper_manager):
        super().__init__()
        
        self.wallpaper_manager = wallpaper_manager
        self.wallpaper_manager.add_download_completed_callback(self.update_state)
        
        self.init_ui()
        self.update_state(self.wallpaper_manager.state)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle(Constants.APP_NAME)
        self.setFixedSize(Constants.UI_MAIN_WIDTH, Constants.UI_MAIN_HEIGHT)
        
        # Widget principal y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(UIConstants.MAIN_MARGIN_H, 
                                      UIConstants.MAIN_MARGIN_V, 
                                      UIConstants.MAIN_MARGIN_H, 
                                      UIConstants.MAIN_MARGIN_V)
        
        # Título y versión
        title_label = QLabel(Constants.APP_NAME)
        title_label.setStyleSheet(f"font-size: {UIConstants.TITLE_FONT_SIZE}px; font-weight: bold;")
        
        version_label = QLabel(f"Version {Constants.APP_VERSION}")
        version_label.setStyleSheet(f"font-size: {UIConstants.VERSION_FONT_SIZE}px;")
        
        # Copyright y enlace
        self.copyright_label = QLabel(Constants.APP_COPYRIGHT)
        self.copyright_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px; color: {UIConstants.LINK_COLOR};")
        self.copyright_label.setOpenExternalLinks(True)
        self.copyright_label.setCursor(Qt.PointingHandCursor)
        self.copyright_label.mousePressEvent = self.open_website
        
        # Checkbox para iniciar con Windows
        self.startup_checkbox = QCheckBox(f"Iniciar {Constants.APP_NAME} con Windows")
        self.startup_checkbox.setChecked(StartupManager.get_run_on_startup())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        
        # Información de la imagen actual
        self.image_title_label = QLabel("Cargando información de la imagen...")
        self.image_title_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px; color: {UIConstants.LINK_COLOR};")
        self.image_title_label.setCursor(Qt.PointingHandCursor)
        self.image_title_label.mousePressEvent = self.open_image_link
        
        # Estado de la aplicación
        self.status_label = QLabel(f"{Constants.APP_NAME} está en funcionamiento.")
        self.status_label.setStyleSheet(f"font-size: {UIConstants.COPYRIGHT_FONT_SIZE}px;")
        
        # Botón de salir
        exit_button = QPushButton(f"Salir de {Constants.APP_NAME}")
        exit_button.clicked.connect(self.exit_app)
        
        # Añadir widgets al layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(version_label)
        main_layout.addWidget(self.copyright_label)
        main_layout.addStretch(1)
        main_layout.addWidget(self.startup_checkbox)
        main_layout.addStretch(1)
        main_layout.addWidget(self.image_title_label)
        main_layout.addWidget(self.status_label)
        
        # Layout para botón inferior
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(exit_button)
        main_layout.addLayout(button_layout)
    
    def update_state(self, state):
        """Actualiza la interfaz con el estado actual."""
        if not state["copyright"]:
            self.image_title_label.setText("Esperando información de la imagen...")
        else:
            self.image_title_label.setText(state["copyright"])
            # Guarda la URL para cuando el usuario haga clic
            self.image_title_label.setProperty("url", state["picture_url"])
    
    def toggle_startup(self, state):
        """Cambia la configuración de inicio con Windows."""
        StartupManager.set_run_on_startup(state == Qt.Checked)
    
    def open_website(self, event):
        """Abre el sitio web del proyecto."""
        self.open_url(Constants.get_bing_website_url())
    
    def open_image_link(self, event):
        """Abre la URL de la imagen actual."""
        url = self.image_title_label.property("url")
        if url:
            self.open_url(url)
    
    def open_url(self, url):
        """Abre una URL en el navegador predeterminado."""
        try:
            # En Windows, esto abrirá la URL en el navegador predeterminado
            os.startfile(url)
        except Exception:
            try:
                # Intenta con subprocess como alternativa
                subprocess.run(['start', url], shell=True, check=True)
            except Exception:
                pass  # Si falla, simplemente ignoramos el error
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        # Oculta la ventana en lugar de cerrar la aplicación
        self.hide()
        event.ignore()
    
    def exit_app(self):
        """Cierra la aplicación completamente."""
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()


class WallpaperNavigatorWindow(QDialog):
    """Ventana para navegar por los fondos de pantalla."""
    
    def __init__(self, wallpaper_manager):
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
        self.setWindowTitle("Bing Wallpaper")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Guardamos una referencia al factor de zoom
        self.zoom_factor = self.wallpaper_manager.get_zoom_factor()
        
        # Registramos el callback para cuando cambie el zoom
        self.wallpaper_manager.add_zoom_changed_callback(self.on_zoom_changed)
        
        # Inicializamos la interfaz
        self.init_ui()
        self.update_content()
        self.update_window_size()
    
    def update_window_size(self):
        """Actualiza el tamaño de la ventana según el factor de zoom."""
        # Aplicar el factor de zoom a las dimensiones base
        base_width, base_height = Constants.UI_NAV_BASE_WIDTH, Constants.UI_NAV_BASE_HEIGHT
        scaled_width = int(base_width * self.zoom_factor)
        scaled_height = int(base_height * self.zoom_factor)
        self.setFixedSize(scaled_width, scaled_height)
        
        # Reposiciona la ventana
        self.position_window()
    
    def on_zoom_changed(self, new_zoom_factor):
        """Manejador para cuando cambia el factor de zoom."""
        self.zoom_factor = new_zoom_factor
        
        # Recreamos la interfaz con el nuevo factor de zoom
        self.recreate_ui()
    
    def recreate_ui(self):
        """Recrea la interfaz de usuario con el nuevo factor de zoom."""
        # Limpiamos cualquier widget existente
        if self.layout():
            # Eliminar todos los widgets del layout
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Eliminar el layout
            QWidget().setLayout(self.layout())
        
        # Actualizamos el tamaño de la ventana
        self.update_window_size()
        
        # Recreamos la interfaz
        self.init_ui()
        self.update_content()
    
    def position_window(self):
        """Posiciona la ventana sobre el system tray."""
        from PyQt5.QtWidgets import QApplication
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        
        # En Windows, el system tray suele estar en la esquina inferior derecha
        self.move(screen_rect.width() - self.width() - UIConstants.TRAY_OFFSET_X, 
                  screen_rect.height() - self.height() - UIConstants.TRAY_OFFSET_Y)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Factor de zoom para escalar elementos
        zoom = self.zoom_factor
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor principal con borde redondeado y sombra
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet(f"""
            #container {{
                background-color: {Constants.BACKGROUND_COLOR};
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                color: {Constants.TEXT_COLOR};
            }}
        """)
        
        # Aplicamos efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(Constants.UI_SHADOW_BLUR * zoom)
        shadow_color = QColor(*Constants.UI_SHADOW_COLOR)
        shadow.setColor(shadow_color)
        shadow.setOffset(0, Constants.UI_SHADOW_OFFSET * zoom)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        margin = int(Constants.UI_MARGIN * zoom)
        container_layout.setContentsMargins(margin, margin, margin, margin)
        container_layout.setSpacing(int(UIConstants.LAYOUT_SPACING * zoom))
        
        # Barra superior con título y botones
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        # Logo de Bing
        bing_label = QLabel("Microsoft Bing")
        bing_label.setStyleSheet(f"""
            font-size: {int(UIConstants.BING_TITLE_FONT_SIZE * zoom)}px;
            font-weight: bold;
            color: white;
        """)
        
        # Botones de la barra superior
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        btn_size = int(Constants.UI_BUTTON_SIZE * zoom)
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(btn_size, btn_size)
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        minimize_btn.clicked.connect(self.hide)
        
        share_btn = QPushButton("⤴")
        share_btn.setFixedSize(btn_size, btn_size)
        share_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        
        # Botón de favorito
        self.favorite_btn = QPushButton(UIConstants.FAVORITE_ICON_INACTIVE)
        self.favorite_btn.setFixedSize(btn_size, btn_size)
        self.favorite_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                color: {UIConstants.FAVORITE_HOVER_COLOR};
            }}
        """)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        
        # Botón de configuración con menú
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(btn_size, btn_size)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings_menu)
        
        buttons_layout.addWidget(minimize_btn)
        buttons_layout.addWidget(share_btn)
        buttons_layout.addWidget(self.favorite_btn)
        buttons_layout.addWidget(settings_btn)
        
        header_layout.addWidget(bing_label)
        header_layout.addStretch(1)
        header_layout.addLayout(buttons_layout)
        
        # Contenido principal con la imagen y la descripción
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(
            int(UIConstants.CONTENT_MARGIN * zoom), 
            int(UIConstants.CONTENT_PADDING_V * zoom), 
            int(UIConstants.CONTENT_MARGIN * zoom), 
            int(UIConstants.CONTENT_MARGIN * zoom))
        content_layout.setSpacing(int(UIConstants.CONTENT_SPACING * zoom))
        
        # Imagen miniatura - Escalada con el factor de zoom
        self.thumbnail_label = QLabel()
        thumb_width = int(UIConstants.THUMB_WIDTH * zoom)
        thumb_height = int(UIConstants.THUMB_HEIGHT * zoom)
        self.thumbnail_label.setFixedSize(thumb_width, thumb_height)
        self.thumbnail_label.setStyleSheet(f"""
            border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            background-color: {UIConstants.THUMB_BG_COLOR};
        """)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        # Información del wallpaper
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(int(UIConstants.HEADER_SPACING * zoom))
        
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"""
            font-size: {int(UIConstants.NAV_TITLE_FONT_SIZE * zoom)}px;
            font-weight: bold;
            color: white;
            margin-right: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
        """)
        
        self.copyright_label = QLabel()
        self.copyright_label.setStyleSheet(f"""
            font-size: {int(UIConstants.NAV_COPYRIGHT_FONT_SIZE * zoom)}px;
            color: rgba(255, 255, 255, 0.7);
        """)
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.copyright_label)
        info_layout.addStretch(1)
        
        content_layout.addWidget(self.thumbnail_label)
        content_layout.addLayout(info_layout, 1)
        
        # Barra de navegación
        nav_layout = QHBoxLayout()
        nav_margin = int(UIConstants.NAV_MARGIN * zoom)
        nav_layout.setContentsMargins(nav_margin, 0, nav_margin, nav_margin)
        nav_layout.setSpacing(0)
        
        self.prev_button = QPushButton("⟨ Anterior")
        self.prev_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: {int(UIConstants.BUTTON_PADDING_V * zoom)}px {int(UIConstants.BUTTON_PADDING_H * zoom)}px;
                font-size: {int(UIConstants.NAV_BUTTON_FONT_SIZE * zoom)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            }}
            QPushButton:disabled {{
                color: {UIConstants.DISABLED_COLOR};
            }}
        """)
        self.prev_button.clicked.connect(self.navigate_to_previous)
        
        self.next_button = QPushButton("Siguiente ⟩")
        self.next_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: {int(UIConstants.BUTTON_PADDING_V * zoom)}px {int(UIConstants.BUTTON_PADDING_H * zoom)}px;
                font-size: {int(UIConstants.NAV_BUTTON_FONT_SIZE * zoom)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UIConstants.HOVER_COLOR};
                border-radius: {int(UIConstants.CONTENT_MARGIN * zoom)}px;
            }}
            QPushButton:disabled {{
                color: {UIConstants.DISABLED_COLOR};
            }}
        """)
        self.next_button.clicked.connect(self.navigate_to_next)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.next_button)
        
        # Agregamos todos los layouts al contenedor principal
        container_layout.addLayout(header_layout)
        container_layout.addLayout(content_layout, 1)
        container_layout.addLayout(nav_layout)
        
        # Agregamos el contenedor al layout principal
        main_layout.addWidget(container)
    
    def show_settings_menu(self):
        """Muestra el menú de configuración."""
        zoom = self.zoom_factor
        
        settings_menu = QMenu(self)
        settings_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {UIConstants.MENU_BG_COLOR};
                color: white;
                border: {UIConstants.MENU_BORDER_WIDTH}px solid {UIConstants.MENU_BORDER_COLOR};
                border-radius: {int(UIConstants.MENU_BORDER_RADIUS * zoom)}px;
                padding: {int(UIConstants.MENU_PADDING * zoom)}px;
                font-size: {int(UIConstants.MENU_FONT_SIZE * zoom)}px;
            }}
            QMenu::item {{
                padding: {int(UIConstants.MENU_ITEM_PADDING_V * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_H * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_V * zoom)}px {int(UIConstants.MENU_ITEM_PADDING_H * zoom)}px;
                border-radius: {int(UIConstants.MENU_ITEM_BORDER_RADIUS * zoom)}px;
            }}
            QMenu::item:selected {{
                background-color: {UIConstants.HOVER_COLOR};
            }}
        """)
        
        # Opciones del menú
        run_startup_action = settings_menu.addAction("Iniciar con Windows")
        run_startup_action.setCheckable(True)
        run_startup_action.setChecked(StartupManager.get_run_on_startup())
        run_startup_action.triggered.connect(lambda checked: StartupManager.set_run_on_startup(checked))
        
        # Opción para ajustar zoom
        zoom_menu = settings_menu.addMenu("Ajustar tamaño")
        
        for name, factor in Constants.ZOOM_OPTIONS:
            zoom_action = zoom_menu.addAction(name)
            zoom_action.setCheckable(True)
            zoom_action.setChecked(abs(self.zoom_factor - factor) < 0.1)
            
            # Función para aplicar el cambio de zoom
            def apply_zoom(checked, new_factor=factor):
                if checked:
                    self.wallpaper_manager.set_zoom_factor(new_factor)
            
            zoom_action.triggered.connect(apply_zoom)
        
        settings_menu.addSeparator()
        
        # Opción para abrir la carpeta de favoritos
        favorites_action = settings_menu.addAction("Abrir carpeta de favoritos")
        favorites_action.triggered.connect(WallpaperFavorites.open_favorites_folder)
        
        settings_menu.addSeparator()
        
        exit_action = settings_menu.addAction("Salir de la aplicación")
        from PyQt5.QtWidgets import QApplication
        exit_action.triggered.connect(QApplication.instance().quit)
        
        # Muestra el menú en la posición del cursor
        settings_menu.exec_(QCursor.pos())
    
    def open_main_window(self):
        """Abre la ventana principal."""
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().postEvent(self, QEvent(QEvent.Type.Hide))
        # Luego llamamos a la función que muestra la ventana principal usando QTimer
        # para evitar problemas de temporización con el cierre del menú
        QTimer.singleShot(100, lambda: QApplication.instance().access_app_window())
    
    def toggle_favorite(self):
        """Alterna el estado de favorito del wallpaper actual."""
        if self.wallpaper_manager.toggle_current_favorite():
            self.update_favorite_button()
    
    def update_favorite_button(self):
        """Actualiza el estado visual del botón de favorito."""
        is_favorite = self.wallpaper_manager.is_current_favorite() is not None
        
        # Actualizar el estilo y texto del botón
        zoom = self.zoom_factor
        if is_favorite:
            self.favorite_btn.setText(UIConstants.FAVORITE_ICON_ACTIVE)
            self.favorite_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {UIConstants.FAVORITE_COLOR};
                    font-weight: bold;
                    border: none;
                    border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                    font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
                }}
                QPushButton:hover {{
                    background-color: {UIConstants.HOVER_COLOR};
                    color: {UIConstants.FAVORITE_HOVER_COLOR};
                }}
            """)
        else:
            self.favorite_btn.setText(UIConstants.FAVORITE_ICON_INACTIVE)
            self.favorite_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: {int(Constants.UI_BORDER_RADIUS * zoom)}px;
                    font-size: {int(UIConstants.BUTTON_FONT_SIZE * zoom)}px;
                }}
                QPushButton:hover {{
                    background-color: {UIConstants.HOVER_COLOR};
                    color: {UIConstants.FAVORITE_HOVER_COLOR};
                }}
            """)
    
    

    def update_content(self):
        """Actualiza el contenido de la ventana con el wallpaper actual."""
        # Obtenemos la información ACTUALIZADA del wallpaper actual
        current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
        
        # MEJORA: Manejar correctamente el caso de inicio en frío
        if not current_wallpaper:
            # Verificamos si ya tenemos un contador de intentos
            retry_count = getattr(self, "_retry_count", 0)
            
            if retry_count > 10:  # Máximo 10 intentos (10 segundos)
                # Después de varios intentos, mostramos mensaje más claro
                self.title_label.setText("No se pudo cargar el wallpaper")
                self.copyright_label.setText("Intente más tarde o reinicie la aplicación")
                # Reseteamos contador para futuros intentos
                self._retry_count = 0
                return
            
            # Mostramos mensaje de carga con contador
            self.title_label.setText(f"Descargando imagen de Bing... ({retry_count+1})")
            self.copyright_label.setText("Por favor espere mientras se obtienen los datos iniciales")
            
            # Limpiamos miniatura anterior si existe
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("Cargando...")
            
            # Incrementamos contador para siguiente intento
            self._retry_count = retry_count + 1
            
            # Programamos nuevo intento en 1 segundo
            QTimer.singleShot(1000, self.update_content)
            return
        
        # Si llegamos aquí, tenemos datos - reseteamos contador
        self._retry_count = 0
        
        # Resto del método original
        # Aplicar factor de zoom
        zoom = self.zoom_factor
        
        # Actualiza la miniatura
        idx = self.wallpaper_manager.current_wallpaper_index
        
        # Obtener la ruta de la miniatura según la fuente
        if self.wallpaper_manager.current_source == "bing":
            thumb_file = Constants.get_thumbnail_file(idx)
        else:  # Favorito
            # Usar el archivo original para los favoritos
            thumb_file = Path(current_wallpaper.get("file_path", ""))
        
        if thumb_file.exists():
            pixmap = QPixmap(str(thumb_file))
            # Usamos una escala óptima para la imagen con el factor de zoom
            thumb_width = int(UIConstants.THUMB_WIDTH * zoom)
            thumb_height = int(UIConstants.THUMB_HEIGHT * zoom)
            self.thumbnail_label.setPixmap(pixmap.scaled(
                thumb_width, thumb_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Si no existe la miniatura, intentamos descargarla si tenemos URL
            if self.wallpaper_manager.current_source == "bing" and "thumbnail_url" in current_wallpaper:
                try:
                    self.thumbnail_label.setText("Descargando miniatura...")
                    QApplication.processEvents()  # Forzamos actualización de UI
                    
                    response = requests.get(current_wallpaper["thumbnail_url"])
                    response.raise_for_status()
                    with open(thumb_file, 'wb') as f:
                        f.write(response.content)
                    
                    # Intentamos mostrar la imagen recién descargada
                    if thumb_file.exists():
                        pixmap = QPixmap(str(thumb_file))
                        thumb_width = int(UIConstants.THUMB_WIDTH * zoom)
                        thumb_height = int(UIConstants.THUMB_HEIGHT * zoom)
                        self.thumbnail_label.setPixmap(pixmap.scaled(
                            thumb_width, thumb_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        self.thumbnail_label.setText("No se pudo cargar la imagen")
                except Exception as e:
                    print(f"Error al descargar miniatura: {str(e)}")
                    self.thumbnail_label.setText("Error al descargar")
            else:
                self.thumbnail_label.setText("Imagen no disponible")
        
        # Parsea y formatea mejor el título y copyright
        if "copyright" in current_wallpaper:
            title_parts = current_wallpaper["copyright"].split("(©")
            title = title_parts[0].strip()
            # Limita el título a dos líneas basado en el tamaño y zoom
            max_length = int(UIConstants.TITLE_CHAR_LIMIT_FACTOR / zoom)  # Menos caracteres si es más grande
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
            
            copyright_text = "©" + title_parts[1] if len(title_parts) > 1 else ""
            
            self.title_label.setText(title)
            self.copyright_label.setText(copyright_text)
        else:
            self.title_label.setText("Sin título disponible")
            self.copyright_label.setText("")
        
        # Muestra la fuente actual en la interfaz
        if self.wallpaper_manager.current_source == "favorite":
            if not self.title_label.text().startswith("⭐"):
                self.title_label.setText(f"⭐ {self.title_label.text()}")
        
        # Actualiza los botones de navegación
        self.update_navigation_buttons()
        
        # Actualiza el estado del botón de favorito
        self.update_favorite_button()

    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación."""
        # Obtenemos información actualizada
        wallpaper_count = self.wallpaper_manager.get_wallpaper_count()
        current_idx = self.wallpaper_manager.current_wallpaper_index
        
        # Lógica revisada para los botones de navegación
        # "Anterior" navega a wallpapers más antiguos (índices mayores)
        can_go_previous = (
            # Hay más wallpapers en la colección actual
            (current_idx < wallpaper_count - 1) or 
            # O estamos en Bing y hay favoritos disponibles
            (self.wallpaper_manager.current_source == "bing" and len(self.wallpaper_manager.favorites) > 0)
        )
        
        # "Siguiente" navega a wallpapers más recientes (índices menores)
        can_go_next = (
            # Hay wallpapers anteriores en la colección actual
            (current_idx > 0) or 
            # O estamos en favoritos y hay wallpapers Bing disponibles
            (self.wallpaper_manager.current_source == "favorite" and len(self.wallpaper_manager.wallpaper_history) > 0)
        )
        
        self.prev_button.setEnabled(can_go_previous)
        self.next_button.setEnabled(can_go_next)

    def navigate_to_previous(self):
        """Navega al wallpaper anterior (más antiguo)."""
        if self.wallpaper_manager.navigate_to_previous_wallpaper():
            # Aquí hay un punto clave: Después de la navegación,
            # actualizamos el contenido de forma explícita
            self.update_content()

    def navigate_to_next(self):
        """Navega al wallpaper siguiente (más reciente)."""
        if self.wallpaper_manager.navigate_to_next_wallpaper():
            # Actualizamos el contenido después de la navegación
            self.update_content()    
    
    
    
    
    def mousePressEvent(self, event):
        """Gestiona el evento de pulsación del ratón para mover la ventana."""
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Gestiona el evento de movimiento del ratón para mover la ventana."""
        if hasattr(self, 'offset'):
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Gestiona el evento de liberación del ratón."""
        if hasattr(self, 'offset'):
            del self.offset
        else:
            super().mouseReleaseEvent(event)
    
    # Cierra la ventana si se presiona Escape
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
    
    # Asegura que la ventana se cierra al perder el foco
    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)