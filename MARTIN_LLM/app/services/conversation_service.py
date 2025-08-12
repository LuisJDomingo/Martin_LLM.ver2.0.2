# -*- coding: utf-8 -*-
from MARTIN_LLM.app.database.db_manager import DatabaseManager
from typing import Optional, Dict, List

db = DatabaseManager()

def get_or_create_conversation(model: str, conversation_id: Optional[str] = None) -> Dict:
    print(f"?? get_or_create_conversation: model={model}, conversation_id={conversation_id}")

    if conversation_id:
        print("?? Buscando conversacion existente...")
        conversation = db.get_conversation(conversation_id)
        if conversation:
            print("? Conversacion encontrada.")
            return conversation
        else:
            print("?? Conversacion no encontrada. Se creara una nueva.")
    else:
        print("?? No se proporciono conversation_id. Se creara una nueva conversacion.")

    new_conversation_id = db.create_conversation(model=model)
    print(f"?? Nueva conversacion creada con ID: {new_conversation_id}")
    return db.get_conversation(new_conversation_id)

def save_message(conversation_id: str, content: str, role: str, context: Optional[List[str]] = None):
    print(f"?? Guardando mensaje: conversation_id={conversation_id}, role={role}")
    print(f"?? Contexto del mensaje: {context}")
    db.add_message(conversation_id=conversation_id, content=content, role=role, context=context)
