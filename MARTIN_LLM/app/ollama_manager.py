# -*- coding: utf-8 -*-
# app/ollama_manager.py

import requests
import json

class OllamaManager:
    """
    Clase para gestionar la interacción con el API de Ollama, como
    listar, descargar y verificar modelos.
    """
    def __init__(self, base_url="http://localhost:11434"):
        """
        Inicializa el gestor con la URL base del API de Ollama.
        """
        self.base_url = base_url
        self.api_tags_url = f"{self.base_url}/api/tags"
        self.api_pull_url = f"{self.base_url}/api/pull"
        self.api_show_url = f"{self.base_url}/api/show"
        self.api_delete_url = f"{self.base_url}/api/delete"

    def get_local_models(self) -> list:
        """
        Obtiene una lista de todos los modelos disponibles localmente en Ollama.
        Cada elemento de la lista es un diccionario con detalles del modelo.
        """
        try:
            response = requests.get(self.api_tags_url, timeout=10)
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.RequestException as e:
            print(f"[OllamaManager] Error al obtener modelos locales: {e}")
            # Devuelve una lista vacía para que la app pueda continuar sin crashear.
            return []
    def stop(self):
        """
        Método de apagado para cumplir con la interfaz de limpieza.
        No hace nada, ya que este manager no controla procesos persistentes.
        """
        print("[OllamaManager] Recibida señal de stop. No se requieren acciones.")
        pass
    def is_model_available(self, model_name: str) -> bool:
        """
        Verifica si un modelo específico está disponible localmente.
        Usa el endpoint /api/show que es más directo que listar todos.
        """
        print(f"[OllamaManager] Verificando si el modelo '{model_name}' está disponible localmente...")
        payload = {"name": model_name}
        try:
            response = requests.post(self.api_show_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
    def uninstall_model(self, model_name: str) -> bool:
        """
        Desinstala un modelo específico usando el endpoint /api/delete de Ollama.
        
        Args:
            model_name (str): Nombre del modelo a desinstalar
            
        Returns:
            bool: True si la desinstalación fue exitosa, False en caso contrario
        """
        print(f"[OllamaManager] Desinstalando modelo '{model_name}'...")
        payload = {"name": model_name}
        try:
            response = requests.delete(self.api_delete_url, json=payload, timeout=30)
            response.raise_for_status()
            print(f"[ollama_manager.py][OllamaManager][uninstall_model] Modelo '{model_name}' desinstalado exitosamente.")
            return True
        except requests.RequestException as e:
            print(f"[OllamaManager] Error al desinstalar el modelo '{model_name}': {e}")
            return False
            # El endpoint devuelve 200 si el modelo existe, 404 si no.
            if response.status_code == 200:
                print(f"[OllamaManager] Modelo '{model_name}' encontrado.")
                return True
            elif response.status_code == 404:
                print(f"[OllamaManager] Modelo '{model_name}' no encontrado localmente.")
                return False
            else:
                # Manejar otros códigos de estado si es necesario
                response.raise_for_status()
                return False
        except requests.RequestException as e:
            print(f"[ollama_manager.py][OllamaManager][is_model_available] Error al verificar el modelo '{model_name}': {e}")
            # Asumir que no está disponible si hay un error de conexión.
            return False

    def pull_model(self, model_name: str, progress_callback=None):
        """
        Descarga un modelo desde el registro de Ollama, con soporte para streaming.
        Invoca un callback con los datos de progreso del stream.
        """
        print(f"[OllamaManager] Iniciando descarga del modelo: '{model_name}'.")
        payload = {"name": model_name, "stream": True}
        try:
            # Usar un timeout largo para la conexión inicial, pero el stream puede durar mucho más.
            response = requests.post(self.api_pull_url, json=payload, stream=True, timeout=30)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    
                    if progress_callback:
                        progress_callback(data)
                    
                    if "error" in data:
                        raise RuntimeError(f"Ollama devolvió un error: {data['error']}")

            print(f"[OllamaManager] Stream del modelo '{model_name}' procesado exitosamente.")

        except Exception as e:
            error_msg = f"Error durante la descarga del modelo '{model_name}': {e}"
            print(f"[OllamaManager] {error_msg}")
            raise RuntimeError(error_msg) from e

    def delete_model(self, model_name: str) -> tuple[bool, str]:
        """
        Elimina un modelo local de Ollama usando el API.
        Devuelve una tupla (éxito, mensaje).
        """
        print(f"[OllamaManager] Solicitando eliminación del modelo: '{model_name}'...")
        payload = {"name": model_name}
        try:
            # Usamos requests.delete para el método HTTP DELETE
            response = requests.delete(self.api_delete_url, json=payload, timeout=60)
            response.raise_for_status() # Lanza excepción para códigos 4xx/5xx
            
            print(f"[OllamaManager] Modelo '{model_name}' eliminado exitosamente.")
            return True, f"Modelo '{model_name}' eliminado con éxito."
        except requests.RequestException as e:
            error_msg = f"Error al eliminar el modelo '{model_name}': {e}"
            print(f"[OllamaManager] {error_msg}")
            return False, error_msg
