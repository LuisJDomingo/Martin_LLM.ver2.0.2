# TESTS/test_chat_interface.py
import pytest
from unittest.mock import MagicMock, patch

# Intenta importar pytest-qt. Si no está, falla con un mensaje útil.
try:
    from pytestqt.qtbot import QtBot
except ImportError:
    pytest.fail(
        "El paquete 'pytest-qt' es necesario para ejecutar estas pruebas. \n"
        "Por favor, instálalo ejecutando: pip install pytest-qt"
    )

# Importa las clases necesarias de tu aplicación.
# Asegúrate de que los paths son correctos según tu estructura.
from MARTIN_LLM.ui.chat_interface import ChatInterface
from MARTIN_LLM.app.chat_engine import ChatEngine
from MARTIN_LLM.app.services.login_service import UserService

# --- Fixtures de Prueba ---
# Las fixtures son funciones que preparan el entorno para las pruebas.

@pytest.fixture
def mock_chat_engine(monkeypatch):
    """Crea un mock del ChatEngine para no depender de la lógica real del modelo."""
    mock = MagicMock(spec=ChatEngine)
    mock.provider = None
    mock.history = []
    mock.conversation_id = None
    return mock

@pytest.fixture
def mock_user_service(monkeypatch):
    """Crea un mock del UserService para no interactuar con la base de datos."""
    mock = MagicMock(spec=UserService)
    mock.get_user_conversations.return_value = []
    mock.is_first_login.return_value = True
    return mock

@pytest.fixture
def chat_interface_widget(qtbot: QtBot, mock_chat_engine, mock_user_service):
    """
    Crea una instancia del widget ChatInterface para ser usada en las pruebas.
    Esta es la fixture principal que prepara el componente a probar.
    """
    # Datos de usuario falsos para la prueba
    test_user_id = "test_user_id"
    test_username = "test_user"

    # Crea la instancia del widget
    widget = ChatInterface(
        user_id=test_user_id,
        username=test_username,
        chat_engine=mock_chat_engine,
        user_service=mock_user_service
    )
    
    # Registra el widget con qtbot para que lo gestione
    qtbot.addWidget(widget)
    
    yield widget
    
    # Código de limpieza después de la prueba (si es necesario)
    widget.close()

# --- Pruebas de QA para ChatInterface ---

def test_chat_interface_creation(chat_interface_widget: ChatInterface):
    """
    Prueba 1 (Smoke Test): Verifica que la ventana de chat se crea correctamente.
    
    Objetivo: Asegurar que la interfaz se puede instanciar sin errores y es visible.
    """
    print("Ejecutando: test_chat_interface_creation")
    assert chat_interface_widget is not None, "El widget ChatInterface no debería ser None."
    assert chat_interface_widget.isVisible(), "El widget ChatInterface debería estar visible después de crearse."
    print("Completado: test_chat_interface_creation - Éxito")

def test_initial_ui_state(chat_interface_widget: ChatInterface):
    """
    Prueba 2: Verifica el estado inicial de los componentes clave de la UI.

    Objetivo: Asegurar que los elementos importantes están presentes y en su estado esperado
              cuando la aplicación se inicia.
    """
    print("Ejecutando: test_initial_ui_state")
    # El campo de texto para el prompt debe existir y estar vacío
    assert chat_interface_widget.input_text is not None, "El campo de texto de entrada (input_text) debe existir."
    assert chat_interface_widget.input_text.toPlainText() == "", "El campo de texto de entrada debe estar vacío al inicio."

    # El botón de enviar debe existir y estar habilitado
    assert chat_interface_widget.send_button is not None, "El botón de enviar (send_button) debe existir."
    assert chat_interface_widget.send_button.isEnabled(), "El botón de enviar debe estar habilitado al inicio."

    # El selector de modo debe existir y estar en modo "Chat" por defecto
    assert chat_interface_widget.mode_selector is not None, "El selector de modo debe existir."
    assert chat_interface_widget.mode_selector.currentData() == "chat", "El modo por defecto debe ser 'chat'."
    print("Completado: test_initial_ui_state - Éxito")

def test_send_message_without_model_selected(chat_interface_widget: ChatInterface, qtbot: QtBot):
    """
    Prueba 3: Simula el envío de un mensaje sin un modelo seleccionado.

    Objetivo: Verificar que la aplicación muestra una advertencia si el usuario intenta
              enviar un mensaje sin haber seleccionado un modelo primero.
    """
    print("Ejecutando: test_send_message_without_model_selected")
    # Mock para QMessageBox para que no bloquee la prueba
    with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
        # Escribir texto en el input
        chat_interface_widget.input_text.setPlainText("Hola mundo")
        
        # Simular clic en el botón de enviar
        qtbot.mouseClick(chat_interface_widget.send_button, qtbot.button_map['left'])

        # Verificar que se llamó a la advertencia
        mock_warning.assert_called_once()
        # Verificar que el mensaje de advertencia es el esperado
        args, _ = mock_warning.call_args
        assert "Por favor, selecciona un modelo" in args[1]
    
    print("Completado: test_send_message_without_model_selected - Éxito")

# Para ejecutar estas pruebas:
# 1. Asegúrate de tener pytest y pytest-qt instalados:
#    pip install pytest pytest-qt
# 2. Navega al directorio raíz de tu proyecto en la terminal.
# 3. Ejecuta pytest:
#    pytest MARTIN_LLM/TESTS/test_chat_interface.py
