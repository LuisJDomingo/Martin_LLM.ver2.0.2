# -*- coding: utf-8 -*-
# ui/chat_interface.py

import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QSpacerItem,
                             QButtonGroup,
                             QTextEdit, QLineEdit, QPushButton, QLabel, QCheckBox,
                             QMessageBox, QFrame, QSplitter, QListWidget,
                             QListWidgetItem, QFileDialog, QApplication, QSizePolicy, QToolButton, QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QPoint
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QIcon, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.style as mpl_style
import psutil

from app.llm_providers import BaseLLMProvider, LlamaCppProvider, OllamaProvider
from app.services.file_processing_service import extract_text
from app.services.login_service import UserService
from app.ollama_manager import OllamaManager # Asegúrate que esta clase existe y funciona
from app.chat_engine import ChatEngine, SYSTEM_PROMPT
import qtawesome as qta
# Importar los workers desde su nuevo módulo
from app.workers import Worker, AgentWorker, ReasonerWorker, CleanupWorker
from ui.model_manager_widget import ModelManagerWidget
from ui.llm_parameters_widget import LLMParametersWidget
from ui.closing_dialog import ClosingDialog
from ui.conversation_load_dialog import ConversationLoadDialog
from bson.objectid import ObjectId
import json
# from app.agent import AGENT_SYSTEM_PROMPT_TEMPLATE
from ui.process_log_window import ProcessLogWindow # Importar la nueva ventana de log


class SystemStatsWidget(QFrame):
    """Widget para mostrar estadísticas del sistema con diseño futurista horizontal"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        """Configura la interfaz de estadísticas con layout horizontal en la parte inferior"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        mpl_style.use("dark_background")

        self.figure = Figure(figsize=(10, 2.5), facecolor="#242831")
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
            return f"#{r:02x}{g:02x}{b:02x}"

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

class ChatInterface(QMainWindow):
    """Interfaz principal de chat en PyQt6"""

    logout_requested = pyqtSignal()
    def __init__(self, user_id, username, chat_engine: ChatEngine, user_service: UserService, parent=None):
        super().__init__(parent)
        print(f"[DEBUG] Creando ChatInterface para user_id={user_id}, username={username}")
        # Atributos
        self.user_id = user_id
        self.username = username
        self.selected_model_name = ""
        self.agent_mode = False
        self.reasoner_mode = False
        self.model_manager = None
        self.stats_timer = None
        self.worker_thread = None

        # Usamos las instancias pasadas por el controlador
        self.chat_engine = chat_engine
        self.user_service = user_service
        self.cleanup_in_progress = False
        self.is_ready_to_close = False
        # Configurar ventana
        self.setWindowTitle(f"Martin LLM - {username}")
        self.setMinimumSize(1200, 800)
        self.ollama_manager = OllamaManager()

        # Inicializar la ventana de log de procesos
        self.process_log_window = ProcessLogWindow(parent=self)
        self.process_log_window.hide() # Ocultar por defecto

        # --- INICIALIZACIÓN DIRECTA Y ROBUSTA ---
        # Se elimina la inicialización en segundo plano. Todo se hace ahora de forma síncrona.
        self.resize(1400, 900)
        self.setup_ui()
        self.populate_recent_conversations()
        self.setup_stats_timer()
        self.add_system_message("SISTEMA INICIALIZADO Y LISTO.", show_rating_buttons=False)

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        print("[DEBUG] ChatInterface.setup_ui llamado")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(10)

        self.create_top_bar(frame_layout)
        self.create_central_area(frame_layout)
        main_layout.addWidget(main_frame)

    def show_model_manager_event(self, event):
        """Maneja el evento de clic en la etiqueta del modelo."""
        self.show_model_manager()
    def create_top_bar(self, parent_layout):
        """Crea la barra superior solo para la selección del modelo."""
        top_bar_frame = QFrame()
        top_bar_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        top_bar_frame.setObjectName("topBarFrame")
        top_bar_frame.setStyleSheet("QFrame#topBarFrame { border-bottom: 1px solid #3d4650; border-radius: 0; background-color: #1a1d23; }")
        top_bar_layout = QHBoxLayout(top_bar_frame)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)
        top_bar_layout.setSpacing(10)

        initial_model_name = "[NINGUNO SELECCIONADO]"
        if self.chat_engine and self.chat_engine.provider:
            model_path = Path(self.chat_engine.provider.model_identifier)
            initial_model_name = model_path.name.upper()
            self.selected_model_name = self.chat_engine.provider.model_identifier

        models_label = QLabel("Modelo:")
        models_label.setStyleSheet("font-weight: bold; color: #a0aec0;")
        top_bar_layout.addWidget(models_label)

        self.model_label = QLabel(f"[{initial_model_name}]")
        self.model_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.model_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.model_label.setToolTip("Haz clic para gestionar los modelos")
        self.model_label.mousePressEvent = self.show_model_manager_event
        top_bar_layout.addWidget(self.model_label)

        top_bar_layout.addStretch(1)

        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(5)
        user_info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        profile_icon = QLabel()
        profile_icon.setPixmap(qta.icon("fa5s.user-circle", color="#90cdf4").pixmap(22, 22))
        user_info_layout.addWidget(profile_icon)

        username_label = QLabel(self.username.upper())
        username_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #90cdf4;")
        user_info_layout.addWidget(username_label)

        top_bar_layout.addLayout(user_info_layout)

        top_bar_layout.addStretch(1)

        actions_label = QLabel("Acciones:")
        actions_label.setStyleSheet("font-weight: bold; color: #a0aec0;")
        top_bar_layout.addWidget(actions_label)

        controls = [
            {"icon": qta.icon("fa5.file"), "tooltip": "Nueva conversación", "action": self.start_new_conversation},
            {"icon": qta.icon("fa5.folder-open"), "tooltip": "Cargar conversación", "action": self.load_conversation},
            {"icon": qta.icon("fa5s.file-export"), "tooltip": "Exportar conversación", "action": self.export_conversation},
            {"icon": qta.icon("fa5s.sign-out-alt"), "tooltip": "Cerrar sesión", "action": self.logout},
        ]
        for ctrl in controls:
            btn = QPushButton()
            btn.setIcon(ctrl["icon"])
            btn.setToolTip(ctrl["tooltip"])
            btn.setFixedSize(35, 35)
            btn.clicked.connect(ctrl["action"])
            top_bar_layout.addWidget(btn)

        parent_layout.addWidget(top_bar_frame)
    def create_central_area(self, parent_layout):
        """Crea el área central con chat, entrada y estadísticas"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.left_panel = self.create_left_panel_widget()
        self.left_panel.setObjectName("leftSidePanel")

        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(10)

        # Create a scroll area for chat history
        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setObjectName("historyScrollArea")

        # Widget to hold the messages
        self.history_content_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_content_widget)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(5)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align messages to the top

        self.history_scroll_area.setWidget(self.history_content_widget)

        chat_layout.addWidget(self.create_mode_selection_widget())
        chat_layout.addWidget(self.history_scroll_area, stretch=1)

        # Indicador de carga
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)  # Modo indeterminado
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setTextVisible(False)
        self.loading_indicator.setFixedHeight(5) # Más delgado y discreto
        chat_layout.addWidget(self.loading_indicator)

        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_text = QTextEdit()
        self.input_text.setObjectName("inputText")
        self.input_text.setMaximumHeight(82)
        self.input_text.setPlaceholderText("Escribe tu prompt aquí...")
        self.input_text.keyPressEvent = self.input_key_press
        input_layout.addWidget(self.input_text)

        action_buttons_layout = QVBoxLayout()
        action_buttons_layout.setSpacing(5)
        self.send_button = QPushButton()
        self.send_button.setIcon(qta.icon("fa5s.paper-plane"))
        self.send_button.setToolTip("Enviar mensaje (Enter)")
        self.send_button.setFixedSize(80, 80)
        self.send_button.clicked.connect(self.send_message)
        self.attach_button = QPushButton()
        self.attach_button.setIcon(qta.icon("fa5s.paperclip"))
        self.attach_button.setToolTip("Adjuntar archivo")
        self.attach_button.setFixedSize(80, 40)
        self.attach_button.clicked.connect(self.attach_file)

        action_buttons_layout.addWidget(self.send_button)
        action_buttons_layout.addWidget(self.attach_button)
        input_layout.addLayout(action_buttons_layout)
        chat_layout.addWidget(input_frame)

        right_panel = QWidget()
        right_panel.setObjectName("rightSidePanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        system_prompt_widget = self.create_system_prompt_widget()
        self.parameters_panel = self.create_parameters_panel()
        self.system_stats_panel = self.create_system_stats_panel()

        right_layout.addWidget(self.parameters_panel)
        right_layout.addWidget(system_prompt_widget)
        right_layout.addWidget(self.system_stats_panel)

        right_layout.addStretch(1)

        main_splitter.addWidget(self.left_panel)
        main_splitter.addWidget(chat_frame)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([250, 800, 400])
        parent_layout.addWidget(main_splitter)
    def create_mode_selection_widget(self):
        """Crea y devuelve el widget para seleccionar el modo de operación."""
        mode_frame = QFrame()
        mode_frame.setObjectName("topBarFrame")
        mode_frame.setStyleSheet("QFrame#topBarFrame { border-top: 1px solid #3d4650; border-bottom: 1px solid #3d4650; border-radius: 0; background-color: #1a1d23; }")

        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(10, 5, 10, 5)
        mode_layout.setSpacing(15)

        self.toggle_panel_button = QPushButton(qta.icon('fa5s.align-justify', color="white"), "")
        self.toggle_panel_button.setToolTip("Mostrar/Ocultar panel de conversaciones")
        self.toggle_panel_button.setFixedSize(35, 35)
        self.toggle_panel_button.clicked.connect(self.toggle_left_panel)
        mode_layout.addWidget(self.toggle_panel_button)

        mode_title = QLabel("MODO:")
        mode_title.setStyleSheet("font-weight: bold; color: #a0aec0;")
        mode_layout.addWidget(mode_title)

        self.mode_button_group = QButtonGroup(self)

        self.chat_mode_radio = QRadioButton("Chat")
        self.chat_mode_radio.setToolTip("Conversación normal con el modelo.")
        self.chat_mode_radio.setChecked(True)

        self.agent_mode_radio = QRadioButton("Agente")
        self.agent_mode_radio.setToolTip("Activa el modo agente para realizar tareas con herramientas.")

        self.reasoner_mode_radio = QRadioButton("Razonador")
        self.reasoner_mode_radio.setToolTip("Activa el modo razonador para planificar y ejecutar tareas muy complejas.")

        mode_layout.addWidget(self.chat_mode_radio)
        mode_layout.addWidget(self.agent_mode_radio)
        mode_layout.addWidget(self.reasoner_mode_radio)
        mode_layout.addStretch()

        self.mode_button_group.addButton(self.chat_mode_radio)
        self.mode_button_group.addButton(self.agent_mode_radio)
        self.mode_button_group.addButton(self.reasoner_mode_radio)
        self.mode_button_group.buttonToggled.connect(self.on_mode_changed)

        return mode_frame
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
        self.update_prompt_btn.clicked.connect(self.update_system_prompt)
        content_layout.addWidget(self.update_prompt_btn)

        collapsible_panel = CollapsiblePanel("SYSTEM PROMPT", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)
        return collapsible_panel
    def create_system_stats_panel(self):
        content_widget = SystemStatsWidget()
        collapsible_panel = CollapsiblePanel("MONITOR DEL SISTEMA", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)      # desplegado al iniciar
        return collapsible_panel
    def create_parameters_panel(self):
        """Crea el panel plegable para los parámetros del LLM."""
        content_widget = LLMParametersWidget()
        content_widget.parameters_changed.connect(self.on_parameters_changed)

        collapsible_panel = CollapsiblePanel("PARÁMETROS DEL MODELO", content_widget=content_widget)
        collapsible_panel.content.setVisible(True)
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
        try:
            self.recent_convs_list.clear()
            conversations = self.user_service.get_user_conversations(self.user_id)
            if not conversations:
                placeholder_item = QListWidgetItem("No hay conversaciones recientes.")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.recent_convs_list.addItem(placeholder_item)
                self.recent_convs_list.setMinimumWidth(200)  # ancho mínimo por defecto
                return

            sorted_convs = sorted(conversations, key=lambda x: x.get('timestamp', datetime.min), reverse=True)

            max_row_width = 0  # vamos a calcular el ancho máximo necesario

            for conv in sorted_convs:
                conv_id = str(conv.get("_id"))
                title = conv.get("title", "Sin título")
                timestamp = conv.get("timestamp", datetime.now())
                date_str = timestamp.strftime('%Y-%m-%d') if isinstance(timestamp, datetime) else "Fecha desc."

                row_widget = QWidget()
                row_widget.setObjectName("recentConvRow")
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(5, 2, 5, 2)
                row_layout.setSpacing(5)

                title_label = QLabel(f"[{date_str}] {title}")
                title_label.setToolTip(f"Doble clic para cargar: {title}")
                title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                title_label.setMinimumWidth(80)  # siempre muestra algo del título

                rename_button = QPushButton(qta.icon('fa5s.edit', color="white"), "")
                rename_button.setFixedSize(20, 20)
                rename_button.setToolTip("Renombrar conversación")
                rename_button.setStyleSheet("""
                    QPushButton { border-radius: 10px; background: transparent; padding: 0; }
                    QPushButton:hover { background-color: #4a90e2; }
                """)
                rename_button.clicked.connect(lambda checked=False, c_id=conv_id, c_title=title: self.rename_recent_conversation(c_id, c_title))

                delete_button = QPushButton(qta.icon('fa5s.trash-alt', color="white"), "")
                delete_button.setFixedSize(20, 20)
                delete_button.setToolTip("Eliminar esta conversación")
                delete_button.setStyleSheet("""
                    QPushButton { border-radius: 10px; background: transparent; padding: 0; }
                    QPushButton:hover { background-color: #4a90e2; }
                """)
                delete_button.clicked.connect(lambda checked=False, c_id=conv_id: self.delete_recent_conversation(c_id))

                row_layout.addWidget(title_label)
                row_layout.addWidget(rename_button)
                row_layout.addWidget(delete_button)

                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, conv_id)
                size_hint = row_widget.sizeHint()
                size_hint.setHeight(max(size_hint.height(), 40))
                item.setSizeHint(size_hint)

                self.recent_convs_list.addItem(item)
                self.recent_convs_list.setItemWidget(item, row_widget)

                # calcular ancho necesario para esta fila
                row_width = row_widget.sizeHint().width()
                max_row_width = max(max_row_width, row_width)

            # aplicar el ancho mínimo calculado al panel
            self.recent_convs_list.setMinimumWidth(max_row_width + 20)  # un pequeño margen

        except Exception as e:
            print(f"Error al poblar conversaciones recientes: {e}")
            self.recent_convs_list.clear()
            self.recent_convs_list.addItem("Error al cargar.")
            self.recent_convs_list.setMinimumWidth(200)
    def rename_recent_conversation(self, conversation_id: str, current_title: str):
        """Permite al usuario renombrar una conversación."""
        new_title, ok = QInputDialog.getText(self, "Renombrar Conversación", 
                                             "Nuevo título:", QLineEdit.EchoMode.Normal, 
                                             current_title)
        if ok and new_title and new_title.strip() != current_title:
            success = self.user_service.update_conversation_title(self.user_id, conversation_id, new_title.strip())
            if success:
                self.populate_recent_conversations()
                # Si la conversación renombrada es la actual, actualizamos el título en el motor
                if self.chat_engine and self.chat_engine.conversation_id == conversation_id:
                    self.chat_engine.title = new_title.strip()
            else:
                QMessageBox.critical(self, "Error", "No se pudo renombrar la conversación.")

    def delete_recent_conversation(self, conversation_id: str):
        """Maneja la eliminación o archivado de una conversación de la lista."""
        reply = QMessageBox.question(self, "Confirmar Acción",
                                     "¿Estás seguro de que quieres quitar esta conversación de la lista?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success = self.user_service.delete_or_archive_conversation(self.user_id, conversation_id)
            if success:
                self.populate_recent_conversations()
            else:
                QMessageBox.critical(self, "Error", "No se pudo realizar la operación.")
    def update_system_prompt(self):
        """Actualiza el System Prompt en el chat engine."""
        new_prompt = self.system_prompt_edit.toPlainText().strip()
        print(f"[DEBUG] nuevo system prompt: {new_prompt}")
        if self.chat_engine:
            self.chat_engine.system_prompt = new_prompt
            # Proporcionar feedback visual al usuario
            self.add_system_message("SYSTEM PROMPT ACTUALIZADO.")
            QMessageBox.information(self, "Actualizado", 
                                   "El System Prompt ha sido actualizado para la conversación actual.")
        else:
            QMessageBox.warning(self, "Sin conversación activa", 
                               "Debes seleccionar un modelo e iniciar una conversación para poder actualizar el System Prompt.")
    def input_key_press(self, event):
        """Maneja las pulsaciones de tecla en el campo de entrada"""
        from PyQt6.QtCore import Qt     
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return
        # Llamar al método original
        QTextEdit.keyPressEvent(self.input_text, event)
    def setup_stats_timer(self):
        """Configura el temporizador para actualizar estadísticas"""
        self.stats_timer = QTimer()
        # self.stats_timer.timeout.connect(self.stats_widget.update_stats)
        self.stats_timer.timeout.connect(self.system_stats_panel.content.update_stats)
        self.stats_timer.start(7000)  # Actualizar cada 7 segundos       
    def show_model_manager(self):
        """Muestra el gestor de modelos justo debajo de la etiqueta."""
        if self.model_manager and self.model_manager.isVisible():
            self.model_manager.activateWindow()
            return   
        self.model_manager = ModelManagerWidget(self)
        self.model_manager.model_selected.connect(self.on_model_selected)
        # Calcular la posición para que aparezca debajo de la etiqueta del modelo
        # Obtenemos la posición del borde inferior izquierdo de la etiqueta en coordenadas globales
        bottom_left = self.model_label.mapToGlobal(QPoint(0, self.model_label.height()))
        # Añadimos un pequeño margen para que no esté pegado
        self.model_manager.move(bottom_left.x(), bottom_left.y() + 5)
        self.model_manager.show()
    def on_model_selected(self, model_identifier):
        """Maneja la selección de un modelo para iniciar una nueva conversación."""
        print(f"[DEBUG] ChatInterface.on_model_selected llamado con modelo: {model_identifier}")
        
        self.add_system_message(f"CARGANDO MODELO: {Path(model_identifier).name}...")
        QApplication.processEvents() # Update UI to show loading message

        try:
            # --- LÓGICA DE SELECCIÓN DE PROVEEDOR ---
            if model_identifier.lower().endswith('.gguf'):
                # Es un modelo local GGUF, usamos LlamaCppProvider
                provider = LlamaCppProvider(model_path=model_identifier)
                display_name = Path(model_identifier).name
            else:
                # Es un modelo de Ollama, usamos OllamaProvider
                provider = OllamaProvider(model_name=model_identifier)
                display_name = model_identifier

            # Aplicar los parámetros actuales de la UI al nuevo proveedor
            if hasattr(self, 'parameters_panel'):
                current_params = self.parameters_panel.content.get_current_parameters()
                print(f"[DEBUG] Aplicando parámetros al nuevo modelo: {current_params}")
                provider.set_generation_parameters(**current_params)

            # Actualizar el proveedor en el ChatEngine existente
            self.chat_engine.provider = provider
            
            self.selected_model_name = model_identifier # Guardamos el identificador completo
            self.model_label.setText(f"> MODELO: [{display_name.upper()}] - ACTIVO")

            # Al seleccionar un nuevo modelo, siempre iniciamos una nueva conversación.
            self.chat_engine.start_new()
            self.system_prompt_edit.setPlainText(SYSTEM_PROMPT)
            
            # Limpiar historial y mostrar mensaje
            self.clear_history()
            self.add_system_message(f"MODELO {display_name} CARGADO EXITOSAMENTE")
            self.add_to_history({"role": "assistant", "content": "Sistema listo para recibir comandos."})

        except Exception as e:
            error_msg = f"No se pudo cargar el modelo '{Path(model_identifier).name}':\n{e}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "Error al Cargar Modelo", error_msg)
            self.model_label.setText(f"> MODELO: [ERROR AL CARGAR]")
            self.chat_engine.provider = None
    def _create_message_widget(self, role, content, message_obj=None, show_rating_buttons=True):
        """Crea un widget para un mensaje individual con su contenido y botones de calificación."""
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(5, 5, 5, 5)
        message_layout.setSpacing(2)

        # Role label
        if role == "user":
            display_role = "Usuario"
            style = "font-weight: bold; color: #366de4;"
            alignment = Qt.AlignmentFlag.AlignRight
        elif role == "assistant":
            display_role = "Martin LLM"
            style = "font-weight: bold; color: #9ae6b4;"
            alignment = Qt.AlignmentFlag.AlignLeft
        elif role == "system":
            display_role = "Sistema"
            style = "font-weight: bold; color: #fbb6ce;"
            alignment = Qt.AlignmentFlag.AlignCenter
        else:
            display_role = role.capitalize()
            style = "font-weight: bold; color: #e1e5e9;"
            alignment = Qt.AlignmentFlag.AlignLeft

        role_label = QLabel(display_role)
        role_label.setStyleSheet(style)
        role_label.setAlignment(alignment)
        message_layout.addWidget(role_label)

        # Message content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("background-color: #2d3748; padding: 10px; border-radius: 8px;")
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_label.setAlignment(alignment)
        message_layout.addWidget(content_label)

        # Rating buttons (only for assistant messages and if enabled)
        if role == "assistant" and show_rating_buttons:
            rating_layout = QHBoxLayout()
            rating_layout.setContentsMargins(0, 0, 0, 0)
            rating_layout.setSpacing(5)
            if alignment == Qt.AlignmentFlag.AlignRight:
                rating_layout.addStretch()
            self.create_rating_buttons(rating_layout, role, content)
            if alignment == Qt.AlignmentFlag.AlignLeft:
                rating_layout.addStretch()
            message_layout.addLayout(rating_layout)

        # Add stretch to push messages to top/bottom based on alignment
        outer_layout = QHBoxLayout()
        if alignment == Qt.AlignmentFlag.AlignRight:
            outer_layout.addStretch()
            outer_layout.addWidget(message_widget)
        else:
            outer_layout.addWidget(message_widget)
            outer_layout.addStretch()

        container_widget = QWidget()
        container_widget.setLayout(outer_layout)
        return container_widget

    def add_to_history(self, message_obj, show_rating_buttons=True):
        """Añade un mensaje al historial de la UI.

        Args:
            message_obj (dict): Diccionario con 'role' y 'content'.
            show_rating_buttons (bool): Si se deben mostrar los botones de rating para este mensaje.
        """
        role = message_obj.get("role", "unknown")
        content = message_obj.get("content", "")

        message_widget = self._create_message_widget(role, content, message_obj, show_rating_buttons)
        self.history_layout.addWidget(message_widget)
        QTimer.singleShot(10, lambda: self.history_scroll_area.verticalScrollBar().setValue(self.history_scroll_area.verticalScrollBar().maximum()))

    def add_system_message(self, message, show_rating_buttons=False):
        """Añade un mensaje del sistema al historial.

        Args:
            message (str): El contenido del mensaje del sistema.
            show_rating_buttons (bool): Si se deben mostrar los botones de rating para este mensaje.
        """
        system_message_obj = {"role": "system", "content": message}
        self.add_to_history(system_message_obj, show_rating_buttons=show_rating_buttons)

    def send_message(self):
        """Envía el mensaje del usuario al motor de chat."""
        user_message = self.input_text.toPlainText().strip()
        if not user_message:
            return

        if not self.chat_engine.provider:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un modelo antes de enviar un mensaje.")
            return

        # Añadir mensaje del usuario al historial lógico y UI
        user_message_obj = {"role": "user", "content": user_message}
        self.chat_engine.history.append(user_message_obj)
        self.add_to_history(user_message_obj, show_rating_buttons=False) # No mostrar botones de rating para mensajes de usuario

        self.input_text.clear()
        self.send_button.setEnabled(False)
        self.loading_indicator.setVisible(True)

        # Determinar qué worker ejecutar basado en el modo
        if self.agent_mode:
            self.run_agent_worker(user_message)
        elif self.reasoner_mode:
            self.run_reasoner_worker(user_message)
        else:
            # Modo chat normal
            self.run_chat_worker(user_message)

    def run_chat_worker(self, user_message: str):
        """Inicia el worker para el modo de chat normal."""
        self.worker_thread = QThread()
        self.worker = Worker(self.chat_engine, user_message)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        
        # Limpieza
        self.worker.response_ready.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def run_agent_worker(self, user_message: str):
        """Inicia el worker para el modo agente."""
        # Importaciones locales para evitar dependencias circulares a nivel de módulo
        from MARTIN_LLM.app.agent import Agent

        if not isinstance(self.chat_engine.provider, BaseLLMProvider):
            self.handle_error("El proveedor de modelo actual no es compatible con el modo agente.")
            return

        self.add_system_message("MODO AGENTE INICIADO. OBJETIVO: " + user_message, show_rating_buttons=False)
        self.process_log_window.show() # Mostrar la ventana de log
        self.process_log_window.append_log(f"MODO AGENTE INICIADO. OBJETIVO: {user_message}")
        
        current_system_prompt = self.chat_engine.system_prompt if self.chat_engine else SYSTEM_PROMPT
        agent = Agent(self.chat_engine.provider, custom_prompt=current_system_prompt)
        self.worker_thread = QThread()
        self.worker = AgentWorker(agent, user_message)
        self.worker.moveToThread(self.worker_thread)

        # Conectar señales
        self.worker_thread.started.connect(self.worker.run)
        self.worker.agent_step.connect(self.display_agent_step)
        self.worker.response_ready.connect(self.handle_agent_response)
        self.worker.error_occurred.connect(self.handle_error)
        
        # Limpieza
        self.worker.response_ready.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()
    def run_reasoner_worker(self, user_objective: str):
        """Inicia el worker para el modo razonador (Plan-and-Execute)."""
        # Importaciones locales para evitar dependencias circulares a nivel de módulo
        from MARTIN_LLM.app.reasoner import Reasoner

        if not isinstance(self.chat_engine.provider, BaseLLMProvider):
            self.handle_error("El proveedor de modelo actual no es compatible con el modo razonador.")
            return

        self.add_system_message("MODO RAZONADOR INICIADO. OBJETIVO: " + user_objective, show_rating_buttons=False)
        self.process_log_window.show() # Mostrar la ventana de log
        self.process_log_window.append_log(f"MODO RAZONADOR INICIADO. OBJETIVO: {user_objective}")
        
        self.worker_thread = QThread()
        current_system_prompt = self.chat_engine.system_prompt if self.chat_engine else SYSTEM_PROMPT
        self.worker = ReasonerWorker(self.chat_engine.provider, user_objective, custom_prompt=current_system_prompt)
        self.worker.moveToThread(self.worker_thread)

        # Conectar señales
        self.worker_thread.started.connect(self.worker.run)
        self.worker.plan_ready.connect(self.display_reasoner_plan)
        self.worker.step_result.connect(self.display_reasoner_step_result)
        self.worker.response_ready.connect(self.handle_response) # Reutilizamos el manejador final
        self.worker.error_occurred.connect(self.handle_error)
        
        # Limpieza
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
            step_message = f"🤔 Pensando: {thought}\n- ⚡ Acción: Usar herramienta \'{tool_name}\' con argumentos: \'{args}\'"
        self.add_system_message(step_message, show_rating_buttons=False)
        self.process_log_window.append_log(step_message)
    def handle_agent_response(self, response: str):
        """Maneja la respuesta final del agente."""
        self.add_system_message("AGENTE HA FINALIZADO LA TAREA.", show_rating_buttons=False)
        self.process_log_window.append_log("AGENTE HA FINALIZADO LA TAREA.")
        # Añadir la respuesta final del agente al historial lógico
        assistant_message = {"role": "assistant", "content": response}
        if self.chat_engine:
            self.chat_engine.history.append(assistant_message)
        self.handle_response(assistant_message) # Reutiliza el manejador de respuesta normal
    def handle_response(self, response_content):
        """Maneja la respuesta exitosa del worker."""
        print("[UI] Manejando respuesta del worker.")
        self.loading_indicator.setVisible(False)
        # Create a message object from the response content
        response_obj = {"role": "assistant", "content": response_content}
        # Add assistant response to logical history
        if self.chat_engine:
            self.chat_engine.history.append(response_obj)
        self.add_to_history(response_obj) # Pass the full message object
        # Now, with the complete and updated history, save.
        self.save_conversation(is_autosave=True)
        self.send_button.setEnabled(True)
        self.input_text.setFocus()
        # Ocultar la ventana de log si no estamos en modo agente/razonador
        if not self.agent_mode and not self.reasoner_mode:
            self.process_log_window.hide()
    def handle_error(self, error_msg):
        """Maneja un error del worker."""
        print(f"[UI] Manejando error del worker: {error_msg}")
        self.loading_indicator.setVisible(False)
        self.add_to_history({"role": "assistant", "content": f"ERROR: {error_msg}"})
        self.send_button.setEnabled(True)
        self.input_text.setFocus()
        self.process_log_window.append_log(f"ERROR: {error_msg}")
        self.process_log_window.show() # Asegurarse de que la ventana de log esté visible en caso de error
    def start_new_conversation(self):
        """Inicia una nueva conversación"""
        if not self.chat_engine or not self.chat_engine.provider:
            QMessageBox.warning(self, "Advertencia", 
                               "Debes seleccionar un modelo primero.")
            return
        
        # Limpiar la UI y reiniciar el motor de chat para una nueva conversación
        self.clear_history()
        self.chat_engine.start_new()
        self.add_system_message("NUEVA CONVERSACIÓN INICIADA.", show_rating_buttons=False)
        self.add_to_history({"role": "assistant", "content": "Sistema listo para recibir comandos."}, show_rating_buttons=False)
        self.process_log_window.clear_log() # Limpiar el log al iniciar nueva conversación
        self.process_log_window.hide() # Ocultar la ventana de log

    def save_conversation(self, is_autosave=False):
        """Guarda la conversación actual"""
        print("[DEBUG] SAVE_CONVERSATION en ChatInterface")
        
        if not self.chat_engine:
            if not is_autosave:
                QMessageBox.warning(self, "Advertencia", 
                                   "No hay conversación activa para guardar.")
            return
        
        if not self.user_id:
            if not is_autosave:
                QMessageBox.critical(self, "Error", "No hay usuario autenticado.")
            return
        
        try:
            if not self.chat_engine.conversation_id:
                # Crear nueva conversación
                print("[DEBUG] No hay ID de conversación, creando una nueva.")
                conv_data = {
                    "user_id": self.user_id, # <-- AÑADIDO: Esencial para asociar la conversación al usuario
                    "model": self.chat_engine.provider.model_identifier,
                    "title": self.generate_conversation_title(),
                    "timestamp": datetime.now(),
                    "messages": self.chat_engine.history,
                    "system_prompt": self.chat_engine.system_prompt,
                    "metadata": {}
                }
                
                new_id = self.user_service.create_conversation(self.user_id, conv_data) # This seems to pass user_id twice, let's check the service
                if new_id:
                    self.chat_engine.conversation_id = new_id
                    
                    if not is_autosave:
                        self.add_system_message("CONVERSACIÓN GUARDADA EN LA BASE DE DATOS", show_rating_buttons=False)
                        QMessageBox.information(self, "Guardado", 
                                               "Conversación guardada correctamente.")
                    
                    self.populate_recent_conversations()
                else:
                    if not is_autosave:
                        QMessageBox.critical(self, "Error", "No se pudo crear la conversación en la base de datos.")
            else:
                # Actualizar conversación existente
                print(f"[DEBUG] Actualizando conversación existente: {self.chat_engine.conversation_id}")
                conv_data_to_update = {
                    "messages": self.chat_engine.history,
                    "system_prompt": self.chat_engine.system_prompt,
                    "metadata": {},
                    "timestamp": datetime.now(),
                    "title": self.generate_conversation_title(),
                    "model": self.chat_engine.provider.model_identifier # <-- AÑADIR PARA CONSISTENCIA
                }
                
                self.user_service.update_conversation(
                    self.user_id, self.chat_engine.conversation_id, conv_data_to_update)
                
                if not is_autosave:
                    self.add_system_message("CONVERSACIÓN ACTUALIZADA EN LA BASE DE DATOS", show_rating_buttons=False)
                    QMessageBox.information(self, "Actualizado", 
                                           "Los cambios han sido guardados.")
                
                self.populate_recent_conversations()
                    
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la conversación: {e}")
            if not is_autosave:
                QMessageBox.critical(self, "Error", 
                                    f"No se pudo guardar la conversación: {e}")

    def create_rating_buttons(self, layout, role, message):
        """Crea y configura los botones de calificación."""
        thumbs_up_button = QPushButton(qta.icon("fa5s.thumbs-up", color="#68d391"), "")
        thumbs_up_button.setToolTip("Respuesta útil")
        thumbs_up_button.setFixedSize(30, 30)
        thumbs_up_button.setStyleSheet("background: transparent; border: none;")
        thumbs_up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        thumbs_up_button.clicked.connect(lambda ch, r=role, m=message: self.rate_message(r, m, "up"))

        thumbs_down_button = QPushButton(qta.icon("fa5s.thumbs-down", color="#f56565"), "")
        thumbs_down_button.setToolTip("Respuesta no útil")
        thumbs_down_button.setFixedSize(30, 30)
        thumbs_down_button.setStyleSheet("background: transparent; border: none;")
        thumbs_down_button.setCursor(Qt.CursorShape.PointingHandCursor)
        thumbs_down_button.clicked.connect(lambda ch, r=role, m=message: self.rate_message(r, m, "down"))

        layout.addWidget(thumbs_up_button)
        layout.addWidget(thumbs_down_button)

        # Deshabilitar los botones después de un clic para evitar múltiples votos
        thumbs_up_button.clicked.connect(lambda: (thumbs_up_button.setEnabled(False), thumbs_down_button.setEnabled(False)))
        thumbs_down_button.clicked.connect(lambda: (thumbs_up_button.setEnabled(False), thumbs_down_button.setEnabled(False)))

    def rate_message(self, role, content, rating):
        """Maneja la calificación de un mensaje.

        Args:
            role (str): "user" o "assistant"
            content (str): El texto del mensaje.
            rating (str): "up" o "down"
        """
        if not self.chat_engine or not self.chat_engine.conversation_id:
            QMessageBox.warning(self, "Advertencia", "No hay conversación activa.")
            return

        # Buscar el mensaje específico en el historial y añadir la calificación
        for msg in self.chat_engine.history:
            if msg["role"] == role and msg["content"] == content:
                msg["rating"] = rating
                print(f"Mensaje calificado: {role} - {content} - {rating}")
                break

        # Guardar la conversación actualizada
        try:
            self.save_conversation(is_autosave=True)
        except Exception as e:
            print(f"Error al guardar la conversación después de la calificación: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar la calificación: {e}")
    def export_conversation(self):
        """Exporta la conversación actual a un archivo .txt o .json."""
        if not self.chat_engine or not self.chat_engine.history:
            QMessageBox.warning(self, "Sin conversación", "No hay una conversación activa para exportar.")
            return

        # Generar un nombre de archivo por defecto
        default_filename = self.generate_conversation_title().replace(" ", "_").lower()

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar Conversación",
            f"{default_filename}",
            "JSON files (*.json);;Text files (*.txt)"
        )

        if not file_path:
            return # El usuario canceló

        try:
            if selected_filter.startswith("JSON"):
                # Exportar a JSON
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
                    f.write(f"Fecha de exportación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n")
                    f.write(f"--- SYSTEM PROMPT ---\n{self.chat_engine.system_prompt}\n\n--- HISTORIAL ---\n")
                    for message in self.chat_engine.history:
                        f.write(f"[{message.get("role", "unknown").upper()}]\n{message.get("content", "")}\n\n---\n")
            
            self.add_system_message(f"CONVERSACIÓN EXPORTADA A: {Path(file_path).name}", show_rating_buttons=False)
            QMessageBox.information(self, "Exportación Exitosa", f"La conversación ha sido exportada a\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"No se pudo exportar la conversación:\n{e}")
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
            conversations = self.user_service.get_user_conversations(self.user_id)
            if not conversations:
                QMessageBox.information(self, "Sin conversaciones", "No tienes conversaciones guardadas.")
                return
            dialog = ConversationLoadDialog(conversations, self)
            if dialog.exec():
                conv_id = dialog.get_selected_conversation_id()
                if conv_id:
                    self.load_selected_conversation(conv_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las conversaciones: {e}")
    def load_selected_conversation(self, conv_id):
        """Carga los datos de una conversación específica en la UI."""
        self.add_system_message(f"CARGANDO CONVERSACIÓN ID: {conv_id}...", show_rating_buttons=False)
        conv_data = self.user_service.get_conversation(self.user_id, conv_id)
        if not conv_data:
            QMessageBox.critical(self, "Error", "No se pudo cargar la conversación.")
            return
        
        model_identifier = conv_data.get("model", "default_model")
        
        try:
            # 1. Configurar el proveedor y el motor de chat con el modelo de la conversación.
            if model_identifier.lower().endswith(".gguf"):
                provider = LlamaCppProvider(model_path=model_identifier)
                display_name = Path(model_identifier).name
            else:
                provider = OllamaProvider(model_name=model_identifier)
                display_name = model_identifier

            # Aplicar los parámetros actuales de la UI al nuevo proveedor
            if hasattr(self, "parameters_panel"):
                current_params = self.parameters_panel.content.get_current_parameters()
                print(f"[DEBUG] Aplicando parámetros al modelo cargado: {current_params}")
                provider.set_generation_parameters(**current_params)

            self.chat_engine.provider = provider
            self.selected_model_name = model_identifier
            self.selected_model_name = model_identifier # <-- AÑADIDO para consistencia
            self.model_label.setText(f"> MODELO: [{display_name.upper()}] - ACTIVO")

            # 2. Cargar los datos de la conversación en el motor de chat usando el método dedicado.
            history = conv_data.get("messages", [])
            system_prompt = conv_data.get("system_prompt", SYSTEM_PROMPT)
            self.chat_engine.load_conversation(
                conversation_id=conv_id,
                history=history,
                system_prompt=system_prompt
            )
            self.system_prompt_edit.setPlainText(system_prompt)

            # 3. Actualizar la interfaz de usuario.
            self.clear_history()
            self.add_system_message(f"CONVERSACIÓN CARGADA: {conv_data.get("title", "Sin título")}", show_rating_buttons=False)
            self.repopulate_history_ui()
            self.populate_recent_conversations()
        except Exception as e:
            QMessageBox.critical(self, "Error al Cargar Modelo", f"No se pudo cargar el modelo \'{model_identifier}\' asociado a esta conversación:\n{e}")
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
                self.add_system_message(f"ARCHIVO CARGADO: {file_path}", show_rating_buttons=False)
                current_prompt = self.input_text.toPlainText()
                new_prompt = f"Basado en el siguiente contenido del archivo \'{Path(file_path).name}\':\n\n---\n{text}\n---\n\n{current_prompt}"
                self.input_text.setPlainText(new_prompt)
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                    f"No se pudo procesar el archivo: {e}")
    def repopulate_history_ui(self):
        """Vuelve a dibujar el historial en la UI a partir de self.chat_engine.history."""
        for msg in self.chat_engine.history:
            self.add_to_history(msg)
    def start_cleanup_process(self, on_finish_callback):
        """Muestra el diálogo de cierre e inicia el worker de limpieza."""
        if self.cleanup_in_progress:
            return
        
        self.cleanup_in_progress = True
        self.closing_dialog = ClosingDialog()
        self.cleanup_worker = CleanupWorker(self.ollama_manager)
        self.cleanup_thread = QThread()
        self.cleanup_worker.moveToThread(self.cleanup_thread)

        self.cleanup_worker.finished.connect(on_finish_callback)
        self.cleanup_thread.started.connect(self.cleanup_worker.run)

        self.cleanup_thread.start()
        self.closing_dialog.show()
    def do_logout(self):
        """Acción final para cerrar sesión."""
        self.cleanup_in_progress = False
        self.closing_dialog.close()
        self.logout_requested.emit()
        # Clean up the thread
        self.cleanup_thread.quit()
        self.cleanup_thread.wait()

    def do_quit(self):
        """Acción final para salir de la aplicación."""
        self.cleanup_in_progress = False
        self.closing_dialog.close()
        self.is_ready_to_close = True
        self.close()
    def logout(self):
        """Initiates the cleanup process for logging out."""
        if self.cleanup_in_progress:
            return
        print("[ChatInterface] Logout requested. Starting cleanup...")
        self.start_cleanup_process(self.do_logout)
    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        if self.is_ready_to_close:
            # La limpieza ha terminado, aceptar el evento para cerrar la app.
            super().closeEvent(event)
            return

        if self.cleanup_in_progress:
            # Ya hay un cierre en proceso, ignorar peticiones subsecuentes.
            event.ignore()
            return
        
        # Es la primera petición de cierre, iniciar el proceso de limpieza.
        event.ignore()
        self.start_cleanup_process(self.do_quit)
    def on_mode_changed(self, button, checked):
        """Maneja el cambio de modo de operación (Chat, Agente, Razonador)."""
        if not checked:
            return # Solo actuar sobre el botón que fue seleccionado

        if button is self.chat_mode_radio:
            self.agent_mode = False
            self.reasoner_mode = False
            self.add_system_message("MODO CHAT ACTIVADO.", show_rating_buttons=False)
            self.input_text.setPlaceholderText("Escribe tu prompt aquí...")
            self.process_log_window.hide() # Ocultar la ventana de log en modo chat
        elif button is self.agent_mode_radio:
            self.agent_mode = True
            self.reasoner_mode = False
            self.chat_engine.system_prompt = AGENT_SYSTEM_PROMPT_TEMPLATE
            self.add_system_message("MODO AGENTE ACTIVADO. Los prompts se tratarán como objetivos para el agente.", show_rating_buttons=False)
            self.input_text.setPlaceholderText("Escribe tu objetivo para el agente aquí...")
            self.process_log_window.show() # Mostrar la ventana de log en modo agente
        elif button is self.reasoner_mode_radio:
            self.agent_mode = False
            self.reasoner_mode = True
            self.add_system_message("MODO RAZONADOR ACTIVADO. Los prompts se tratarán como objetivos complejos a planificar.", show_rating_buttons=False)
            self.input_text.setPlaceholderText("Escribe tu objetivo complejo aquí...")
            self.process_log_window.show() # Mostrar la ventana de log en modo razonador
    def toggle_left_panel(self):
        """Muestra u oculta el panel de conversaciones recientes."""
        if hasattr(self, "left_panel"):
            self.left_panel.setVisible(not self.left_panel.isVisible())