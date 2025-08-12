import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from pymongo import MongoClient, DESCENDING
# Las importaciones deben ser directas, asumiendo que estos archivos existen en tu proyecto.
# Si db_config.py está en la raíz, la importación sería: from db_config import ...
# Si está en una carpeta 'config', sería: from config.db_config import ...
# Lo mismo aplica para los modelos y el manager.
from config.db_config import MONGODB_URI, DB_NAME, COLLECTION_CONVERSATIONS, COLLECTION_MESSAGES
from app.database.models import Conversation, Message
from app.database.db_manager import DatabaseManager
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

def test_mongodb_connection():
    """Verifica la conexión con MongoDB"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✓ Conexion a MongoDB exitosa")
        return True
    except Exception as e:
        print(f"✗ Error al conectar a MongoDB: {e}")
        return False

def test_database():
    """Prueba las operaciones de la base de datos"""
    print("\n=== Iniciando pruebas de base de datos ===")
    
    if not test_mongodb_connection():
        print("No se puede continuar sin conexión a MongoDB")
        return

    try:
        db = DatabaseManager()
        
        print("\nCreando conversacion...")
        conv_id = db.create_conversation("llama2")
        print(f"ID de conversacion creada: {conv_id}")
        
        print("\nVerificando conversacion en la base de datos...")
        db_client = MongoClient(MONGODB_URI)
        db_instance = db_client[DB_NAME]
        conv_doc = db_instance.conversations.find_one({"_id": ObjectId(conv_id)})
        if conv_doc:
            print("✓ Conversacion encontrada en la base de datos")
            print(f"Datos: {conv_doc}")
        else:
            print("✗ Conversacion no encontrada en la base de datos")
        
        print("\nAnadiendo mensajes...")
        db.add_message(conv_id, "Hola, ¿cómo estas?", "user")
        db.add_message(conv_id, "¡Hola! Estoy bien, ¿en qué puedo ayudarte?", "assistant")
        
        print("\nVerificando mensajes en la base de datos...")
        messages = list(db_instance.messages.find({"conversation_id": ObjectId(conv_id)}))
        print(f"Mensajes encontrados: {len(messages)}")
        for msg in messages:
            print(f"- {msg['role']}: {msg['content']}")
        
        print("\nRecuperando conversacion completa...")
        conv = db.get_conversation(conv_id)
        
        if conv is None:
            print("✗ Error: get_conversation devolvió None")
            return
            
        print("\nMensajes en la conversacion recuperada:")
        for msg in conv.messages:
            print(f"{msg.role}: {msg.content}")
            
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
    print("\n=== Pruebas completadas ===")