import requests
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5.QtGui import QCursor, QPalette, QColor
from PyQt5.QtWidgets import (QLabel, QCheckBox, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMenu, 
                             QAction, QDialog, QFrame, QMessageBox,
                             QApplication)

from constants import Constants
from run_windows_startup import StartupManager
from wallpaper_favorites import WallpaperFavorites
from pathlib import Path
from logger import log_error, log_info
from resource_utils import open_url, open_folder
from ui_components import create_label, create_button, create_container, load_pixmap
from file_utils import file_exists
from http_client import download_file

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
        self.wallpaper_manager.zoom_changed.connect(self.on_zoom_changed)
        
        # Inicializamos la interfaz
        self.init_ui()
        self.update_content()
        self.update_window_size()
    
    def update_window_size(self):
        """Actualiza el tamaño de la ventana según el factor de zoom."""
        # Aplicar el factor de zoom a las dimensiones base
        base_width, base_height = Constants.UI.NAV_BASE_WIDTH, Constants.UI.NAV_BASE_HEIGHT
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
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        
        # Calculate position ensuring window stays within screen bounds
        x_pos = min(screen_rect.width() - self.width() - Constants.UI.TRAY_OFFSET_X,
                    screen_rect.width() - self.width())
        y_pos = min(screen_rect.height() - self.height() - Constants.UI.TRAY_OFFSET_Y,
                    screen_rect.height() - self.height())
        
        # Ensure positions are positive
        x_pos = max(0, x_pos)
        y_pos = max(0, y_pos)
        
        self.move(x_pos, y_pos)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Factor de zoom para escalar elementos
        zoom = self.zoom_factor
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor principal con borde redondeado y sombra
        container = create_container(
            border_radius=Constants.UI.BORDER_RADIUS,
            background=Constants.UI.BACKGROUND_COLOR,
            shadow={
                'blur': Constants.UI.SHADOW_BLUR,
                'color': QColor(*Constants.UI.SHADOW_COLOR),
                'offset': Constants.UI.SHADOW_OFFSET
            },
            zoom_factor=zoom
        )
        container.setObjectName("container")
        
        container_layout = QVBoxLayout(container)
        margin = int(Constants.UI.MARGIN * zoom)
        container_layout.setContentsMargins(margin, margin, margin, margin)
        container_layout.setSpacing(int(6 * zoom))  # Espaciado entre elementos
        
        # Barra superior con título y botones
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(int(4 * zoom))  # Espaciado entre elementos
        
        # Logo de Bing
        bing_label = create_label(
            Constants.UI.MAIN_WINDOW_TITLE,
            Constants.UI.BING_TITLE_FONT_SIZE,
            bold=True,
            color=Constants.UI.TEXT_COLOR,
            zoom_factor=zoom
        )
        
        # Botones de la barra superior
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(int(4 * zoom))  # Espaciado entre elementos
        
        btn_size = int(Constants.UI.BUTTON_SIZE * zoom)
        
        # Botón minimizar
        minimize_btn = create_button(
            "−",
            font_size=Constants.UI.BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            border_radius=Constants.UI.BORDER_RADIUS,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
        minimize_btn.setFixedSize(btn_size, btn_size)
        minimize_btn.clicked.connect(self.hide)
        
        # Botón compartir
        share_btn = create_button(
            "⤴",
            font_size=Constants.UI.BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            border_radius=Constants.UI.BORDER_RADIUS,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
        share_btn.setFixedSize(btn_size, btn_size)
        
        # Botón de favorito
        self.favorite_btn = create_button(
            Constants.UI.FAVORITE_ICON_INACTIVE,
            font_size=Constants.UI.BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            border_radius=Constants.UI.BORDER_RADIUS,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
        self.favorite_btn.setFixedSize(btn_size, btn_size)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        
        # Botón de configuración con menú
        settings_btn = create_button(
            "⚙",
            font_size=Constants.UI.BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            border_radius=Constants.UI.BORDER_RADIUS,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
        settings_btn.setFixedSize(btn_size, btn_size)
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
        content_margin = int(Constants.UI.MARGIN * zoom)
        content_padding = int(8 * zoom)  # Padding vertical
        content_layout.setContentsMargins(
            content_margin, 
            content_padding, 
            content_margin, 
            content_margin)
        content_layout.setSpacing(int(12 * zoom))  # Espaciado entre elementos
        
        # Imagen miniatura - Escalada con el factor de zoom
        self.thumbnail_label = QLabel()
        thumb_width = int(Constants.UI.THUMB_WIDTH * zoom)
        thumb_height = int(Constants.UI.THUMB_HEIGHT * zoom)
        self.thumbnail_label.setFixedSize(thumb_width, thumb_height)
        self.thumbnail_label.setStyleSheet(f"""
            border-radius: {int(Constants.UI.MARGIN * zoom)}px;
            background-color: {Constants.UI.THUMB_BG_COLOR};
        """)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        # Información del wallpaper
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(int(4 * zoom))  # Espaciado entre elementos
        
        self.title_label = create_label(
            "",
            Constants.UI.NAV_TITLE_FONT_SIZE,
            bold=True,
            color=Constants.UI.TEXT_COLOR,
            zoom_factor=zoom
        )
        self.title_label.setWordWrap(True)
        
        self.copyright_label = create_label(
            "",
            Constants.UI.NAV_COPYRIGHT_FONT_SIZE,
            color="rgba(255, 255, 255, 0.7)",
            zoom_factor=zoom
        )
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.copyright_label)
        info_layout.addStretch(1)
        
        content_layout.addWidget(self.thumbnail_label)
        content_layout.addLayout(info_layout, 1)
        
        # Barra de navegación
        nav_layout = QHBoxLayout()
        nav_margin = int(Constants.UI.MARGIN * zoom)
        nav_layout.setContentsMargins(nav_margin, 0, nav_margin, nav_margin)
        nav_layout.setSpacing(0)
        
        self.prev_button = create_button(
            "⟨ Anterior",
            font_size=Constants.UI.NAV_BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            padding=(4, 8),
            border_radius=Constants.UI.MARGIN,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
        self.prev_button.clicked.connect(self.navigate_to_previous)
        
        self.next_button = create_button(
            "Siguiente ⟩",
            font_size=Constants.UI.NAV_BUTTON_FONT_SIZE,
            color=Constants.UI.TEXT_COLOR,
            padding=(4, 8),
            border_radius=Constants.UI.MARGIN,
            zoom_factor=zoom,
            hover_color=Constants.UI.HOVER_COLOR
        )
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
                background-color: {Constants.UI.MENU_BG_COLOR};
                color: white;
                border: {Constants.UI.MENU_BORDER_WIDTH}px solid {Constants.UI.MENU_BORDER_COLOR};
                border-radius: {int(Constants.UI.MENU_BORDER_RADIUS * zoom)}px;
                padding: {int(Constants.UI.MENU_PADDING * zoom)}px;
                font-size: {int(Constants.UI.MENU_FONT_SIZE * zoom)}px;
            }}
            QMenu::item {{
                padding: {int(Constants.UI.MENU_ITEM_PADDING_V * zoom)}px {int(Constants.UI.MENU_ITEM_PADDING_H * zoom)}px;
                border-radius: {int(Constants.UI.MENU_ITEM_BORDER_RADIUS * zoom)}px;
            }}
            QMenu::item:selected {{
                background-color: {Constants.UI.HOVER_COLOR};
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
        exit_action.triggered.connect(QApplication.instance().quit)
        
        # Muestra el menú en la posición del cursor
        settings_menu.exec_(QCursor.pos())
    
    def toggle_favorite(self):
        """Alterna el estado de favorito del wallpaper actual."""
        if self.wallpaper_manager.toggle_current_favorite():
            self.update_favorite_button()
    
    def update_favorite_button(self):
        """Actualiza el estado visual del botón de favorito."""
        is_favorite = self.wallpaper_manager.is_current_favorite() is not None
        
        border_radius = int(Constants.UI.BORDER_RADIUS * self.zoom_factor)
        font_size = int(Constants.UI.BUTTON_FONT_SIZE * self.zoom_factor)
        
        stylesheet = (
            f"QPushButton {{ "
            f"background-color: transparent; "
            f"font-weight: bold; "
            f"border: none; "
            f"border-radius: {border_radius}px; "
            f"font-size: {font_size}px; "
        )
        
        if is_favorite:
            self.favorite_btn.setText(Constants.UI.FAVORITE_ICON_ACTIVE)
            stylesheet += f"color: {Constants.UI.FAVORITE_COLOR}; }}"
        else:
            self.favorite_btn.setText(Constants.UI.FAVORITE_ICON_INACTIVE)
            stylesheet += f"color: white; }}"
        
        stylesheet += (
            f" QPushButton:hover {{ "
            f"background-color: {Constants.UI.HOVER_COLOR}; "
            f"color: {Constants.UI.FAVORITE_HOVER_COLOR}; "
            f"}}"
        )
        
        self.favorite_btn.setStyleSheet(stylesheet)
    
    def update_content(self):
        """Actualiza el contenido de la ventana con el wallpaper actual."""
        # Obtenemos la información ACTUALIZADA del wallpaper actual
        current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
        
        # Manejar el caso de inicio en frío
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
        
        if file_exists(thumb_file):
            pixmap = load_pixmap(
                thumb_file, 
                width=Constants.UI.THUMB_WIDTH, 
                height=Constants.UI.THUMB_HEIGHT, 
                keep_aspect_ratio=True, 
                zoom_factor=zoom
            )
            self.thumbnail_label.setPixmap(pixmap)
        else:
            # Si no existe la miniatura, intentamos descargarla si tenemos URL
            if self.wallpaper_manager.current_source == "bing" and "thumbnail_url" in current_wallpaper:
                try:
                    self.thumbnail_label.setText("Descargando miniatura...")
                    QApplication.processEvents()  # Forzamos actualización de UI
                    
                    if download_file(current_wallpaper["thumbnail_url"], thumb_file):
                        # Intentamos mostrar la imagen recién descargada
                        pixmap = load_pixmap(
                            thumb_file, 
                            width=Constants.UI.THUMB_WIDTH, 
                            height=Constants.UI.THUMB_HEIGHT, 
                            keep_aspect_ratio=True, 
                            zoom_factor=zoom
                        )
                        self.thumbnail_label.setPixmap(pixmap)
                    else:
                        self.thumbnail_label.setText("No se pudo cargar la imagen")
                except Exception as e:
                    log_error(f"Error al descargar miniatura: {str(e)}")
                    self.thumbnail_label.setText("Error al descargar")
            else:
                self.thumbnail_label.setText("Imagen no disponible")
        
        # Parsea y formatea mejor el título y copyright
        if "copyright" in current_wallpaper:
            title_parts = current_wallpaper["copyright"].split("(©")
            title = title_parts[0].strip()
            # Limita el título a dos líneas basado en el tamaño y zoom
            max_length = int(Constants.UI.TITLE_CHAR_LIMIT_FACTOR / zoom)  # Menos caracteres si es más grande
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
        
        # Forzar actualización visual
        self.prev_button.style().unpolish(self.prev_button)
        self.prev_button.style().polish(self.prev_button)
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)
        self.prev_button.update()
        self.next_button.update()

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