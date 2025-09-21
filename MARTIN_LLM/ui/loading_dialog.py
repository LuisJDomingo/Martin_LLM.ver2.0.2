# -*- coding: utf-8 -*-
# ui/loading_dialog.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from .custom_widgets import FadeInMixin

class LoadingDialog(FadeInMixin, QDialog):
    """Ventana de carga con tema sci-fi para PyQt6"""
    
    # Señal emitida cuando la carga está completa
    loading_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Cargando Martin LLM")
        self.setFixedSize(400, 150)

        # Configurar ventana sin bordes del sistema
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Variables para arrastrar ventana
        self.drag_position = None
        
        self.setup_ui()
        
        # Centrar la ventana en la pantalla
        self.center_on_screen()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Frame principal
        main_frame = QFrame()
        main_frame.setObjectName("loadingFrame")
        # El estilo se hereda del stylesheet global de la aplicación

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)

        # Título
        title_label = QLabel("Cargando Martin LLM...")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        # El estilo se hereda del stylesheet global
        frame_layout.addWidget(title_label)

        # Etiqueta de estado
        self.status_label = QLabel("Iniciando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Consolas", 10))
        # El estilo se hereda del stylesheet global
        frame_layout.addWidget(self.status_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(350)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setTextVisible(True)
        # Forzar altura y estilo del texto vía stylesheet para sobreescribir estilos globales
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 40px;
                min-height: 40px;
                max-height: 40px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
            }
        """)
        # El estilo se hereda del stylesheet global de la aplicación
        frame_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(main_frame)

        # Hacer que la ventana sea arrastrable
        main_frame.mousePressEvent = self.mouse_press_event
        main_frame.mouseMoveEvent = self.mouse_move_event
        
    def center_on_screen(self):
        """Centra la ventana en la pantalla"""
        screen = self.screen()
        if screen:
            screen_rect = screen.geometry()
            x = (screen_rect.width() - self.width()) // 2
            y = (screen_rect.height() - self.height()) // 2
            self.move(x, y)

    def mouse_press_event(self, event):
        """Maneja el evento de presionar mouse para arrastrar"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouse_move_event(self, event):
        """Maneja el evento de mover mouse para arrastrar"""
        if (event.buttons() == Qt.MouseButton.LeftButton and 
            self.drag_position is not None):
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def update_status(self, progress_value, status_text):
        """Actualiza el progreso y el texto de estado"""
        self.progress_bar.setValue(progress_value)
        self.status_label.setText(status_text)
        
    def simulate_loading(self):
        """Simula un proceso de carga con diferentes etapas"""
        stages = [
            (10, "Verificando sistema..."),
            (25, "Iniciando Ollama..."),
            (40, "Cargando servicios..."),
            (60, "Preparando interfaz..."),
            (80, "Configurando componentes..."),
            (95, "Finalizando..."),
            (100, "¡Listo!")
        ]

        self.current_stage = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_stage)
        self.timer.start(500)  # 500ms entre cada etapa
        
    def _next_stage(self):
        """Avanza a la siguiente etapa de carga"""
        if self.current_stage < len(self.stages):
            progress, text = self.stages[self.current_stage]
            self.update_status(progress, text)
            self.current_stage += 1
        else:
            self.timer.stop()
            QTimer.singleShot(500, self._complete_loading)

    def _complete_loading(self):
        """Completa la carga y emite la señal"""
        self.loading_complete.emit()
        self.close()
        
    def start_loading(self):
        """Inicia el proceso de carga"""
        self.stages: list[tuple[int, str]] = [
            (10, "Verificando sistema..."),
            (25, "Iniciando Ollama..."),
            (40, "Cargando servicios..."),
            (60, "Preparando interfaz..."),
            (80, "Configurando componentes..."),
            (95, "Finalizando..."),
            (100, "¡Listo!")
        ]
        
        self.current_stage = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_stage)
        self.timer.start(800)  # 800ms entre cada etapa
