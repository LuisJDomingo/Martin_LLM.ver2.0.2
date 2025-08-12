# -*- coding: utf-8 -*-
# ui/popup_window.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QComboBox, 
                             QMessageBox, QApplication, QFrame)
from PyQt6.QtCore import Qt

# Importaciones absolutas
from MARTIN_LLM.app.model_selection import get_online_ollama_models, get_local_ollama_models_subprocess
from MARTIN_LLM.app.model_loader import query_ollama

class PopupWindow(QWidget):
    """Ventana emergente para selección y consulta de modelos en PyQt6"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ChatLuisGPT")
        self.setMinimumSize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)

        # Model Selection
        self.model_label = QLabel("Selecciona un modelo:")
        self.model_label.setObjectName("modelLabel")
        layout.addWidget(self.model_label)

        self.model_selection = QComboBox()
        self.load_models()
        self.model_selection.currentIndexChanged.connect(self.update_model_label)
        layout.addWidget(self.model_selection)

        self.selected_model_label = QLabel(f"Modelo actual: {self.model_selection.currentText()}")
        self.selected_model_label.setObjectName("selectedModelLabel")
        self.selected_model_label.setStyleSheet("color: #00FFFF; font-style: italic;")
        layout.addWidget(self.selected_model_label)

        # Prompt Input
        self.prompt_label = QLabel("Tu prompt:")
        self.prompt_label.setObjectName("promptLabel")
        layout.addWidget(self.prompt_label)

        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Escribe tu prompt aquí...")
        self.prompt_text.setMaximumHeight(120)
        layout.addWidget(self.prompt_text)

        # Send Button
        self.send_button = QPushButton("ENVIAR")
        self.send_button.setMinimumHeight(40)
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.on_send)

        # Response Output
        self.response_label = QLabel("Respuesta:")
        self.response_label.setObjectName("responseLabel")
        layout.addWidget(self.response_label)

        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        layout.addWidget(self.response_text)

    def load_models(self):
        """Carga los modelos disponibles en el combobox"""
        try:
            online_models = get_online_ollama_models()
            local_models = get_local_ollama_models_subprocess()

            available_models = sorted(set(local_models + online_models))
            if not available_models:
                available_models = ["llama3"]

            self.model_selection.addItems(available_models)
        except Exception as e:
            print(f"Error cargando modelos: {e}")
            self.model_selection.addItems(["llama3"])

    def update_model_label(self):
        """Actualiza la etiqueta del modelo seleccionado"""
        current_model = self.model_selection.currentText()
        self.selected_model_label.setText(f"Modelo actual: {current_model}")
        self.setWindowTitle(f"ChatLuisGPT - Modelo actual: {current_model}")

    def on_send(self):
        """Maneja el evento de envío del prompt"""
        user_prompt = self.prompt_text.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Advertencia", "Escribe un prompt primero.")
            return

        self.response_text.clear()
        model = self.model_selection.currentText()
        
        # Mostrar mensaje de procesamiento
        self.response_text.setPlainText("Procesando...")
        QApplication.processEvents()  # Permitir que se actualice la UI
        
        try:
            response = query_ollama(model, user_prompt)
            self.response_text.setPlainText(f"Modelo: {model}\n\n{response}")
        except Exception as e:
            self.response_text.setPlainText(f"Error: {str(e)}")

def show_popup():
    """Función para mostrar la ventana emergente (compatibilidad con código existente)"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    window = PopupWindow()
    window.show()
    
    if app:
        app.exec()

if __name__ == "__main__":
    show_popup()
