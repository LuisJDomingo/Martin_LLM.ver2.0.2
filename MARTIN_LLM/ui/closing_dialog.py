# -*- coding: utf-8 -*-
# ui/closing_dialog.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .custom_widgets import FadeInMixin

class ClosingDialog(FadeInMixin, QDialog):
    """Ventana para mostrar durante el cierre de la aplicación."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Cerrando...")
        self.setFixedSize(400, 180) # Aumentada la altura para que el texto no se corte
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.drag_position = None
        
        self.setup_ui()
        self.center_on_screen()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame") # Usará el estilo del frame principal
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        title_label = QLabel("Cerrando Martin LLM...")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        frame_layout.addWidget(title_label)
        
        status_label = QLabel("Guardando estado y finalizando procesos...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Modo indeterminado
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setFixedWidth(350)
        frame_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(main_frame)
        
    def center_on_screen(self):
        screen = self.screen()
        if screen:
            screen_rect = screen.geometry()
            x = (screen_rect.width() - self.width()) // 2
            y = (screen_rect.height() - self.height()) // 2
            self.move(x, y)