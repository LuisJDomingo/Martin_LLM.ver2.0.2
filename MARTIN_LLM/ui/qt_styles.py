# -*- coding: utf-8 -*-
# ui/qt_styles.py (Versión Mejorada)
"""
Sistema de estilos PyQt6 con tema sci-fi mejorado para una apariencia más limpia.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

def get_futuristic_stylesheet():
    """Retorna el stylesheet completo para el tema futurista mejorado."""
    return """
    /* Estilo base para toda la aplicación */
    QWidget {
        background-color: #1a1d23; /* Fondo principal oscuro */
        color: #e1e5e9; /* Texto principal claro */
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 10pt;
        border: none;
    }
    
    /* Ventana principal */
    QMainWindow, QDialog {
        background-color: #1a1d23; /* Fondo para el área fuera del mainFrame */
        border: 1px solid #ffffff; /* Borde blanco suave */
    }
    
    /* Frames y contenedores */
    QFrame {
        background-color: transparent; /* Fondo transparente por defecto */
        border: none;
        border-radius: 8px;
        margin: 0px;
        padding: 0px;
    }

    /* Frame principal que contiene toda la UI debajo de la barra de título */
    QFrame#mainFrame {
        background-color: #1a1d23;
        border: none;
        border-radius: 0px;
    }

    /* Paneles laterales izquierdo y derecho */
    QWidget#leftSidePanel {
        background-color: #1a1d23; /* Mismo fondo que el principal */
        border: none; /* Sin bordes */
    }

    QWidget#rightSidePanel {
        background-color: #1a1d23; /* Mismo fondo que el principal */
        border: none; /* Sin bordes */
    }

    /* Área de scroll del historial de chat */
    QScrollArea#historyScrollArea {
        background-color: #1a1d23; /* Fondo oscuro para el área de chat */
        border: none;
    }

    /* Contenido dentro del área de scroll */
    QWidget#history_content_widget {
        background-color: #1a1d23;
    }

    /* Estilo para el encabezado de los paneles plegables */
    QWidget#collapsibleHeader {
        background-color: transparent;
        border-bottom: 1px solid #3d4650;
        padding: 5px;
    }
    
    /* Barra de título personalizada */
    QFrame#customTitleBar {
        background-color: #242831;
    }

    /* Botones de control de ventana (Minimizar, Maximizar, Toggle Panels) */
    QPushButton#windowControlButton {
        background-color: transparent;
        border: none;
        border-radius: 4px;
    }
    QPushButton#windowControlButton:hover { background-color: rgba(255, 255, 255, 0.1); }
    QPushButton#windowControlButton:pressed { background-color: rgba(255, 255, 255, 0.15); }

    /* ================================================================== */
    /* Botones - Estilo Minimalista                                       */
    /* ================================================================== */
    QPushButton {
        background-color: transparent;
        color: #e1e5e9;
        border: 1px solid #4a5568; /* Borde sutil para botones secundarios */
        border-radius: 8px; /* Esquinas redondeadas para botones estándar */
        padding: 6px 12px;
        font-weight: 600;
        font-size: 9pt;
    }
    
    QPushButton:hover {
        background-color: #2d3748; /* Fondo oscuro sutil al pasar el ratón */
        border-color: #6b7280;
    }
    
    QPushButton:pressed {
        background-color: #1a1d23; /* Ligeramente más oscuro al presionar */
        border-color: #4a5568;
    }
    
    QPushButton:disabled {
        background-color: transparent;
        color: #6b7280;
        border-color: #374151;
    }

    /* Botón de Enviar específico */
    QPushButton#sendButton {
        background-color: #ffffff; /* Fondo blanco */
        border: 1px solid #d1d5db; /* Borde gris claro */
        border-radius: 20px; /* Botón de enviar más redondeado */
        color: #1a1d23; /* El color del texto no afecta al icono, pero es buena práctica */
    }
    QPushButton#sendButton:hover {
        background-color: #f3f4f6; /* Gris muy claro */
        border-color: #9ca3af;
    }
    QPushButton#sendButton:pressed {
        background-color: #e5e7eb; /* Gris un poco más oscuro */
        border-color: #6b7280;
    }

    /* Botones de acción principal (Instalar, Usar, etc.) */
    QPushButton#useModelButton, QPushButton#installModelButton, QPushButton#primaryButton {
        background-color: #357abd; /* Azul sólido */
        border: 1px solid #2c5282;
        color: #ffffff;
    }
    QPushButton#useModelButton:hover, QPushButton#installModelButton:hover, QPushButton#primaryButton:hover {
        background-color: #4a90e2; /* Azul más brillante */
        border-color: #3182ce;
    }
    QPushButton#useModelButton:pressed, QPushButton#installModelButton:pressed, QPushButton#primaryButton:pressed {
        background-color: #2c5282; /* Azul más oscuro */
    }

    /* Botones de solo icono (Adjuntar, Nueva Conv, etc.) */
    QPushButton#iconButton {
        background-color: transparent;
        border: 1px solid #a0aec0; /* Borde sutil gris claro */
        /* Un radio grande (mitad del tamaño del botón más grande) asegura que
           todos los botones cuadrados se vuelvan circulares. */
        border-radius: 18px; /* Mitad de 35-36px para asegurar círculo */
        padding: 8px;
    }
    QPushButton#iconButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: white;
    }
    QPushButton#iconButton:pressed {
        background-color: rgba(255, 255, 255, 0.15);
    }

    /* Botón de peligro (Desinstalar, Eliminar) */
    QPushButton#uninstallModelButton, QPushButton#deleteButton, QPushButton#cancelButton {
        background-color: #c53030;
        border-color: #9b2c2c;
        color: white;
    }
    QPushButton#uninstallModelButton:hover, QPushButton#deleteButton:hover, QPushButton#cancelButton:hover {
        background-color: #e53e3e;
        border-color: #c53030;
    }
    QPushButton#uninstallModelButton:pressed, QPushButton#deleteButton:pressed, QPushButton#cancelButton:pressed {
        background-color: #9b2c2c;
        border-color: #742a2a;
    }

    /* Botón de acción positiva (verde) */
    QPushButton#positiveButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
        min-width: 90px;
    }
    QPushButton#positiveButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #45a049, stop:1 #3d8b40);
    }
    QPushButton#positiveButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d8b40, stop:1 #2e7d32);
    }

    /* Botón secundario (azul) */
    QPushButton#secondaryButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
        min-width: 90px;
    }
    QPushButton#secondaryButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976D2, stop:1 #1565C0);
    }

    /* Botón de cerrar de la ventana */
    QPushButton#closeButton {
        background-color: transparent;
        border: none;
        border-radius: 4px;
    }
    QPushButton#closeButton:hover { background-color: #c53030; }
    QPushButton#closeButton:pressed { background-color: #9b2c2c; }
    
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
    
    QTextEdit#inputText {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 2px solid #4a5568;
        border-radius: 20px; /* Más redondeado */
        padding: 8px 15px; /* Menos alto y más padding horizontal */
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 11pt;
        selection-background-color: #4a90e2;
        selection-color: #ffffff;
        line-height: 1.4;
    }

    /* ComboBoxes con estilo unificado (para selectores de modo y modelo) */
    QComboBox#modeSelector, QComboBox#installedModelsCombo {
        background-color: #1a1d23;
        color: #a0aec0;
        border: 1px solid #3d4650;
        border-radius: 5px;
        padding: 5px;
        min-width: 120px;
    }

    /* Ajuste específico para el selector de modo para que sea más pequeño */
    QComboBox#modeSelector {
        min-width: 50px;
        max-width: 50px;
        /* Se anula el padding-left general de 5px y se establece uno
           específico para centrar el icono visualmente. */
        padding-left: 17px;
        border: none; /* Eliminar el borde */
        background-color: transparent; /* Hacer el fondo transparente */
    }
    QComboBox#modeSelector::drop-down, QComboBox#installedModelsCombo::drop-down {
        border: none;
    }
    QComboBox#modeSelector QAbstractItemView, QComboBox#installedModelsCombo QAbstractItemView {
        background-color: #1a1d23;
        color: #a0aec0;
        selection-background-color: #2d3748;
    }

    /* Asegurar que el desplegable del selector de modo sea suficientemente ancho */
    QComboBox#modeSelector QAbstractItemView {
        min-width: 140px;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #242831;
        width: 10px;
        border: none;
        border-radius: 5px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a5568;
        border-radius: 5px;
        min-height: 20px;
        margin: 1px;
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
        background-color: #242831;
        height: 10px;
        border: none;
        border-radius: 5px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #4a5568;
        border-radius: 5px;
        min-width: 20px;
        margin: 1px;
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
    
    /* Tooltips */
    QToolTip {
        background-color: #2d3748;
        color: #e1e5e9;
        border: 1px solid #4a5568;
        padding: 5px;
        border-radius: 4px;
    }
    """

def apply_futuristic_theme(app: QApplication):
    """Aplica el tema futurista a la aplicación."""
    stylesheet = get_futuristic_stylesheet()
    app.setStyleSheet(stylesheet)
    
ADDITIONAL_LOGIN_STYLES = """
/* Estilos específicos para el diálogo de recuperación de contraseña */
QDialog {
    background-color: #1a1d23;
    color: #e1e5e9;
}

QDialog QLabel {
    color: #e1e5e9;
    background-color: transparent;
}

QDialog QLineEdit {
    background-color: #2d3748;
    color: #e1e5e9;
    border: 2px solid #4a5568;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 10pt;
    selection-background-color: #4a90e2;
    selection-color: #ffffff;
}

QDialog QLineEdit:focus {
    border-color: #4a90e2;
    background-color: #374151;
}

/* Estilos para los botones del diálogo */
QDialogButtonBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd);
    color: #ffffff;
    border: 1px solid #2c5282;
    border-radius: 6px;
    padding: 6px 15px;
    font-weight: 600;
    font-size: 9pt;
    min-width: 80px;
    min-height: 25px;
}

QDialogButtonBox QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ba0f2, stop:1 #4682cd);
    border-color: #3182ce;
}

QDialogButtonBox QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3182ce, stop:1 #2c5282);
    border-color: #2a4365;
}

/* Estilos para enlaces de recuperación de contraseña */
QLabel[linkActivated] {
    color: #4a90e2;
    text-decoration: none;
}

QLabel[linkActivated]:hover {
    color: #5ba0f2;
    text-decoration: underline;
}

/* Estilos para campos de email con validación */
QLineEdit[emailValid="true"] {
    border: 2px solid #68d391;
}

QLineEdit[emailValid="false"] {
    border: 2px solid #f56565;
}

/* Estilos para etiquetas de advertencia y error */
QLabel[warningLabel="true"] {
    color: #f6ad55;
    font-size: 9pt;
    background-color: #2d3748;
    border: 1px solid #f6ad55;
    border-radius: 4px;
    padding: 5px;
    margin: 2px 0px;
}

QLabel[errorLabel="true"] {
    color: #f56565;
    font-size: 9pt;
    background-color: #2d3748;
    border: 1px solid #f56565;
    border-radius: 4px;
    padding: 5px;
    margin: 2px 0px;
}

/* Estilos para el frame de consentimiento */
QFrame[consentFrame="true"] {
    background-color: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 8px;
    padding: 10px;
    margin: 10px 0px;
}

/* Estilos para títulos de sección */
QLabel[sectionTitle="true"] {
    font-weight: bold;
    font-size: 11pt;
    color: #68d391;
}

/* Estilos para texto de consentimiento */
QLabel[consentText="true"] {
    color: #e1e5e9;
    font-size: 9pt;
    line-height: 1.4;
}

/* Estilos para etiquetas de checkbox */
QLabel[checkboxLabel="true"] {
    color: #68d391;
    font-size: 10pt;
}

/* Mejoras para el layout de dos paneles en login */
QWidget[imagePanel="true"] {
    background-color: #1a1d23;
    border-right: 1px solid #3d4650;
}

QWidget[formPanel="true"] {
    background-color: #1a1d23;
}

/* Estilos para subtítulos */
QLabel[subtitle="true"] {
    color: #a0aec0;
    font-size: 10pt;
    margin-bottom: 10px;
}

/* ================================================================== */
/* Estilos para Hardware Config Dialog                                */
/* ================================================================== */

QDialog#hardwareConfigDialog {
    background-color: #2d3748;
}

QDialog#hardwareConfigDialog QFrame#hardwareCard,
QDialog#hardwareConfigDialog QFrame#optionsCard,
QDialog#hardwareConfigDialog QFrame#notificationCard {
    background-color: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-radius: 15px;
    padding: 20px;
    margin: 10px;
}

QDialog#hardwareConfigDialog QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: white;
    margin: 20px 0px;
}

QDialog#hardwareConfigDialog QLabel#subtitleLabel {
    font-size: 14px;
    color: #b8c6db;
    margin-bottom: 30px;
}

QDialog#hardwareConfigDialog QLabel#cardTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 15px;
}

QDialog#hardwareConfigDialog QLabel#hardwareInfo {
    background-color: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin: 5px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    color: #e8f4fd;
}

QDialog#hardwareConfigDialog QRadioButton {
    color: white;
    font-size: 13px;
    font-weight: bold;
    spacing: 10px;
    margin: 8px 0px;
}

QDialog#hardwareConfigDialog QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QDialog#hardwareConfigDialog QRadioButton::indicator::unchecked {
    border: 2px solid rgba(255, 255, 255, 0.6);
    border-radius: 9px;
    background-color: transparent;
}

QDialog#hardwareConfigDialog QRadioButton::indicator::checked {
    border: 2px solid #4CAF50;
    border-radius: 9px;
    background-color: #4CAF50;
}

QDialog#hardwareConfigDialog QRadioButton#recommendedOption {
    color: #4CAF50;
    font-weight: bold;
}

QDialog#hardwareConfigDialog QLabel#optionDescription {
    color: #b8c6db;
    font-size: 11px;
    margin-left: 30px;
    margin-bottom: 10px;
}

QDialog#hardwareConfigDialog QProgressBar {
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.1);
    height: 12px;
    text-align: center;
}

QDialog#hardwareConfigDialog QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #8BC34A);
    border-radius: 6px;
}

QDialog#hardwareConfigDialog QLabel#statusLabel {
    color: #b8c6db;
    font-size: 12px;
    font-weight: bold;
    margin: 15px;
}

"""

def apply_additional_login_styles(app):
    """Aplica los estilos adicionales para login y registro."""
    current_stylesheet = app.styleSheet()
    app.setStyleSheet(current_stylesheet + ADDITIONAL_LOGIN_STYLES)