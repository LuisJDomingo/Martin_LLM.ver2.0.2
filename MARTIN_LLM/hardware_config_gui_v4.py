# -*- coding: utf-8 -*-
# hardware_config_gui_v4.py - Interfaz gráfica moderna y funcional para configuración de hardware

import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QRadioButton, QButtonGroup, 
    QPushButton, QProgressBar, QMessageBox,
    QGroupBox, QGridLayout, QFrame, QScrollArea,
    QSpacerItem, QSizePolicy, QTextEdit, QCheckBox, QStackedWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

# Añadir la raíz del proyecto al path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from hardware_detector import HardwareDetector
from ui.qt_styles import apply_futuristic_theme, apply_additional_login_styles
from ui.custom_widgets import FramelessWindowMixin, CustomTitleBar

class HardwareDetectionThread(QThread):
    """Thread para ejecutar la detección de hardware sin bloquear la UI."""
    
    detection_complete = pyqtSignal(dict)
    detection_progress = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.detector = None
    
    def run(self):
        """Ejecuta la detección de hardware."""
        try:
            self.detection_progress.emit("🔍 Detectando hardware disponible...")
            self.detector = HardwareDetector()
            
            self.detection_progress.emit("✅ Detección completada")
            
            # Emitir los resultados
            result = {
                'hardware_info': self.detector.system_info,
                'recommended_config': self.detector.recommended_config
            }
            self.detection_complete.emit(result)
            
        except Exception as e:
            self.detection_progress.emit(f"❌ Error: {str(e)}")

class HardwareConfigDialog(FramelessWindowMixin, QDialog):
    """Diálogo moderno para configurar hardware que sigue el estilo de la aplicación."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.styleSheet() + "border: 1px solid #ffffff;")
        self._init_frameless_mixin()
        self.title_bar = CustomTitleBar(self, "Configuración de Hardware", show_max_min=True)
        
        self.recommended_config = {}
        self.selected_config = {}
        self.detector = None
        self.button_group = QButtonGroup()
        
        self.setWindowTitle("⚙️ Configuración de Hardware - MARTIN LLM")
        self.setFixedSize(800, 700)
        self.setModal(True)
        
        self.apply_styles()
        self.setupUI()
        self.start_hardware_detection()
    
    def apply_styles(self):
        apply_futuristic_theme(self)
        apply_additional_login_styles(self)
        self.setStyleSheet(self.styleSheet() + '''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1e3c72, stop:1 #2a5298);
                color: white;
            }
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin: 20px 0px;
            }
            QLabel#subtitleLabel {
                font-size: 14px;
                color: #b8c6db;
                margin-bottom: 30px;
            }
            QFrame#hardwareCard, QFrame#optionsCard, QFrame#notificationCard {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 15px;
            }
            QLabel#hardwareInfo {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #e8f4fd;
            }
            QRadioButton {
                color: white;
                font-size: 13px;
                font-weight: bold;
                spacing: 10px;
                margin: 8px 0px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid rgba(255, 255, 255, 0.6);
                border-radius: 9px;
                background-color: transparent;
            }
            QRadioButton::indicator::checked {
                border: 2px solid #4CAF50;
                border-radius: 9px;
                background-color: #4CAF50;
            }
            QRadioButton#recommendedOption {
                color: #4CAF50;
                font-weight: bold;
            }
            QLabel#optionDescription {
                color: #b8c6db;
                font-size: 11px;
                margin-left: 30px;
                margin-bottom: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
            QPushButton#secondaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
            }
            QPushButton#secondaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
            QPushButton#cancelButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:1 #d32f2f);
            }
            QPushButton#cancelButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #c62828);
            }
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.1);
                height: 12px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 6px;
            }
            QLabel#statusLabel {
                color: #b8c6db;
                font-size: 12px;
                font-weight: bold;
                margin: 15px;
            }
        ''')

    def setupUI(self):
        """Configura la interfaz de usuario."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.title_bar)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Vista de progreso
        self.progress_widget = QWidget()
        self.create_progress_view()
        self.stacked_widget.addWidget(self.progress_widget)

        # Vista de contenido principal
        self.main_content_widget = QWidget()
        self.create_main_content_view()
        self.stacked_widget.addWidget(self.main_content_widget)

        # Vista de notificación
        self.notification_widget = QWidget()
        self.create_notification_view()
        self.stacked_widget.addWidget(self.notification_widget)

    def create_progress_view(self):
        """Crea la vista de progreso."""
        layout = QVBoxLayout(self.progress_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        self.create_header(layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        
        self.status_label = QLabel("🔍 Iniciando detección de hardware...")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def create_main_content_view(self):
        """Crea la vista de contenido principal."""
        main_layout = QVBoxLayout(self.main_content_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        self.create_header(main_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        self.hardware_info_card = QFrame()
        self.hardware_info_card.setObjectName("hardwareCard")
        content_layout.addWidget(self.hardware_info_card)

        self.config_options_card = QFrame()
        self.config_options_card.setObjectName("optionsCard")
        content_layout.addWidget(self.config_options_card)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        self.create_buttons(main_layout)

    def create_notification_view(self):
        """Crea la vista de notificación."""
        layout = QVBoxLayout(self.notification_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        self.notification_card = QFrame()
        self.notification_card.setObjectName("notificationCard")
        card_layout = QVBoxLayout(self.notification_card)
        
        self.notification_title = QLabel()
        self.notification_title.setObjectName("cardTitle")
        self.notification_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.notification_title)

        self.notification_message = QLabel()
        self.notification_message.setWordWrap(True)
        self.notification_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.notification_message)

        self.notification_details = QLabel()
        self.notification_details.setWordWrap(True)
        self.notification_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.notification_details)

        layout.addWidget(self.notification_card)

        close_button = QPushButton("Cerrar")
        close_button.setFixedWidth(120)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def create_header(self, layout):
        """Crea el header del diálogo."""
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("⚙️ Configuración de Hardware")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Optimice MARTIN LLM para obtener el mejor rendimiento en su sistema")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
    
    def populate_hardware_info_card(self):
        """Puebla la tarjeta con información del hardware detectado."""
        layout = QVBoxLayout(self.hardware_info_card)
        layout.setSpacing(15)
        
        title = QLabel("💻 Hardware Detectado")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        
        info_layout = QGridLayout()
        info_layout.setSpacing(10)
        
        cpu_cores = self.hardware_info.get('cpu_cores', 'N/A')
        cpu_info = QLabel(f"🔧 Procesador: {cpu_cores} núcleos")
        cpu_info.setObjectName("hardwareInfo")
        info_layout.addWidget(cpu_info, 0, 0)
        
        platform = self.hardware_info.get('platform', 'N/A')
        architecture = self.hardware_info.get('architecture', 'N/A')
        platform_info = QLabel(f"💻 Sistema: {platform} ({architecture})")
        platform_info.setObjectName("hardwareInfo")
        info_layout.addWidget(platform_info, 0, 1)
        
        has_nvidia = self.hardware_info.get('has_nvidia_gpu', False)
        nvidia_text = "🎮 GPU NVIDIA: " + ("✅ Detectada" if has_nvidia else "❌ No detectada")
        nvidia_info = QLabel(nvidia_text)
        nvidia_info.setObjectName("hardwareInfo")
        info_layout.addWidget(nvidia_info, 1, 0)
        
        has_cuda = self.hardware_info.get('has_cuda', False)
        cuda_text = "⚡ CUDA: " + ("✅ Disponible" if has_cuda else "❌ No disponible")
        cuda_info = QLabel(cuda_text)
        cuda_info.setObjectName("hardwareInfo")
        info_layout.addWidget(cuda_info, 1, 1)
        
        has_intel = self.hardware_info.get('has_intel_gpu', False)
        intel_text = "💎 GPU Intel: " + ("✅ Detectada" if has_intel else "❌ No detectada")
        intel_info = QLabel(intel_text)
        intel_info.setObjectName("hardwareInfo")
        info_layout.addWidget(intel_info, 2, 0)
        
        has_amd = self.hardware_info.get('has_amd_gpu', False)
        amd_text = "🔥 GPU AMD: " + ("✅ Detectada" if has_amd else "❌ No detectada")
        amd_info = QLabel(amd_text)
        amd_info.setObjectName("hardwareInfo")
        info_layout.addWidget(amd_info, 2, 1)
        
        layout.addLayout(info_layout)

    def populate_configuration_options_card(self):
        """Puebla la tarjeta con opciones de configuración."""
        layout = QVBoxLayout(self.config_options_card)
        layout.setSpacing(15)
        
        title = QLabel("⚙️ Opciones de Configuración")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        
        options = self.get_configuration_options()
        
        for i, option in enumerate(options):
            radio = QRadioButton(option['name'])
            if i == 0:
                radio.setText(f"⭐ {option['name']} (Recomendado)")
                radio.setObjectName("recommendedOption")
                radio.setChecked(True)
                self.selected_config = option['config']
            
            radio.toggled.connect(
                lambda checked, cfg=option['config']: self.on_option_selected(checked, cfg)
            )
            
            self.button_group.addButton(radio)
            layout.addWidget(radio)
            
            desc = QLabel(option['description'])
            desc.setObjectName("optionDescription")
            desc.setWordWrap(True)
            layout.addWidget(desc)

    def create_buttons(self, layout):
        """Crea los botones del diálogo."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.redetect_btn = QPushButton("🔄 Detectar de Nuevo")
        self.redetect_btn.setObjectName("secondaryButton")
        self.redetect_btn.clicked.connect(self.start_hardware_detection)
        
        button_layout.addWidget(self.redetect_btn)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.apply_btn = QPushButton("✅ Aplicar Configuración")
        self.apply_btn.clicked.connect(self.apply_configuration)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        layout.addLayout(button_layout)
    
    def start_hardware_detection(self):
        """Inicia la detección de hardware."""
        self.stacked_widget.setCurrentWidget(self.progress_widget)
        
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("🔍 Detectando hardware disponible...")
        
        self.detection_thread = HardwareDetectionThread()
        self.detection_thread.detection_progress.connect(self.update_detection_status)
        self.detection_thread.detection_complete.connect(self.on_detection_complete)
        self.detection_thread.start()
    
    def update_detection_status(self, message):
        """Actualiza el estado de la detección."""
        self.status_label.setText(message)
    
    def on_detection_complete(self, result):
        """Maneja la finalización de la detección."""
        self.hardware_info = result['hardware_info']
        self.recommended_config = result['recommended_config']
        self.detector = self.detection_thread.detector
        
        # Limpiar layouts existentes
        self.clear_layout(self.hardware_info_card.layout())
        self.clear_layout(self.config_options_card.layout())

        self.populate_hardware_info_card()
        self.populate_configuration_options_card()
        
        QTimer.singleShot(500, lambda: self.stacked_widget.setCurrentWidget(self.main_content_widget))

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def get_configuration_options(self):
        """Obtiene las opciones de configuración disponibles."""
        options = []
        
        rec_desc = self.recommended_config.get('description', 'Configuración óptima')
        options.append({
            'name': 'Automática',
            'description': f"{rec_desc} - Esta es la configuración más adecuada para su hardware actual.",
            'config': self.recommended_config
        })
        
        cpu_cores = self.hardware_info.get('cpu_cores', 4)
        options.append({
            'name': 'Solo CPU',
            'description': f"Usar únicamente el procesador ({cpu_cores} núcleos) - Máxima compatibilidad, velocidad moderada.",
            'config': {
                'type': 'force_cpu',
                'n_gpu_layers': 0,
                'n_threads': cpu_cores,
                'requires_cuda_build': False,
                'description': 'Solo CPU'
            }
        })
        
        if self.hardware_info.get('has_nvidia_gpu', False):
            options.append({
                'name': 'GPU NVIDIA',
                'description': "Usar GPU NVIDIA con aceleración CUDA - Máximo rendimiento (requiere drivers CUDA actualizados).",
                'config': {
                    'type': 'force_nvidia',
                    'n_gpu_layers': -1,
                    'requires_cuda_build': True,
                    'description': 'GPU NVIDIA'
                }
            })
        
        return options
    
    def on_option_selected(self, checked, config):
        """Maneja la selección de una opción."""
        if checked:
            self.selected_config = config
    
    def apply_configuration(self):
        """Aplica la configuración seleccionada."""
        if not self.selected_config:
            self.show_notification("Error", "No se ha seleccionado ninguna configuración.", "")
            return
        
        try:
            config_data = {
                'hardware_info': self.hardware_info,
                'selected_config': self.selected_config,
                'timestamp': __import__('datetime').datetime.now().isoformat(),
                'auto_generated': False
            }
            
            with open('hardware_config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            config_name = self.selected_config.get('description', 'Configuración seleccionada')
            gpu_layers = self.selected_config.get('n_gpu_layers', 0)
            cpu_threads = self.selected_config.get('n_threads', 'automático')
            
            self.show_notification(
                "✅ Configuración Guardada",
                f"Configuración '{config_name}' aplicada exitosamente.",
                f"GPU Layers: {gpu_layers}\nCPU Threads: {cpu_threads}\n\nMARTIN LLM usará esta configuración automáticamente."
            )
            
        except Exception as e:
            self.show_notification("Error", f"No se pudo guardar la configuración:", f"{str(e)}")

    def show_notification(self, title, message, details):
        self.notification_title.setText(title)
        self.notification_message.setText(message)
        self.notification_details.setText(details)
        self.stacked_widget.setCurrentWidget(self.notification_widget)

def main():
    """Función principal para ejecutar el configurador independientemente."""
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    dialog = HardwareConfigDialog()
    result = dialog.exec()
    
    return result

if __name__ == "__main__":
    sys.exit(main())
