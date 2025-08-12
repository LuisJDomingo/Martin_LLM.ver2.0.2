# -*- coding: utf-8 -*-
# ui/registration_widget.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QMessageBox,
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal

# Importación absoluta
from app.services.login_service import UserService

class RegistrationWidget(QWidget):
    """Widget para el registro de nuevos usuarios."""

    # Señales
    registration_complete = pyqtSignal() # Emitida cuando el registro es exitoso
    registration_cancelled = pyqtSignal() # Emitida cuando se cancela

    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        if not user_service:
            raise ValueError("RegistrationWidget requiere una instancia de UserService.")

        self.user_service = user_service
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario del widget de registro."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        container_frame = QFrame()
        container_frame.setObjectName("loginContainerFrame")
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        container_frame.setMinimumSize(420, 500)

        container_layout = QVBoxLayout(container_frame)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(15)
        self.setWindowTitle("Registro de Nuevo Usuario")

        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        container_layout.addWidget(title_label)

        # --- Campos de entrada ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")
        self.username_input.setMinimumHeight(35)
        container_layout.addWidget(QLabel("Usuario:"))
        container_layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        self.email_input.setMinimumHeight(35)
        container_layout.addWidget(QLabel("Correo Electrónico (para recuperación):"))
        container_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña (mínimo 4 caracteres)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        container_layout.addWidget(QLabel("Contraseña:"))
        container_layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(35)
        container_layout.addWidget(QLabel("Confirmar Contraseña:"))
        container_layout.addWidget(self.confirm_password_input)

        # --- Consentimiento de datos ---
        share_data_layout = QHBoxLayout()
        share_data_layout.setSpacing(10)
        share_data_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.share_data_checkbox = QCheckBox()
        self.share_data_checkbox.setChecked(True)
        share_data_layout.addWidget(self.share_data_checkbox)

        share_data_label = QLabel("Acepto compartir mis conversaciones anónimamente para mejorar el modelo.")
        share_data_label.setWordWrap(True)
        share_data_label.setToolTip("Tus conversaciones se usarán para entrenar futuros modelos. No se guardará información personal identificable.")
        share_data_label.mousePressEvent = lambda event: self.share_data_checkbox.toggle()
        share_data_layout.addWidget(share_data_label)
        container_layout.addLayout(share_data_layout)

        # --- Botones ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.register_button = QPushButton("REGISTRAR CUENTA")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.register)

        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setObjectName("uninstallModelButton") # Estilo rojo
        self.cancel_button.clicked.connect(self.registration_cancelled.emit)

        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)
        container_layout.addLayout(button_layout)

        main_layout.addWidget(container_frame)
        self.setLayout(main_layout)

    def register(self):
        """Maneja la lógica y validación del registro."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validaciones
        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "Campos Incompletos", "Por favor, rellena todos los campos.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Contraseñas no Coinciden", "Las contraseñas introducidas no son iguales.")
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.password_input.setFocus()
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Contraseña Débil", "La contraseña debe tener al menos 4 caracteres.")
            return

        # TODO: Añadir una validación básica de email con regex si se desea.

        share_data_consent = self.share_data_checkbox.isChecked()

        # Llamar al servicio para registrar
        user_id = self.user_service.register_user(
            username=username,
            password=password,
            email=email,
            share_data=share_data_consent
        )

        if user_id:
            QMessageBox.information(self, "Registro Exitoso",
                                   f"¡Cuenta para '{username}' creada con éxito!\nAhora puedes volver a la pantalla de inicio para entrar.")
            self.registration_complete.emit()
        else:
            QMessageBox.critical(self, "Error de Registro",
                                 "El nombre de usuario ya existe. Por favor, elige otro.")
            self.username_input.setFocus()
            self.username_input.selectAll()