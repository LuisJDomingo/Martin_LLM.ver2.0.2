# -*- coding: utf-8 -*-
# ui/login_widget.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Importación relativa para acceder al paquete 'app' desde 'ui'
from app.services.login_service import UserService

class LoginWidget(QWidget):
    """Widget de login con tema sci-fi para PyQt6"""
    
    # Señal emitida cuando el login es exitoso
    login_success = pyqtSignal(str, str)  # user_id, username
    registration_requested = pyqtSignal() # Emitida cuando el usuario quiere registrarse
    
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        print("[DEBUG] Creando LoginWidget")
        
        if not user_service:
            raise ValueError("LoginWidget requiere una instancia de UserService.")
        
        self.user_service = user_service
        self.remember_me_checked = False
        
        self.setup_ui()
        self.load_remembered_credentials()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        print("[DEBUG] LoginWidget.setup_ui llamado")
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        
        # Frame contenedor central
        container_frame = QFrame()
        container_frame.setObjectName("loginContainerFrame") # Asignamos un nombre para un estilo específico
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        container_frame.setMinimumSize(380, 380)  # Cambiado a tamaño mínimo para permitir expansión
        
        # Layout del contenedor
        container_layout = QVBoxLayout(container_frame)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(15)
        self.setWindowTitle(f"titulo marco windows")
        
        # Título
        title_label = QLabel("Bienvenido, soy Martin,un asistente virtual")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")  # Usa el estilo de qt_styles.py
        container_layout.addWidget(title_label)
        
        # Campo de usuario
        user_label = QLabel("Usuario:")
        # user_label.setStyleSheet(...) # Eliminado para usar el estilo global
        container_layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu nombre de usuario")
        self.username_input.setMinimumHeight(35)
        self.username_input.returnPressed.connect(self.login)
        container_layout.addWidget(self.username_input)
        
        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        # password_label.setStyleSheet(...) # Eliminado para usar el estilo global
        container_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingresa tu contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.login)
        container_layout.addWidget(self.password_input)
        
        # Checkbox "Recordarme" con etiqueta clickeable
        remember_me_layout = QHBoxLayout()
        remember_me_layout.setSpacing(10)
        remember_me_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.remember_checkbox = QCheckBox()
        remember_me_label = QLabel("Recordarme")
        remember_me_label.mousePressEvent = lambda event: self.remember_checkbox.toggle()
        remember_me_layout.addWidget(self.remember_checkbox)
        remember_me_layout.addWidget(remember_me_label)
        container_layout.addLayout(remember_me_layout)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton("ENTRAR")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.login)
        
        self.register_button = QPushButton("REGISTRARSE")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.registration_requested.emit)

        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        container_layout.addLayout(button_layout)
        
        # Agregar el contenedor al layout principal
        main_layout.addWidget(container_frame)
        
        self.setLayout(main_layout)
        
    def login(self):
        """Maneja el proceso de login"""
        print("[DEBUG] LoginWidget.login llamado")
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", 
                               "Por favor, ingresa usuario y contraseña")
            return
        
        auth_result = self.user_service.authenticate_user(username, password)
        
        if auth_result:
            user_id, username = auth_result
            print(f"[DEBUG] Resultado autenticación: user_id={user_id}, username={username}")
            
            # Manejar recordarme
            if self.remember_checkbox.isChecked():
                self.user_service.remember_user(self.username_input.text(), 
                                               self.password_input.text())
            else:
                self.user_service.forget_user()
            
            # Emitir señal de login exitoso
            self.login_success.emit(user_id, username)
            
        else:
            print("[DEBUG] Login fallido")
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()
            
    def load_remembered_credentials(self):
        """Carga las credenciales recordadas si existen"""
        username, password = self.user_service.get_remembered_user()
        if username and password:
            self.username_input.setText(username)
            self.password_input.setText(password)
            self.remember_checkbox.setChecked(True)
            print("[DEBUG] Credenciales recordadas cargadas")
