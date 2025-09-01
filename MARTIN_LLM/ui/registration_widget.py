# -*- coding: utf-8 -*-
# ui/registration_widget.py (Versión Mejorada)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QMessageBox,
                             QFrame, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import re

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

    def _validate_email(self, email: str) -> bool:
        """Valida el formato de un email."""
        if not email:
            return True  # El email es opcional
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def setup_ui(self):
        """Configura la interfaz de usuario del widget de registro."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        container_frame = QFrame()
        container_frame.setObjectName("loginContainerFrame")
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        container_frame.setMinimumSize(500, 650)

        container_layout = QVBoxLayout(container_frame)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container_layout.setSpacing(15)
        self.setWindowTitle("Registro de Nuevo Usuario")

        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        container_layout.addWidget(title_label)

        subtitle_label = QLabel("Únete a la comunidad de Martin LLM")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #a0aec0; font-size: 10pt; margin-bottom: 10px;")
        container_layout.addWidget(subtitle_label)

        # --- Campos de entrada ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")
        self.username_input.setMinimumHeight(35)
        container_layout.addWidget(QLabel("Usuario:"))
        container_layout.addWidget(self.username_input)

        # Campo de email con validación visual
        email_label = QLabel("Correo Electrónico (opcional):")
        container_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        self.email_input.setMinimumHeight(35)
        self.email_input.textChanged.connect(self.validate_email_field)
        container_layout.addWidget(self.email_input)

        # Etiqueta de advertencia para el email
        self.email_warning_label = QLabel(
            "⚠️ Si no proporcionas un email, no podrás recuperar tu contraseña en caso de olvidarla."
        )
        self.email_warning_label.setStyleSheet("""
            QLabel {
                color: #f6ad55;
                font-size: 9pt;
                background-color: #2d3748;
                border: 1px solid #f6ad55;
                border-radius: 4px;
                padding: 5px;
                margin: 2px 0px;
            }
        """)
        self.email_warning_label.setWordWrap(True)
        self.email_warning_label.setVisible(True)
        container_layout.addWidget(self.email_warning_label)

        # Etiqueta de error para email inválido
        self.email_error_label = QLabel("❌ Formato de email inválido")
        self.email_error_label.setStyleSheet("""
            QLabel {
                color: #f56565;
                font-size: 9pt;
                background-color: #2d3748;
                border: 1px solid #f56565;
                border-radius: 4px;
                padding: 5px;
                margin: 2px 0px;
            }
        """)
        self.email_error_label.setVisible(False)
        container_layout.addWidget(self.email_error_label)

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

        # --- Consentimiento de datos mejorado ---
        consent_frame = QFrame()
        consent_frame.setStyleSheet("""
            QFrame {
                background-color: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0px;
            }
        """)
        consent_layout = QVBoxLayout(consent_frame)
        consent_layout.setSpacing(10)

        # Título de la sección
        consent_title = QLabel("🤝 Contribuye al Futuro de la IA")
        consent_title.setStyleSheet("font-weight: bold; font-size: 11pt; color: #68d391;")
        consent_layout.addWidget(consent_title)

        # Texto descriptivo mejorado
        consent_text = QLabel("""
Ayúdanos a construir un futuro más inteligente. Al activar esta opción, tus conversaciones anónimas y valoraciones serán utilizadas para entrenar y mejorar continuamente nuestros modelos de IA.

🎯 <b>Beneficios de tu contribución:</b>
• Desarrollo de una IA más precisa y útil
• Mejor comprensión de las necesidades de los usuarios
• Avances en la tecnología de inteligencia artificial
• Respuestas más contextuales y relevantes

🔒 <b>Tu privacidad está protegida:</b>
• Todas las conversaciones se anonimizan completamente
• No se almacena información personal identificable
• Los datos se utilizan exclusivamente para investigación y mejora
• Puedes cambiar esta preferencia en cualquier momento

Tu contribución es clave para el avance de la inteligencia artificial y para crear herramientas que realmente ayuden a las personas.
        """)
        consent_text.setWordWrap(True)
        consent_text.setStyleSheet("""
            QLabel {
                color: #e1e5e9;
                font-size: 9pt;
                line-height: 1.4;
                text-align: justify;
            }
        """)
        consent_layout.addWidget(consent_text)

        # Checkbox con etiqueta
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(10)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.share_data_checkbox = QCheckBox()
        self.share_data_checkbox.setChecked(True)  # Por defecto activado
        checkbox_layout.addWidget(self.share_data_checkbox)

        share_data_label = QLabel("✅ <b>Sí, quiero contribuir al desarrollo de la IA</b>")
        share_data_label.setStyleSheet("color: #68d391; font-size: 10pt;")
        share_data_label.mousePressEvent = lambda event: self.share_data_checkbox.toggle()
        checkbox_layout.addWidget(share_data_label)

        consent_layout.addLayout(checkbox_layout)
        container_layout.addWidget(consent_frame)

        # --- Botones ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.register_button = QPushButton("CREAR CUENTA")
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

    def validate_email_field(self):
        """Valida el campo de email en tiempo real y muestra/oculta las etiquetas correspondientes."""
        email = self.email_input.text().strip()
        
        if not email:
            # Si está vacío, mostrar advertencia y ocultar error
            self.email_warning_label.setVisible(True)
            self.email_error_label.setVisible(False)
            self.email_input.setStyleSheet("")  # Estilo normal
        elif self._validate_email(email):
            # Email válido, ocultar ambas etiquetas
            self.email_warning_label.setVisible(False)
            self.email_error_label.setVisible(False)
            self.email_input.setStyleSheet("border: 2px solid #68d391;")  # Borde verde
        else:
            # Email inválido, mostrar error y ocultar advertencia
            self.email_warning_label.setVisible(False)
            self.email_error_label.setVisible(True)
            self.email_input.setStyleSheet("border: 2px solid #f56565;")  # Borde rojo

    def register(self):
        """Maneja la lógica y validación del registro."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validaciones básicas
        if not username:
            QMessageBox.warning(self, "Campo Requerido", "El nombre de usuario es obligatorio.")
            self.username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Campo Requerido", "La contraseña es obligatoria.")
            self.password_input.setFocus()
            return

        if not confirm_password:
            QMessageBox.warning(self, "Campo Requerido", "Debes confirmar tu contraseña.")
            self.confirm_password_input.setFocus()
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Contraseñas no Coinciden", "Las contraseñas introducidas no son iguales.")
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.password_input.setFocus()
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Contraseña Débil", "La contraseña debe tener al menos 4 caracteres.")
            self.password_input.setFocus()
            return

        # Validación de email si se proporciona
        if email and not self._validate_email(email):
            QMessageBox.warning(self, "Email Inválido", 
                               "Por favor, ingresa un correo electrónico válido o déjalo vacío.")
            self.email_input.setFocus()
            return

        share_data_consent = self.share_data_checkbox.isChecked()

        # Llamar al servicio para registrar
        try:
            user_id = self.user_service.register_user(
                username=username,
                password=password,
                email=email if email else None,
                share_data=share_data_consent
            )

            if user_id:
                # Mensaje de éxito personalizado según si proporcionó email o no
                if email:
                    success_message = (
                        f"¡Cuenta para '{username}' creada con éxito!\\n\\n"
                        f"Se ha registrado tu email: {email}\\n"
                        "Podrás usar esta dirección para recuperar tu contraseña si la olvidas.\\n\\n"
                        "Ahora puedes iniciar sesión."
                    )
                else:
                    success_message = (
                        f"¡Cuenta para '{username}' creada con éxito!\\n\\n"
                        "⚠️ Recuerda: Como no proporcionaste un email, no podrás recuperar "
                        "tu contraseña si la olvidas. Asegúrate de recordarla.\\n\\n"
                        "Ahora puedes iniciar sesión."
                    )
                
                QMessageBox.information(self, "Registro Exitoso", success_message)
                self.registration_complete.emit()
            else:
                QMessageBox.critical(self, "Error de Registro",
                                     "El nombre de usuario ya existe. Por favor, elige otro.")
                self.username_input.setFocus()
                self.username_input.selectAll()
        
        except ValueError as e:
            QMessageBox.critical(self, "Error de Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", 
                                f"Ocurrió un error durante el registro: {str(e)}")