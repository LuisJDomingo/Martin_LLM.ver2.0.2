#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que los mensajes de error ahora permiten seleccionar y copiar texto.

Este script muestra diferentes tipos de mensajes usando las nuevas funciones mejoradas.
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QMainWindow
from PyQt6.QtCore import Qt

# Importar las funciones mejoradas
from ui.custom_widgets import (
    show_critical_message, 
    show_warning_message, 
    show_information_message,
    show_question_message,
    show_detailed_error_message
)

class MessageTestWindow(QMainWindow):
    """Ventana de prueba para mostrar diferentes tipos de mensajes."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Mensajes Seleccionables - MARTIN LLM")
        self.setMinimumSize(400, 300)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        
        # Botones para probar diferentes tipos de mensajes
        buttons = [
            ("Mensaje de Error Crítico", self.test_critical_message),
            ("Mensaje de Advertencia", self.test_warning_message),
            ("Mensaje Informativo", self.test_information_message),
            ("Pregunta con Texto Largo", self.test_question_message),
            ("Error Detallado con Stack Trace", self.test_detailed_error_message),
            ("Error con Mensaje Muy Largo", self.test_long_error_message)
        ]
        
        for button_text, handler in buttons:
            button = QPushButton(button_text)
            button.clicked.connect(handler)
            button.setMinimumHeight(40)
            layout.addWidget(button)
        
        # Información
        layout.addWidget(QPushButton("Cerrar").clicked.connect(self.close))
    
    def test_critical_message(self):
        """Prueba mensaje crítico con texto seleccionable."""
        show_critical_message(
            self,
            "Error Crítico de Conexión",
            "No se pudo conectar a la base de datos MongoDB.",
            "Verifique que el servicio MongoDB esté ejecutándose en puerto 27017.\n\n"
            "Error específico: Connection refused (111)\n"
            "Host: localhost:27017\n"
            "Timeout: 30 segundos"
        )
    
    def test_warning_message(self):
        """Prueba mensaje de advertencia."""
        show_warning_message(
            self,
            "Advertencia de Memoria",
            "El sistema está usando más del 90% de la memoria RAM disponible.",
            "RAM actual: 15.2 GB / 16 GB\n"
            "Procesos principales:\n"
            "• Python (MARTIN LLM): 8.5 GB\n" 
            "• Chrome: 3.2 GB\n"
            "• Sistema: 2.1 GB\n\n"
            "Considere cerrar aplicaciones innecesarias."
        )
    
    def test_information_message(self):
        """Prueba mensaje informativo."""
        show_information_message(
            self,
            "Modelo Cargado Exitosamente",
            "El modelo 'llama-3.2-3b-instruct-q4_k_m.gguf' se ha cargado correctamente.",
            "Detalles del modelo:\n"
            "• Nombre: Llama 3.2 3B Instruct\n"
            "• Tamaño: 1.86 GB\n"
            "• Cuantización: Q4_K_M\n"
            "• Contexto máximo: 128,000 tokens\n"
            "• GPU layers: 0 (CPU only)\n"
            "• Threads: 8\n\n"
            "El sistema está listo para recibir comandos."
        )
    
    def test_question_message(self):
        """Prueba mensaje de pregunta."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = show_question_message(
            self,
            "Confirmación de Eliminación Masiva",
            "¿Está seguro de que desea eliminar todas las conversaciones seleccionadas?",
            "Esta acción eliminará permanentemente:\n\n"
            "• 15 conversaciones del último mes\n"
            "• 127 mensajes en total\n"
            "• 3.2 MB de datos de historial\n\n"
            "Esta acción no se puede deshacer.",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            show_information_message(self, "Confirmado", "Has confirmado la eliminación.")
        else:
            show_information_message(self, "Cancelado", "Operación cancelada.")
    
    def test_detailed_error_message(self):
        """Prueba mensaje de error detallado con stack trace."""
        
        # Simular un stack trace realista
        detailed_error = """Traceback (most recent call last):
  File "app/llm_providers.py", line 145, in load_model
    self.model = LlamaLLM(model_path=model_path, n_gpu_layers=gpu_layers)
  File "/usr/local/lib/python3.11/site-packages/llama_cpp/llama.py", line 141, in __init__
    self._model = _LlamaModel(model_path, params)
  File "/usr/local/lib/python3.11/site-packages/llama_cpp/llama.py", line 71, in __init__
    raise ValueError(f"Failed to load model from '{model_path}'")
ValueError: Failed to load model from 'models/broken_model.gguf'

Additional context:
- Model file size: 0 bytes (file appears to be corrupted)
- Available disk space: 45.2 GB
- Model path exists: True
- Model is readable: False
- CUDA available: False
- GPU layers requested: 0

System information:
- OS: Windows 11 (10.0.22631)
- Python: 3.11.5
- llama-cpp-python: 0.2.20
- Available RAM: 16 GB
- CPU: AMD Ryzen 7 5800X (16 cores)"""
        
        show_detailed_error_message(
            self,
            "Error de Carga del Modelo",
            "No se pudo cargar el modelo seleccionado debido a un archivo corrupto.",
            detailed_error
        )
    
    def test_long_error_message(self):
        """Prueba mensaje con texto muy largo para verificar selección."""
        long_message = """Error de configuración del sistema de inteligencia artificial MARTIN LLM v2.0.2:

Se ha detectado un conflicto crítico en la configuración del hardware que impide el funcionamiento óptimo del sistema. El problema se origina en la detección automática de componentes GPU y la asignación de capas de procesamiento neuronal.

DETALLES ESPECÍFICOS DEL ERROR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. HARDWARE DETECTADO:
   • Procesador: AMD Ryzen 7 5800X (8 núcleos, 16 hilos)
   • Memoria RAM: 32 GB DDR4-3200 MHz
   • Tarjeta Gráfica Principal: NVIDIA GeForce RTX 3080 (10 GB VRAM)
   • Tarjeta Gráfica Integrada: AMD Radeon Graphics
   • Almacenamiento: NVMe SSD 1TB (velocidad: 3.500 MB/s lectura)

2. CONFIGURACIÓN PROBLEMÁTICA:
   • GPU Layers solicitadas: 35
   • GPU Layers máximas soportadas: 33
   • Memoria VRAM disponible: 8.2 GB de 10 GB
   • Memoria VRAM requerida: 11.5 GB (INSUFICIENTE)
   
3. CONFLICTOS IDENTIFICADOS:
   • El modelo seleccionado requiere más VRAM de la disponible
   • Las capas GPU exceden el límite de hardware
   • La versión CUDA instalada (11.8) no es compatible con el driver (12.1)
   • El archivo de configuración contiene parámetros inválidos

4. SOLUCIONES RECOMENDADAS:
   ✓ Reducir GPU layers a 28 o menos
   ✓ Actualizar drivers NVIDIA a versión 531.x o superior
   ✓ Liberar VRAM cerrando aplicaciones que usen GPU
   ✓ Considerar usar un modelo de menor tamaño
   ✓ Activar modo híbrido CPU+GPU para distribuir la carga

Este mensaje contiene información técnica detallada que debería ser completamente seleccionable y copiable para poder ser compartida con soporte técnico o para diagnóstico posterior."""
        
        show_critical_message(
            self,
            "Error Crítico de Configuración de Hardware",
            long_message
        )

def main():
    """Función principal para ejecutar las pruebas."""
    app = QApplication(sys.argv)
    
    # Aplicar tema de la aplicación si está disponible
    try:
        from ui.qt_styles import apply_futuristic_theme
        apply_futuristic_theme(app)
    except ImportError:
        print("No se pudo cargar el tema futurista, usando tema por defecto.")
    
    # Crear y mostrar ventana de prueba
    window = MessageTestWindow()
    window.show()
    
    # Información inicial
    show_information_message(
        window,
        "Bienvenido a la Prueba de Mensajes",
        "Esta ventana le permite probar los diferentes tipos de mensajes mejorados.",
        "INSTRUCCIONES:\n\n"
        "1. Haga clic en cualquier botón para mostrar un mensaje\n"
        "2. En cada mensaje, intente seleccionar el texto con el ratón\n"
        "3. Copie el texto seleccionado con Ctrl+C\n"
        "4. Pegue el texto en cualquier aplicación para verificar\n\n"
        "CARACTERÍSTICAS MEJORADAS:\n"
        "• Texto completamente seleccionable\n"
        "• Copiar con teclado (Ctrl+C) y menú contextual\n"
        "• Botón 'Copiar Error' en mensajes detallados\n"
        "• Ventanas redimensionables para texto largo\n"
        "• Mejor legibilidad y accesibilidad"
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()