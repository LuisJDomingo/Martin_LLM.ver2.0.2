# -*- coding: utf-8 -*-
# Martin_LLM/Martin_LLM/paths.py

import os
import sys
from pathlib import Path

def get_app_data_dir() -> Path:
    r"""
    Obtiene el directorio de datos de la aplicación, específico del sistema operativo,
    y lo crea si no existe.

    - Windows: %LOCALAPPDATA%\Martin_LLM
    - macOS:   ~/Library/Application Support/Martin_LLM
    - Linux:   ~/.local/share/Martin_LLM (o $XDG_DATA_HOME/Martin_LLM)
    """
    app_name = "Martin_LLM"

    if sys.platform == "win32":
        base_path = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    elif sys.platform == 'darwin':
        base_path = Path.home() / 'Library' / 'Application Support'
    else:  # Linux y otros
        base_path = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    
    app_data_path = base_path / app_name
    app_data_path.mkdir(parents=True, exist_ok=True)
    return app_data_path

def get_remember_me_path() -> Path:
    """
    Devuelve la ruta completa al archivo que guarda las credenciales de 'Recordarme'.
    """
    return get_app_data_dir() / "remember_me.dat"

def get_log_file_path() -> Path:
    """
    Devuelve la ruta completa al archivo de log para el servidor de Llama.cpp.
    """
    return get_app_data_dir() / "llama_server.log"