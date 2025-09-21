import sys
from pathlib import Path
import os
from datetime import datetime
from typing import Optional, List, Dict
import sqlite3
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from datetime import datetime


sys.path.append(str(Path(__file__).parent.parent.parent))

from config.db_config import (
    MONGODB_URI,
    DB_NAME,
    COLLECTION_CONVERSATIONS,
    COLLECTION_MESSAGES,
    DB_PATH
)
from app.database.models import Conversation, Message


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.conversations = None
        self.messages = None
        self._initialize_db()

    def _initialize_db(self):
        """Inicializa la conexión a MongoDB o crea SQLite como respaldo"""
        # Conectar a MongoDB Atlas solo si el usuario es colaborador.
        if user_consent == 'collaborator':
            try:
                self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
                self.client.server_info()  # Forzar la conexión para verificar
                self.db = self.client[DB_NAME]
                self.conversations = self.db[COLLECTION_CONVERSATIONS]
                self.messages = self.db[COLLECTION_MESSAGES]
                print("[DEBUG] Conexión a MongoDB exitosa.")
            except Exception as e:
                print(f"❌ Error de conexión a MongoDB: {e}")
                # Aquí podrías implementar la lógica de respaldo si es necesario
                self.client = None
                self.db = None
                self.conversations = None
                self.messages = None


    def create_conversation(self, model: str, title: Optional[str] = None) -> str:
        """Crea una nueva conversación"""
        conversation = Conversation(model=model, title=title)

        if self.client:
            result = self.conversations.insert_one(conversation.to_dict())
            return str(result.inserted_id)

    def add_message(self, conversation_id: str, content: str, role: str, context: List = None):
        print(f"\t\t[DEBUG] ADD_MESSAGE en DB_MANAGER/DataBaseManager\n\t\tAñadiendo mensaje a la conversación {conversation_id}")
        """Añade un mensaje a una conversación"""
        message = Message(
            content=content,
            role=role,
            conversation_id=conversation_id,
            context=context
        )
        print(f"\t\t[DEBUG] Mensaje a añadir: {message.to_dict()}")

        if self.client:
            self.messages.insert_one({
                "conversation_id": conversation_id,
                "content": content,
                "role": role,
                "context": context or [],
                "timestamp": datetime.utcnow()
            })
            print(f"\t\t[DEBUG] Mensaje añadido a MongoDB")

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Obtiene una conversación y sus mensajes"""
        if self.client:
            try:
                # Intenta convertir a ObjectId si es posible y buscar por _id
                object_id = ObjectId(conversation_id)
                conversation = self.conversations.find_one({'_id': object_id})
                # print(f"DEBUG - Conversacion encontrada: {conversation}")
            except Exception as e:
                print(f"DEBUG - Error convirtiendo conversation_id a ObjectId: {e}")
                return None

            if conversation:
                # Si el documento ya tiene el array 'messages', úsalo directamente
                if 'messages' in conversation and conversation['messages']:
                    return conversation
                else:
                    # Si no tiene el array, busca en la colección messages (por compatibilidad)
                    messages = list(self.messages.find(
                        {'conversation_id': conversation_id},
                        sort=[('timestamp', 1)]
                    ))
                    conversation['messages'] = messages
                    return conversation

    def list_conversations(self, limit: int = 10) -> List[Dict]:
        """Lista las conversaciones más recientes"""
        if self.client:
            return list(
                self.conversations.find()
                .sort('timestamp', -1)
                .limit(limit)
            )
        else:
            # Usar SQLite
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?',
                    (limit,)
                )
                return [
                    {
                        'id': row[0],
                        'model': row[1],
                        'title': row[2],
                        'timestamp': row[3]
                    }
                    for row in cursor.fetchall()
                ]
            
    def update_conversation_title(self, conversation_id: str, title: str):
        print(f"DEBUG - Actualizando título de conversación: {conversation_id} a {title}")
        """Actualiza el título de una conversación existente"""
        if self.client:
            try:
                self.conversations.update_one(
                    {'_id': ObjectId(conversation_id)},
                    {'$set': {'title': title}}
                )
                print(f"DEBUG - Título actualizado en MongoDB: {title}")
            except Exception as e:
                print(f"ERROR - No se pudo actualizar el título en MongoDB: {e}")

