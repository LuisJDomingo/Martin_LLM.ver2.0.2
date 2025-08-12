# -*- coding: utf-8 -*-
# ui/qt_styles.py
"""
Sistema de estilos PyQt6 con tema sci-fi
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

def get_futuristic_stylesheet():
    """Retorna el stylesheet completo para el tema futurista suave"""
    return """
    /* Estilo base para toda la aplicación */
    QWidget {
        background-color: #1a1d23;
        color: #e1e5e9;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 10pt;
        border: none;
    }
    
    /* Ventana principal */
    QMainWindow {
        background-color: #1a1d23;
        color: #e1e5e9;
    }
    
    /* Frames y contenedores */
    QFrame {
        background-color: #242831;
        border: 1px solid #3d4650;
        border-radius: 8px;
        margin: 0px;
        padding: 5px;
    }

    /* Quitar el fondo del panel de parámetros para un look más integrado */
    QFrame#llmParametersWidget {
        background-color: transparent;
        border: none;
    }

    /* Quitar el borde del panel de login para un look más integrado */
    QFrame#loginContainerFrame {
        border: none;
    }

    /* Quitar el borde del panel izquierdo para un look más integrado */
    QFrame#leftPanelFrame {
        border: none;
    }

    /* Estilo para el encabezado de los paneles plegables */
    QWidget#collapsibleHeader {
        background-color: transparent;
        border: none;
    }
    
    QFrame#topbar {
        background-color: #2c3038;
        border: none;
        border-bottom: 1px solid #4a5568;
        margin: 0px;
        padding: 0px;
    }
    
    /* Botones */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd);
        color: #ffffff;
        border: 1px solid #2c5282;
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: 600;
        font-size: 8pt;
        min-width: 60px;
        min-height: 20px;
        text-align: center;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ba0f2, stop:1 #4682cd);
        border-color: #3182ce;
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3182ce, stop:1 #2c5282);
        border-color: #2a4365;
    }
    
    QPushButton:disabled {
        background-color: #4a5568;
        color: #9ca3af;
        border-color: #6b7280;
    }
    
    /* Botones especiales */
    QPushButton#closeButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f56565, stop:1 #e53e3e);
        color: #ffffff;
        border-color: #c53030;
        max-width: 30px;
        max-height: 30px;
        font-size: 12pt;
        font-weight: bold;
    }
    
    QPushButton#closeButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fc8181, stop:1 #f56565);
        border-color: #e53e3e;
    }
    
    QPushButton#minimizeButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #68d391, stop:1 #48bb78);
        color: #ffffff;
        border-color: #38a169;
        max-width: 30px;
        max-height: 30px;
        font-size: 12pt;
        font-weight: bold;
    }
    
    QPushButton#minimizeButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9ae6b4, stop:1 #68d391);
        border-color: #48bb78;
    }
    
    /* Botones de gestión de modelos */
    QPushButton#useModelButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #68d391, stop:1 #48bb78);
        border-color: #38a169;
    }
    QPushButton#useModelButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9ae6b4, stop:1 #68d391);
        border-color: #48bb78;
    }
    QPushButton#useModelButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #48bb78, stop:1 #38a169);
        border-color: #2f855a;
    }

    QPushButton#uninstallModelButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f56565, stop:1 #e53e3e);
        border-color: #c53030;
    }
    QPushButton#uninstallModelButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fc8181, stop:1 #f56565);
        border-color: #e53e3e;
    }
    QPushButton#uninstallModelButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e53e3e, stop:1 #c53030);
        border-color: #9b2c2c;
    }

    /* Estilo para el icono del panel plegable para asegurar que no tenga borde */
    QLabel#collapsibleIcon {
        border: none;
        background-color: transparent;
    }

    /* Labels */
    QLabel {
        color: #e1e5e9;
        background-color: transparent;
        font-size: 10pt;
    }
    
    QLabel#titleLabel {
        color: #90cdf4;
        font-size: 14pt;
        font-weight: bold;
    }
    
    QLabel#panelTitle {
        color: #a0aec0;
        font-size: 9pt;
        font-weight: bold;
        text-transform: uppercase;
        padding-bottom: 4px;
        margin-bottom: 5px;
    }

    QLabel#systemLabel {
        color: #fbb6ce;
        font-weight: bold;
    }
    
    QLabel#userLabel {
        color: #90cdf4;
        font-weight: bold;
    }
    
    QLabel#aiLabel {
        color: #9ae6b4;
        font-weight: bold;
    }
    
    /* Campos de texto */
    QLineEdit {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 10pt;
        selection-background-color: #4a90e2;
        selection-color: #ffffff;
    }
    
    QLineEdit:focus {
        border-color: #4a90e2;
        background-color: #374151;
    }
    
    QTextEdit {
        background-color: #1a1d23;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 11pt;
        selection-background-color: #4a90e2;
        selection-color: #ffffff;
        line-height: 1.4;
    }
    
    QTextEdit#historyText {
        background-color: #1a1d23;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 8px;
    }
    
    QTextEdit#inputText {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 8px;
        max-height: 120px;
    }
    
    /* Checkboxes */
    QCheckBox {
        color: #e1e5e9;
        spacing: 8px;
        font-size: 10pt;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #4a5568;
        border-radius: 4px;
        background-color: #2d3748;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4a90e2;
        border-color: #4a90e2;
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjUgNEw2IDExLjUgMi41IDgiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
    }
    
    QCheckBox::indicator:hover {
        border-color: #4a90e2;
        background-color: #374151;
    }
    
    /* Radio Buttons */
    QRadioButton {
        background-color: transparent;
        color: #e1e5e9;
        spacing: 8px;
        font-size: 10pt;
    }

    QRadioButton:checked {
        color: #90cdf4; /* Un azul más brillante para el texto */
        font-weight: bold;
    }

    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #4a5568;
        border-radius: 9px; /* Círculo perfecto */
        background-color: #2d3748;
    }

    QRadioButton::indicator:hover {
        border-color: #4a90e2;
    }

    QRadioButton::indicator:checked {
        background-color: #4a90e2;
        border-color: #4a90e2;
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTkuNzUgMy43NUw1LjI1IDguMjVMMi4yNSA1LjI1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
    }
    
    /* ListWidget */
    QListWidget {
        background-color: #242831;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 8px;
        padding: 8px;
        font-size: 10pt;
        alternate-background-color: #2d3748;
    }
    
    QListWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #374151;
        border-radius: 4px;
        margin-bottom: 2px;
    }
    
    QListWidget::item:selected {
        background-color: #4a90e2;
        color: #ffffff;
    }
    
    QListWidget::item:hover {
        background-color: #374151;
        color: #e1e5e9;
    }
    
    QListWidget#recentConvsList {
        border: 1px solid #3d4650;
        padding: 4px;
        font-size: 9pt;
    }

    QListWidget#recentConvsList::item {
        padding: 4px 6px;
        border-bottom: 1px solid #2d3748;
        margin-bottom: 1px;
        border-radius: 2px;
    }

    /* Hace que el fondo de la fila de conversación sea transparente */
    QWidget#recentConvRow {
        background: transparent;
        border: none;
    }

    /* Estilo específico para la lista de modelos para evitar conflictos de padding */
    QListWidget#modelList::item {
        padding: 2px; /* Reducir padding para que el widget interno controle el espacio */
        border: none;
        border-bottom: 1px solid #374151;
        margin: 0;
        border-radius: 0;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #2d3748;
        width: 12px;
        border: none;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a5568;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #4a90e2;
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #2d3748;
        height: 12px;
        border: none;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #4a5568;
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #4a90e2;
    }
    
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
        width: 0px;
    }
    
    /* ComboBox */
    QComboBox {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 6px;
        padding: 8px 12px;
        min-width: 150px;
    }
    
    QComboBox:hover {
        border-color: #4a90e2;
        background-color: #374151;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #e1e5e9;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 6px;
        selection-background-color: #4a90e2;
        selection-color: #ffffff;
    }
    
    /* Progress Bar */
    QProgressBar {
        background-color: #2d3748;
        border: 2px solid #4a5568;
        border-radius: 6px;
        text-align: center;
        color: #e1e5e9;
        font-weight: bold;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd);
        border-radius: 4px;
    }

    QProgressBar#downloadProgressBar {
        border: 2px solid #38a169;
        background-color: #2d3748;
        color: #e1e5e9;
    }

    QProgressBar#downloadProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #68d391, stop:1 #48bb78);
        border-radius: 4px;
    }
    
    /* Menu contextual */
    QMenu {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 8px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenu::item:selected {
        background-color: #4a90e2;
        color: #ffffff;
    }
    
    QMenu::item:disabled {
        color: #9ca3af;
    }
    
    /* Tooltips */
    QToolTip {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 6px;
        padding: 8px;
        font-size: 9pt;
    }
    
    /* Separadores */
    QFrame[frameShape="4"] {
        color: #4a5568;
        background-color: #4a5568;
        height: 1px;
        border: none;
    }
    
    QFrame[frameShape="5"] {
        color: #4a5568;
        background-color: #4a5568;
        width: 1px;
        border: none;
    }
        /* Sliders para parámetros del modelo */
    QSlider::groove:horizontal {
        border: 1px solid #3d4650;
        height: 6px; /* Altura del surco */
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #f56565); /* Degradado de Azul a Rojo */
        margin: 2px 0;
        border-radius: 3px;
    }

    QSlider::handle:horizontal {
        background-color: #e1e5e9; /* Color claro para el manejador */
        border: 1px solid #a0aec0;
        width: 16px;
        height: 16px;
        margin: -6px 0; /* Centrar verticalmente sobre el surco */
        border-radius: 8px; /* Hacerlo circular */
    }

    QSlider::handle:horizontal:hover {
        background-color: #ffffff;
        border-color: #ffffff;
    }
    """

def apply_futuristic_theme(app: QApplication):
    """Aplica el tema futurista suave a la aplicación"""
    # Configurar la fuente por defecto
    font = QFont("Segoe UI", 10)
    if not font.exactMatch():
        font = QFont("Arial", 10)
    app.setFont(font)
    
    # Aplicar el stylesheet
    app.setStyleSheet(get_futuristic_stylesheet())
    
    # Configurar la paleta de colores
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1a1d23"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e1e5e9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#242831"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2d3748"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2d3748"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e1e5e9"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e1e5e9"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#4a90e2"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#90cdf4"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#4a90e2"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#4a90e2"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    app.setPalette(palette)
    
    print("[DEBUG] Tema futurista suave aplicado exitosamente")

def create_loading_stylesheet():
    """Stylesheet específico para la ventana de carga"""
    return """
    QDialog {
        background-color: #0f0f0f;
        border: 2px solid #00FF00;
        border-radius: 10px;
    }
    
    QLabel {
        color: #00FF00;
        font-family: 'Consolas', monospace;
        font-size: 12pt;
        font-weight: bold;
    }
    
    QProgressBar {
        background-color: #111111;
        border: 2px solid #00FF00;
        border-radius: 5px;
        text-align: center;
        color: #00FF00;
        font-weight: bold;
        height: 25px;
    }
    
    QProgressBar::chunk {
        background-color: #00FF00;
        border-radius: 3px;
    }
    """
