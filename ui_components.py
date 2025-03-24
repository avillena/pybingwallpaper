# ui_components.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import (QLabel, QPushButton, QCheckBox, 
                            QFrame, QGraphicsDropShadowEffect)
from constants import Constants

def apply_zoom(size, zoom_factor):
    """Aplica factor de zoom a un valor de tamaño."""
    return int(size * zoom_factor)

def create_label(text, font_size, bold=False, color=None, zoom_factor=1.0):
    """Crea un QLabel con estilo."""
    label = QLabel(text)
    
    # Aplicar estilo
    style = []
    
    # Tamaño de fuente con zoom
    zoomed_size = apply_zoom(font_size, zoom_factor)
    style.append(f"font-size: {zoomed_size}px")
    
    # Peso de fuente
    if bold:
        style.append("font-weight: bold")
    
    # Color del texto
    if color:
        style.append(f"color: {color}")
    
    # Aplicar estilo
    label.setStyleSheet("; ".join(style))
    
    return label

def create_button(text, font_size=None, icon=None, background=None, 
                 color="white", padding=None, border_radius=None, 
                 zoom_factor=1.0, hover_color=None):
    """Crea un QPushButton con estilo."""
    button = QPushButton(text)
    
    # Create proper Qt stylesheet with selectors
    stylesheet = "QPushButton { "
    
    # Add base properties
    if background:
        stylesheet += f"background-color: {background}; "
    else:
        stylesheet += "background-color: transparent; "
    
    stylesheet += f"color: {color}; "
    
    if font_size:
        zoomed_size = apply_zoom(font_size, zoom_factor)
        stylesheet += f"font-size: {zoomed_size}px; "
    
    stylesheet += "border: none; "
    
    if border_radius:
        zoomed_radius = apply_zoom(border_radius, zoom_factor)
        stylesheet += f"border-radius: {zoomed_radius}px; "
    
    if padding:
        if isinstance(padding, tuple) and len(padding) == 2:
            v_padding = apply_zoom(padding[0], zoom_factor)
            h_padding = apply_zoom(padding[1], zoom_factor)
            stylesheet += f"padding: {v_padding}px {h_padding}px; "
        else:
            p = apply_zoom(padding, zoom_factor)
            stylesheet += f"padding: {p}px; "
    
    stylesheet += "}"
    
    # Add hover state as a separate selector
    if hover_color:
        stylesheet += f" QPushButton:hover {{ background-color: {hover_color}; }}"
    
    # Add disabled state with clear visual indication
    stylesheet += f" QPushButton:disabled {{ color: rgba(255, 255, 255, 0.3); background-color: transparent; }}"
    
    button.setStyleSheet(stylesheet)
    
    if icon:
        button.setIcon(QIcon(icon))
    
    return button

def create_container(border_radius=None, background=None, shadow=None, zoom_factor=1.0):
    """Crea un contenedor con estilo y sombra opcional."""
    container = QFrame()
    
    # Aplicar estilo
    style = []
    
    # Fondo
    if background:
        style.append(f"background-color: {background}")
    
    # Radio del borde
    if border_radius:
        zoomed_radius = apply_zoom(border_radius, zoom_factor)
        style.append(f"border-radius: {zoomed_radius}px")
    
    container.setStyleSheet("; ".join(style))
    
    # Aplicar sombra si se solicita
    if shadow and isinstance(shadow, dict):
        shadow_effect = QGraphicsDropShadowEffect()
        
        # Aplicar propiedades de sombra
        if 'blur' in shadow:
            shadow_effect.setBlurRadius(apply_zoom(shadow['blur'], zoom_factor))
        
        if 'color' in shadow:
            shadow_effect.setColor(shadow['color'])
        
        if 'offset' in shadow:
            offset = apply_zoom(shadow['offset'], zoom_factor)
            shadow_effect.setOffset(0, offset)
        
        container.setGraphicsEffect(shadow_effect)
    
    return container

def load_pixmap(image_path, width=None, height=None, keep_aspect_ratio=True, zoom_factor=1.0):
    """Carga y escala un pixmap."""
    pixmap = QPixmap(str(image_path))
    
    # Escalar si se proporcionan dimensiones
    if width or height:
        # Aplicar zoom
        if width:
            width = apply_zoom(width, zoom_factor)
        if height:
            height = apply_zoom(height, zoom_factor)
        
        # Escalar el pixmap
        if width and height:
            if keep_aspect_ratio:
                pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                pixmap = pixmap.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif width:
            pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
        elif height:
            pixmap = pixmap.scaledToHeight(height, Qt.SmoothTransformation)
    
    return pixmap

