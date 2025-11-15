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
from ctransformers import AutoModelForCausalLM

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

class CtransformersProvider(BaseLLMProvider):
    """
    Provider for GGUF models using the ctransformers library.
    """
    def __init__(self, model_path: str, hardware_config=None, **kwargs):
        super().__init__(model_identifier=os.path.basename(model_path))
        self.model_path = model_path
        self.llm = None
        self.hardware_config = hardware_config or self._load_hardware_config()

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        try:
            n_gpu_layers = self._get_gpu_layers()
            model_type = self._get_model_type_from_path(self.model_path)
            
            print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET} GPU Layers: {n_gpu_layers}, Model Type: {model_type}")

            self.llm = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                model_type=model_type,
                gpu_layers=n_gpu_layers,
                **kwargs
            )
            print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET} Model loaded successfully.")

            # Imprimir información detallada del modelo cargado si está disponible
            if hasattr(self.llm, 'metadata') and self.llm.metadata:
                metadata = self.llm.metadata
                print(f"\n{Color.BLUE}┌──────────────────────────────────┐{Color.RESET}")
                print(f"{Color.BLUE}│         MODEL METADATA         │{Color.RESET}")
                print(f"{Color.BLUE}└──────────────────────────────────┘{Color.RESET}")
                
                # Calcular el ancho máximo de las claves para alinear la salida
                max_key_len = max(len(key) for key in metadata.keys()) if metadata else 0
                
                for key, value in metadata.items():
                    # Formatear la clave para que todas tengan el mismo ancho
                    formatted_key = f"{key}:".ljust(max_key_len + 2)
                    print(f"  {Color.YELLOW}{formatted_key}{Color.RESET} {value}")
                
                print(f"{Color.BLUE}────────────────────────────────────{Color.RESET}\n")


        except Exception as e:
            print(f"{Color.RED}[CtransformersProvider] CRITICAL ERROR DURING MODEL LOAD.{Color.RESET}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to load ctransformers model: {e}")

    def _get_model_type_from_path(self, model_path: str) -> str:
        """Infers the model type from the model file path."""
        path_str = str(model_path).lower()
        if "llama-3" in path_str or "llama3" in path_str:
            return "llama"
        if "mistral" in path_str or "mixtral" in path_str:
            return "mistral"
        if "phi-3" in path_str or "phi3" in path_str:
            return "phi3"
        if "gemma" in path_str:
            return "gemma"
        if "command-r" in path_str:
            return "command-r"
        if "phi" in path_str: # Must be after phi-3
            return "phi"
        if "yi" in path_str or "llava" in path_str:
             return "yi"
        # Default fallback for Llama 2 and other llama-like models
        return "llama"

    def query(self, messages: list, format: str = None) -> str:
        if not self.llm:
            return "Error: Ctransformers model not loaded."

        print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET} -> {Color.YELLOW}query(){Color.RESET}")
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET}    {Color.BLUE}Final prompt being sent to model:{Color.RESET}\n---PROMPT START---\n{prompt}\n---PROMPT END---")

        try:
            print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET}    {Color.BLUE}Generating response...{Color.RESET}")
            response = self.llm(
                prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                repetition_penalty=self.repeat_penalty,
            )
            print(f"{Color.GREEN}[CtransformersProvider]{Color.RESET}    {Color.BLUE}Raw response received:{Color.RESET}\n---RESPONSE START---\n{response}\n---RESPONSE END---")
            return response
        except Exception as e:
            print(f"{Color.RED}[CtransformersProvider] Error during response generation: {e}{Color.RESET}")
            import traceback
            traceback.print_exc()
            return f"Error processing model request: {e}"

    def _load_hardware_config(self):
        """Carga la configuración de hardware guardada o usa valores por defecto."""
        import json
        
        config_file = 'hardware_config.json'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('selected_config', {})
        except Exception as e:
            print(f"{Color.YELLOW}[CtransformersProvider] Could not load hardware config: {e}{Color.RESET}")
        
        return {
            'type': 'default_cpu',
            'n_gpu_layers': 0,
            'n_threads': os.cpu_count(),
            'requires_cuda_build': False
        }
    
    def _get_gpu_layers(self):
        """Determina cuántas capas usar en GPU basado en la configuración."""
        if not self.hardware_config:
            return 0
        
        return self.hardware_config.get('n_gpu_layers', 0)

    def shutdown(self):
        print(f"{Color.BLUE}[CtransformersProvider] Releasing model from memory...{Color.RESET}")
        self.llm = None
        print(f"{Color.BLUE}[CtransformersProvider] Resources released.{Color.RESET}")





    
