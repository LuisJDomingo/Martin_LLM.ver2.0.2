# -*- coding: utf-8 -*-
# ui/custom_widgets.py

from PyQt6.QtWidgets import QFrame, QMainWindow, QDialog, QHBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
import qtawesome as qta

class CustomTitleBar(QFrame):
    """Barra de título personalizada y reutilizable."""
    def __init__(self, parent: QWidget, title: str, show_max_min: bool = True):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("customTitleBar")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(10)

        # Icono y Título
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.robot", color="#90cdf4").pixmap(20, 20))
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #e1e5e9; font-size: 11pt;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Botones de control
        if show_max_min and isinstance(parent, QMainWindow):
            self.minimize_button = QPushButton(qta.icon("fa5s.window-minimize", color="white"), "")
            self.minimize_button.setObjectName("windowControlButton")
            self.minimize_button.setToolTip("Minimizar")
            self.minimize_button.setFixedSize(30, 30)
            self.minimize_button.clicked.connect(self.parent_window.showMinimized)
            layout.addWidget(self.minimize_button)

            self.maximize_button = QPushButton(qta.icon("fa5s.window-maximize", color="white"), "")
            self.maximize_button.setObjectName("windowControlButton")
            self.maximize_button.setToolTip("Maximizar")
            self.maximize_button.setFixedSize(30, 30)
            self.maximize_button.clicked.connect(self.parent_window.toggle_maximize)
            layout.addWidget(self.maximize_button)

        self.close_button = QPushButton(qta.icon("fa5s.times", color="white"), "")
        self.close_button.setObjectName("closeButton")
        self.close_button.setToolTip("Cerrar")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_button)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self.parent_window, 'toggle_maximize'):
            self.parent_window.toggle_maximize()
            event.accept()

class FadeInMixin:
    """Mixin para añadir una animación de fade-in a cualquier ventana."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fade_in_animation = None
        self.setWindowOpacity(0.0)

    def showEvent(self, event):
        super().showEvent(event)
        if self.windowOpacity() == 0.0:
            self._fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
            self._fade_in_animation.setDuration(300)
            self._fade_in_animation.setStartValue(0.0)
            self._fade_in_animation.setEndValue(1.0)
            self._fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self._fade_in_animation.start()

class FramelessWindowMixin:
    """
    Mixin que proporciona la lógica para mover una ventana sin marco.
    La clase que lo usa es responsable de crear una instancia de CustomTitleBar y asignarla a self.title_bar.
    """
    def _init_frameless_mixin(self):
        self.drag_position = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            if hasattr(self, 'title_bar') and hasattr(self.title_bar, 'maximize_button'):
                self.title_bar.maximize_button.setIcon(qta.icon("fa5s.window-maximize", color="white"))
                self.title_bar.maximize_button.setToolTip("Maximizar")
        else:
            self.showMaximized()
            if hasattr(self, 'title_bar') and hasattr(self.title_bar, 'maximize_button'):
                self.title_bar.maximize_button.setIcon(qta.icon("fa5s.window-restore", color="white"))
                self.title_bar.maximize_button.setToolTip("Restaurar")

    def mousePressEvent(self, event):
        if hasattr(self, 'title_bar') and self.title_bar.underMouse() and event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif hasattr(super(), 'mousePressEvent'):
             super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_position') and self.drag_position is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        elif hasattr(super(), 'mouseMoveEvent'):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        if hasattr(super(), 'mouseReleaseEvent'):
            super().mouseReleaseEvent(event)

def _show_selectable_message(parent, icon, title, text, informative_text="", buttons=QMessageBox.StandardButton.Ok):
    """Helper para crear mensajes con texto completamente seleccionable y copiable."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    
    # Hacer el texto completamente seleccionable y copiable
    msg_box.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse | 
        Qt.TextInteractionFlag.TextSelectableByKeyboard |
        Qt.TextInteractionFlag.LinksAccessibleByMouse |
        Qt.TextInteractionFlag.LinksAccessibleByKeyboard
    )
    
    # Configurar botones
    msg_box.setStandardButtons(buttons)
    
    # Ajustar tamaño mínimo para mejorar legibilidad
    msg_box.setMinimumWidth(400)
    
    return msg_box.exec()

def show_critical_message(parent, title, text, informative_text=""):
    """Muestra un mensaje crítico con texto seleccionable y copiable."""
    return _show_selectable_message(parent, QMessageBox.Icon.Critical, title, text, informative_text)

def show_warning_message(parent, title, text, informative_text=""):
    """Muestra un mensaje de advertencia con texto seleccionable y copiable."""
    return _show_selectable_message(parent, QMessageBox.Icon.Warning, title, text, informative_text)

def show_information_message(parent, title, text, informative_text=""):
    """Muestra un mensaje informativo con texto seleccionable y copiable."""
    return _show_selectable_message(parent, QMessageBox.Icon.Information, title, text, informative_text)

def show_question_message(parent, title, text, informative_text="", buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
    """Muestra un diálogo de pregunta con texto seleccionable y copiable."""
    return _show_selectable_message(parent, QMessageBox.Icon.Question, title, text, informative_text, buttons)

def show_detailed_error_message(parent, title, brief_text, detailed_text):
    """Muestra un mensaje de error detallado con texto completamente seleccionable."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(brief_text)
    msg_box.setDetailedText(detailed_text)
    
    # Hacer todo el texto seleccionable
    msg_box.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse | 
        Qt.TextInteractionFlag.TextSelectableByKeyboard |
        Qt.TextInteractionFlag.LinksAccessibleByMouse |
        Qt.TextInteractionFlag.LinksAccessibleByKeyboard
    )
    
    # Configurar botones con opción para copiar
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    copy_button = msg_box.addButton("Copiar Error", QMessageBox.ButtonRole.ActionRole)
    
    def copy_to_clipboard():
        from PyQt6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        full_error = f"{title}\n{brief_text}\n\nDetalles:\n{detailed_text}"
        clipboard.setText(full_error)
    
    copy_button.clicked.connect(copy_to_clipboard)
    
    # Ajustar tamaño
    msg_box.setMinimumWidth(500)
    msg_box.setMinimumHeight(300)
    
    return msg_box.exec()
