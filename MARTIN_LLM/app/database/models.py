# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from bson import ObjectId
import bcrypt

@dataclass
class User:
    
    def __init__(self, username: str, password_hash: str, _id=None):
        self.username: str = username
        self.password_hash: str = password_hash
        self.created_at: datetime = field(default_factory=datetime.utcnow)
        self._id = _id

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "username": self.username,
            "password_hash": self.password_hash,
            "created_at": self.created_at
        }

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
@dataclass
class Message:
    content: str
    role: str
    conversation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Optional[List] = None

    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'role': self.role,
            'conversation_id': self.conversation_id,
            'timestamp': self.timestamp,
            'context': self.context
        }

@dataclass
class Conversation:
    id: Optional[str] = None
    user_id: Optional[str] = None  # <- Clave para filtrar por usuario
    model: str = "llama2"
    title: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    messages: List[Message] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "user_id": self.user_id,
            "model": self.model,
            "title": self.title or f"Conversación {self.timestamp.strftime('%Y-%m-%d %H:%M')}",
            "timestamp": self.timestamp,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
        }
        if self.id is not None:
            data["_id"] = self.id
        return data