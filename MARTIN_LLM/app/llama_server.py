# -*- coding: utf-8 -*-
# app/llama_server.py

import sys
import argparse
import logging
import json
from pathlib import Path
from multiprocessing.connection import Listener
from llama_cpp import Llama

# Añadir explícitamente la raíz del proyecto para que los imports funcionen
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - (llama_server) - %(message)s',
    stream=sys.stdout  # Imprimir logs en la consola
)

# ANSI escape codes for colors
class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def find_project_root():
    """Busca la raíz del proyecto subiendo en el árbol de directorios."""
    current_path = Path(__file__).resolve()
    # Sube hasta que encuentre un marcador de proyecto (ej: run.py o .env)
    while current_path != current_path.parent:
        if (current_path / "run.py").exists() or (current_path / ".env").exists():
            return current_path
        current_path = current_path.parent
    # Fallback al directorio actual si no se encuentra
    return Path.cwd()

def main():
    """
    Este script se ejecuta en un proceso separado.
    Carga un modelo GGUF y escucha en un puerto para recibir peticiones.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-path",
        required=False,
        default=None,
        help="Ruta al archivo del modelo GGUF. Si no se especifica, se usará 'models/model.gguf' por defecto."
    )
    parser.add_argument(
        "--n-gpu-layers",
        type=int,
        default=0,
        help="Número de capas a descargar en la GPU. -1 para todas las posibles, 0 para solo CPU."
    )
    parser.add_argument("--port", required=True, type=int, help="Puerto en el que escuchar.")
    parser.add_argument(
        "--authkey",
        required=False,
        help=(
            "Clave de autenticación para la conexión segura entre procesos "
            "(no relacionada con autenticación de usuarios). "
            "Por defecto: 'martin_llm'"
        )
    )
    args, _ = parser.parse_known_args()

    address = ('localhost', args.port)

    project_root = find_project_root()

    if args.model_path:
        model_path = Path(args.model_path)
    else:
        # Si no se proporciona --model-path, usar el valor por defecto.
        print(f"{Color.YELLOW}[LLAMA_SERVER] No se especificó --model-path. Usando 'models/model.gguf' por defecto.{Color.RESET}")
        model_path = project_root / "models" / "model.gguf"

    # Si la ruta es relativa, la resolvemos desde la raíz del proyecto.
    if not model_path.is_absolute():
        print(f"{Color.BLUE}[LLAMA_SERVER] Resolviendo ruta relativa desde: {project_root}{Color.RESET}")
        logging.info(f"Resolviendo ruta relativa del modelo desde: {project_root}")
        model_path = (project_root / model_path).resolve()

    print(f"{Color.BLUE}[LLAMA_SERVER] Cargando modelo desde ruta absoluta: {model_path}{Color.RESET}")
    logging.info(f"Ruta absoluta del modelo a cargar: {model_path}")
    
    # Añadir una verificación explícita para dar un error más claro.
    if not model_path.exists():
        print(f"{Color.RED}[LLAMA_SERVER] FATAL: El archivo del modelo no existe en la ruta especificada: {model_path}{Color.RESET}")
        sys.exit(1)

    try:
        model_params = {
            "model_path": str(model_path),
            "n_gpu_layers": args.n_gpu_layers,
            "verbose": True,
            "n_batch": 512,
            "n_ctx": 4096 # Contexto por defecto, puede ser sobreescrito
        }
        logging.info(f"Parámetros de carga para Llama.cpp: {model_params}")
        print(f"{Color.GREEN}[llama_server]{Color.RESET} -> {Color.YELLOW}main(){Color.RESET}: Intentando cargar el modelo con los siguientes parámetros:\n{json.dumps(model_params, indent=2)}")

        llm = Llama(
            **model_params
        )
        print(f"{Color.GREEN}[llama_server]{Color.RESET} -> {Color.YELLOW}main(){Color.RESET}: Modelo cargado con éxito.")
        logging.info("Modelo cargado exitosamente en memoria.")
    except Exception as e:
        logging.error(f"FATAL: No se pudo cargar el modelo: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Usar authkey proporcionado o valor por defecto para desarrollo
    authkey_str = args.authkey or "martin_llm"
    authkey = authkey_str.encode('utf-8')
    print(f"{Color.GREEN}[llama_server]{Color.RESET} -> {Color.YELLOW}main(){Color.RESET}: Usando authkey para conexión entre procesos.")
    logging.info("Authkey para conexión IPC establecida.")

    with Listener(address, authkey=authkey) as listener:
        print(f"{Color.GREEN}[llama_server]{Color.RESET} -> {Color.YELLOW}main(){Color.RESET}: Escuchando en el puerto {args.port}...")
        logging.info(f"Servidor escuchando en {address}")
        try:
            with listener.accept() as conn:
                print(f"{Color.GREEN}[llama_server]{Color.RESET} -> {Color.YELLOW}main(){Color.RESET}: Conexión aceptada desde {listener.last_accepted}")
                logging.info(f"Conexión aceptada desde {listener.last_accepted}")
                while True:
                    try:
                        msg = conn.recv()
                        if msg == 'shutdown':
                            print(f"{Color.GREEN}[llama_server]{Color.RESET}    {Color.BLUE}Señal de apagado recibida.{Color.RESET}")
                            logging.info("Señal de apagado recibida. Terminando...")
                            break

                        print(f"{Color.GREEN}[llama_server]{Color.RESET}    {Color.BLUE}Petición recibida. Procesando...{Color.RESET}")
                        logging.info(f"Petición de inferencia recibida:\n{json.dumps(msg, indent=2, ensure_ascii=False)}")

                        response = llm.create_chat_completion(**msg)

                        print(f"{Color.GREEN}[llama_server]{Color.RESET}    {Color.BLUE}Respuesta generada. Enviando al cliente...{Color.RESET}")
                        logging.info(f"Respuesta generada por el modelo:\n{json.dumps(response, indent=2, ensure_ascii=False)}")
                        conn.send(response)
                    except EOFError:
                        print(f"{Color.YELLOW}[llama_server] El cliente se ha desconectado.{Color.RESET}")
                        logging.warning("El cliente se ha desconectado (EOFError).")
                        break
                    except Exception as e:
                        error_response = {"error": str(e)}
                        logging.error(f"Error procesando la petición en el bucle de escucha: {e}", exc_info=True)
                        try:
                            conn.send(error_response)
                        except Exception:
                            # Si no podemos enviar el error, simplemente salimos
                            break
        except Exception as e:
            print(f"{Color.RED}[LLAMA_SERVER] Error en el listener: {e}{Color.RESET}")
            logging.error(f"Error crítico en el listener principal: {e}", exc_info=True)
    print(f"{Color.BLUE}[LLAMA_SERVER] Apagando.{Color.RESET}")

if __name__ == "__main__":
    main()
