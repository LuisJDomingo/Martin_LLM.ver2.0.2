# -*- coding: utf-8 -*- 
# ui/chat_interface.py

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QSpacerItem, QComboBox, QInputDialog,
    QButtonGroup, QGraphicsBlurEffect,
    QTextEdit, QLineEdit, QPushButton, QLabel, QCheckBox,
    QMessageBox, QFrame, QSplitter, QListWidget,
    QListWidgetItem, QFileDialog, QApplication, QSizePolicy, QToolButton, QProgressBar, QScrollArea,
    QGraphicsOpacityEffect
    
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, Qt, QAbstractAnimation, QThread, QParallelAnimationGroup
from PyQt6.QtGui import QFontMetrics
import psutil
import qtawesome as qta
from matplotlib import style as mpl_style
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QIcon, QPixmap
import markdown
from app.llm_providers import BaseLLMProvider
from app.chat_engine import ChatEngine, SYSTEM_PROMPT
from app.services.login_service import UserService
from app.llm_providers import CtransformersProvider
from ui.process_log_window import ProcessLogWindow
from app.workers import Worker, AgentWorker, ReasonerWorker, CleanupWorker
from ui.model_manager_widget import ModelManagerWidget
from ui.llm_parameters_widget import LLMParametersWidget
from ui.closing_dialog import ClosingDialog
from ui.conversation_load_dialog import ConversationLoadDialog
from bson.objectid import ObjectId
from .custom_widgets import FramelessWindowMixin, CustomTitleBar, FadeInMixin, show_critical_message, show_warning_message, show_information_message, show_question_message, show_detailed_error_message
import json
from datetime import datetime, date, timedelta
from collections import OrderedDict


class ModelComboBox(QComboBox):
    """
    Un QComboBox personalizado que abre el gestor de modelos si no hay modelos instalados
    y el usuario hace clic en él.
    """
    open_model_manager_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.no_models_text = "No hay modelos instalados"

    def mousePressEvent(self, event):
        """
        Sobrescribe el evento de clic del ratón. Si el ComboBox está en el estado
        'sin modelos', emite una señal para abrir el gestor de modelos.
        De lo contrario, se comporta como un QComboBox normal.
        """
        if self.count() == 1 and self.itemText(0) == self.no_models_text:
            self.open_model_manager_requested.emit()
        else:
            super().mousePressEvent(event)

'''class SystemStatsWidget(QFrame):
    """Widget para mostrar estadísticas del sistema con diseño futurista horizontal
       no esta implementado aún, solo hace falta elimianr la notacion de comentario en chat_interface.py"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        """Configura la interfaz de estadísticas con layout horizontal en la parte inferior"""

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = QWidget()
        right_panel = QWidget()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)
        layout.setSpacing(10)

        mpl_style.use("dark_background")

        self.figure = Figure(figsize=(10, 2.5), facecolor="#E6E6E600")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Crear subplots horizontales (1 fila, 3 columnas)
        self.ax_cpu = self.figure.add_subplot(1, 3, 1)
        self.ax_ram = self.figure.add_subplot(1, 3, 2)
        self.ax_disk = self.figure.add_subplot(1, 3, 3)

        for ax in [self.ax_cpu, self.ax_ram, self.ax_disk]:
            ax.set_facecolor("#242831")
            ax.axis("off")
        self.figure.subplots_adjust(left=0.05, right=0.95, top=1.0, bottom=0.0, wspace=0.2)
    def draw_clean_gauge(self, ax, percent, label, color_key):
        """Dibuja un gauge circular limpio y legible con título debajo"""
        ax.clear()
        ax.set_aspect("equal")
        ax.set_facecolor("#1a1d23")
        ax.axis("off")

        primary_color = self.get_heat_color(percent)
        background_color = "#374151"

        sizes = [percent, 100 - percent]
        colors = [primary_color, background_color]

        wedges, texts = ax.pie(sizes,
                              colors=colors,
                              startangle=90,
                              counterclock=False,
                              wedgeprops=dict(width=0.3, edgecolor="none"))

        ax.text(0, 0, f"{int(percent)}%",
                ha="center", va="center",
                color="white",
                fontsize=14,
                weight="bold",
                family="monospace")

        # Añadir etiqueta DEBAJO del círculo
        ax.text(0, -1.6, label,
                ha="center", va="center", color=primary_color,
                fontsize=12,
                weight="bold",
                family="monospace")
        
        # Configurar límites para dar espacio al título debajo
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.9, 1.2)     
    def update_stats(self):
        """Actualiza las estadísticas del sistema"""
        try:
            # Evitar el warning si el canvas aún no tiene tamaño
            if self.canvas.width() == 0 or self.canvas.height() == 0:
                return

            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent

            self.draw_clean_gauge(self.ax_cpu, cpu, "CPU", "cpu")
            self.draw_clean_gauge(self.ax_ram, ram, "RAM", "ram")
            self.draw_clean_gauge(self.ax_disk, disk, "DISCO", "disk")
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    def get_heat_color(self, value):
        """Devuelve un color que va de azul (0%) a rojo (100%) pasando por verde (50%)."""
        value = max(0, min(value, 100))  # Clamp 0-100

        if value < 50:
            # Interpolar entre azul (0,0,255) y verde (0,255,0)
            ratio = value / 50
            r = 0
            g = int(255 * ratio)
            b = int(255 * (1 - ratio))
        else:
            # Interpolar entre verde (0,255,0) y rojo (255,0,0)
            ratio = (value - 50) / 50
            r = int(255 * ratio)
            g = int(255 * (1 - ratio))
            b = 0

        # Devolver como color hexadecimal para matplotlib
            return f"#{r:02x}{g:02x}{b:02x}" '''

class CollapsiblePanel(QWidget):
    def __init__(self, title:str, parent=None, content_widget:QWidget=None):
        super().__init__(parent)

        self.setObjectName("collapsiblePanel")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        # Header (título + icono)
        self.header = QWidget()
        self.header.setObjectName("collapsibleHeader")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        self.header_layout.setSpacing(5)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()

        # Hacemos que el header sea clickable
        self.header.mousePressEvent = self.toggle

        self.main_layout.addWidget(self.header)

        # Contenido plegable
        self.content = content_widget if content_widget is not None else QWidget()
        if not self.content.layout(): self.content.setLayout(QVBoxLayout())
        self.content.setVisible(False)  # inicialmente plegado
        self.main_layout.addWidget(self.content)
    def toggle(self, event):
        is_visible = self.content.isVisible()
        self.content.setVisible(not is_visible)

class ChatInterface(FadeInMixin, QMainWindow, FramelessWindowMixin):
    """Interfaz principal de chat en PyQt6"""

    logout_requested = pyqtSignal()
    def __init__(self, user_id, username, chat_engine: ChatEngine, user_service: UserService, parent=None):
        super().__init__(parent)
        print(f"[chat_interface.py][ChatInterface] __init__: Creando CHAT para user_id={user_id}, username={username}")
        # Initialize left and right panels
        self.left_panel = QWidget()
        self.left_panel.setObjectName("leftSidePanel")

        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightSidePanel")
    
           # Atributos
        self.user_id = user_id
        self.username = username
        self.selected_model_name = ""
        self.agent_mode = False
        self.left_panel_width = 350
        self.right_panel_width = 400
        # Hacer los paneles redimensionables en horizontal
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.reasoner_mode = False
        self.model_manager = None
        self.stats_timer = None
        self.worker_thread = None
        self.running_animations = [] # Lista para mantener las animaciones vivas
        
        # Usamos las instancias pasadas por el controlador
        self.chat_engine = chat_engine
        self.user_service = user_service
        self.persistence_service = self.user_service # Persistence is now always through UserService
        self.cleanup_in_progress = False
        self.is_ready_to_close = False
        self._init_frameless_mixin()

        # Efecto de desenfoque y velo para diálogos modales
        self.blur_effect = QGraphicsBlurEffect()
        self.overlay = QFrame(self)
        self.overlay.setObjectName("dialogOverlay")
        self.overlay.setStyleSheet("""
            QFrame#dialogOverlay {
                background-color: rgba(40, 40, 40, 150);
            }
        """)
        self.overlay.hide()

        # Configurar ventana
        self.setWindowTitle(f"Martin LLM - {username}")
        
        # --- Ajuste dinámico del tamaño de la ventana ---
        screen = QApplication.primaryScreen()
        if screen:
            available_geometry = screen.availableGeometry()
            screen_width = available_geometry.width()
            screen_height = available_geometry.height()
            
            window_width = int(screen_width * 0.85)
            window_height = int(screen_height * 0.85)
            
            self.resize(window_width, window_height)
            
            # Centrar la ventana
            self.move(int((screen_width - window_width) / 2), int((screen_height - window_height) / 2))
            
            self.setMinimumSize(int(screen_width * 0.5), int(screen_height * 0.5))
        else:
            # Fallback a un tamaño fijo si no se puede obtener la pantalla
            self.resize(1400, 900)
            self.setMinimumSize(1200, 800)

        

        # Inicializar la ventana de log de procesos
        self.process_log_window = ProcessLogWindow(parent=self)
        self.process_log_window.hide() # Ocultar por defecto
        
        print("[ChatInterface] __init__: Usando persistencia de usuario registrado (MongoDB).")

        # --- INICIALIZACIÓN DIRECTA Y ROBUSTA ---
        print("[ChatInterface] __init__: Inicialización síncrona iniciada.")
        

        self.setup_ui()
        self.populate_installed_models_combo()
        self.populate_recent_conversations()
        # self.setup_stats_timer()
        print("[ChatInterface] __init__: Inicialización síncrona completada.")

        if self.user_service.is_first_login(self.user_id):
            self.display_welcome_message()
            self.user_service.mark_first_login_completed(self.user_id)
        else:
            return_message = {"role": "assistant", "content": f"¡Hola de nuevo, {self.username}! ¿En qué puedo ayudarte hoy?"}
            self.add_to_history(return_message, show_rating_buttons=False)

    def resizeEvent(self, event):
        """Asegura que el velo de superposición cubra toda la ventana."""
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())

    def display_welcome_message(self):
        """Muestra un mensaje de bienvenida distinto según el consentimiento del usuario."""
        
        # Partes comunes del mensaje
        greeting = f"### ¡Bienvenido a Martin LLM, {self.username}!"
        instructions = """
        Aquí tienes una guía rápida para empezar:

        *   **Selecciona un Modelo:** Usa el menú desplegable en la parte inferior para elegir un modelo. Si no tienes ninguno, haz clic en *Gestionar Modelos* en el panel derecho para instalar uno.
        *   **Elige un Modo:**
            *   **Chat:** Para una conversación normal.
            *   **Agente:** Para darle al modelo acceso a herramientas y que pueda completar tareas.
            *   **Razonador:** Para problemas complejos que requieren planificación.
        *   **Inicia la Conversación:** Escribe tu mensaje en el cuadro de texto y presiona *Enter* o el botón de enviar.
        *   **Gestiona tus Chats:** Usa el panel izquierdo (puedes mostrarlo con el botón de comentarios en la parte superior) para ver, cargar, renombrar o eliminar conversaciones anteriores.

        ¡Disfruta de tu asistente de IA personal!
                """
        
        has_consent = self.user_service.get_user_consent(self.user_id)
        
        if has_consent:
            # Mensaje para usuarios que SÍ consienten
            intro_text = "Gracias por apoyar el proyecto compartiendo tus conversaciones de forma anónima para mejorar la IA."
            full_markdown_text = f"{greeting}\n\n{intro_text}\n\n{instructions}"
        else:
            # Mensaje para usuarios que NO consienten
            privacy_note = """
            ---
            > **Nota de Privacidad:** Has decidido no compartir tus conversaciones. El objetivo de compartirlas es el de mejorar la calidad de las respuestas. Si más adelante deseas apoyar el proyecto, estaremos encantados de recibir tu ayuda.
                        """
            full_markdown_text = f"{greeting}\n\n{instructions}\n\n{privacy_note}"
            
        # El widget de mensaje ahora se encarga de la conversión de Markdown.
        # Pasamos el texto Markdown directamente.
        welcome_message = {"role": "assistant", "content": full_markdown_text}
        self.add_to_history(welcome_message, show_rating_buttons=False)

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        print("[ChatInterface] setup_ui: Configurando la interfaz de usuario principal.")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, f"Martin LLM - {self.username}")
        main_layout.addWidget(self.title_bar)
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(10)

        # Crear y añadir la nueva barra de controles
        self.create_control_bar(frame_layout)

        self.create_central_area(frame_layout)
        main_layout.addWidget(main_frame)

    def create_control_bar(self, parent_layout):
        """Crea una barra de controles para los paneles."""
        control_bar_frame = QFrame()
        control_bar_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        control_bar_frame.setObjectName("topBarFrame") # Reutilizamos un estilo existente
        control_bar_frame.setStyleSheet("QFrame#topBarFrame { border-bottom: none; border-radius: 0; }")
        
        control_layout = QHBoxLayout(control_bar_frame)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(10)

        # Botón para panel izquierdo (Conversaciones)
        self.toggle_left_button = QPushButton(qta.icon('fa5s.comments', color="white"), "")
        self.toggle_left_button.setObjectName("iconButton")
        self.toggle_left_button.setFixedSize(40, 40)
        self.toggle_left_button.setToolTip("Mostrar/Ocultar panel de conversaciones")
        self.toggle_left_button.clicked.connect(self.toggle_left_panel)
        control_layout.addWidget(self.toggle_left_button)

        control_layout.addStretch()

        # Botón para panel derecho (Ajustes) y otros controles
        self.toggle_right_button = QPushButton(qta.icon('fa5s.cog', color="white"), "")
        self.toggle_right_button.setObjectName("iconButton")
        self.toggle_right_button.setFixedSize(40, 40)
        self.toggle_right_button.setToolTip("Mostrar/Ocultar panel de ajustes")
        self.toggle_right_button.clicked.connect(self.toggle_right_panel)
        control_layout.addWidget(self.toggle_right_button)

        parent_layout.addWidget(control_bar_frame)

    def create_central_area(self, parent_layout):
        """Crea el área central con chat, entrada y estadísticas"""
        # Usamos un layout horizontal en lugar de un QSplitter para permitir animaciones.
        central_area_widget = QWidget()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        chat_frame = QFrame()
        splitter.addWidget(chat_frame)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([200, 400, 200])

        central_area_layout = QHBoxLayout(central_area_widget)
        central_area_layout.addWidget(splitter)
        central_area_layout.setContentsMargins(0, 0, 0, 0)
        central_area_layout.setSpacing(0) # Sin espacio entre paneles para un look integrado

        # El botón para toggle se ha movido a la top_bar

        # Create the conversations panel and add it
        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_layout.setSpacing(0)
        self.conversations_panel = self.create_conversations_panel()
        self.left_panel_layout.addWidget(self.conversations_panel)
        # Estado inicial para la animación (oculto)
        self.left_panel.setMaximumWidth(0)

        # --- Central Chat Area ---
        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(20, 0, 20, 0) # Reducido el padding horizontal para un área de chat más ancha
        chat_layout.setSpacing(10)

        # Create a scroll area for chat history
        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setObjectName("historyScrollArea")

        # Widget que contendrá la lista de mensajes y los stretches para centrar
        self.history_content_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_content_widget)
        self.history_layout.setContentsMargins(15, 5, 15, 5)
        self.history_layout.setSpacing(15)

        # Añadir stretches para centrar verticalmente el contenido.
        # Los mensajes se insertarán entre estos dos stretches.
        self.history_layout.addStretch(1)
        self.history_layout.addStretch(1)

        self.history_scroll_area.setWidget(self.history_content_widget)
        chat_layout.addWidget(self.history_scroll_area, stretch=1)

        # Indicador de carga
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)  # Modo indeterminado
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setTextVisible(False)
        self.loading_indicator.setFixedHeight(20)
        
        # Layout para centrar la barra de progreso
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.loading_indicator)
        progress_layout.addStretch()
        chat_layout.addLayout(progress_layout)

        # Input Frame
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(150, 5, 150, 5) # Corregido padding asimétrico

        self.input_text = QTextEdit()
        self.input_text.setObjectName("inputText")
        self.input_text.setPlaceholderText("Escribe tu prompt aquí...")
        self.input_text.keyPressEvent = self.input_key_press
        self.input_text.textChanged.connect(self.adjust_input_text_height)
        input_layout.addWidget(self.input_text)

        # Establecer la altura inicial del input
        self.adjust_input_text_height()
        bottom_bar_widget = QWidget()
        bottom_bar_layout = QHBoxLayout(bottom_bar_widget)

        bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        bottom_bar_layout.setSpacing(10)

        # Selector de modelo instalado
        self.installed_models_combo = ModelComboBox()
        self.installed_models_combo.setObjectName("installedModelsCombo")
        self.installed_models_combo.setToolTip("Seleccionar un modelo instalado localmente")
        self.installed_models_combo.currentIndexChanged.connect(self.on_installed_model_selected)
        self.installed_models_combo.open_model_manager_requested.connect(self.show_model_manager)
        bottom_bar_layout.addWidget(self.installed_models_combo)

        # Selector de modo
        label = QLabel("Modo:")
        bottom_bar_layout.addWidget(label)
        self.mode_selector = self.create_mode_selection_widget()
        bottom_bar_layout.addWidget(self.mode_selector)

        # Botones de acción secundarios
        self.attach_button = QPushButton()
        self.attach_button.setObjectName("iconButton")
        self.attach_button.setIcon(qta.icon("fa5s.paperclip", color="white"))
        self.attach_button.setToolTip("Adjuntar archivo")
        self.attach_button.setFixedSize(40, 40)
        self.attach_button.clicked.connect(self.attach_file)
        bottom_bar_layout.addWidget(self.attach_button)

        self.new_conv_button = QPushButton()
        self.new_conv_button.setObjectName("iconButton")
        self.new_conv_button.setIcon(qta.icon("fa5.file", color="white"))
        self.new_conv_button.setToolTip("Nueva conversación")
        self.new_conv_button.setFixedSize(40, 40)
        self.new_conv_button.clicked.connect(self.start_new_conversation)
        bottom_bar_layout.addWidget(self.new_conv_button)

        self.export_button = QPushButton()
        self.export_button.setObjectName("iconButton")
        self.export_button.setIcon(qta.icon("fa5s.file-export", color="white"))
        self.export_button.setToolTip("Exportar conversación")
        self.export_button.setFixedSize(40, 40)
        self.export_button.clicked.connect(self.export_conversation)
        bottom_bar_layout.addWidget(self.export_button)

        self.logout_button = QPushButton()
        self.logout_button.setObjectName("iconButton")
        self.logout_button.setIcon(qta.icon("fa5s.sign-out-alt", color="white"))
        self.logout_button.setToolTip("Cerrar sesión")
        self.logout_button.setFixedSize(40, 40)
        self.logout_button.clicked.connect(self.logout)
        bottom_bar_layout.addWidget(self.logout_button)

        # Espaciador para empujar el botón de enviar a la derecha
        bottom_bar_layout.addStretch()

        # Botón de enviar
        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setIcon(qta.icon("fa5s.paper-plane", color="#1a1d23"))
        self.send_button.setToolTip("Enviar mensaje (Enter)")
        self.send_button.setFixedSize(80, 40)
        self.send_button.clicked.connect(self.send_message)
        bottom_bar_layout.addWidget(self.send_button)

        input_layout.addWidget(bottom_bar_widget)
        chat_layout.addWidget(input_frame)

        # --- Right Panel Area ---
        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightSidePanel")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        self.model_selection_panel = self.create_model_selection_panel()
        system_prompt_widget = self.create_system_prompt_widget()
        self.parameters_panel = self.create_parameters_panel()
        self.hardware_config_panel = self.create_hardware_config_panel()
        # self.system_stats_panel = self.create_system_stats_panel()
        right_layout.addWidget(self.model_selection_panel)
        right_layout.addWidget(self.parameters_panel)
        right_layout.addWidget(self.hardware_config_panel)
        right_layout.addWidget(system_prompt_widget)
        # right_layout.addWidget(self.system_stats_panel)
        right_layout.addStretch(1)
        # Estado inicial para la animación (oculto)
        self.right_panel.setMaximumWidth(0)

        # Añadir los widgets al layout horizontal
        central_area_layout.addWidget(self.left_panel)

        # Añadir espacio vacío a los lados del panel de chat para estrecharlo.
        # Proporción: 1 (espacio) + 6 (chat) + 1 (espacio) = 8.
        # El chat ocupa 6/8 = 75% del espacio flexible, haciéndolo un 25% más estrecho.
        central_area_layout.addStretch(1)
        central_area_layout.addWidget(chat_frame, 6)
        central_area_layout.addStretch(1)

        central_area_layout.addWidget(self.right_panel)

        parent_layout.addWidget(central_area_widget)

    def create_conversations_panel(self):
        """Crea el panel que contiene la lista de conversaciones."""
        conversations_widget = QFrame()
        conversations_widget.setObjectName("leftPanelFrame")
        left_panel_layout = QVBoxLayout(conversations_widget)
        left_panel_layout.setContentsMargins(10, 10, 10, 10)
        left_panel_layout.setSpacing(10)

        self.conv_title_label = QLabel("Chats")
        self.conv_title_label.setObjectName("panelTitle")
        left_panel_layout.addWidget(self.conv_title_label)
        self.recent_convs_list = QListWidget()
        self.recent_convs_list.setObjectName("recentConvsList")
        self.recent_convs_list.itemDoubleClicked.connect(self.on_recent_conversation_selected)
        left_panel_layout.addWidget(self.recent_convs_list)
        return conversations_widget

    def toggle_left_panel(self):
        """Muestra u oculta el panel de conversaciones recientes con una animación suave."""
        if not hasattr(self, "left_panel"):
            return

        current_width = self.left_panel.maximumWidth()
        target_width = self.left_panel_width if current_width == 0 else 0

        self.left_animation = QPropertyAnimation(self.left_panel, b"maximumWidth")
        self.left_animation.setDuration(300) # Duración en milisegundos
        self.left_animation.setStartValue(current_width)
        self.left_animation.setEndValue(target_width)
        self.left_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.left_animation.start()

    def toggle_right_panel(self):
        """Muestra u oculta el panel de ajustes con una animación suave."""
        if not hasattr(self, "right_panel"):
            return

        current_width = self.right_panel.maximumWidth()
        target_width = self.right_panel_width if current_width == 0 else 0

        self.right_animation = QPropertyAnimation(self.right_panel, b"maximumWidth")
        self.right_animation.setDuration(300) # Duración en milisegundos
        self.right_animation.setStartValue(current_width)
        self.right_animation.setEndValue(target_width)
        self.right_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.right_animation.start()

    def create_mode_selection_widget(self):
        """Crea un combo box para seleccionar el modo de operación."""
        mode_combo = QComboBox()
        mode_combo.setObjectName("modeSelector")

        # Definir modos con iconos y datos
        self.modes_data = [
            {"icon": "fa5s.comments", "text": "Chat", "data": "chat"},
            {"icon": "fa5s.user-secret", "text": "Agente", "data": "agent"},
            {"icon": "fa5s.brain", "text": "Razonador", "data": "reasoner"}
        ]

        for mode in self.modes_data:
            icon = qta.icon(mode["icon"], color="white")
            mode_combo.addItem(icon, mode["text"], userData=mode["data"])

        # Establecer modo por defecto
        mode_combo.setCurrentIndex(0)

        # Conexiones para la lógica de visualización de iconos
        mode_combo.view().pressed.connect(self.on_mode_combo_show_popup)
        mode_combo.currentIndexChanged.connect(self._update_mode_display)

        # Conectar cambio de selección para la lógica de la aplicación
        mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        self.mode_combo = mode_combo  # Asignar el QComboBox a self.mode_combo
        self._update_mode_display(0)  # Llamada inicial para ocultar el texto
        return mode_combo

    def on_mode_combo_show_popup(self, index):
        """Restaura el texto de todos los items antes de mostrar el desplegable."""
        for i, mode_info in enumerate(self.modes_data):
            self.mode_combo.setItemText(i, mode_info["text"])

    def _update_mode_display(self, index):
        """
        Oculta el texto del item seleccionado después de que el desplegable se cierra,
        mostrando solo el icono.
        """
        # Usamos un QTimer para asegurar que el texto se oculte después de que el
        # desplegable se haya cerrado y la selección se haya procesado.
        QTimer.singleShot(0, lambda: self.mode_combo.setItemText(index, ""))

    def create_system_prompt_widget(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(SYSTEM_PROMPT)
        self.system_prompt_edit.setPlaceholderText("Modifica el System Prompt aquí...")
        self.system_prompt_edit.setObjectName("inputText")
        content_layout.addWidget(self.system_prompt_edit)

        self.update_prompt_btn = QPushButton("Actualizar System Prompt")
        self.update_prompt_btn.setObjectName("primaryButton")
        self.update_prompt_btn.clicked.connect(self.update_system_prompt)
        content_layout.addWidget(self.update_prompt_btn)

        collapsible_panel = CollapsiblePanel("SYSTEM PROMPT", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)
        return collapsible_panel
    
    def create_model_selection_panel(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        self.manage_models_button = QPushButton("Gestionar Modelos (Instalar/Eliminar)")
        self.manage_models_button.clicked.connect(self.show_model_manager)
        content_layout.addWidget(self.manage_models_button)

        collapsible_panel = CollapsiblePanel("SELECCIÓN DE MODELO", content_widget=content_widget)
        collapsible_panel.content.setVisible(True) # Initially expanded
        return collapsible_panel

    '''def create_system_stats_panel(self):
        content_widget = SystemStatsWidget()
        collapsible_panel = CollapsiblePanel("MONITOR DEL SISTEMA", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)      # desplegado al iniciar
        return collapsible_panel'''
    
    def create_parameters_panel(self):
        """Crea el panel plegable para los parámetros del LLM."""
        content_widget = LLMParametersWidget()
        content_widget.parameters_changed.connect(self.on_parameters_changed)

        collapsible_panel = CollapsiblePanel("PARÁMETROS DEL MODELO", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)
        return collapsible_panel
    
    def create_hardware_config_panel(self):
        """Crea el panel plegable para la configuración de hardware."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Etiqueta de estado actual
        self.hardware_status_label = QLabel("Cargando configuración...")
        self.hardware_status_label.setWordWrap(True)
        self.hardware_status_label.setStyleSheet(
            "QLabel { "
            "   background-color: #2d3748; "
            "   border: 1px solid #4a5568; "
            "   border-radius: 6px; "
            "   padding: 8px; "
            "   font-size: 10pt; "
            "}"
        )
        content_layout.addWidget(self.hardware_status_label)
        
        # Botón para configurar hardware
        self.configure_hardware_btn = QPushButton("Configurar Hardware")
        self.configure_hardware_btn.setObjectName("primaryButton")
        self.configure_hardware_btn.clicked.connect(self.show_hardware_config)
        content_layout.addWidget(self.configure_hardware_btn)
                
        collapsible_panel = CollapsiblePanel("CONFIGURACIÓN DE HARDWARE", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)
        
        # Actualizar estado inicial
        self.update_hardware_status_display()
        
        return collapsible_panel
    
    def on_parameters_changed(self, params: dict):
        """Se ejecuta cuando un parámetro del modelo cambia en el widget."""
        if self.chat_engine and self.chat_engine.provider:
            self.chat_engine.provider.set_generation_parameters(**params)
    
    def create_left_panel_widget(self):
        """Crea el panel izquierdo que contiene la lista de conversaciones."""
        left_panel_widget = QFrame()
        left_panel_widget.setObjectName("leftPanelFrame")
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(10, 10, 10, 10)
        left_panel_layout.setSpacing(10)

        title_label = QLabel("CONVERSACIONES")
        title_label.setObjectName("panelTitle")
        left_panel_layout.addWidget(title_label)
        
        self.recent_convs_list = QListWidget()
        self.recent_convs_list.setObjectName("recentConvsList")
        self.recent_convs_list.itemDoubleClicked.connect(self.on_recent_conversation_selected)
        left_panel_layout.addWidget(self.recent_convs_list)
        return left_panel_widget
    
    def populate_recent_conversations(self):
        """Carga las conversaciones del usuario en la lista, ordenadas por fecha."""
        print("[DEBUG] populate_recent_conversations: Iniciando...")
        try:
            self.recent_convs_list.clear()
            print(f"[DEBUG] populate_recent_conversations: Llamando a self.persistence_service.get_user_conversations para user_id: {self.user_id}")
            conversations = self.persistence_service.get_user_conversations(self.user_id)
            print(f"[DEBUG] populate_recent_conversations: Datos recibidos de get_user_conversations: {conversations}")

            print(f"[DEBUG] populate_recent_conversations: Se encontraron {len(conversations) if conversations else 0} conversaciones.")
            if not conversations:
                print("[DEBUG] populate_recent_conversations: No hay conversaciones, añadiendo placeholder y saliendo.")
                placeholder_item = QListWidgetItem("No hay conversaciones recientes.")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.recent_convs_list.addItem(placeholder_item)
                return

            print(f"[DEBUG] populate_recent_conversations: Conversaciones recibidas del servicio: {conversations}")

            # Normalizar todos los timestamps a objetos datetime ANTES de ordenar.
            print("[DEBUG] populate_recent_conversations: Normalizando timestamps...")
            for conv in conversations:
                ts = conv.get('timestamp')
                print(f"[DEBUG] populate_recent_conversations: Procesando conv, timestamp original: {ts} (tipo: {type(ts)})")
                if isinstance(ts, str):
                    try:
                        conv['timestamp'] = datetime.fromisoformat(ts)
                        print(f"[DEBUG] populate_recent_conversations: Timestamp convertido de string a datetime: {conv['timestamp']}")
                    except ValueError:
                        conv['timestamp'] = datetime.min
                        print(f"[DEBUG] populate_recent_conversations: Timestamp string inválido, asignando datetime.min")
                elif not isinstance(ts, datetime):
                    conv['timestamp'] = datetime.min # Asegurar que siempre sea un datetime
                    print(f"[DEBUG] populate_recent_conversations: Timestamp no es string ni datetime, asignando datetime.min")

            sorted_convs = sorted(conversations, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            print("[DEBUG] populate_recent_conversations: Conversaciones ordenadas por fecha.")

            max_calculated_width = 0

            # --- Agrupación de conversaciones ---
            print("[DEBUG] populate_recent_conversations: Agrupando conversaciones por fecha...")
            groups = OrderedDict()
            today = date.today()
            yesterday = today - timedelta(days=1)
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

            for conv in sorted_convs:
                timestamp = conv.get("timestamp", datetime.now())
                if not isinstance(timestamp, datetime):
                    print(f"[DEBUG] populate_recent_conversations: Saltando conversación sin timestamp válido: {conv.get('_id')}")
                    continue

                conv_date = timestamp.date()
                
                if conv_date == today:
                    group_key = "Hoy"
                elif conv_date == yesterday:
                    group_key = "Ayer"
                else:
                    group_key = f"{conv_date.day} de {meses[conv_date.month - 1]} de {conv_date.year}"

                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(conv)

            print(f"[DEBUG] populate_recent_conversations: Grupos creados: {list(groups.keys())}")

            # --- Poblado del QListWidget ---
            def add_header_item(text):
                print(f"[DEBUG] populate_recent_conversations: Añadiendo cabecera de grupo: {text}")
                header_item = QListWidgetItem(text.upper())
                header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                header_item.setForeground(QColor("#a0aec0"))
                self.recent_convs_list.addItem(header_item)

            def add_conv_item(conv):
                nonlocal max_calculated_width
                conv_id = str(conv.get("_id"))
                title = conv.get("title", "Sin título")
                print(f"[DEBUG] populate_recent_conversations: Añadiendo item para conversación ID: {conv_id}, Título: '{title}'")

                words = title.split()
                if len(words) > 5:
                    display_title = " ".join(words[:5]) + "..."
                else:
                    display_title = title

                row_widget = QWidget()
                row_widget.setObjectName("recentConvRow")
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(5, 2, 5, 2)
                row_layout.setSpacing(5)
                title_label = QLabel(display_title)
                title_label.setToolTip(f"Doble clic para cargar: {title}")
                title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                rename_button = QPushButton(qta.icon('fa5s.edit', color="white"), "")
                rename_button.setFixedSize(20, 20)
                rename_button.setToolTip("Renombrar conversación")
                rename_button.setStyleSheet("QPushButton { border-radius: 10px; background: transparent; padding: 0; } QPushButton:hover { background-color: #4a90e2; }")
                rename_button.clicked.connect(lambda checked=False, c_id=conv_id, c_title=title: self.rename_recent_conversation(c_id, c_title))

                delete_button = QPushButton(qta.icon('fa5s.trash-alt', color="white"), "")
                delete_button.setFixedSize(20, 20)
                delete_button.setToolTip("Eliminar esta conversación")
                delete_button.setStyleSheet("QPushButton { border-radius: 10px; background: transparent; padding: 0; } QPushButton:hover { background-color: #4a90e2; }")
                delete_button.clicked.connect(lambda checked=False, c_id=conv_id: self.delete_recent_conversation(c_id))

                row_layout.addWidget(title_label)
                row_layout.addWidget(rename_button)
                row_layout.addWidget(delete_button)

                font_metrics = QFontMetrics(title_label.font())
                title_width = font_metrics.horizontalAdvance(display_title)
                required_width = 10 + title_width + 10 + 40
                max_calculated_width = max(max_calculated_width, required_width)

                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, conv_id)
                item.setSizeHint(row_widget.sizeHint())

                self.recent_convs_list.addItem(item)
                self.recent_convs_list.setItemWidget(item, row_widget)

            print("[DEBUG] populate_recent_conversations: Poblando la lista de widgets...")
            for group_name, convs_in_group in groups.items():
                add_header_item(group_name)
                for conv in convs_in_group:
                    add_conv_item(conv)

            if max_calculated_width > 0:
                total_panel_width = max_calculated_width + 20
                new_width = max(350, min(total_panel_width, 500))
                self.left_panel_width = new_width
                print(f"[DEBUG] populate_recent_conversations: Ancho del panel calculado: {new_width}px")

                if self.left_panel.maximumWidth() > 0:
                    self.left_panel.setMaximumWidth(self.left_panel_width)
            print("[DEBUG] populate_recent_conversations: Finalizado con éxito.")
        except Exception as e:
            print(f"[DEBUG] populate_recent_conversations: ❌ Error al poblar conversaciones: {e}")
            self.recent_convs_list.clear()
            self.recent_convs_list.addItem("Error al cargar.")
    
    def rename_recent_conversation(self, conversation_id: str, current_title: str):
        """Permite al usuario renombrar una conversación."""
        new_title, ok = QInputDialog.getText(self, "Renombrar Conversación", 
                                             "Nuevo título:", QLineEdit.EchoMode.Normal, 
                                             current_title)
        if ok and new_title and new_title.strip() != current_title:
            success = self.persistence_service.update_conversation_title(self.user_id, conversation_id, new_title.strip())
            if success:
                print(f"[DEBUG][chat_interface.py][ChatInterface] rename_recent_conversation: ✅ Conversación ID: {conversation_id} renombrada a '{new_title.strip()}'")
                self.populate_recent_conversations()
                if self.chat_engine and self.chat_engine.conversation_id == conversation_id:
                    self.chat_engine.title = new_title.strip()
            else:
                print(f"[DEBUG] rename_recent_conversation: ❌ Error al renombrar conversación ID: {conversation_id}")
                show_critical_message(self, "Error", "No se pudo renombrar la conversación.")

    def delete_recent_conversation(self, conversation_id: str):
        """Maneja la eliminación o archivado de una conversación de la lista."""
        reply = show_question_message(self, "Confirmar Acción",
                                     "¿Estás seguro de que quieres quitar esta conversación de la lista?",
                                     buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)            
        if reply == QMessageBox.StandardButton.Yes:
            success = self.persistence_service.delete_or_archive_conversation(self.user_id, conversation_id)
            if success:
                self.populate_recent_conversations()
            else:
                show_critical_message(self, "Error", "No se pudo realizar la operación.")
    
    def update_system_prompt(self):
        """Actualiza el System Prompt en el chat engine."""
        new_prompt = self.system_prompt_edit.toPlainText().strip()
        print(f"[DEBUG] nuevo system prompt: {new_prompt}")
        if self.chat_engine:
            self.chat_engine.system_prompt = new_prompt
            self.add_system_message("SYSTEM PROMPT ACTUALIZADO.")
            show_information_message(self, "Actualizado", 
                                   "El System Prompt ha sido actualizado para la conversación actual.")
        else:
            show_warning_message(self, "Sin conversación activa", 
                               "Debes seleccionar un modelo e iniciar una conversación para poder actualizar el System Prompt.")
    
    def input_key_press(self, event):
        """Maneja las pulsaciones de tecla en el campo de entrada"""
        from PyQt6.QtCore import Qt     
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return
        QTextEdit.keyPressEvent(self.input_text, event)

    def adjust_input_text_height(self):
        """Ajusta la altura del QTextEdit dinámicamente según el contenido."""
        document = self.input_text.document()
        content_height = document.size().height()
        
        font_metrics = self.input_text.fontMetrics()
        single_line_height = font_metrics.height()

        chrome_height = 20 

        min_height = single_line_height + chrome_height
        max_height = (single_line_height * 5) + chrome_height

        target_height = content_height + chrome_height
        final_height = max(min_height, min(target_height, max_height))
        self.input_text.setFixedHeight(int(final_height))
    
    '''def setup_stats_timer(self):
        """Configura el temporizador para actualizar estadísticas"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.system_stats_panel.content.update_stats)
        self.stats_timer.start(7000)  # Actualizar cada 7 segundos  '''     
    
    def show_model_manager(self):
        """Muestra el gestor de modelos como un diálogo modal centrado."""
        if self.model_manager and self.model_manager.isVisible():            
            self.model_manager.activateWindow()
            return   
        self.model_manager = ModelManagerWidget(self)
        self.model_manager.model_selected.connect(self.on_model_selected)
        self.model_manager.exec() # Show as modal dialog        
        self.populate_installed_models_combo() # Refrescar la lista después de cerrar el gestor
   
    def on_model_selected(self, model_identifier):
        """Maneja la selección de un modelo para iniciar una nueva conversación."""
        print(f"[DEBUG] ChatInterface.on_model_selected llamado con modelo: {model_identifier}")
        
        self.add_system_message(f"CARGANDO MODELO: {Path(model_identifier).name}...")
        QApplication.processEvents()
        print(f"[ChatInterface] on_model_selected: Modelo seleccionado: {model_identifier}")

        try:
            if model_identifier.lower().endswith('.gguf'):
                provider = CtransformersProvider(model_path=model_identifier)
                display_name = Path(model_identifier).name
            else:
                # This case should no longer happen as we only load GGUF files
                show_critical_message(self, "Error de Modelo", f"El archivo seleccionado no es un modelo GGUF válido: {model_identifier}")
                return
            print(f"[ChatInterface] on_model_selected: Proveedor '{type(provider).__name__}' creado para el modelo.")

            if hasattr(self, 'parameters_panel'):
                current_params = self.parameters_panel.content.get_current_parameters()
                print(f"[DEBUG] Aplicando parámetros al nuevo modelo: {current_params}")
                provider.set_generation_parameters(**current_params)

            self.chat_engine.provider = provider
            
            self.selected_model_name = model_identifier
            self.update_installed_models_combo_selection()

            self.chat_engine.start_new()
            print("[ChatInterface] on_model_selected: Nueva conversación iniciada en chat_engine.")
            self.system_prompt_edit.setPlainText(SYSTEM_PROMPT)
            
            def on_history_cleared():
                self.add_system_message(f"MODELO {display_name} CARGADO EXITOSAMENTE, Sistema listo para recibir comandos.")
            self.clear_history(on_finished_callback=on_history_cleared)

        except Exception as e:
            error_msg = f"No se pudo cargar el modelo '{Path(model_identifier).name}':\n{e}"
            print(f"[ERROR] {error_msg}")
            show_critical_message(self, "Error al Cargar Modelo", error_msg)
            self.chat_engine.provider = None
    
    def _create_message_widget(self, role, content, message_obj=None, show_rating_buttons=True):
        """Crea un widget para un mensaje individual, devolviendo el contenedor y el editor de contenido."""
        
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(3)

        if role == "user":
            display_role = "Tú"
            style = "font-weight: bold; color: #90cdf4;"
            alignment = Qt.AlignmentFlag.AlignRight
        elif role == "assistant":
            display_role = "Martin LLM"
            style = "font-weight: bold; color: #9ae6b4;"
            alignment = Qt.AlignmentFlag.AlignLeft
        else:
            display_role = role.capitalize()
            style = "font-weight: bold; color: #e1e5e9;"
            alignment = Qt.AlignmentFlag.AlignLeft

        role_label = QLabel(display_role)
        role_label.setStyleSheet(style)
        role_label.setAlignment(alignment)
        message_layout.addWidget(role_label)

        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'sane_lists'])
        content_edit.setHtml(html_content)
        content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d3748;
                padding: 10px;
                border-radius: 8px;
                border: none;
                color: white;
            }
        """)
        content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        message_layout.addWidget(content_edit)

        if role == "assistant" and show_rating_buttons:
            rating_layout = QHBoxLayout()
            rating_layout.setContentsMargins(0, 2, 5, 0)
            rating_layout.setSpacing(5)
            rating_layout.addStretch()
            self.create_rating_buttons(rating_layout, role, content, message_obj)
            message_layout.addLayout(rating_layout)

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        if alignment == Qt.AlignmentFlag.AlignRight:
            outer_layout.addStretch(11)
            outer_layout.addWidget(message_widget, 9)
            outer_layout.addStretch(4)
        else:
            outer_layout.addStretch(4)
            outer_layout.addWidget(message_widget, 9)
            outer_layout.addStretch(11)

        container_widget = QWidget()
        container_widget.setLayout(outer_layout)
        
        return container_widget, content_edit

    def add_to_history(self, message_obj, show_rating_buttons=True, scroll_to_bottom=True):
        """Añade un mensaje al historial de la UI con una animación de fade-in."""
        role = message_obj.get("role", "unknown")
        content = message_obj.get("content", "")

        message_widget, content_edit = self._create_message_widget(role, content, message_obj, show_rating_buttons)

        # --- Animación de Fade-In ---
        opacity_effect = QGraphicsOpacityEffect(message_widget)
        message_widget.setGraphicsEffect(opacity_effect)
        
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(450)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        animation.finished.connect(lambda: self.running_animations.remove(animation))
        self.running_animations.append(animation)
        
        animation.start()

        # Insertar el nuevo mensaje
        self.history_layout.insertWidget(self.history_layout.count() - 1, message_widget)
        
        def adjust_and_scroll():
            self._adjust_message_height(content_edit)
            if scroll_to_bottom:
                # Damos un pequeño respiro extra para que el scroll máximo se actualice
                QTimer.singleShot(10, self.scroll_to_bottom_animated)

        # Ajustar la altura y hacer scroll después de un breve retraso
        QTimer.singleShot(50, adjust_and_scroll)

    def _adjust_message_height(self, content_edit):
        """Ajusta la altura de un QTextEdit de mensaje para que encaje con su contenido."""
        doc_height = content_edit.document().size().height()
        stylesheet_padding = 20 # 10px top + 10px bottom
        content_edit.setFixedHeight(int(doc_height + stylesheet_padding))

    def add_system_message(self, message: str, show_rating_buttons: bool = False):
        """Muestra un mensaje del sistema en la barra de estado."""
        print(f"[SYSTEM_STATUS] {message}")
        self.statusBar().showMessage(message, 7000)

    def clear_history(self, on_finished_callback=None):
        """Limpia el historial de chat de la UI, ejecutando un callback al finalizar."""
        
        widgets_to_remove = []
        for i in range(self.history_layout.count()):
            item = self.history_layout.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())

        if not widgets_to_remove:
            while self.history_layout.count() > 0:
                item = self.history_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.history_layout.addStretch(1)
            self.history_layout.addStretch(1)
            if on_finished_callback:
                on_finished_callback()
            return

        self.animation_group = QParallelAnimationGroup(self)
        for widget in widgets_to_remove:
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)
            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(200)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation_group.addAnimation(animation)

        def on_animations_finished():
            for widget in widgets_to_remove:
                self.history_layout.removeWidget(widget)
                widget.deleteLater()
            
            while self.history_layout.count() > 0:
                item = self.history_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.history_layout.addStretch(1)
            self.history_layout.addStretch(1)
            
            self.animation_group = None
            if on_finished_callback:
                on_finished_callback()

        self.animation_group.finished.connect(on_animations_finished)
        self.animation_group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def send_message(self):
        """Envía el mensaje del usuario al motor de chat."""
        print("[ChatInterface] send_message: Intento de enviar mensaje.")
        
        user_message = self.input_text.toPlainText().strip()
        if not user_message:
            return

        if not self.chat_engine.provider:
            show_warning_message(self, "Advertencia", "Por favor, selecciona un modelo antes de enviar un mensaje.")
            return

        user_message_obj = {"role": "user", "content": user_message}
        self.chat_engine.history.append(user_message_obj)
        self.add_to_history(user_message_obj, show_rating_buttons=False)
        self.input_text.clear()
        self.send_button.setEnabled(False)
        self.loading_indicator.setVisible(True)

        if self.agent_mode:
            self.run_agent_worker(user_message)
        elif self.reasoner_mode:
            self.run_reasoner_worker(user_message)
        else:
            self.run_chat_worker(user_message)

    def run_chat_worker(self, user_message: str):
        """Inicia el worker para el modo de chat normal."""
        self.worker_thread = QThread()
        self.worker = Worker(self.chat_engine, user_message)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        
        self.worker.response_ready.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def run_agent_worker(self, user_message: str):
        """Inicia el worker para el modo agente."""
        from app.agent import Agent
        from app.llm_providers import CtransformersProvider

        if not isinstance(self.chat_engine.provider, CtransformersProvider):
            self.handle_error("Por favor, selecciona un modelo LLM real antes de usar el modo Agente.")
            return

        self.add_system_message("MODO AGENTE INICIADO. OBJETIVO: " + user_message)
        self.process_log_window.show()
        self.process_log_window.append_log(f"MODO AGENTE INICIADO. OBJETIVO: {user_message}")
        
        current_system_prompt = self.chat_engine.system_prompt if self.chat_engine else SYSTEM_PROMPT
        agent = Agent(self.chat_engine.provider, custom_prompt=current_system_prompt)
        self.worker_thread = QThread()
        self.worker = AgentWorker(agent, user_message)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.agent_step.connect(self.display_agent_step)
        self.worker.response_ready.connect(self.handle_agent_response)
        self.worker.error_occurred.connect(self.handle_error)
        
        self.worker.response_ready.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def run_reasoner_worker(self, user_objective: str):
        """Inicia el worker para el modo razonador (Plan-and-Execute)."""
        from app.reasoner import Reasoner
        from app.llm_providers import CtransformersProvider

        if not isinstance(self.chat_engine.provider, CtransformersProvider):
                    self.handle_error("Por favor, selecciona un modelo LLM real antes de usar el modo Razonador.")
                    return

        self.add_system_message("MODO RAZONADOR INICIADO. OBJETIVO: " + user_objective)
        self.process_log_window.show()
        self.process_log_window.append_log(f"MODO RAZONADOR INICIADO. OBJETIVO: {user_objective}")
        
        self.worker_thread = QThread()
        current_system_prompt = self.chat_engine.system_prompt if self.chat_engine else SYSTEM_PROMPT
        self.worker = ReasonerWorker(self.chat_engine.provider, user_objective, custom_prompt=current_system_prompt)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.plan_ready.connect(self.display_reasoner_plan)
        self.worker.step_result.connect(self.display_reasoner_step_result)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        
        self.worker.response_ready.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()
    
    def display_reasoner_plan(self, plan: list):
        plan_text = "\n".join([f"  - Paso {i+1}: {step}" for i, step in enumerate(plan)])
        self.add_system_message(f"📝 PLAN GENERADO:\n{plan_text}", show_rating_buttons=False)
        self.process_log_window.append_log(f"📝 PLAN GENERADO:\n{plan_text}")
    
    def display_reasoner_step_result(self, step_index: int, task: str, result: str):
        self.add_system_message(f"▶️ EJECUTANDO PASO {step_index}: {task}\n✅ RESULTADO: {result[:200]}...", show_rating_buttons=False)
        self.process_log_window.append_log(f"▶️ EJECUTANDO PASO {step_index}: {task}\n✅ RESULTADO: {result[:200]}...")
    
    def display_agent_step(self, thought: str, tool_name: str, args: str):
        """Muestra el paso actual del agente en la UI."""
        if tool_name == "finish":
            step_message = f"🤔 Pensando: {thought}\n- ✅ Acción: Finalizar con la respuesta."
        else:
            step_message = f"🤔 Pensando: {thought}\n- ⚡ Acción: Usar herramienta '{tool_name}' con argumentos: '{args}'"
        self.add_system_message(step_message, show_rating_buttons=False)
        self.process_log_window.append_log(step_message)
    
    def handle_agent_response(self, response: str):
        """Maneja la respuesta final del agente."""
        self.add_system_message("AGENTE HA FINALIZADO LA TAREA.", show_rating_buttons=False)
        self.process_log_window.append_log("AGENTE HA FINALIZADO LA TAREA.")
        self.handle_response(response)
    
    def handle_response(self, response_content):
        """Maneja la respuesta exitosa del worker."""
        self.loading_indicator.setVisible(False)
        response_obj = {"role": "assistant", "content": response_content}
        if self.chat_engine:
            self.chat_engine.history.append(response_obj)
        self.add_to_history(response_obj)
        self.save_conversation(is_autosave=True)
        self.send_button.setEnabled(True)
        self.input_text.setFocus()
    
    def handle_error(self, error_msg):
        """Maneja un error del worker."""
        self.loading_indicator.setVisible(False)
        self.add_to_history({"role": "assistant", "content": f"ERROR: {error_msg}"})
        self.send_button.setEnabled(True)
        self.input_text.setFocus()
        self.process_log_window.append_log(f"ERROR: {error_msg}")
        self.process_log_window.show()
    
    def start_new_conversation(self):
        """Inicia una nueva conversación"""
        if not self.chat_engine or not self.chat_engine.provider:
            show_warning_message(self, "Advertencia", 
                               "Debes seleccionar un modelo primero.")
            return
        
        def on_history_cleared():
            self.chat_engine.start_new()
            self.add_system_message("NUEVA CONVERSACIÓN INICIADA.")
            self.add_system_message("Sistema listo para recibir comandos.")
            self.process_log_window.clear_log()
            self.process_log_window.hide()
        self.clear_history(on_finished_callback=on_history_cleared)

    def save_conversation(self, is_autosave=False):
        """Guarda la conversación actual"""
        if not self.chat_engine or not is_autosave:
            return
        
        if not self.user_id:
            return
        
        try:
            if not self.chat_engine.conversation_id:
                conv_data = {
                    "user_id": self.user_id,
                    "model": self.chat_engine.provider.model_identifier,
                    "title": self.generate_conversation_title(),
                    "timestamp": datetime.now(),
                    "messages": self.chat_engine.history,
                    "system_prompt": self.chat_engine.system_prompt,
                    "metadata": {}
                }
                new_id = self.persistence_service.create_conversation(self.user_id, conv_data)
                if new_id:
                    self.chat_engine.conversation_id = new_id
                    self.populate_recent_conversations()
            else:
                conv_data_to_update = {
                    "messages": self.chat_engine.history,
                    "system_prompt": self.chat_engine.system_prompt,
                    "metadata": {},
                    "timestamp": datetime.now(),
                    "title": self.generate_conversation_title(),
                    "model": self.chat_engine.provider.model_identifier
                }
                self.persistence_service.update_conversation(
                    self.user_id, self.chat_engine.conversation_id, conv_data_to_update)
                self.populate_recent_conversations()
        except Exception as e:
            print(f"[ChatInterface] save_conversation: ❌ Error al guardar la conversación: {e}")

    def create_rating_buttons(self, layout, role, message, message_obj=None):
        """Crea y configura los botones de calificación con estado visual."""
        
        rating = message_obj.get("rating") if message_obj else None

        # --- Colores ---
        color_default = "white"
        color_up = "#2ecc71"  # Verde
        color_down = "#e74c3c" # Rojo

        # --- Iconos ---
        icon_up_normal = qta.icon("fa5s.thumbs-up", color=color_default)
        icon_up_hover = qta.icon("fa5s.thumbs-up", color=color_up)
        icon_down_normal = qta.icon("fa5s.thumbs-down", color=color_default)
        icon_down_hover = qta.icon("fa5s.thumbs-down", color=color_down)

        # --- Botones ---
        thumbs_up_button = QPushButton(icon_up_normal, "")
        thumbs_down_button = QPushButton(icon_down_normal, "")

        for btn in [thumbs_up_button, thumbs_down_button]:
            btn.setToolTip("Respuesta útil" if btn is thumbs_up_button else "Respuesta no útil")
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("background: transparent; border: none;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        def set_button_state():
            if rating == "up":
                thumbs_up_button.setIcon(icon_up_hover)  # Verde fijo
                thumbs_up_button.setEnabled(False)
                thumbs_down_button.setEnabled(True)  # Permitir recambiar
            elif rating == "down":
                thumbs_down_button.setIcon(icon_down_hover)  # Rojo fijo
                thumbs_up_button.setEnabled(True)  # Permitir recambiar
                thumbs_down_button.setEnabled(False)

        def hover_in_up(e):
            if thumbs_up_button.isEnabled():
                thumbs_up_button.setIcon(icon_up_hover)
        def hover_out_up(e):
            if thumbs_up_button.isEnabled():
                thumbs_up_button.setIcon(icon_up_normal)

        def hover_in_down(e):
            if thumbs_down_button.isEnabled() or rating == "down":
                thumbs_down_button.setIcon(icon_down_hover)
        def hover_out_down(e):
            if thumbs_down_button.isEnabled():
                thumbs_down_button.setIcon(icon_down_normal)

        thumbs_up_button.enterEvent = hover_in_up
        thumbs_up_button.leaveEvent = hover_out_up
        thumbs_down_button.enterEvent = hover_in_down
        thumbs_down_button.leaveEvent = hover_out_down

        print(f"[DEBUG] Estado inicial de calificación: {rating}")

        print("[DEBUG] Botón de valoración clickeado.")
        def on_rate(new_rating):
            nonlocal rating
            rating = new_rating
            print(f"[DEBUG] Usuario ha calificado con: {new_rating}")
            self.rate_message(role, message, new_rating)
            set_button_state()

        # --- Lógica de estado y eventos ---
        
        def set_button_state():
            # Desactivar botones y fijar color si ya hay una calificación
            if rating == "up":
                thumbs_up_button.setIcon(icon_up_hover) # Color verde fijo
                thumbs_up_button.setEnabled(False)
                thumbs_down_button.setEnabled(False)
            elif rating == "down":
                thumbs_down_button.setIcon(icon_down_hover) # Color rojo fijo
                thumbs_up_button.setEnabled(False)
                thumbs_down_button.setEnabled(False)

        # --- Eventos de Hover ---
        def hover_in_up(e):
            if thumbs_up_button.isEnabled():
                thumbs_up_button.setIcon(icon_up_hover)
        def hover_out_up(e):
            if thumbs_up_button.isEnabled():
                thumbs_up_button.setIcon(icon_up_normal)

        def hover_in_down(e):
            if thumbs_down_button.isEnabled():
                thumbs_down_button.setIcon(icon_down_hover)
        def hover_out_down(e):
            if thumbs_down_button.isEnabled():
                thumbs_down_button.setIcon(icon_down_normal)

        thumbs_up_button.enterEvent = hover_in_up
        thumbs_up_button.leaveEvent = hover_out_up
        thumbs_down_button.enterEvent = hover_in_down
        thumbs_down_button.leaveEvent = hover_out_down

        # --- Eventos de Click ---
        def on_rate(new_rating):
            nonlocal rating
            rating = new_rating
            self.rate_message(role, message, new_rating)
            set_button_state() # Actualizar estado visual permanentemente

        thumbs_up_button.clicked.connect(lambda: print("[DEBUG] Thumbs up clickeado.") or on_rate("up"))
        thumbs_down_button.clicked.connect(lambda: print("[DEBUG] Thumbs down clickeado.") or on_rate("down"))

        # --- Estado Inicial ---
        set_button_state()

        layout.addWidget(thumbs_up_button)
        layout.addWidget(thumbs_down_button)
        set_button_state()

    def rate_message(self, role, content, rating):
        """Maneja la calificación de un mensaje."""
        if not self.chat_engine or not self.chat_engine.conversation_id:
            show_warning_message(self, "Advertencia", "No hay conversación activa.")
            return

        for msg in self.chat_engine.history:
            if msg["role"] == role and msg["content"] == content:
                msg["rating"] = rating
                break

        try:
            self.save_conversation(is_autosave=True)
        except Exception as e:
            show_critical_message(self, "Error", f"No se pudo guardar la calificación: {e}")
    
    def export_conversation(self):
        """Exporta la conversación actual a un archivo .txt o .json."""
        if not self.chat_engine or not self.chat_engine.history:
            show_warning_message(self, "Sin conversación", "No hay una conversación activa para exportar.")
            return

        default_filename = self.generate_conversation_title().replace(" ", "_").lower()

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Exportar Conversación",
            f"{default_filename}",
            "JSON files (*.json);;Text files (*.txt)"
        )

        if not file_path:
            return

        try:
            if selected_filter.startswith("JSON"):
                export_data = {
                    "conversation_id": str(self.chat_engine.conversation_id),
                    "model": self.chat_engine.provider.model_identifier,
                    "title": self.generate_conversation_title(),
                    "exported_at": datetime.now().isoformat(),
                    "system_prompt": self.chat_engine.system_prompt,
                    "history": self.chat_engine.history
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=4, ensure_ascii=False)
            else: # Exportar a TXT
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Conversación Exportada\n======================\n")
                    f.write(f"Modelo: {self.chat_engine.provider.model_identifier}\n")
                    f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"--- SYSTEM PROMPT ---\n{self.chat_engine.system_prompt}\n\n--- HISTORIAL ---")
                    for message in self.chat_engine.history:
                        f.write(f"[{message.get('role', 'unknown').upper()}]\n{message.get('content', '')}\n\n---\n")
            
            self.add_system_message(f"Conversación exportada a: {Path(file_path).name}")
            show_information_message(self, "Exportación Exitosa", f"La conversación ha sido exportada a\n{file_path}")
        except Exception as e:
            show_critical_message(self, "Error de Exportación", f"No se pudo exportar la conversación:\n{e}")
    
    def generate_conversation_title(self):
        """Genera un título para la conversación"""
        if self.chat_engine and self.chat_engine.history:
            first_message = next((msg["content"] for msg in self.chat_engine.history 
                                 if msg["role"] == "user"), "Sin descripción")
            return first_message[:50]
        return "Conversación sin título"
    
    def load_conversation(self):
        """Carga una conversación"""
        try:
            conversations = self.persistence_service.get_user_conversations(self.user_id)
            if not conversations:
                show_information_message(self, "Sin conversaciones", "No tienes conversaciones guardadas.")
                return
            dialog = ConversationLoadDialog(conversations, self)
            if dialog.exec():
                conv_id = dialog.get_selected_conversation_id()
                if conv_id:
                    self.load_selected_conversation(conv_id)
        except Exception as e:
            show_critical_message(self, "Error", f"No se pudieron cargar las conversaciones: {e}")
    
    def load_selected_conversation(self, conv_id):
        """Carga los datos de una conversación específica en la UI."""
        self.add_system_message(f"Cargando conversación ID: {conv_id}...")        
        conv_data = self.persistence_service.get_conversation(self.user_id, conv_id)
        if not conv_data:
            show_critical_message(self, "Error", "No se pudo cargar la conversación.")
            return

        model_identifier = conv_data.get("model", "default_model")
        
        try:
            if model_identifier.lower().endswith(".gguf"):
                provider = CtransformersProvider(model_path=model_identifier)
            else:
                # This case should no longer happen as we only load GGUF files
                show_critical_message(self, "Error de Modelo", f"El modelo guardado en esta conversación no es un archivo GGUF: {model_identifier}")
                return

            if hasattr(self, "parameters_panel"):
                current_params = self.parameters_panel.content.get_current_parameters()
                provider.set_generation_parameters(**current_params)

            self.chat_engine.provider = provider
            self.selected_model_name = model_identifier
            self.update_installed_models_combo_selection()
            history = conv_data.get("messages", [])
            system_prompt = conv_data.get("system_prompt", SYSTEM_PROMPT)
            self.chat_engine.load_conversation(
                conversation_id=conv_id,
                history=history,
                system_prompt=system_prompt
            )
            self.system_prompt_edit.setPlainText(system_prompt)

            def on_history_cleared():
                self.add_system_message(f"Conversación cargada: {conv_data.get('title', 'Sin título')}")
                self.repopulate_history_ui()
                self.populate_recent_conversations()
            self.clear_history(on_finished_callback=on_history_cleared)           
        except Exception as e:
            show_critical_message(self, "Error al Cargar Modelo", f"No se pudo cargar el modelo '{model_identifier}' asociado a esta conversación:\n{e}")
    
    def on_recent_conversation_selected(self, item):
        """Maneja la selección de una conversación reciente de la lista."""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        if conv_id:
            self.load_selected_conversation(conv_id)
    
    def attach_file(self):
        """Adjunta un archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", 
            "Todos los archivos (*);;Archivos de texto (*.txt);;Documentos (*.pdf *.doc *.docx)"
        )        
        if file_path:
            try:
                text = extract_text(file_path)
                self.add_system_message(f"ARCHIVO CARGADO: {file_path}")
                current_prompt = self.input_text.toPlainText()
                new_prompt = f"Basado en el siguiente contenido del archivo '{Path(file_path).name}' :\n\n---\n{text}\n---\n\n{current_prompt}"
                self.input_text.setPlainText(new_prompt)
            except Exception as e:
                show_critical_message(self, "Error", 
                                    f"No se pudo procesar el archivo: {e}")
    
    def repopulate_history_ui(self):
        """Vuelve a dibujar el historial en la UI a partir de self.chat_engine.history."""
        content_edits = []
        for msg in self.chat_engine.history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Creamos el widget sin animaciones ni scroll individual
            message_widget, content_edit = self._create_message_widget(role, content, msg, show_rating_buttons=True)
            
            # Lo añadimos directamente al layout
            self.history_layout.insertWidget(self.history_layout.count() - 1, message_widget)
            content_edits.append(content_edit)

        # Después de añadir todos los widgets, ajustamos sus alturas.
        # Usamos un timer para asegurar que todos los widgets se hayan añadido al layout
        # antes de intentar medir su contenido.
        def adjust_all_heights():
            for editor in content_edits:
                self._adjust_message_height(editor)
            # Finalmente, hacemos scroll al fondo.
            self.scroll_to_bottom_animated()

        QTimer.singleShot(100, adjust_all_heights)

    def scroll_to_bottom_animated(self):
        """Anima el scroll vertical hasta su valor máximo."""
        scrollbar = self.history_scroll_area.verticalScrollBar()
        # Usamos una animación para el scroll, para que sea suave
        self.scroll_animation = QPropertyAnimation(scrollbar, b"value")
        self.scroll_animation.setDuration(400) # Duración en milisegundos
        self.scroll_animation.setStartValue(scrollbar.value())
        self.scroll_animation.setEndValue(scrollbar.maximum())
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.scroll_animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    
    def start_cleanup_process(self, on_finish_callback):
        """Muestra el diálogo de cierre e inicia el worker de limpieza."""
        if self.cleanup_in_progress:
            return
        
        self.centralWidget().setGraphicsEffect(self.blur_effect)
        self.overlay.show()
        self.overlay.raise_()

        self.cleanup_in_progress = True
        self.closing_dialog = ClosingDialog()
        self.cleanup_worker = CleanupWorker(None)
        self.cleanup_thread = QThread()
        self.cleanup_worker.moveToThread(self.cleanup_thread)

        self.cleanup_worker.finished.connect(self.cleanup_thread.quit)
        
        self.cleanup_thread.finished.connect(self.cleanup_worker.deleteLater)
        self.cleanup_thread.finished.connect(self.cleanup_thread.deleteLater)
        self.cleanup_thread.finished.connect(on_finish_callback)

        self.cleanup_thread.started.connect(self.cleanup_worker.run)

        self.cleanup_thread.start()
        self.closing_dialog.show()
    
    def do_logout(self):
        """Acción final para cerrar sesión. Se ejecuta cuando el hilo de limpieza ha terminado."""
        self.centralWidget().setGraphicsEffect(None)
        self.overlay.hide()
        self.cleanup_in_progress = False
        self.closing_dialog.close()
        self.logout_requested.emit()
        self.is_ready_to_close = True
        self.close()

    def do_quit(self):
        """Acción final para salir de la aplicación. Se ejecuta cuando el hilo de limpieza ha terminado."""
        self.centralWidget().setGraphicsEffect(None)
        self.overlay.hide()
        self.cleanup_in_progress = False
        self.closing_dialog.close()
        self.is_ready_to_close = True
        self.close()

    def logout(self):
        """Initiates the cleanup process for logging out."""
        if self.cleanup_in_progress:
            return
        self.start_cleanup_process(self.do_logout)
    
    def show_hardware_config(self):
        if hasattr(self, 'hardware_dialog') and self.hardware_dialog.isVisible():
            self.hardware_dialog.activateWindow()
            return
        """Muestra el configurador de hardware para que el usuario pueda cambiar CPU/GPU."""
        try:
            from hardware_config_gui_v4 import HardwareConfigDialog
            
            self.add_system_message("ABRIENDO CONFIGURADOR DE HARDWARE...")
            
            self.hardware_dialog = HardwareConfigDialog(self)
            
            def handle_accepted():
                self.update_hardware_status_display()
                self.add_system_message(
                    "CONFIGURACIÓN DE HARDWARE ACTUALIZADA. "
                    "Los cambios se aplicarán cuando cargue el próximo modelo."
                )

            def handle_rejected():
                self.add_system_message("Configuración de hardware cancelada.")

            self.hardware_dialog.accepted.connect(handle_accepted)
            self.hardware_dialog.rejected.connect(handle_rejected)
            
            self.hardware_dialog.show()
            
        except ImportError as e:
            show_critical_message(self, "Error", 
                               f"No se pudo cargar el configurador de hardware.\n\n" 
                               f"Error: {e}\n\n" 
                               f"Ejecute 'python hardware_config_gui_v4.py' desde terminal.")
        except Exception as e:
            show_critical_message(self, "Error", 
                               f"Error inesperado al abrir configurador de hardware: {e}")
    
    def update_hardware_status_display(self):
        """Actualiza la información mostrada sobre la configuración de hardware actual."""
        try:
            import os
            import json
            
            if os.path.exists('hardware_config.json'):
                with open('hardware_config.json', 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                selected_config = config_data.get('selected_config', {})
                hardware_info = config_data.get('hardware_info', {})
                
                # Crear texto de estado
                config_type = selected_config.get('description', 'Configuración desconocida')
                gpu_layers = selected_config.get('n_gpu_layers', 0)
                cpu_threads = selected_config.get('n_threads', 'auto')
                
                status_text = f"Actual: {config_type}\n"
                status_text += f"GPU Layers: {gpu_layers}\n"
                status_text += f"CPU Threads: {cpu_threads}\n\n"
                
                # Agregar información del hardware detectado
                cpu_cores = hardware_info.get('cpu_cores', 'N/A')
                has_nvidia = hardware_info.get('has_nvidia_gpu', False)
                has_cuda = hardware_info.get('has_cuda', False)
                
                status_text += f"Hardware: {cpu_cores} núcleos CPU"
                if has_nvidia:
                    status_text += f", GPU NVIDIA"
                    if has_cuda:
                        status_text += f" (CUDA)"
                
                self.hardware_status_label.setText(status_text)
                
            else:
                self.hardware_status_label.setText(
                    "No hay configuración de hardware.\n"
                    "Haga clic en 'Configurar Hardware' para optimizar el rendimiento."
                )
                
        except Exception as e:
            self.hardware_status_label.setText(f"Error cargando configuración: {e}")
    
    def redetect_hardware(self):
        """Lanza una nueva detección de hardware."""
        try:
            from hardware_detector import HardwareDetector
            import os
            
            # Eliminar configuración actual para forzar nueva detección
            if os.path.exists('hardware_config.json'):
                reply = show_question_message(self, "Redetectar Hardware",
                                           "Esto eliminará la configuración actual y detectará de nuevo el hardware.\n\n"
                                           "¿Está seguro?",
                                           buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                os.remove('hardware_config.json')
            
            # Lanzar configurador
            self.show_hardware_config()
            
            # Actualizar display después de un momento
            QTimer.singleShot(2000, self.update_hardware_status_display)
            
            self.add_system_message(
                "HARDWARE REDETECTADO. "
                "La nueva configuración se aplicará cuando cargue el próximo modelo."
            )
            
        except Exception as e:
            show_critical_message(self, "Error", f"Error redetectando hardware: {e}")

    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        if self.is_ready_to_close:
            super().closeEvent(event)
            return

        if self.cleanup_in_progress:
            event.ignore()
            return
        
        event.ignore()
        self.start_cleanup_process(self.do_quit)

    def on_mode_changed(self, index):
        """Maneja el cambio de modo de operación (Chat, Agente, Razonador)."""
        
        mode = self.mode_combo.itemData(index)

        from app.agent import Agent
        from app.reasoner import Reasoner
        from app.chat_engine import SYSTEM_PROMPT as CHAT_SYSTEM_PROMPT
        
        if not self.chat_engine or not self.chat_engine.provider:
            self.add_system_message("ERROR: No hay un modelo cargado. No se puede cambiar de modo.")
            self.mode_combo.setCurrentIndex(0)
            return

        if mode == "chat":
            self.agent_mode = False
            self.reasoner_mode = False
            self.chat_engine.system_prompt = CHAT_SYSTEM_PROMPT
            self.system_prompt_edit.setPlainText(CHAT_SYSTEM_PROMPT)
            self.add_system_message("MODO CHAT ACTIVADO.")
            self.input_text.setPlaceholderText("Escribe tu prompt aquí...")

        elif mode == "agent":
            self.agent_mode = True
            self.reasoner_mode = False
            try:
                agent_for_prompt = Agent(self.chat_engine.provider)
                agent_prompt = agent_for_prompt.system_prompt
                self.chat_engine.system_prompt = agent_prompt
                self.system_prompt_edit.setPlainText(agent_prompt)
                self.add_system_message("MODO AGENTE ACTIVADO.")
                self.input_text.setPlaceholderText("Describe el objetivo para el agente...")
            except Exception as e:
                self.add_system_message(f"Error al activar modo Agente: {e}")
                self.mode_combo.setCurrentIndex(0)

        elif mode == "reasoner":
            self.agent_mode = False
            self.reasoner_mode = True
            try:
                reasoner_for_prompt = Reasoner(self.chat_engine.provider)
                reasoner_prompt = reasoner_for_prompt.system_prompt
                self.chat_engine.system_prompt = reasoner_prompt
                self.system_prompt_edit.setPlainText(reasoner_prompt)
                self.add_system_message("MODO RAZONADOR ACTIVADO.")
                self.input_text.setPlaceholderText("Describe el objetivo complejo para planificar...")
            except Exception as e:
                self.add_system_message(f"Error al activar modo Razonador: {e}")
                self.mode_combo.setCurrentIndex(0)

    def populate_installed_models_combo(self):
        """Carga los modelos locales (GGUF y Ollama) en el QComboBox."""
        self.installed_models_combo.blockSignals(True)
        self.installed_models_combo.clear()

        all_local_models = []
        try:
            models_dir = Path("models")
            if models_dir.exists():
                for f in models_dir.iterdir():
                    if f.is_file() and f.suffix.lower() == ".gguf":
                        all_local_models.append({'identifier': str(f.resolve()), 'display': f.name})
        except Exception as e:
            print(f"Error al leer modelos GGUF locales: {e}")

        

        if not all_local_models:
            self.installed_models_combo.addItem(self.installed_models_combo.no_models_text)
            self.installed_models_combo.setEnabled(True)
        else:
            self.installed_models_combo.setEnabled(True)
            self.installed_models_combo.addItem("[Seleccionar un modelo]", userData=None)
            
            sorted_models = sorted(all_local_models, key=lambda x: x['display'])
            for model in sorted_models:
                self.installed_models_combo.addItem(model['display'], userData=model['identifier'])
        
        self.update_installed_models_combo_selection()
        self.installed_models_combo.blockSignals(False)

    def on_installed_model_selected(self, index):
        """Maneja la selección de un modelo desde el QComboBox."""
        if index <= 0:
            return
        model_identifier = self.installed_models_combo.itemData(index)
        if model_identifier and self.selected_model_name != model_identifier:
            self.on_model_selected(model_identifier)

    def update_installed_models_combo_selection(self):
        """Actualiza la selección del QComboBox para que coincida con el modelo activo."""
        if self.selected_model_name:
            for i in range(self.installed_models_combo.count()):
                if self.installed_models_combo.itemData(i) == self.selected_model_name:
                    self.installed_models_combo.setCurrentIndex(i)
                    return
        self.installed_models_combo.setCurrentIndex(0)
