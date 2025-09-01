# -*- coding: utf-8 -*-
# app/services/local_persistence_service.py

import os
import uuid
from datetime import datetime
from pathlib import Path
from tinydb import TinyDB, Query

class LocalPersistenceService:
    """
    Servicio para gestionar la persistencia de conversaciones en una base de datos
    local (TinyDB) para usuarios que no consienten compartir sus datos.
    """
    def __init__(self, username: str):
        """
        Inicializa el servicio de persistencia local.

        Args:
            username (str): El nombre del usuario para crear un archivo de DB único.
        """
        storage_path = Path("data/local_storage")
        storage_path.mkdir(parents=True, exist_ok=True)
        
        db_file = storage_path / f"{username}.json"
        self.db = TinyDB(db_file, indent=4, ensure_ascii=False)
        self.conversations = self.db.table('conversations')
        print(f"✅ Servicio de persistencia local inicializado para '{username}' en: {db_file}")

    def get_conversation(self, user_id: str, conversation_id: str) -> dict | None:
        """Obtiene una conversación específica por su ID."""
        Conversation = Query()
        result = self.conversations.search(Conversation._id == conversation_id)
        return result[0] if result else None

    def create_conversation(self, user_id: str, conv_data: dict) -> str:
        """Crea una nueva conversación."""
        # Generamos un ID único para la conversación, similar a como lo haría Mongo
        conv_id = str(uuid.uuid4())
        conv_data['_id'] = conv_id
        
        # Asegurarnos de que el timestamp es un string para la serialización JSON
        if isinstance(conv_data.get('timestamp'), datetime):
            conv_data['timestamp'] = conv_data['timestamp'].isoformat()

        self.conversations.insert(conv_data)
        return conv_id

    def update_conversation(self, user_id: str, conversation_id: str, update_data: dict):
        """Actualiza una conversación existente."""
        Conversation = Query()
        
        # Asegurarnos de que el timestamp es un string
        if isinstance(update_data.get('timestamp'), datetime):
            update_data['timestamp'] = update_data['timestamp'].isoformat()

        self.conversations.update(update_data, Conversation._id == conversation_id)

    def update_conversation_title(self, user_id: str, conversation_id: str, new_title: str) -> bool:
        """Actualiza solo el título de una conversación."""
        Conversation = Query()
        update_data = {
            "title": new_title,
            "timestamp": datetime.now().isoformat()
        }
        result = self.conversations.update(update_data, Conversation._id == conversation_id)
        return len(result) > 0

    def delete_or_archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Elimina una conversación de la base de datos local."""
        Conversation = Query()
        result = self.conversations.remove(Conversation._id == conversation_id)
        print(f"[LocalPersistence] Conversación {conversation_id} eliminada.")
        return len(result) > 0

    def get_user_conversations(self, user_id: str, limit: int = 0):
        """Obtiene todas las conversaciones del usuario, ordenadas por fecha."""
        all_convs = self.conversations.all()
        
        # Convertir timestamps de string a datetime para ordenar
        for conv in all_convs:
            ts_str = conv.get('timestamp')
            if isinstance(ts_str, str):
                try:
                    conv['timestamp_dt'] = datetime.fromisoformat(ts_str)
                except ValueError:
                    conv['timestamp_dt'] = datetime.min
            else:
                conv['timestamp_dt'] = datetime.min

        # Ordenar por el objeto datetime
        sorted_convs = sorted(all_convs, key=lambda x: x['timestamp_dt'], reverse=True)

        # Limpiar el campo temporal
        for conv in sorted_convs:
            del conv['timestamp_dt']

        if limit > 0:
            return sorted_convs[:limit]
        
        return sorted_convs

    def get_conversation_details(self, conversation_id: str):
        """Obtiene todos los detalles de una conversación, incluyendo mensajes."""
        Conversation = Query()
        result = self.conversations.search(Conversation._id == conversation_id)
        return result[0] if result else None

    def get_user_consent(self, user_id: str) -> bool:
        """Para compatibilidad de interfaz, este servicio siempre implica no consentimiento."""
        return False