# -*- coding: utf-8 -*-
# ui/llm_parameters_widget.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal

class LLMParametersWidget(QFrame):
    """Widget para configurar parámetros del LLM como temperatura y top_p."""
    parameters_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("llmParametersWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # --- Temperatura ---
        self.temp_slider, self.temp_value_label = self._create_slider_row(
            layout, "Temperatura:", 0, 200, 80, 
            "Controla la aleatoriedad. Valores más altos (ej: 1.2) son más creativos, valores bajos (ej: 0.2) son más deterministas."
        )
        self.temp_slider.valueChanged.connect(lambda value: self._on_parameter_change("temperature", value / 100.0, self.temp_value_label))

        # --- Top P ---
        self.top_p_slider, self.top_p_value_label = self._create_slider_row(
            layout, "Top P:", 0, 100, 90,
            "Nucleus sampling. Considera solo los tokens con una probabilidad acumulada superior a este valor. Ayuda a evitar tokens muy improbables."
        )
        self.top_p_slider.valueChanged.connect(lambda value: self._on_parameter_change("top_p", value / 100.0, self.top_p_value_label))

        # --- Repeat Penalty ---
        self.repeat_penalty_slider, self.repeat_penalty_value_label = self._create_slider_row(
            layout, "Penalización:", 90, 150, 110, # Rango de 0.9 a 1.5, inicial en 1.1
            "Penaliza la repetición de palabras. Valores > 1.0 desincentivan la repetición. Un valor común es 1.1."
        )
        self.repeat_penalty_slider.valueChanged.connect(lambda value: self._on_parameter_change("repeat_penalty", value / 100.0, self.repeat_penalty_value_label))

    def _create_slider_row(self, parent_layout, label_text, min_val, max_val, initial_val, tooltip):
        """Helper para crear una fila con etiqueta, slider y valor."""
        row_layout = QHBoxLayout()
        
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setToolTip(tooltip)
        row_layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial_val)
        slider.setToolTip(tooltip)
        row_layout.addWidget(slider)

        value_label = QLabel(f"{initial_val / 100.0:.2f}")
        value_label.setFixedWidth(40)
        value_label.setToolTip(tooltip)
        row_layout.addWidget(value_label)

        parent_layout.addLayout(row_layout)
        return slider, value_label

    def _on_parameter_change(self, name, value, label_widget):
        """Actualiza la etiqueta y emite la señal de cambio."""
        label_widget.setText(f"{value:.2f}")
        self.parameters_changed.emit({name: value})

    def get_current_parameters(self) -> dict:
        """Devuelve un diccionario con los valores actuales de los parámetros."""
        return {
            "temperature": self.temp_slider.value() / 100.0,
            "top_p": self.top_p_slider.value() / 100.0,
            "repeat_penalty": self.repeat_penalty_slider.value() / 100.0
        }