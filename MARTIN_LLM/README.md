## Clase Chat Engine

La clase que controla la conversación. Tiene:

self.history: una lista con todos los mensajes, en formato dict: {"role": "user"|"assistant"|"system", "content": str}.

get_full_prompt(): construye el prompt plano estilo "conversación", útil para modelos tipo LLaMA, Mistral, etc. que no entienden directamente roles como GPT-4.


# Martin_LLM - Asistente de Chat Local con Ollama
Version: 1.0.0

## Descripción
Martin_LLM es una aplicación de chat que proporciona una interfaz para interactuar con modelos de lenguaje de Ollama. Ofrece tanto una interfaz gráfica como modo consola, y permite mantener conversaciones contextuales con el modelo.

## Estructura del Proyecto


Martin_LLM/		
|
├── app/ 
│   ├── init.py 
│   ├── model_loader.py    # Gestión de conexión con Ollama 
│   ├── chat_engine.py     # Motor principal del chat 
│   ├── chat_test.py       # Modo consola 
│   └── shortcut_listener.py # Interfaz de atajos y GUI 
|
├── ui/ 
│   └── popup_window.py    # Componentes de interfaz gráfica 
|
└── main.py               # Punto de entrada principal

## Componentes Principales

### 1. Model Loader (model_loader.py)
Gestiona la comunicación con el servicio Ollama.

**Características principales:**
- Verificación de estado del servicio
- Gestión de conexiones
- Manejo de contexto de conversación
- Control de recursos del sistema

**Funciones clave:**
- `query_ollama()`: Realiza consultas al modelo
- `check_system_resources()`: Monitorea recursos del sistema
- `verify_ollama_connection()`: Verifica conectividad

### 2. Chat Engine (chat_engine.py)
Motor principal que gestiona la lógica de conversación.

**Características:**
- Mantiene historial de conversación
- Gestiona contexto entre mensajes
- Formatea prompts para el modelo

**Métodos principales:**

class ChatEngine: 
	def init(self, model="llama3") 
	def ask(self, user_input: str) -> str def reset(self) 
	def get_conversation_history()

### 3. Interfaz Gráfica (shortcut_listener.py)
Implementa la interfaz gráfica y control de atajos.

**Características:**
- Ventana de chat interactiva
- Historial visual de mensajes
- Botones de control
- Atajos de teclado

**Componentes UI:**
- Área de historial
- Campo de entrada de texto
- Botones de control (Enviar, Limpiar, Reiniciar)

## Modos de Uso

### 1. Modo Atajo (Por defecto)

	python main.py 

- Activa el modo de atajo (Ctrl+Shift+L)
- Permite acceso rápido al chat desde cualquier aplicación

### 2. Modo GUI Directo

	python main.py --gui

- Abre directamente la interfaz gráfica
- Proporciona todas las funcionalidades de chat

### 3. Modo Consola

	python main.py --chat

- Interfaz de línea de comandos
- Ideal para pruebas y debugging

## Requisitos del Sistema

### Software
- Python 3.8+
- Ollama instalado y en ejecución
- Modelo llama3 disponible en Ollama

### Dependencias Python

requests 
keyboard 
psutil 
tkinter

### Hardware Recomendado
- CPU: 4+ núcleos
- RAM: 8GB mínimo
- Espacio en disco: 1GB para modelos

## Configuración

### 1. Instalación
	
	git clone [repo-url] cd Martin_LLM 
	pip install -r requirements.txt

### 2. Preparación de Ollama
	
	ollama pull llama3 
	ollama serve

### 3. Verificación

	python main.py 

## Características Principales

1. **Gestión de Contexto**
   - Mantiene coherencia en conversaciones
   - Límite configurable de contexto

2. **Interfaz Adaptable**
   - Modo GUI completo
   - Modo consola
   - Acceso rápido por atajo

3. **Control de Recursos**
   - Monitoreo de uso de CPU
   - Control de memoria
   - Timeouts configurables

4. **Manejo de Errores**
   - Recuperación automática
   - Mensajes informativos
   - Reinicio de contexto

## Limitaciones Conocidas

1. Requiere Ollama en ejecución
2. El tiempo de primera respuesta puede ser largo
3. Uso intensivo de memoria con contextos largos

## Mantenimiento

### Logs y Diagnóstico
- Verificación de estado: `python main.py --chat`
- Monitoreo de recursos integrado
- Mensajes de error detallados

### Resolución de Problemas
1. Error de conexión:
   - Verificar Ollama (`ollama serve`)
   - Comprobar puerto 11434

2. Respuestas lentas:
   - Reducir tamaño de contexto
   - Verificar recursos disponibles

3. Errores de GUI:
   - Reiniciar aplicación
   - Verificar tkinter

## Futuras Mejoras
1. Soporte para más modelos
2. Persistencia de conversaciones
3. Configuración personalizable
4. Mejoras en la interfaz gráfica

## Contribuciones
Las contribuciones son bienvenidas. Por favor, sigue estas pautas:
1. Fork del repositorio
2. Crear rama feature/fix
3. Enviar pull request

## Licencia
[Especificar licencia]
