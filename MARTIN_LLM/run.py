# -*- coding: utf-8 -*-
# run.py - Launcher script CORREGIDO PARA PYINSTALLER

import sys
from pathlib import Path

# ANSI escape codes for colors
class Color:
    BLUE = '\033[94m'
    RESET = '\033[0m'

print(f"{Color.BLUE}[run.py] Iniciando...{Color.RESET}")
# --- INICIO: Solución al problema de importación ---
# 1. Obtener la ruta del directorio donde se encuentra este script (la raíz del proyecto)
project_root = Path(__file__).resolve().parent
# 2. Añadir la raíz del proyecto al sys.path.
#    Esto permite que Python encuentre módulos como 'app', 'ui', 'config.py', etc.
#    de forma consistente, tanto en la ejecución normal como en el proceso servidor.
sys.path.insert(0, str(project_root))

# --- INICIO: Definir la ruta raíz para toda la aplicación ---
# 3. Importar el módulo de configuración y establecer la ruta raíz.
#    Esto asegura que cualquier otro módulo pueda acceder a la ruta base de forma fiable.
import config
config.PROJECT_ROOT = project_root
# --- FIN: Definir la ruta raíz ---

def is_server_process_call():
    """
    Comprueba si este script se ha invocado para actuar como el proceso de servidor de Llama.cpp
    buscando un argumento específico.
    """
    # Este print es muy ruidoso, lo dejamos sin color o lo comentamos
    # print(f"[run.py]is_server_process_call() -> sys.argv: {sys.argv}")
    if __name__ == '__main__':
    # --- INICIO NORMAL DE LA APLICACIÓN GUI ---
        from multiprocessing import freeze_support
        freeze_support() # Necesario para la compatibilidad con multiprocessing en Windows
        from main_qt import main
        sys.exit(main())

if __name__ == '__main__':
    # print("[run.py] is_server_process_call():", is_server_process_call())
    if is_server_process_call():
        # --- INVOCACIÓN DEL PROCESO SERVIDOR ---
        # Este bloque se ejecuta solo cuando LlamaCppProvider lo invoca.
        # Se importa y ejecuta directamente el main del servidor.
        print(f"{Color.BLUE}[run.py] Detectada invocación de proceso servidor. Iniciando llama_server...{Color.RESET}")
        try:
            from app.llama_server import main as server_main
            server_main()
        except Exception as e:
            print(f"\033[91m[run.py] ERROR FATAL al ejecutar el módulo servidor: {e}{Color.RESET}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # --- INICIO NORMAL DE LA APLICACIÓN GUI ---
        from multiprocessing import freeze_support
        freeze_support() # Necesario para la compatibilidad con multiprocessing en Windows
        from main_qt import main
        sys.exit(main())