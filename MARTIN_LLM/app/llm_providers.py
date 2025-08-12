# -*- coding: utf-8 -*-
# app/llm_providers.py - VERSIÓN CORREGIDA PARA PYINSTALLER

import sys
import subprocess
import socket
import secrets
import time
import os
import contextlib
from multiprocessing.connection import Client
from pathlib import Path
from abc import ABC, abstractmethod
import requests
from llama_cpp import Llama

# ANSI escape codes for colors
class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# Importar la utilidad de rutas desde la raíz del proyecto.
try:
    from paths import get_log_file_path
except ImportError:
    print(f"{Color.RED}Error: No se pudo importar 'get_log_file_path' desde 'paths'. Usando ruta por defecto.{Color.RESET}")
    # Fallback si el import relativo falla
    def get_log_file_path():
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        return logs_dir / "llama_server.log"

@contextlib.contextmanager
def chdir_if_packaged(path: Path):
    """Context manager to temporarily change directory only if the app is frozen."""
    if getattr(sys, 'frozen', False):
        original_dir = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(original_dir)
    else:
        yield
# --- Llama.cpp Provider ---
try:
    from llama_cpp import Llama
    print(f"{Color.GREEN}Llama.cpp importado correctamente.{Color.RESET}")
except ImportError:
    Llama = None
class BaseLLMProvider(ABC):
    """Clase base abstracta para todos los proveedores de LLM."""
    def __init__(self, model_identifier: str, **kwargs):
        self.model_identifier = model_identifier
        # Parámetros de generación con valores por defecto
        self.temperature = 0.8
        self.top_p = 0.9
        self.repeat_penalty = 1.1  # Valor por defecto común para penalizar repeticiones
        print(f"{Color.BLUE}[BaseLLMProvider] Inicializado para el modelo: {model_identifier}{Color.RESET}")
        print(f"{Color.BLUE}-------------------------------------------------------------------------{Color.RESET}")
    @abstractmethod
    def query(self, messages: list, format: str = None) -> str:
        """Envía una lista de mensajes al modelo y devuelve la respuesta."""
        pass
    def shutdown(self):
        """
        Limpia cualquier recurso utilizado por el proveedor, como procesos en segundo plano.
        La implementación por defecto no hace nada.
        """
        pass
    def set_generation_parameters(self, **kwargs):
        """Establece los parámetros de generación como temperatura, top_p, etc."""
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
            print(f"{Color.BLUE}[BaseLLMProvider] Temperatura ajustada a: {self.temperature}{Color.RESET}")
        if "top_p" in kwargs:
            self.top_p = kwargs["top_p"]
            print(f"{Color.BLUE}[BaseLLMProvider] Top P ajustado a: {self.top_p}{Color.RESET}")
        if "repeat_penalty" in kwargs:
            self.repeat_penalty = kwargs["repeat_penalty"]
            print(f"{Color.BLUE}[BaseLLMProvider] Repeat Penalty ajustado a: {self.repeat_penalty}{Color.RESET}")

class LlamaCppProvider(BaseLLMProvider):
    """
    Proveedor para modelos GGUF locales usando llama-cpp-python.
    Versión con carga directa y robusta.
    """
    def __init__(self, model_path: str, **kwargs):
        # --- NO CAMBIAR ESTA PARTE ---
        super().__init__(model_identifier=os.path.basename(model_path))
        self.model_path = model_path
        self.llm = None
        print(f"{Color.BLUE}-------------------------------------------------------------------------{Color.RESET}")
        print(f"{Color.BLUE}[LlamaCppProvider] Iniciando en modo de CARGA DIRECTA.{Color.RESET}")
        print(f"{Color.BLUE}[LlamaCppProvider] Ruta del modelo: {self.model_path}{Color.RESET}")
        print(f"{Color.BLUE}-------------------------------------------------------------------------{Color.RESET}")        

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"No se encontró el archivo del modelo en: {self.model_path}")

        # Determinar la ruta base para la carga de librerías nativas.
        # Esto es crucial para aplicaciones empaquetadas (cx_Freeze/PyInstaller).
        if getattr(sys, 'frozen', False):
            # Aplicación empaquetada: la base es el directorio del ejecutable.
            base_path = Path(os.path.dirname(sys.executable))
        else:
            # Entorno de desarrollo: la base es la raíz del proyecto.
            base_path = Path(__file__).resolve().parents[1]

        print(f"{Color.BLUE}[LlamaCppProvider] Usando base_path para librerías: {base_path}{Color.RESET}")

        try:
            # Usamos el context manager para cambiar temporalmente el directorio de trabajo.
            # Esto es CRUCIAL para que llama.cpp encuentre sus librerías .dll/.so.
            with chdir_if_packaged(base_path):
                # Importamos Llama aquí para evitar conflictos de carga temprana.
                from llama_cpp import Llama
                
                # Creamos la instancia con los parámetros más seguros y compatibles,
                # replicando la configuración del script de prueba que funcionó.
                self.llm = Llama(
                    model_path=self.model_path,
                    n_gpu_layers=0,      # Forzar CPU para máxima compatibilidad
                    verbose=True,        # Máxima información de salida
                    n_ctx=2048         # Usamos el contexto que necesitas para tu app
                )
            print(f"{Color.GREEN}[LlamaCppProvider] Modelo cargado exitosamente en memoria.{Color.RESET}")

        except Exception as e:
            print(f"{Color.RED}[LlamaCppProvider] ERROR CRÍTICO DURANTE LA CARGA DEL MODELO.{Color.RESET}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Falló la carga directa del modelo Llama.cpp: {e}")

    def query(self, messages: list, format: str = None) -> str:
        """
        Genera una respuesta usando la instancia de Llama cargada.
        (Esta función reemplaza a tu `query` anterior que usaba `self.connection`).
        """
        if not self.llm:
            print(f"{Color.YELLOW}[LlamaCppProvider] Se intentó hacer una consulta pero el modelo no está cargado.{Color.RESET}")
            return "Error: El modelo LLM no está cargado."

        params = {
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repeat_penalty": self.repeat_penalty,
            "max_tokens": 1024, # Es buena idea definir un máximo de tokens
        }
        
        if format == "json":
            params["response_format"] = {"type": "json_object"}
            print(f"{Color.BLUE}[LlamaCppProvider] Solicitando salida JSON al modelo.{Color.RESET}")

        try:
            # Llamamos directamente al objeto llm
            response = self.llm.create_chat_completion(**params)
            
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            if not content:
                print(f"{Color.YELLOW}[LlamaCppProvider] El modelo devolvió una respuesta vacía. Respuesta completa: {response}{Color.RESET}")
                return "Error: El modelo no generó una respuesta."
            return content
        except Exception as e:
            print(f"{Color.RED}[LlamaCppProvider] Error durante la generación de la respuesta: {e}{Color.RESET}")
            return f"Error al procesar la solicitud del modelo: {e}"

    def shutdown(self):
        """Libera los recursos del modelo."""
        print(f"{Color.BLUE}[LlamaCppProvider] Liberando modelo de la memoria...{Color.RESET}")
        # En el modo de carga directa, simplemente eliminamos la referencia.
        # El recolector de basura de Python se encargará de liberar la memoria.
        self.llm = None
        print(f"{Color.BLUE}[LlamaCppProvider] Recursos liberados.{Color.RESET}")
    

# --- Ollama Provider (sin cambios) ---
class OllamaProvider(BaseLLMProvider):
    """Proveedor que interactúa con el API de Ollama."""

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_identifier=model_name)
        self.chat_api_url = "http://localhost:11434/api/chat"
        print(f"[OllamaProvider] Inicializado para el modelo: {model_name}")

    def query(self, messages: list, format: str = None) -> str:
        payload = {
            "model": self.model_identifier,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "repeat_penalty": self.repeat_penalty
            }
        }
        if format:
            payload['format'] = format
        
        try:
            response = requests.post(self.chat_api_url, json=payload, timeout=240)
            response.raise_for_status()
            data = response.json()
            message_content = data.get('message', {}).get('content', '')
            return message_content or "Error: El modelo de Ollama no generó una respuesta."
        except requests.RequestException as e:
            return f"Error de conexión con Ollama: {e}"
        except Exception as e:
            return f"Error inesperado al consultar Ollama: {e}"