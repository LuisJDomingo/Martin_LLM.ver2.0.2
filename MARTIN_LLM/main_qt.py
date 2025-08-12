# -*- coding: utf-8 -*-
# main_qt.py

import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QWidget
from PyQt6.QtGui import QIcon
from dotenv import load_dotenv

# --- Importación de la configuración centralizada ---
import config # Usamos la configuración establecida por run.py

# ANSI escape codes for colors
class Color:
    BLUE = '\033[94m'
    RESET = '\033[0m'
    YELLOW = '\033[93m'

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso.
    Esta versión está CORREGIDA para funcionar con cx_Freeze.
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return Path(os.path.join(base_path, relative_path))
# Cargar variables de entorno desde un archivo .env
# ¡Esto debe hacerse ANTES de importar cualquier módulo de la app que las necesite!
print("\n--- INICIALIZACIÓN DE ENTORNO ---")
import os
from datetime import datetime

def load_environment():
    """Carga las variables de entorno desde el archivo .env."""
    dotenv_path = resource_path('.env')
    print(f"Buscando archivo de configuración en: {dotenv_path.absolute()}")
    if dotenv_path.exists():
        print(f"{Color.BLUE}[main_qt.py] Archivo .env encontrado. Cargando variables...{Color.RESET}")
        load_dotenv(dotenv_path=dotenv_path)
        print(f"{Color.BLUE}[main_qt.py] Variables de entorno cargadas.{Color.RESET}")
    else:
        print(f"{Color.YELLOW}[AVISO] No se encontró el archivo .env en la ruta esperada.{Color.RESET}")
        print("La aplicación usará configuraciones por defecto (ej: base de datos local).")

# --- CARGA TEMPRANA DE VARIABLES DE ENTORNO ---
load_environment()

# --- IMPORTACIONES POST-ENTORNO ---
# Ahora que las variables están cargadas, podemos importar nuestros módulos de forma segura.
from app.chat_engine import ChatEngine
from app.llm_providers import BaseLLMProvider, LlamaCppProvider, OllamaProvider
from app.services.login_service import UserService
from ui.login_widget import LoginWidget
from ui.registration_widget import RegistrationWidget
from ui.chat_interface import ChatInterface
from ui.qt_styles import apply_futuristic_theme

class Logger:
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log = open(log_file_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

# Crear ruta al archivo log (con fecha/hora si quieres)
def setup_logging():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"martin_debug_{now}.log")
    logger = Logger(log_path)

    sys.stdout = logger
    sys.stderr = logger  # También errores no capturados
    return logger

class ApplicationController:
    def __init__(self, provider: BaseLLMProvider, app_icon=None):
        self.app_icon = app_icon
        self.login_window = None
        self.registration_window = None
        self.chat_window = None
        
        # --- 1. INICIALIZACIÓN DEL BACKEND ---
        # Se preparan los componentes principales una sola vez al inicio.
        # El proveedor ahora se recibe como argumento, no se crea aquí.
        self.provider = provider
        self.user_service = UserService() # <-- Servicio centralizado
        # Se asume que el proveedor es válido, la validación se hace antes de crear el controlador.
        self.chat_engine = ChatEngine(provider=self.provider)

    def shutdown(self):
        """Limpia los recursos del controlador, como el proveedor inicial."""
        print("[ApplicationController] Iniciando apagado...")
        if self.provider:
            self.provider.shutdown()
            self.provider = None

    def show_login(self):
        if self.chat_window:
            # The cleanup process in ChatInterface handles the closing dialog.
            # We just need to ensure the window is hidden and the reference is cleared.
            self.chat_window.hide()
            self.chat_window = None
        if self.registration_window:
            self.registration_window.close()
            self.registration_window = None

        # Pasamos el servicio de usuario al widget de login
        self.login_window = LoginWidget(user_service=self.user_service)
        if self.app_icon:
            self.login_window.setWindowIcon(self.app_icon)
        self.login_window.login_success.connect(self.show_chat)
        self.login_window.registration_requested.connect(self.show_registration)
        self.login_window.show()

    def show_registration(self):
        """Cierra la ventana de login y muestra la de registro."""
        if self.login_window:
            self.login_window.close()
            self.login_window = None

        self.registration_window = RegistrationWidget(user_service=self.user_service)
        if self.app_icon:
            self.registration_window.setWindowIcon(self.app_icon)

        # Conectar señales para volver al login después del registro
        self.registration_window.registration_complete.connect(self.show_login)
        self.registration_window.registration_cancelled.connect(self.show_login)
        self.registration_window.show()

    def show_chat(self, user_id, username):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        
        # Comprobar si el proveedor Y el motor de chat se cargaron correctamente
        if not self.chat_engine:
            print("No se puede iniciar el chat porque el proveedor de LLM no se cargó.")
            # Aquí deberías mostrar un error al usuario y quizás volver al login o cerrar.
            # Por ejemplo, con un QMessageBox.
            sys.exit(1) # Salir si no hay modelo, ya que la app no puede funcionar.
            return

        # Pasamos el ChatEngine y el UserService a la interfaz de chat.
        self.chat_window = ChatInterface(
            user_id=user_id, 
            username=username, 
            chat_engine=self.chat_engine, 
            user_service=self.user_service)
        if self.app_icon:
            self.chat_window.setWindowIcon(self.app_icon)
        self.chat_window.logout_requested.connect(self.show_login)
        # El controlador es responsable de mostrar la ventana.
        self.chat_window.show()

def initialize_ollama_provider():
    """
    Intenta inicializar y devolver el proveedor de Ollama.
    Asume que ya se ha verificado que Ollama es una opción viable.
    """
    from app.ollama_manager import OllamaManager
    
    print("[main_qt.py] Inicializando OllamaProvider...")
    ollama_manager = OllamaManager()
    local_ollama_models = ollama_manager.get_local_models()

    # Esta comprobación es una salvaguarda, pero la lógica principal está en el despachador.
    if not local_ollama_models:
        return None, "No se encontraron modelos locales en Ollama."

    # Usar el primer modelo disponible en Ollama
    first_model_name = local_ollama_models[0]['name']
    print(f"[main_qt.py] Usando el primer modelo de Ollama encontrado: {first_model_name}")
    try:
        provider = OllamaProvider(model_name=first_model_name)
        return provider, None
    except Exception as e:
        return None, f"Falló la inicialización de OllamaProvider con el modelo '{first_model_name}': {e}"

# --- COPIA Y REEMPLAZA TU FUNCIÓN ACTUAL CON ESTA ---

def initialize_local_provider(parent=None, app_icon=None):
    """
    Inicializa y devuelve el proveedor local Llama.cpp (GGUF).
    Esta versión está optimizada para funcionar en un entorno empaquetado (cx_Freeze).
    """
    print("[main_qt.py] Intentando inicializar LlamaCppProvider...")

    # 1. Determinar la ruta base (funciona en desarrollo y empaquetado)
    if getattr(sys, 'frozen', False):
        # Si es un .exe, la base es el directorio del ejecutable
        base_path = os.path.dirname(sys.executable)
    else:
        # Si es un script .py, la base es el directorio del script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"[main_qt.py] Directorio base de la aplicación detectado: {base_path}")

    # 2. Construir la ruta absoluta al modelo
    model_file_path = os.path.join(base_path, "models", "model.gguf")
    print(f"[main_qt.py] Ruta absoluta calculada para el modelo GGUF: {model_file_path}")

    # 3. Verificar si el modelo existe en la ruta esperada
    if not os.path.exists(model_file_path):
        print(f"[ERROR] No se encontró el modelo en la ruta por defecto: {model_file_path}")
        # (Tu lógica para buscar el archivo manualmente es buena, la mantenemos)
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("<b>Modelo Local no Encontrado</b>")
        msg_box.setInformativeText(
            f"El archivo 'model.gguf' no se encontró en la carpeta 'models'.\n\n"
            "¿Deseas buscar el archivo manualmente?"
        )
        msg_box.setWindowTitle("Seleccionar Modelo Local")
        if app_icon: msg_box.setWindowIcon(app_icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(parent, "Selecciona un archivo de modelo GGUF", "", "Modelos GGUF (*.gguf)")
            if file_path:
                model_file_path = file_path
            else:
                return None, "No se seleccionó ningún archivo. La aplicación no puede continuar."
        else:
            return None, "Se requiere un modelo local para continuar sin Ollama."

    # --- LA SOLUCIÓN CLAVE PARA [WinError 267] ---
    provider = None
    try:
        # Guardamos el directorio de trabajo actual
        cwd_original = os.getcwd()
        # Cambiamos al directorio donde está el .exe (o el script)
        # Esto asegura que Llama.cpp encuentre sus archivos .dll
        os.chdir(base_path)
        print(f"[main_qt.py] Directorio de trabajo cambiado temporalmente a: {base_path}")

        print(f"[main_qt.py] Cargando modelo GGUF desde: {model_file_path}")
        # Importante: LlamaCppProvider se crea DENTRO del bloque try
        provider = LlamaCppProvider(
            model_path=model_file_path,
            verbose=True  # Mantenemos verbose=True para depurar
        )
        print("[main_qt.py] Proveedor LlamaCppProvider creado exitosamente.")
        return provider, None

    except Exception as e:
        # Capturamos el error para mostrarlo de forma clara
        import traceback
        traceback.print_exc() # Imprime el error completo en el log
        error_message = f"No se pudo cargar el archivo de modelo GGUF '{os.path.basename(model_file_path)}'.\n\nCausa: {e}"
        return None, error_message

    finally:
        # Nos aseguramos de restaurar el directorio de trabajo original
        if 'cwd_original' in locals():
            os.chdir(cwd_original)
            print(f"[main_qt.py] Directorio de trabajo restaurado a: {cwd_original}")

def initialize_provider(parent=None, app_icon=None):
    """
    Determina el mejor proveedor disponible de forma inteligente.
    1. Intenta usar Ollama SI está en ejecución Y tiene modelos.
    2. Si no, recurre al modelo local GGUF.
    """
    print("\n--- CONFIGURACIÓN DEL PROVEEDOR LLM ---")
    
    # --- Lógica de Despacho (Prioridad Local) --- 
    # 1. Intentar inicializar el proveedor local GGUF primero.
    print("[main_qt.py] Decisión: Priorizando proveedor local (GGUF).")
    provider, error_message = initialize_local_provider(parent, app_icon)
    if provider:
        print("[main_qt.py] Proveedor local GGUF cargado exitosamente.")
        return provider, None
    
    print(f"[main_qt.py] Falló la carga del proveedor local: {error_message}. Intentando fallback a Ollama.")

    # 2. Si el proveedor local falla, intentar usar Ollama como fallback.
    from app.model_loader import verify_ollama_connection # Importación local para claridad
    from app.ollama_manager import OllamaManager

    ollama_ok, _ = verify_ollama_connection()
    if ollama_ok:
        ollama_manager = OllamaManager()
        if ollama_manager.get_local_models():
            print("[main_qt.py] Decisión: Ollama es viable. Intentando inicializar.")
            provider_ollama, error_ollama = initialize_ollama_provider()
            if provider_ollama:
                return provider_ollama, None
    
    # 3. Si ambos fallan, devolver el error del proveedor local.
    print("[main_qt.py] Fallback a Ollama no fue posible. No se pudo inicializar ningún proveedor.")
    return None, error_message

def show_critical_error(app_icon, title, text, informative_text):
    """Muestra un cuadro de diálogo de error crítico y sale de la aplicación."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText(f"<b>{title}</b>")
    msg_box.setInformativeText(informative_text)
    msg_box.setWindowTitle("Error de Inicialización")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if app_icon:
        msg_box.setWindowIcon(app_icon)
    msg_box.exec()
    sys.exit(1)

def main():
    """Función principal que inicializa y ejecuta la aplicación."""
    print("[main_qt.py][main()] Función principal que inicializa y ejecuta la aplicación. ")
    import socket    
    # --- Comprobación de instancia única (mejorada) ---
    # El socket debe mantenerse en una variable para mantener el bloqueo del puerto.
    # Si bind() falla, otra instancia se está ejecutando.
    lock_socket = socket.socket()
    print("[main_qt.py][main()] Comprobando si hay otra instancia en ejecucion...")
    try:
        lock_socket.bind(("localhost", 65432))
    except OSError:
        print("Otra instancia ya se está ejecutando.")
        # Una app con GUI podría mostrar un QMessageBox aquí, pero como QApplication
        # aún no está inicializado, simplemente salimos.
        sys.exit(0)
    # --- Inicialización de la Aplicación ---
    # Este código se mueve fuera del bloque condicional para que siempre se ejecute.
    print("[main_qt.py][main()] Iniciando la aplicación...]")
    app = QApplication(sys.argv)
    print("[main_qt.py][main()] Aplicación inicializada.")
    app_icon = None
    icon_path = resource_path('ui/assets/app_icon.ico')
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
        print("[main_qt.py][main()] Icono de la aplicación cargado.")
    else:
        print(f"ADVERTENCIA: No se encontró el icono de la aplicación en {icon_path}")

    from ui.qt_styles import apply_futuristic_theme
    apply_futuristic_theme(app)

    # --- LÓGICA DE INICIALIZACIÓN HÍBRIDA ---
    # 1. Inicializar el mejor proveedor disponible (Ollama o GGUF).
    print("[main_qt.py][main()] Iniciando proveedor de Ollama...")
    provider, error_message = initialize_provider(parent=None, app_icon=app_icon)

    if not provider:
        show_critical_error(
            app_icon, "Error Crítico al Iniciar",
            "No se pudo cargar ningún modelo de lenguaje (LLM).",
            error_message or "Ocurrió un error desconocido."
        )
        return 1

    # 2. Si el proveedor es válido, crear el controlador y ejecutar la aplicación.
    controller = ApplicationController(provider=provider, app_icon=app_icon)
    try:
        controller.show_login()
        return app.exec()
    finally:
        controller.shutdown()

if __name__ == "__main__":
    logger = setup_logging()
    print("🚀 Iniciando Martin LLM...")
    exit_code = 0
    try:
        # Llamar a la función principal que contiene toda la lógica de la aplicación.
        exit_code = main()
    except Exception as e:
        print(f"💥 Excepción no controlada en el nivel más alto: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1  # Indicar un error
    finally:
        logger.close()
        print(f"🛑 Martin LLM cerrado. Código de salida: {exit_code}")
        sys.exit(exit_code)