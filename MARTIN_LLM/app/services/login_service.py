# -*- coding: utf-8 -*-
# app/services/login_service.py

import os
import uuid
import bcrypt
from pymongo import MongoClient, DESCENDING
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime
from bson import ObjectId

# Importar la utilidad de rutas desde la raíz del proyecto.
from paths import get_remember_me_path

class UserService:
    """
    Servicio centralizado para gestionar la lógica de usuarios, autenticación,
    y persistencia de conversaciones en MongoDB.
    """
    def __init__(self):
        try:
            # Cargar configuración desde variables de entorno
            connection_string = os.environ.get('MONGO_CONNECTION_STRING')
            db_name = os.environ.get('DB_NAME', 'martin_llm')
            secret_key_str = os.environ.get('SECRET_KEY')

            if not connection_string:
                print("⚠️ ADVERTENCIA: No se encontró la variable de entorno 'MONGO_CONNECTION_STRING'. Usando base de datos local por defecto.")
                connection_string = "mongodb://localhost:27017/"

            print(f"[DEBUG] Conectando a la base de datos: {connection_string.split('@')[-1].split('/')[0]}")
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Forzar conexión para verificarla inmediatamente
            self.client.server_info()
            self.db = self.client[db_name]
            self.users = self.db['users']
            self.conversations = self.db['conversations']
            print("✅ Conexión a MongoDB exitosa.")

        except Exception as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            print("⚠️ El historial de chat y la autenticación no funcionarán. La app funcionará en modo sin persistencia.")
            self.db = None # Marcar la DB como no disponible

        # Configuración de encriptación para "Recordarme"
        try:
            if not secret_key_str:
                raise ValueError("'SECRET_KEY' no configurada en .env.")
            # Fernet requiere una clave de 32 bytes codificada en base64
            secret_key = secret_key_str.encode()
            self.fernet = Fernet(secret_key)
        except (ValueError, TypeError) as e:
            print(f"❌ ERROR DE SEGURIDAD: La 'SECRET_KEY' en .env no es válida. {e}")
            print('⚠️ La función \'Recordarme\' no será segura. Genera una nueva clave con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
            self.fernet = None

    def _hash_password(self, password: str) -> bytes:
        """Genera un hash de la contraseña."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _verify_password(self, password: str, hashed_password: bytes) -> bool:
        """Verifica una contraseña contra su hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def register_user(self, username, password, email, share_data):
        """Registra un nuevo usuario en la base de datos."""
        if self.db is None: return None
        if self.users.find_one({"username_lower": username.lower()}):
            return None  # Usuario ya existe
        
        hashed_password = self._hash_password(password)
        user_data = {
            "username": username,
            "username_lower": username.lower(),
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "share_data_consent": share_data
        }
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)

    def authenticate_user(self, username, password):
        """Autentica un usuario y devuelve su ID y nombre si es exitoso."""
        if self.db is None: return None
        user = self.users.find_one({"username_lower": username.lower()})
        if user and self._verify_password(password, user['password']):
            return str(user['_id']), user['username']
        return None

    def remember_user(self, username, password):
        """Encripta y guarda las credenciales del usuario."""
        if not self.fernet: return
        try:
            credentials = f"{username}::{password}".encode('utf-8')
            encrypted_credentials = self.fernet.encrypt(credentials)
            with open(get_remember_me_path(), "wb") as f:
                f.write(encrypted_credentials)
        except Exception as e:
            print(f"Error al guardar credenciales: {e}")

    def get_remembered_user(self):
        """Desencripta y devuelve las credenciales guardadas."""
        if not self.fernet: return None, None
        try:
            path = get_remember_me_path()
            if not path.exists(): return None, None
            
            with open(path, "rb") as f:
                encrypted_credentials = f.read()
            
            decrypted_credentials = self.fernet.decrypt(encrypted_credentials).decode('utf-8')
            username, password = decrypted_credentials.split("::", 1)
            return username, password
        except InvalidToken:
            print("Error: No se pudo desencriptar la contraseña guardada. El archivo puede estar corrupto o la clave ha cambiado.")
            self.forget_user() # Limpiar archivo corrupto
            return None, None
        except Exception as e:
            print(f"Error al cargar credenciales: {e}")
            return None, None

    def forget_user(self):
        """Elimina el archivo de credenciales guardadas."""
        path = get_remember_me_path()
        if path.exists():
            os.remove(path)

    # --- Métodos de gestión de conversaciones ---

    def get_conversation(self, user_id: str, conversation_id: str) -> dict | None:
        """Obtiene una conversación específica por su ID, verificando que pertenezca al usuario."""
        if self.db is None: return None
        try:
            return self.conversations.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
        except Exception as e:
            print(f"[UserService] Error al obtener la conversación {conversation_id}: {e}")
            return None

    def create_conversation(self, user_id: str, conv_data: dict) -> str:
        """Crea una nueva conversación para un usuario con los datos proporcionados."""
        if self.db is None: return str(uuid.uuid4())
        conv_data['user_id'] = user_id # Asegurarse de que el user_id está en los datos
        result = self.conversations.insert_one(conv_data)
        return str(result.inserted_id)

    def update_conversation(self, user_id: str, conversation_id: str, update_data: dict):
        """Actualiza una conversación existente."""
        if self.db is None: return
        try:
            self.conversations.update_one(
                {"_id": ObjectId(conversation_id), "user_id": user_id},
                {"$set": update_data}
            )
        except Exception as e:
            print(f"Error al actualizar la conversación {conversation_id}: {e}")

    def delete_or_archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Elimina una conversación de la base de datos."""
        if self.db is None: return False
        try:
            result = self.conversations.delete_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
            print("[UserService] conversacion eliminada con éxito")
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar la conversación {conversation_id}: {e}")
            return False

    def get_user_conversations(self, user_id: str, limit: int = 0):
        """
        Obtiene las conversaciones de un usuario, ordenadas por fecha.
        Acepta un límite opcional para obtener solo las más recientes.
        """
        if self.db is None: return []
        # Ordenar por timestamp descendente para obtener las más recientes primero
        query = self.conversations.find(
            {"user_id": user_id},
            {"messages": 0} # Excluir el campo de mensajes para que la carga sea más rápida
        ).sort("timestamp", DESCENDING)

        if limit > 0:
            query = query.limit(limit)
            
        return list(query)

    def get_conversation_details(self, conversation_id: str):
        """Obtiene todos los detalles de una conversación, incluyendo mensajes."""
        if self.db is None: return None
        try:
            return self.conversations.find_one({"_id": ObjectId(conversation_id)})
        except Exception as e:
            print(f"Error al obtener detalles de la conversación {conversation_id}: {e}")
            return None