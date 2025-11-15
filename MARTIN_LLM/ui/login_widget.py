# -*- coding: utf-8 -*-
# ui/login_widget.py (Versión Mejorada)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox,
                             QFrame, QSizePolicy, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import re
import os
from pathlib import Path

from .custom_widgets import FramelessWindowMixin, CustomTitleBar, FadeInMixin, show_critical_message, show_warning_message, show_information_message

# Importación relativa para acceder al paquete 'app' desde 'ui'
from app.services.login_service import UserService

class PasswordResetDialog(FadeInMixin, QDialog, FramelessWindowMixin):
    """Diálogo para restablecer contraseña"""
    
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        self._init_frameless_mixin()
        self.user_service = user_service
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo de recuperación"""
        self.setMinimumSize(400, 250)
        
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, "Restablecer Contraseña", show_max_min=False)
        window_layout.addWidget(self.title_bar)

        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        window_layout.addWidget(content_frame)
        
        # Título
        title_label = QLabel("Recuperación de Contraseña")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        content_layout.addWidget(title_label)
        
        # Instrucciones
        instructions_label = QLabel(
            "Ingresa tu nombre de usuario y correo electrónico para restablecer tu contraseña."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(instructions_label)
        
        # Campo de usuario
        content_layout.addWidget(QLabel("Usuario:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu nombre de usuario")
        self.username_input.setMinimumHeight(35)
        content_layout.addWidget(self.username_input)
        
        # Campo de email
        content_layout.addWidget(QLabel("Correo Electrónico:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        self.email_input.setMinimumHeight(35)
        content_layout.addWidget(self.email_input)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.reset_password)
        button_box.rejected.connect(self.reject)
        content_layout.addWidget(button_box)
        
    def reset_password(self):
        """Maneja la lógica de restablecimiento de contraseña"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        
        if not username or not email:
            show_warning_message(self, "Campos Vacíos", 
                               "Por favor, ingresa tanto el usuario como el correo electrónico.")
            return
            
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            show_warning_message(self, "Email Inválido", 
                               "Por favor, ingresa un correo electrónico válido.")
            return
        
        # Aquí se implementaría la lógica real de recuperación de contraseña
        # Por ahora, simulamos el proceso
        success = self.user_service.request_password_reset(username, email)
        
        if success:
            show_information_message(self, "Solicitud Enviada", 
                                   "Se ha enviado un enlace de recuperación a tu correo electrónico.")
            self.accept()
        else:
            show_critical_message(self, "Error", 
                                "No se encontró una cuenta con esos datos. Verifica tu usuario y correo.")

class LoginWidget(FadeInMixin, QMainWindow, FramelessWindowMixin):
    """Widget de login con tema sci-fi para PyQt6"""
    
    # Señal emitida cuando el login es exitoso
    login_success = pyqtSignal(str, str)  # user_id, username
    
    registration_requested = pyqtSignal() # Emitida cuando el usuario quiere registrarse
    
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        print("[LoginWidget] __init__: Creando widget de login.")
        
        if not user_service:
            raise ValueError("LoginWidget requiere una instancia de UserService.")
        
        self.user_service = user_service
        self._init_frameless_mixin()
        self.setup_ui()
        self.load_remembered_credentials()

        # --- Ajuste dinámico del tamaño de la ventana ---
        screen = QApplication.primaryScreen()
        if screen:
            available_geometry = screen.availableGeometry()
            screen_width = available_geometry.width()
            screen_height = available_geometry.height()
            
            window_width = int(screen_width * 0.5)
            window_height = int(screen_height * 0.6)
            
            self.resize(window_width, window_height)
            
            # Centrar la ventana
            self.move(int((screen_width - window_width) / 2), int((screen_height - window_height) / 2))
            
            self.setMinimumSize(int(screen_width * 0.4), int(screen_height * 0.5))
        else:
            # Fallback a un tamaño fijo si no se puede obtener la pantalla
            self.resize(850, 550)
            self.setMinimumSize(800, 500)
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        print("[LoginWidget] setup_ui: Configurando la interfaz de usuario del login.")
        
        main_container = QWidget()
        window_layout = QVBoxLayout(main_container)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, "Martin LLM - Inicio de Sesión", show_max_min=False)
        window_layout.addWidget(self.title_bar)

        form_content_widget = QWidget()
        window_layout.addWidget(form_content_widget)
        self.setCentralWidget(main_container)

        # Layout principal
        main_layout = QHBoxLayout(form_content_widget)
        main_layout.setSpacing(20)
        
        # Panel izquierdo para la imagen
        image_panel = QWidget()
        # image_panel.setMinimumSize(400, 500) # Eliminado para flexibilidad
        image_layout = QVBoxLayout(image_panel)
        image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Cargar y mostrar la imagen
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buscar la imagen en diferentes ubicaciones posibles
        possible_paths = [
            "ui\\assets\\Generated Image September 06, 2025 - 11_02AM.png",

            "assets/login_background.png", 
            "login_background.png"
        ]
        
        image_loaded = False
        for path in possible_paths:
            print(f"[DEBUG] Checking path: {path}")
            if os.path.exists(path):
                print(f"[DEBUG] Path exists: {path}")
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    print(f"[DEBUG] Image loaded successfully from: {path}")
                    # Escalar la imagen manteniendo la proporción
                    scaled_pixmap = pixmap.scaled(380, 300, Qt.AspectRatioMode.KeepAspectRatio, 
                                                 Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                    image_loaded = True
                    break
                else:
                    print(f"[DEBUG] QPixmap failed to load image from: {path} (isNull=True)")
            else:
                print(f"[DEBUG] Path does not exist: {path}")
        
        if not image_loaded:
            # Si no se puede cargar la imagen, mostrar un placeholder
            image_label.setText("MARTIN LLM\\n\\nAsistente Virtual\\nInteligente")
            image_label.setStyleSheet("""
                QLabel {
                    color: #4a90e2;
                    font-size: 18pt;
                    font-weight: bold;
                    text-align: center;
                    background-color: #2d3748;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            image_label.setMinimumSize(380, 300)
        
        image_layout.addWidget(image_label)
        
        # Panel derecho para el formulario de login
        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setSpacing(20)
        
        # Frame contenedor central
        container_frame = QFrame()
        container_frame.setObjectName("loginContainerFrame")
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        # container_frame.setMinimumSize(380, 450) # Eliminado para flexibilidad
        
        # Layout del contenedor
        container_layout = QVBoxLayout(container_frame)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Bienvenido a Martin LLM")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        container_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Tu asistente virtual inteligente")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #a0aec0; font-size: 10pt;")
        container_layout.addWidget(subtitle_label)
        
        # Campo de usuario
        user_label = QLabel("Usuario:")
        container_layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu nombre de usuario")
        self.username_input.setMinimumHeight(35)
        self.username_input.returnPressed.connect(self.login)
        container_layout.addWidget(self.username_input)
        
        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        container_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingresa tu contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.login)
        container_layout.addWidget(self.password_input)
        
        # Layout para checkbox y enlace de recuperación
        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)
        
        # Checkbox "Recordarme"
        remember_layout = QHBoxLayout()
        remember_layout.setSpacing(5)
        remember_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.remember_checkbox = QCheckBox()
        remember_label = QLabel("Recordarme")
        remember_label.mousePressEvent = lambda event: self.remember_checkbox.toggle()
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addWidget(remember_label)
        
        options_layout.addLayout(remember_layout)
        options_layout.addStretch()
        
        # Enlace de recuperación de contraseña
        forgot_password_label = QLabel('<a href="#" style="color: #4a90e2; text-decoration: none;">¿Olvidaste tu contraseña?</a>')
        forgot_password_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        forgot_password_label.linkActivated.connect(self.show_password_reset_dialog)
        forgot_password_label.mousePressEvent = lambda event: self.show_password_reset_dialog()
        options_layout.addWidget(forgot_password_label)
        
        container_layout.addLayout(options_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton("INICIAR SESIÓN")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.login)
        
        self.register_button = QPushButton("REGISTRARSE")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.registration_requested.emit)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        container_layout.addLayout(button_layout)
        
        
        
        # Agregar el contenedor al panel del formulario
        form_layout.addWidget(container_frame)
        
        # Se asignan factores de estiramiento para que los paneles se redimensionen proporcionalmente.
        # El panel del formulario (3) obtiene más espacio que el de la imagen (2).
        main_layout.addWidget(image_panel, 2)
        main_layout.addWidget(form_panel, 3)
        
    def show_password_reset_dialog(self):
        """Muestra el diálogo de recuperación de contraseña"""
        dialog = PasswordResetDialog(self.user_service, self)
        dialog.exec()
        
    def login(self):
        """Maneja el proceso de login"""
        print("[LoginWidget] login: Intento de inicio de sesión.")
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            show_warning_message(self, "Campos vacíos", 
                               "Por favor, ingresa usuario y contraseña")
            return
        
        auth_result = self.user_service.authenticate_user(username, password)
        
        if auth_result:
            user_id, username = auth_result
            print(f"[LoginWidget] login: Autenticación exitosa para '{username}'. Emitiendo señal login_success.")
            
            # Manejar recordarme
            if self.remember_checkbox.isChecked():
                self.user_service.remember_user(self.username_input.text(), 
                                               self.password_input.text())
            else:
                self.user_service.forget_user()
            
            # Emitir señal de login exitoso
            self.login_success.emit(user_id, username)
            
        else:
            print("[LoginWidget] login: Autenticación fallida.")
            show_critical_message(self, "Error", "Usuario o contraseña incorrectos")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()
            
    def load_remembered_credentials(self):
        """Carga las credenciales recordadas si existen"""
        print("[LoginWidget] load_remembered_credentials: Intentando cargar credenciales recordadas.")
        username, password = self.user_service.get_remembered_user()
        if username and password:
            self.username_input.setText(username)
            self.password_input.setText(password)
            self.remember_checkbox.setChecked(True)
            print("[LoginWidget] load_remembered_credentials: Credenciales encontradas y cargadas.")
        else:
            print("[LoginWidget] load_remembered_credentials: No se encontraron credenciales.")