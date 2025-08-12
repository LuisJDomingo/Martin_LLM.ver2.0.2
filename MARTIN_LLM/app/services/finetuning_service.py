# -*- coding: utf-8 -*-
# app/services/finetuning_service.py

import os
import re
import subprocess
import sys
import tempfile
from PyQt6.QtCore import QObject, pyqtSignal

class FinetuningWorker(QObject):
    """Worker para ejecutar el proceso de fine-tuning de Ollama en un hilo separado."""
    progress_updated = pyqtSignal(int, str) # percentage, message
    finished = pyqtSignal(bool, str) # success, message

    def __init__(self, base_model: str, new_model_name: str, training_data: str):
        super().__init__()
        self.base_model = base_model
        self.new_model_name = new_model_name
        self.training_data = training_data
        self.process = None
        self._is_stopped = False

    def stop(self):
        """Solicita la detención del proceso de fine-tuning."""
        self._is_stopped = True
        if self.process:
            print("[FinetuningWorker] Solicitud de detención recibida, terminando proceso.")
            self.process.terminate()

    def run(self):
        temp_dir = tempfile.mkdtemp()
        data_file_path = os.path.join(temp_dir, "training_data.jsonl")
        modelfile_path = os.path.join(temp_dir, "Modelfile")

        try:
            # 1. Escribir los datos de entrenamiento a un archivo temporal
            self.progress_updated.emit(0, "Guardando datos de entrenamiento...")
            with open(data_file_path, "w", encoding="utf-8") as f:
                f.write(self.training_data)

            # 2. Crear el Modelfile
            self.progress_updated.emit(5, "Creando Modelfile...")
            # La instrucción 'PARAMETER train' no es válida en un Modelfile de Ollama.
            # 'ollama create' no realiza entrenamiento en un dataset, sino que crea variantes
            # de un modelo (ej. con un nuevo system prompt) o aplica adaptadores.
            modelfile_content = f"FROM {self.base_model}"
            with open(modelfile_path, "w", encoding="utf-8") as f:
                f.write(modelfile_content)

            # 3. Ejecutar 'ollama create'
            self.progress_updated.emit(10, f"Iniciando 'ollama create' para {self.new_model_name}...")
            command = ["ollama", "create", self.new_model_name, "-f", modelfile_path]
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            # 4. Leer la salida del proceso en tiempo real
            full_output = []
            for line in iter(self.process.stdout.readline, ''):
                if self._is_stopped:
                    break
                
                line = line.strip()
                percentage = -1
                status_text = line
                full_output.append(line)

                progress_match = re.search(r'(\d+)%', line)
                if progress_match:
                    percentage = int(progress_match.group(1))
                    status_text = "Descargando capas..."
                elif "success" in line.lower():
                    percentage = 100
                    status_text = "Finalizado con éxito"
                elif "writing manifest" in line:
                    percentage = 95
                    status_text = "Escribiendo manifiesto"
                elif "verifying sha256" in line:
                    percentage = 90
                    status_text = "Verificando checksum"

                self.progress_updated.emit(percentage, status_text)

            self.process.stdout.close()
            return_code = self.process.wait()

            if self._is_stopped:
                self.finished.emit(False, "Proceso de fine-tuning cancelado por el usuario.")
            elif return_code == 0:
                self.finished.emit(True, f"Modelo '{self.new_model_name}' creado con éxito.")
            else:
                error_details = "\n".join(full_output)
                self.finished.emit(False, f"El proceso de fine-tuning falló con código {return_code}.\n\nDetalles:\n{error_details}")

        except Exception as e:
            self.finished.emit(False, f"Error inesperado durante el fine-tuning: {e}")
        finally:
            # Limpieza de archivos temporales
            try:
                if os.path.exists(data_file_path): os.remove(data_file_path)
                if os.path.exists(modelfile_path): os.remove(modelfile_path)
                os.rmdir(temp_dir)
            except OSError as e:
                print(f"Error limpiando archivos temporales: {e}")