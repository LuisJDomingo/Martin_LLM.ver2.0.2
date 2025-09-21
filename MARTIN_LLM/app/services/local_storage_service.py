# -*- coding: utf-8 -*-
# app/services/local_storage_service.py

import os
import json
import uuid
from datetime import datetime

# Obtener la ruta base del proyecto de una manera más robusta
try:
    from paths import get_project_root
    BASE_DIR = get_project_root()
except ImportError:
    # Fallback si paths.py no está disponible o es llamado desde un contexto extraño
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LOCAL_STORAGE_PATH = os.path.join(BASE_DIR, "data", "local_storage")

class LocalStorageService:
    """
    Gestiona el almacenamiento y recuperación de conversaciones en el sistema de archivos local.
    """
    def __init__(self):
        print("[LocalStorageService] __init__: Inicializando servicio de almacenamiento local.")
        os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

    def _get_user_storage_path(self, user_id: str) -> str:
        """Devuelve la ruta de la carpeta de almacenamiento para un usuario específico."""
        path = os.path.join(LOCAL_STORAGE_PATH, str(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    def create_conversation(self, user_id: str, conv_data: dict) -> str:
        """
        Crea un nuevo archivo JSON para una conversación y devuelve su ID.
        """
        print(f"[LocalStorageService] create_conversation: Creando nueva conversación local para usuario '{user_id}'.")
        user_path = self._get_user_storage_path(user_id)
        conversation_id = str(uuid.uuid4())
        file_path = os.path.join(user_path, f"{conversation_id}.json")

        # Añadir metadatos importantes a la conversación
        conv_data['_id'] = conversation_id
        conv_data['user_id'] = user_id
        conv_data['timestamp'] = datetime.utcnow().isoformat()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conv_data, f, indent=4, ensure_ascii=False)
            print(f"[LocalStorageService] create_conversation: Conversación local creada en: {file_path}")
            return conversation_id
        except IOError as e:
            print(f"[LocalStorageService] create_conversation: ❌ Error al escribir el archivo de conversación: {e}")
            return None

    def get_user_conversations(self, user_id: str, limit: int = 0) -> list:
        """
        Obtiene una lista de todas las conversaciones de un usuario desde el almacenamiento local.
        """
        print(f"[LocalStorageService] get_user_conversations: Obteniendo conversaciones locales para '{user_id}'.")
        user_path = self._get_user_storage_path(user_id)
        conversations = []
        try:
            files = [f for f in os.listdir(user_path) if f.endswith('.json')]
            
            # Ordenar archivos por fecha de modificación (más recientes primero)
            files.sort(key=lambda f: os.path.getmtime(os.path.join(user_path, f)), reverse=True)

            for file_name in files:
                file_path = os.path.join(user_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                    # Cargar solo metadatos, no los mensajes completos para eficiencia
                    conversations.append({
                        "_id": conv.get("_id"),
                        "title": conv.get("title", "Sin Título"),
                        "timestamp": conv.get("timestamp")
                    })
            
            if limit > 0:
                return conversations[:limit]
            return conversations
        except (IOError, json.JSONDecodeError) as e:
            print(f"[LocalStorageService] get_user_conversations: ❌ Error al leer conversaciones: {e}")
            return []

    def get_conversation_details(self, user_id: str, conversation_id: str) -> dict | None:
        """
        Obtiene los detalles completos de una conversación específica.
        """
        print(f"[LocalStorageService] get_conversation_details: Obteniendo detalles de '{conversation_id}'.")
        user_path = self._get_user_storage_path(user_id)
        file_path = os.path.join(user_path, f"{conversation_id}.json")

        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"[LocalStorageService] get_conversation_details: ❌ Error al leer el archivo: {e}")
            return None

    def update_conversation(self, user_id: str, conversation_id: str, update_data: dict):
        """
        Actualiza una conversación existente en el almacenamiento local.
        """
        print(f"[LocalStorageService] update_conversation: Actualizando '{conversation_id}'.")
        user_path = self._get_user_storage_path(user_id)
        file_path = os.path.join(user_path, f"{conversation_id}.json")

        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r+', encoding='utf-8') as f:
                conv = json.load(f)
                conv.update(update_data)
                # Actualizar timestamp en cada modificación
                conv['timestamp'] = datetime.utcnow().isoformat()
                f.seek(0)
                json.dump(conv, f, indent=4, ensure_ascii=False)
                f.truncate()
            return True
        except (IOError, json.JSONDecodeError) as e:
            print(f"[LocalStorageService] update_conversation: ❌ Error al actualizar: {e}")
            return False

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        Elimina un archivo de conversación.
        """
        print(f"[LocalStorageService] delete_conversation: Eliminando '{conversation_id}'.")
        user_path = self._get_user_storage_path(user_id)
        file_path = os.path.join(user_path, f"{conversation_id}.json")

        if not os.path.exists(file_path):
            return False
            
        try:
            os.remove(file_path)
            print(f"[LocalStorageService] delete_conversation: Conversación '{conversation_id}' eliminada.")
            return True
        except IOError as e:
            print(f"[LocalStorageService] delete_conversation: ❌ Error al eliminar: {e}")
            return False
