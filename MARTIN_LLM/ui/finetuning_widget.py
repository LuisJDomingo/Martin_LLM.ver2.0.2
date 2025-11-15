# -*- coding: utf-8 -*- 
# ui/finetuning_widget.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QProgressBar, QMessageBox
from PyQt6.QtCore import pyqtSignal
from .custom_widgets import show_critical_message, show_warning_message, show_information_message

class FineTuningWidget(QFrame):
    """Widget para configurar e iniciar el proceso de fine-tuning."""
    start_finetuning_requested = pyqtSignal(str, str) # new_model_name, training_data
    stop_finetuning_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Nombre del nuevo modelo
        name_layout = QHBoxLayout()
        name_label = QLabel("Nombre del nuevo modelo:")
        self.new_model_name_edit = QLineEdit()
        self.new_model_name_edit.setPlaceholderText("ej: mi-modelo-tuneado:latest")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.new_model_name_edit)
        layout.addLayout(name_layout)

        # Área de datos de entrenamiento
        data_label = QLabel("Datos de entrenamiento (formato JSONL):")
        layout.addWidget(data_label)
        self.training_data_edit = QTextEdit()
        self.training_data_edit.setPlaceholderText('{"messages": [{"role": "user", "content": "Pregunta..."}, {"role": "assistant", "content": "Respuesta..."}]}
{"messages": [{"role": "user", "content": "Otra pregunta..."}, {"role": "assistant", "content": "Otra respuesta..."}]}')
        self.training_data_edit.setMinimumHeight(150)
        self.training_data_edit.setObjectName("inputText") # Reutilizar estilo
        layout.addWidget(self.training_data_edit)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Fine-Tuning")
        self.start_button.clicked.connect(self.on_start_clicked)
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Detener")
        self.stop_button.setObjectName("uninstallModelButton") # Reutilizar estilo rojo
        self.stop_button.setVisible(False)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)

        # Progreso y estado
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

    def on_start_clicked(self):
        new_model_name = self.new_model_name_edit.text().strip()
        training_data = self.training_data_edit.toPlainText().strip()

        if not new_model_name or ":" not in new_model_name:
            show_warning_message(self, "Nombre Inválido", "Por favor, especifica un nombre para el nuevo modelo, incluyendo una etiqueta (ej: 'mi-modelo:latest').")
            return

        if not training_data:
            show_warning_message(self, "Datos Vacíos", "Por favor, proporciona los datos de entrenamiento en formato JSONL.")
            return

        self.start_button.setVisible(False)
        self.stop_button.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Preparando entorno...")
        self.status_label.setVisible(True)
        self.start_finetuning_requested.emit(new_model_name, training_data)

    def on_stop_clicked(self):
        self.stop_finetuning_requested.emit()
        self.status_label.setText("Deteniendo proceso...")

    def update_status(self, percentage: int, message: str):
        self.status_label.setText(message)
        if percentage >= 0:
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{message} ({percentage}%)")
        else:
            self.progress_bar.setFormat(message)

    def on_finetuning_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        self.stop_button.setVisible(False)
        self.start_button.setVisible(True)
        self.start_button.setEnabled(True)
        self.status_label.setText(message)
        if "cancelado" in message.lower():
            show_warning_message(self, "Cancelado", message)
        elif success:
            show_information_message(self, "Éxito", f"Fine-tuning completado con éxito.\n{message}")
        else:
            show_critical_message(self, "Error", f"El fine-tuning ha fallado.\n{message}")
