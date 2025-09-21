# Documentación del Proyecto MARTIN_LLM

## Introducción
Este documento describe los scripts principales del proyecto MARTIN_LLM, detallando sus funcionalidades clave y las partes importantes del código.

## Archivos y Funcionalidades

### 1. `app/agent.py`
Implementa la lógica de un agente que sigue el ciclo Pensamiento -> Acción -> Observación.

#### Funciones Clave:
- `__init__`: Inicializa el agente con un proveedor de lenguaje. Si no se proporciona un prompt personalizado, elige uno por defecto.
- `_parse_llm_response`: Intenta analizar la respuesta del LLM en formato JSON.
- `run`: Ejecuta el bucle del agente repartido en varios pasos, como pensar la acción, ejecutarla y observar los resultados.
- `execute_task`: Alias para `run`, se usa para mayor claridad en el contexto de ejecución individual de tareas.

#### Partes Importantes:
```python
class Agent:
    def __init__(self, provider: BaseLLMProvider, custom_prompt: str = None):
        # Inicialización del agente
        self.provider = provider
        # Prompt del sistema
        self.system_prompt = f"--- Constructo ---"
```
#### Ejecución del bucle:
```python
for i in range(5):
    # Pensar, Actuar, Observar
    response_text = self.provider.query(messages_for_provider, format="json")
    action_data = self._parse_llm_response(response_text)
    # Ejecutar acción
```

### 2. `app/chat_engine.py`
Gestiona el estado de las conversaciones de chat, incluyendo el manejo del historial y el prompt del sistema.

#### Funciones Clave:
- `__init__`: Inicializa los atributos de la conversación, estableciendo valores predeterminados.
- `start_new`: Inicia una nueva conversación reseteando todos los estados a los predeterminados.
- `load_conversation`: Carga una conversación existente, definiendo el ID y el historial.

#### Partes Importantes:
```python
class ChatEngine:
    def __init__(self, provider: BaseLLMProvider | None):
        # Inicialización
        self.history = []
        self.system_prompt = SYSTEM_PROMPT
```

### 3. `app/database/db_manager.py`
Interfaz para gestionar conversaciones y mensajes en la base de datos (MongoDB o SQLite).

#### Funciones Clave:
- `__init__`: Inicializa conexiones y selecciones de base de datos.
- `create_conversation`: Crea una nueva entrada de conversación.
- `get_conversation`: Recupera una conversación y sus mensajes.

#### Partes Importantes:
```python
class DatabaseManager:
    def __init__(self):
        # Inicialización de la base de datos
        self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
```

### 4. `app/llama_server.py`
Módulo del servidor que carga un modelo GGUF y escucha en un puerto para recibir peticiones.

#### Funciones Clave:
- `main`: Configura y ejecuta el servidor, cargando el modelo y escuchando las peticiones.

#### Partes Importantes:
```python
def main():
    # Cargar modelo
    llm = Llama(
        model_path=str(model_path),
        n_gpu_layers=args.n_gpu_layers,
        verbose=True,
        n_batch=512
    )
```

### 5. `app/llm_providers.py`
Define proveedores de lenguaje como `LlamaCppProvider` y `OllamaProvider`.

#### Funciones Clave:
- `BaseLLMProvider`: Clase base para todos los proveedores de LLM.
- `LlamaCppProvider`: Proveedor para modelos GGUF usando llama-cpp-python.
- `OllamaProvider`: Interactúa con el API de Ollama.

#### Partes Importantes:
```python
class LlamaCppProvider(BaseLLMProvider):
    def __init__(self, model_path: str, **kwargs):
        # Inicialización
        self.llm = Llama(
            model_path=self.model_path,
            n_gpu_layers=0,
            verbose=True,
            n_ctx=2048
        )
```

## Conclusión
Este documento proporciona una descripción de los scripts clave que componen el proyecto MARTIN_LLM, con detalles relevantes sobre las funcionalidades y líneas importantes de cada archivo.