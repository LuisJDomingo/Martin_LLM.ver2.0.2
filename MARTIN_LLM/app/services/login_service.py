# -*- coding: utf-8 -*-
# app/services/login_service.py (Versión Mejorada)

import os
import uuid
import bcrypt
from pymongo import MongoClient, DESCENDING
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
import re

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
            connection_string = os.environ.get('MONGODB_URI')
            db_name = os.environ.get('DB_NAME', 'martin_llm')
            secret_key_str = os.environ.get('SECRET_KEY')

            if not connection_string:
                print("⚠️ ADVERTENCIA: No se encontró la variable de entorno 'MONGODB_URI'. Usando base de datos local por defecto.")
                connection_string = "mongodb://localhost:27017/"

            print(f"[DEBUG] Conectando a la base de datos: {connection_string.split('@')[-1].split('/')[0]}")
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Forzar conexión para verificarla inmediatamente
            self.client.server_info()
            self.db = self.client[db_name]
            self.users = self.db['users']
            self.conversations = self.db['conversations']
            self.password_resets = self.db['password_resets']  # Nueva colección para tokens de recuperación
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

    def _validate_email(self, email: str) -> bool:
        """Valida el formato de un email."""
        if not email:
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def register_user(self, username, password, email, share_data):
        """Registra un nuevo usuario en la base de datos."""
        if self.db is None: 
            return None
            
        if self.users.find_one({"username_lower": username.lower()}):
            return None  # Usuario ya existe
        
        # Validar email si se proporciona
        if email and not self._validate_email(email):
            raise ValueError("Formato de email inválido")
        
        hashed_password = self._hash_password(password)
        user_data = {
            "username": username,
            "username_lower": username.lower(),
            "email": email if email else None,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "share_data_consent": share_data
        }
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)

    def authenticate_user(self, username, password):
        """Autentica un usuario y devuelve su ID y nombre si es exitoso."""
        if self.db is None: 
            return None
            
        user = self.users.find_one({"username_lower": username.lower()})
        if user and self._verify_password(password, user['password']):
            return str(user['_id']), user['username']
        return None

    def _send_reset_email(self, to_email: str, username: str, reset_token: str):
            """Envía un correo real con el enlace de recuperación de contraseña."""
            try:
                smtp_host = os.environ.get("SMTP_HOST", "smtp-relay.brevo.com")
                smtp_port = int(os.environ.get("SMTP_PORT", 587))
                smtp_user = os.environ.get("SMTP_USER")  # normalmente tu email de Brevo
                smtp_pass = os.environ.get("SMTP_PASS")  # la API Key de Brevo

                if not smtp_user or not smtp_pass:
                    print("⚠️ No se configuraron credenciales SMTP. No se envió email.")
                    return False

                reset_link = f"https://tuapp.com/reset-password?token={reset_token}"

                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Restablecimiento de contraseña"
                msg["From"] = smtp_user
                msg["To"] = to_email

                text = f"Hola {username},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{reset_link}\n\nEste enlace caduca en 24 horas."
                html = f"""
                <html>
                <body>
                    <p>Hola <b>{username}</b>,<br><br>
                    Haz clic en el siguiente enlace para restablecer tu contraseña:<br>
                    <a href="{reset_link}">{reset_link}</a><br><br>
                    Este enlace caduca en 24 horas.
                    </p>
                </body>
                </html>
                """

                msg.attach(MIMEText(text, "plain"))
                msg.attach(MIMEText(html, "html"))

                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(msg["From"], [to_email], msg.as_string())

                print(f"✅ Correo de restablecimiento enviado a {to_email}")
                return True

            except Exception as e:
                print(f"❌ Error al enviar correo: {e}")
                return False
    def request_password_reset(self, username: str, email: str) -> bool:
        """
        Solicita un restablecimiento de contraseña.
        En una implementación real, esto enviaría un email con un enlace de recuperación.
        """
        if self.db is None:
            return False
            
        # Buscar usuario por nombre y email
        user = self.users.find_one({
            "username_lower": username.lower(),
            "email": email
        })
        
        if not user:
            return False
            
        # Generar token de recuperación
        reset_token = secrets.token_urlsafe(32)
        expiry_time = datetime.utcnow() + timedelta(hours=24)  # Token válido por 24 horas
        
        # Guardar token en la base de datos
        reset_data = {
            "user_id": user["_id"],
            "username": user["username"],
            "email": email,
            "token": reset_token,
            "created_at": datetime.utcnow(),
            "expires_at": expiry_time,
            "used": False
        }
        
        # Eliminar tokens anteriores del usuario
        self.password_resets.delete_many({"user_id": user["_id"]})
        
        # Insertar nuevo token
        self.password_resets.insert_one(reset_data)
        
        enviado = self._send_reset_email(email, user["username"], reset_token)
        return enviado
        
        # En una implementación real, aquí se enviaría el email
        print(f"[DEBUG] Token de recuperación generado para {username}: {reset_token}")
        print(f"[DEBUG] El token expira el: {expiry_time}")
        
        # Por ahora, simular que el email se envió correctamente
        return True

    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """
        Restablece la contraseña usando un token de recuperación.
        """
        if self.db is None:
            return False
            
        # Buscar token válido
        reset_request = self.password_resets.find_one({
            "token": token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not reset_request:
            return False
            
        # Actualizar contraseña del usuario
        new_hashed_password = self._hash_password(new_password)
        result = self.users.update_one(
            {"_id": reset_request["user_id"]},
            {"$set": {"password": new_hashed_password}}
        )
        
        if result.modified_count > 0:
            # Marcar token como usado
            self.password_resets.update_one(
                {"_id": reset_request["_id"]},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
            return True
            
        return False

    def get_user_by_email(self, email: str) -> dict:
        """Obtiene un usuario por su email."""
        if self.db is None:
            return None
            
        return self.users.find_one({"email": email})

    def remember_user(self, username, password):
        """Encripta y guarda las credenciales del usuario."""
        if not self.fernet: 
            return
            
        try:
            credentials = f"{username}::{password}".encode('utf-8')
            encrypted_credentials = self.fernet.encrypt(credentials)
            with open(get_remember_me_path(), "wb") as f:
                f.write(encrypted_credentials)
        except Exception as e:
            print(f"Error al guardar credenciales: {e}")

    def get_remembered_user(self):
        """Desencripta y devuelve las credenciales guardadas."""
        if not self.fernet: 
            return None, None
            
        try:
            path = get_remember_me_path()
            if not path.exists(): 
                return None, None
            
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

    # --- Métodos de gestión de conversaciones (sin cambios) ---

    def get_conversation(self, user_id: str, conversation_id: str) -> dict | None:
        """Obtiene una conversación específica por su ID, verificando que pertenezca al usuario."""
        if self.db is None: 
            return None
            
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
        if self.db is None: 
            return str(uuid.uuid4())
            
        conv_data['user_id'] = user_id # Asegurarse de que el user_id está en los datos
        result = self.conversations.insert_one(conv_data)
        return str(result.inserted_id)

    def update_conversation(self, user_id: str, conversation_id: str, update_data: dict):
        """Actualiza una conversación existente."""
        if self.db is None: 
            return
            
        try:
            self.conversations.update_one(
                {"_id": ObjectId(conversation_id), "user_id": user_id},
                {"$set": update_data}
            )
        except Exception as e:
            print(f"Error al actualizar la conversación {conversation_id}: {e}")

    def update_conversation_title(self, user_id: str, conversation_id: str, new_title: str) -> bool:
        """Actualiza solo el título de una conversación."""
        if self.db is None:
            return False
        try:
            result = self.conversations.update_one(
                {"_id": ObjectId(conversation_id), "user_id": user_id},
                {"$set": {"title": new_title, "timestamp": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar el título de la conversación {conversation_id}: {e}")
            return False

    def delete_or_archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Elimina una conversación de la base de datos."""
        if self.db is None: 
            return False
            
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
        if self.db is None: 
            return []
            
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
        if self.db is None: 
            return None
            
        try:
            return self.conversations.find_one({"_id": ObjectId(conversation_id)})
        except Exception as e:
            print(f"Error al obtener detalles de la conversación {conversation_id}: {e}")
            return None
