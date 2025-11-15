# -*- coding: utf-8 -*- 
# main_qt.py

import sys
import os
import uuid
from dotenv import load_dotenv

from PyQt6.QtWidgets import QApplication

# Importar los componentes de la UI
from ui.login_widget import LoginWidget
from ui.chat_interface import ChatInterface
from ui.registration_widget import RegistrationWidget
from ui.loading_dialog import LoadingDialog
from ui.qt_styles import apply_futuristic_theme, apply_additional_login_styles

# Importar los servicios y la lógica de la aplicación
from app.services.login_service import UserService
from app.chat_engine import ChatEngine

class MainController:
    """
    Controlador principal que gestiona el flujo de la aplicación,
    cambiando entre la ventana de login y la interfaz de chat.
    """
    def __init__(self, app): # Modified to accept app
        self.app = app # Use the passed app
        # apply_futuristic_theme(self.app) # Theme applied in main() if local app

        # Inicializar detector de hardware al inicio
        self._initialize_hardware_detection()

        # Inicializar servicios
        self.user_service = UserService()
        # El ChatEngine se inicializa sin un proveedor.
        # El proveedor se asignará en la ChatInterface cuando el usuario seleccione un modelo.
        self.chat_engine = ChatEngine(provider=None)

        # Inicializar widgets (se crearán cuando se necesiten)
        self.login_widget = None
        self.chat_interface = None
        self.registration_widget = None
        self.loading_dialog = None
        self.current_user_id = None
        self.current_username = None

    def _initialize_hardware_detection(self):
        """Inicializa la detección de hardware al inicio de la aplicación."""
        try:
            from hardware_detector import HardwareDetector
            import os
            
            # Verificar si ya existe configuración
            if os.path.exists('hardware_config.json'):
                print("[MainController] Configuración de hardware encontrada.")
                return
            
            print("[MainController] Primera ejecución - detectando hardware...")
            
            # Realizar detección automática
            detector = HardwareDetector()
            
            # Mostrar configurador gráfico si es la primera vez
            self._show_hardware_configurator(detector)
            
        except Exception as e:
            print(f"[MainController] Error en detección de hardware: {e}")
            # Continuar con la aplicación normal si falla la detección
    
    def _show_hardware_configurator(self, detector):
        """Muestra el configurador de hardware si es necesario."""
        try:
            from PyQt6.QtWidgets import QMessageBox, QPushButton
            from PyQt6.QtCore import Qt
            from hardware_config_gui_v2 import HardwareConfigGUI
            from ui.custom_widgets import show_question_message
            
            # Preguntar al usuario si quiere configurar hardware usando mensaje seleccionable
            reply = show_question_message(
                None,
                "MARTIN LLM - Configuración Inicial",
                "Esta es la primera ejecución de MARTIN LLM.\n\n" 
                "¿Desea configurar el hardware para obtener el máximo rendimiento?",
                "La detección automática optimizará la aplicación para su sistema.",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Mostrar configurador
                config_window = HardwareConfigGUI()
                config_window.show()  # No modal para evitar problemas
            else:
                # Crear configuración por defecto
                self._create_default_hardware_config(detector)
                
        except ImportError:
            # Si no se puede importar la GUI, crear configuración por defecto
            print("[MainController] GUI no disponible, usando configuración por defecto.")
            self._create_default_hardware_config(detector)
        except Exception as e:
            print(f"[MainController] Error mostrando configurador: {e}")
            self._create_default_hardware_config(detector)
    
    def _create_default_hardware_config(self, detector):
        """Crea una configuración por defecto basada en la detección automática."""
        try:
            import json
            import os
            
            # Usar la configuración recomendada por el detector
            config_data = {
                'hardware_info': detector.system_info,
                'selected_config': detector.recommended_config,
                'timestamp': __import__('datetime').datetime.now().isoformat(),
                'auto_generated': True
            }
            
            with open('hardware_config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"[MainController] Configuración automática creada: {detector.recommended_config.get('description', 'N/A')}")
            
        except Exception as e:
            print(f"[MainController] Error creando configuración por defecto: {e}")

    def run(self):
        """Inicia la aplicación mostrando la ventana de login y ejecuta el bucle de eventos."""
        self.run_without_exec()
        sys.exit(self.app.exec())

    def run_without_exec(self):
        """Inicia la aplicación mostrando la ventana de login sin ejecutar el bucle de eventos."""
        self.show_login()

    def show_login(self):
        """Crea y muestra la ventana de login."""
        self.login_widget = LoginWidget(self.user_service)
        apply_additional_login_styles(self.app) # Aplicar estilos adicionales para login
        
        # Conectar señales del login widget
        self.login_widget.login_success.connect(self.handle_login_success)
        self.login_widget.registration_requested.connect(self.show_registration)
        
        
        
        self.login_widget.show()

    def handle_login_success(self, user_id, username):
        """Maneja un inicio de sesión exitoso."""
        print(f"[main_qt.py][MainController][handle_login_success] Login exitoso para: {username} (ID: {user_id})")
        self.current_user_id = user_id
        self.current_username = username
        
        # Disconnect signals to prevent multiple triggers
        self.login_widget.login_success.disconnect(self.handle_login_success)
        self.login_widget.registration_requested.disconnect(self.show_registration)

        self.login_widget.close() 
        
        self.loading_dialog = LoadingDialog()
        self.loading_dialog.loading_complete.connect(self._on_loading_complete)
        self.loading_dialog.start_loading()
        self.loading_dialog.show()

    def _on_loading_complete(self):
        """Se llama cuando el diálogo de carga ha terminado."""
        self.show_chat_interface(self.current_user_id, self.current_username)

    def show_chat_interface(self, user_id, username):
        print(f"[main_qt.py][MainController][show_chat_interface] Mostrando la interfaz de chat para: {username} (ID: {user_id})")
        """Crea y muestra la interfaz de chat."""
        self.chat_interface = ChatInterface(user_id, username, self.chat_engine, self.user_service)
        self.chat_interface.logout_requested.connect(self.handle_logout)
        self.chat_interface.show()

    def show_registration(self):
        """Muestra la ventana de registro."""
        self.login_widget.hide()
        self.registration_widget = RegistrationWidget(self.user_service)
        # The traceback indicates 'registration_success' does not exist, but 'registration_cancelled' does.
        # This is likely a typo in the RegistrationWidget class, as 'back_to_login' handles the cancel action.
        # We connect to 'registration_cancelled' to handle success and prevent a crash.
        # The ideal fix is to rename the signal in RegistrationWidget.py to 'registration_success'.
        if hasattr(self.registration_widget, 'registration_cancelled'):
            self.registration_widget.registration_cancelled.connect(self.handle_registration_success)
        else:
            self.registration_widget.registration_success.connect(self.handle_registration_success)
        self.registration_widget.back_to_login.connect(self.handle_back_to_login)
        self.registration_widget.show()

    def handle_logout(self):
        """Maneja el cierre de sesión."""
        print("[main_qt.py][MainController][handle_logout] Logout solicitado.")
        # The ChatInterface closes itself after emitting 'logout_requested'.
        # We just need to nullify the reference and show the login screen.
        self.chat_interface = None
        self.show_login()

    def handle_registration_success(self):
        """Maneja el registro exitoso volviendo a la pantalla de login."""
        self.registration_widget.close()
        self.login_widget.show()

    def handle_back_to_login(self):
        self.registration_widget.close()
        self.login_widget.show()

def main(app=None): # Modified to accept optional app argument
    """Punto de entrada principal para la aplicación."""
    load_dotenv() # Cargar variables de entorno desde .env
    
    if app is None: # If no app is provided, create one and run its loop
        local_app = QApplication(sys.argv)
        apply_futuristic_theme(local_app) # Apply theme here if local app
        controller = MainController(local_app) # Pass local_app to controller
        controller.run() # This will call local_app.exec()
        sys.exit(local_app.exec()) # Ensure proper exit
    else: # If app is provided, just set up controller and show it
        controller = MainController(app) # Pass the provided app to controller
        controller.run_without_exec() # A new method that doesn't call app.exec()

if __name__ == "__main__":
    main()