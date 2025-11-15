# Martín LLM - Asistente de IA de Escritorio

**Martín LLM** es una completa aplicación de escritorio diseñada para interactuar con modelos de lenguaje grandes (LLMs) de forma local. Proporciona una interfaz de usuario robusta y una arquitectura modular para gestionar conversaciones, modelos y bases de datos, todo desde la comodidad de tu PC.

---

## ✨ Características Principales

- **Interfaz Gráfica Completa**: Construida con PyQt6 para una experiencia de usuario fluida y moderna.
- **Gestión de Usuarios**: Sistema de inicio de sesión y registro de usuarios.
- **Soporte para Modelos Locales**: Interactúa con modelos de lenguaje en formato GGUF directamente en tu máquina.
- **Gestión de Conversaciones**: Guarda y carga conversaciones anteriores desde una base de datos MongoDB.
- **Arquitectura Modular**: Código organizado para facilitar el mantenimiento y la escalabilidad.
- **Empaquetado para Distribución**: Incluye archivos de especificaciones (`.spec`) para crear un ejecutable con PyInstaller.

---

## 🚀 Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno de desarrollo.

### 1. Prerrequisitos

- **Python**: Versión 3.9 o superior.
- **MongoDB**: Una instancia de MongoDB debe estar en ejecución.
- **Git**: Para clonar el repositorio.

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone [URL_DEL_REPOSITORIO]
    cd MARTIN_LLM.ver2.0.2/MARTIN_LLM
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuración

- **Base de Datos**: El proyecto utiliza MongoDB. El script `start_mongodb.py` puede ser usado para iniciar el servicio si está configurado localmente. Asegúrate de que la configuración en `config/db_config.py` apunte a tu instancia de base de datos.
- **Modelos**: Descarga los modelos en formato GGUF que desees usar y colócalos en la carpeta `models`.

### 4. Ejecución de la Aplicación

Para iniciar la aplicación con la interfaz gráfica, ejecuta:

```bash
python main_qt.py
```

---

## 💻 Uso de la Aplicación

- **Inicio de Sesión**: Inicia la aplicación y accede con tus credenciales o regístrate como un nuevo usuario.
- **Chat Principal**: Una vez dentro, serás recibido por la interfaz de chat principal donde puedes comenzar a interactuar con el LLM.
- **Gestión de Modelos**: Utiliza el gestor de modelos para ver los modelos locales y descargar nuevos.
- **Cargar Conversaciones**: Puedes cargar conversaciones anteriores para continuar desde donde las dejaste.

---

## 📂 Estructura del Proyecto

El proyecto tiene una arquitectura bien definida para separar responsabilidades:

```
MARTIN_LLM/
├── app/                # Lógica de negocio principal
│   ├── database/       # Gestión de la base de datos (MongoDB)
│   ├── services/       # Lógica de servicios (conversaciones, archivos, modelos)
│   ├── agent.py        # Lógica del agente de IA
│   └── chat_engine.py  # Motor principal del chat
├── ui/                 # Componentes de la interfaz gráfica (PyQt6)
│   ├── chat_interface.py # Widget principal del chat
│   ├── login_widget.py   # Widget de inicio de sesión
│   └── ...
├── config/             # Archivos de configuración
├── data/               # Datos de la aplicación (e.g., base de datos)
├── TESTS/              # Pruebas automatizadas
├── main_qt.py          # Punto de entrada de la aplicación GUI
└── requirements.txt    # Dependencias de Python
```

---

## 🛠️ Futuras Mejoras

- [ ] Implementar un sistema de plugins para extender funcionalidades.
- [ ] Añadir soporte para más proveedores de LLMs.
- [ ] Mejorar las herramientas de fine-tuning directamente desde la interfaz.
- [ ] Internacionalización para soportar múltiples idiomas en la UI.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas colaborar, por favor sigue estos pasos:

1.  Haz un **fork** del repositorio.
2.  Crea una nueva **rama** para tu mejora o corrección.
3.  Realiza tus cambios y envíalos a tu fork.
4.  Abre una **pull request** describiendo los cambios realizados.

---

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia [MIT](LICENSE.txt).