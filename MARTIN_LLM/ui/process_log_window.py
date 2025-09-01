from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class ProcessLogWindow(QDialog):
    def __init__(self, title="Registro de Proceso", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.layout = QVBoxLayout(self)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1d23;
                color: #e1e5e9;
                border: 1px solid #4a5568;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        self.layout.addWidget(self.log_display)

        self.clear_button = QPushButton("Limpiar Log")
        self.clear_button.clicked.connect(self.clear_log)
        self.layout.addWidget(self.clear_button)

    def append_log(self, message):
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def clear_log(self):
        self.log_display.clear()

    def closeEvent(self, event):
        # Ignorar el evento de cierre para que la ventana no se cierre con la X
        event.ignore()
        self.hide()
