# -*- coding: utf-8 -*-
# ui/registration_widget.py

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox,
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import re

from .custom_widgets import FramelessWindowMixin, CustomTitleBar, FadeInMixin
from app.services.login_service import UserService

class RegistrationWidget(FadeInMixin, QMainWindow, FramelessWindowMixin):
    """Widget de registro de nuevos usuarios."""
    
    # --- SEÑALES ---
    registration_success = pyqtSignal()
    back_to_login = pyqtSignal()
    
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        if not user_service:
            raise ValueError("RegistrationWidget requiere una instancia de UserService.")
        
        self.user_service = user_service
        self._init_frameless_mixin()
        self.setup_ui()

        # --- Ajuste dinámico del tamaño de la ventana ---
        screen = QApplication.primaryScreen()
        if screen:
            available_geometry = screen.availableGeometry()
            screen_width = available_geometry.width()
            screen_height = available_geometry.height()
            
            window_width = int(screen_width * 0.3)
            window_height = int(screen_height * 0.5)
            
            self.resize(window_width, window_height)
            
            # Centrar la ventana
            self.move(int((screen_width - window_width) / 2), int((screen_height - window_height) / 2))
            
            self.setMinimumSize(int(screen_width * 0.25), int(screen_height * 0.4))
        else:
            # Fallback a un tamaño fijo si no se puede obtener la pantalla
            self.resize(450, 650)
            self.setMinimumSize(400, 600)

    def setup_ui(self):
        main_container = QWidget()
        window_layout = QVBoxLayout(main_container)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, "Registro de Nuevo Usuario", show_max_min=False)
        window_layout.addWidget(self.title_bar)

        content_frame = QFrame()
        content_frame.setObjectName("loginContainerFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(15)
        window_layout.addWidget(content_frame)
        self.setCentralWidget(main_container)

        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)

        # Campos del formulario
        content_layout.addWidget(QLabel("Usuario:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Elige un nombre de usuario")
        self.username_input.setMinimumHeight(35)
        content_layout.addWidget(self.username_input)

        content_layout.addWidget(QLabel("Correo Electrónico (Opcional):"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@correo.com")
        self.email_input.setMinimumHeight(35)
        content_layout.addWidget(self.email_input)

        content_layout.addWidget(QLabel("Contraseña:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mínimo 8 caracteres")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        content_layout.addWidget(self.password_input)

        content_layout.addWidget(QLabel("Confirmar Contraseña:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Repite la contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(35)
        content_layout.addWidget(self.confirm_password_input)

        # Consentimiento
        consent_frame = QFrame()
        consent_frame.setObjectName("consentFrame")
        consent_layout = QVBoxLayout(consent_frame)
        consent_text = QLabel(
            "Para ayudar a mejorar la IA, ¿permites que tus conversaciones "
            "se usen de forma anónima para entrenar futuros modelos?"
        )
        consent_text.setWordWrap(True)
        self.share_data_checkbox = QCheckBox("Sí, acepto compartir datos anónimos")
        self.share_data_checkbox.setChecked(True)
        consent_layout.addWidget(consent_text)
        consent_layout.addWidget(self.share_data_checkbox)
        content_layout.addWidget(consent_frame)

        # Botones
        button_layout = QHBoxLayout()
        self.register_button = QPushButton("REGISTRARSE")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.register)
        
        self.back_button = QPushButton("VOLVER")
        self.back_button.setMinimumHeight(40)
        self.back_button.clicked.connect(self.back_to_login.emit)

        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.register_button)
        content_layout.addLayout(button_layout)

    def register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        share_data = self.share_data_checkbox.isChecked()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Campos Requeridos", "Usuario y contraseña son obligatorios.")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Contraseña Débil", "La contraseña debe tener al menos 8 caracteres.")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        try:
            user_id = self.user_service.register_user(username, password, email, share_data)
            if user_id:
                QMessageBox.information(self, "Éxito", f"Usuario '{username}' registrado. Ahora puedes iniciar sesión.")
                self.registration_success.emit()
            else:
                QMessageBox.critical(self, "Error", "El nombre de usuario ya está en uso.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {e}")