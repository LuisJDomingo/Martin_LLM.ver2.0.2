from typing import List, Dict
from datetime import datetime
import uuid

from app.llm_providers import BaseLLMProvider

# System prompt por defecto
SYSTEM_PROMPT = (
    "Eres ChatLuisGPT, un asistente experto, amigable y directo, "
    "que ayuda al usuario a resolver problemas de programación, automatización y uso general del PC. "
    "Sé claro, conciso y no des rodeos innecesarios."
)

# Modelo por defecto que se intentará descargar si no hay ninguno disponible en Ollama.
DEFAULT_OLLAMA_MODEL = "llama3:8b"


class ChatEngine:
    """
    Clase para gestionar el estado en memoria de una conversación.
    Es agnóstica al proveedor del modelo y a la capa de persistencia.
    """
    def __init__(self, provider: BaseLLMProvider):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("El proveedor debe ser una instancia de BaseLLMProvider.")
        
        self.provider = provider
        # El ID y el historial son gestionados por la capa de UI a través de servicios.
        # Se inicializan aquí para una nueva conversación.
        self.conversation_id: str | None = None
        self.system_prompt: str = SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.start_new() # Iniciar con un ID y estado limpios.

    def start_new(self):
        """
        Inicia una nueva conversación en memoria, reseteando el historial y el ID.
        """
        self.conversation_id = None
        self.history = []
        print(f"[ChatEngine] Nueva conversación iniciada (sin ID persistente)...")

    def load_conversation(self, conversation_id: str, history: List[Dict[str, str]], system_prompt: str):
        """
        Carga el estado de una conversación existente.
        Este método es llamado por la capa de UI.
        """
        self.conversation_id = conversation_id
        self.history = history
        self.system_prompt = system_prompt
        print(f"[ChatEngine] Conversación {conversation_id[:8]} cargada en memoria.")

    def ask(self, user_message: str) -> str:
        """
        Procesa un mensaje del usuario, obtiene una respuesta del proveedor
        y actualiza el historial en memoria. La persistencia es manejada por la UI.
        """
        # El historial ahora se gestiona en la UI.
        # Preparamos los mensajes para el proveedor, incluyendo el historial actual y el nuevo mensaje.
        current_history = self.history.copy()
        current_history.append({"role": "user", "content": user_message})

        # Preparar el historial completo para el proveedor, incluyendo el system prompt
        messages_for_provider = [{"role": "system", "content": self.system_prompt}] + current_history

        try:
            response_text = self.provider.query(messages=messages_for_provider)
        except Exception as e:
            print(f"[ChatEngine] Error al consultar al proveedor: {e}")
            response_text = f"Se produjo un error en el motor de chat: {e}"
        
        return response_text
