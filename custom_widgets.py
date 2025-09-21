# -*- coding: utf-8 -*-
# ui/custom_widgets.py

from PyQt6.QtWidgets import QFrame, QMainWindow, QDialog, QHBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
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