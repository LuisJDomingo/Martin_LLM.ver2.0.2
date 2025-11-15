from pymongo import MongoClient
from bson import ObjectId
import os

# Conectar a MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['martin_llm']
conversations = db['conversations']

# Buscar la conversación específica
conv_id = '68792c6ed56e8cf925a5bdfe'
print(f'Buscando conversación con ID: {conv_id}')

# Buscar por diferentes campos posibles
print('\n=== Búsqueda por _id ===')
try:
    result = conversations.find_one({'_id': ObjectId(conv_id)})
    print(f'Resultado por _id: {result}')
except Exception as e:
    print(f'Error buscando por _id: {e}')

print('\n=== Búsqueda por id (string) ===')
result = conversations.find_one({'id': conv_id})
print(f'Resultado por id: {result}')

print('\n=== Todas las conversaciones ===')
all_convs = list(conversations.find())
for conv in all_convs:
    _id = conv.get('_id')
    id_field = conv.get('id')
    user_id = conv.get('user_id')
    print(f'_id: {_id}, id: {id_field}, user_id: {user_id}')

print('\n=== Conversaciones del usuario específico ===')
user_id = '686b9204db7f4df0bc21a70a'
user_convs = list(conversations.find({'user_id': user_id}))
for conv in user_convs:
    _id = conv.get('_id')
    id_field = conv.get('id')
    title = conv.get('title', 'Sin título')
    print(f'_id: {_id}, id: {id_field}, title: {title}')
