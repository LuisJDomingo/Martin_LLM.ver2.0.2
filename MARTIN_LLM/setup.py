import sys
import os
from cx_Freeze import setup, Executable

# --- CONFIGURACIÓN BASE ---
base_dir = os.path.dirname(os.path.abspath(__file__))

# --- MODO DE DEPURACIÓN: Habilitar la consola para ver los 'print()' ---
# Cuando solucionemos el error, puedes volver a poner "Win32GUI"
# Por ahora, lo dejamos en None para que la consola aparezca.
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

print("--- Compilando en modo de DEPURACIÓN (consola habilitada) ---")


# --- DEPENDENCIAS DE LA APLICACIÓN ---

# Paquetes principales que tu aplicación necesita.
# cx_Freeze los buscará y los incluirá con sus dependencias.
packages = [
    "PyQt6",
    "sqlite3",
    "requests",
    "llama_cpp",
    "llama_cpp.server",  # Incluido explícitamente para el servidor de llama.cpp
    "psutil",
    "dotenv",
    "matplotlib",
    "numpy",
    "PIL", 
    "dns",
]

# Módulos específicos que cx_Freeze podría no encontrar automáticamente.
includes = [
    "app",
    "ui",
    "pathlib",
    "matplotlib.backends.backend_qtagg",  # Backend genérico para PyQt5/6
]

# Paquetes que sabemos que NO usas. Excluirlos reduce el tamaño del ejecutable.
excludes = [
    "tkinter", "scipy", "cv2", "tensorflow", "torch", "test",
    "unittest", "pdb", "pydoc", "doctest",
    # ¡CORREGIDO! Se eliminó "PIL" de aquí para evitar conflictos.
]


# --- ARCHIVOS Y CARPETAS ADICIONALES ---

# Lista de archivos y carpetas que se copiarán a la carpeta de distribución.
include_files = []

# Incluir la carpeta de modelos si existe (sin duplicados)
models_dir = os.path.join(base_dir, "models")
if os.path.exists(models_dir):
    include_files.append((models_dir, "models"))

# Incluir la carpeta de assets de la UI si existe
assets_dir = os.path.join(base_dir, "ui", "assets")
if os.path.exists(assets_dir):
    include_files.append((assets_dir, os.path.join("ui", "assets")))

# Incluir el archivo .env si existe
env_file = os.path.join(base_dir, ".env")
if os.path.exists(env_file):
    include_files.append((env_file, ".env"))


# --- OPCIONES DE COMPILACIÓN ---

build_exe_options = {
    "packages": packages,
    "includes": includes,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,
    "build_exe": "dist",  # Carpeta de salida
    "zip_exclude_packages": ["*"], # Evita que los paquetes se compriman en library.zip
}


# --- DEFINICIÓN DEL EJECUTABLE ---

executables = [
    Executable(
        script="run.py",
        base=base,
        target_name="Martin_LLM.exe",
        icon=os.path.join(assets_dir, "app_icon.ico") if os.path.exists(assets_dir) else None,
    )
]


# --- CONFIGURACIÓN PRINCIPAL DE SETUPTOOLS ---

setup(
    name="Martin LLM",
    version="2.0.1",
    description="Aplicación de chat con modelos LLM",
    author="Luis J. Domingo",
    options={"build_exe": build_exe_options},
    executables=executables
)

# NOTA: La función post_build con atexit no es fiable con cx_Freeze
# y ha sido eliminada para evitar comportamientos inesperados.
# Es mejor ejecutar scripts de verificación por separado después de la compilación.
