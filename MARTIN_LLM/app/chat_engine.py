# -*- coding: utf-8 -*-
# app/chat_engine.py

from datetime import datetime
from app.llm_providers import BaseLLMProvider
from bson.objectid import ObjectId

# Prompt del sistema por defecto
SYSTEM_PROMPT = """Eres Martin, un asistente de IA avanzado, útil y conciso. Tu objetivo es proporcionar respuestas claras y directas. Evita las disculpas, las introducciones innecesarias y el texto de relleno. Ve al grano y responde a la pregunta del usuario de la forma más eficiente posible."""

class ChatEngine:
    """
    Gestiona el estado de una conversación de chat, incluyendo el historial,
    el prompt del sistema y el proveedor de LLM.
    """
    def __init__(self, provider: BaseLLMProvider | None):
        """
        Inicializa el motor de chat.

        Args:
            provider (BaseLLMProvider | None): El proveedor de LLM que se utilizará. Puede ser None inicialmente.
        """
        # La comprobación de tipo estricta se modifica para permitir 'None'.
        # Se validará que el proveedor no sea None en los métodos que lo requieran.
        if provider is not None and not isinstance(provider, BaseLLMProvider):
            raise TypeError("El proveedor, si se proporciona, debe ser una instancia de BaseLLMProvider.")
        
        self.provider = provider
        self.conversation_id = None
        self.history = []
        self.system_prompt = SYSTEM_PROMPT
        self.title = "Nueva Conversación"

    def start_new(self):
        """Inicia una nueva conversación, reseteando el estado."""
        self.conversation_id = None
        self.history = []
        self.title = "Nueva Conversación"
        self.system_prompt = SYSTEM_PROMPT # Reset to default
        print("[ChatEngine] Nueva conversación iniciada.")

    def load_conversation(self, conversation_id, history, system_prompt):
        """Carga una conversación existente."""
        self.conversation_id = conversation_id
        self.history = history
        self.system_prompt = system_prompt
        print(f"[ChatEngine] Conversación {conversation_id} cargada.")

    def get_full_prompt(self):
        """Construye el prompt completo para enviar al LLM."""
        full_prompt = [{"role": "system", "content": self.system_prompt}] + self.history
        return full_prompt