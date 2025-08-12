# -*- coding: utf-8 -*-
# ui/model_manager_widget.py
import re
import os
import subprocess
import sys
import requests
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
                             QListWidget, QPushButton, QMessageBox, QFrame, QWidget,
                             QListWidgetItem, QMenu, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QObject, QThread
from PyQt6.QtGui import QFont, QAction, QColor

# Importaciones absolutas
from app.model_selection import get_local_ollama_models_subprocess, get_online_ollama_models
from app.ollama_manager import OllamaManager

class ModelLoaderWorker(QObject):
    """Worker para cargar listas de modelos en un hilo separado."""
    finished = pyqtSignal(list, list, list, str) # local_gguf_models, ollama_models_details, online_models_names, error_string

    def run(self):
        """Ejecuta la carga de modelos y emite el resultado."""
        local_gguf_files = []
        ollama_models = []
        online_models = []
        error_messages = []

        # 0. Buscar modelos GGUF locales
        try:
            models_dir = "models"
            if os.path.exists(models_dir):
                for filename in os.listdir(models_dir):
                    if filename.lower().endswith(".gguf"):
                        file_path = os.path.join(models_dir, filename)
                        local_gguf_files.append(file_path)
        except Exception as e:
            error_messages.append(f"No se pudieron leer los modelos locales de la carpeta 'models'.\n({e})")

        # 1. Cargar modelos locales desde la API
        try:
            ollama_manager = OllamaManager()
            local_models = ollama_manager.get_local_models()
            for model_data in local_models:
                size_bytes = model_data.get("size", 0)
                size_gb = size_bytes / (1024**3)
                ollama_models.append({
                    'name': model_data['name'],
                    'size': f"{size_gb:.1f} GB"
                })
        except Exception as e:
            error_messages.append(f"No se pudo conectar con el API de Ollama. Asegúrate de que se está ejecutando.\n({e})")

        # 2. Cargar modelos online
        try:
            online_models = get_online_ollama_models()
        except requests.exceptions.RequestException as e:
            error_messages.append(f"No se pudo obtener la lista de modelos online.\nRevisa tu conexión a internet.\n({e})")
        
        self.finished.emit(local_gguf_files, ollama_models, online_models, "\n".join(error_messages))

class InstallWorker(QObject):
    """Worker para instalar modelos en un hilo separado."""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str) # error_msg, model_name

    def __init__(self, model_name):
        print("[ui/model_manager_widget.py] -> InstallWorker.__init__")
        super().__init__()
        self.model_name = model_name

    def run(self): # Ejecuta la instalación del modelo en un hilo separado.
        print(f"PASO 2.2: [ui/model_manager_widget.py] -> InstallWorker.run -> El hilo ha comenzado a ejecutar la tarea para '{self.model_name}'.")
        try:
            print(f"PASO 2.3: [ui/model_manager_widget.py] -> InstallWorker.run -> Ejecutando 'ollama pull {self.model_name}' en un proceso separado.")
            command = ["ollama", "pull", self.model_name]
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            print(f"PASO 2.4: [ui/model_manager_widget.py] -> InstallWorker.run -> Proceso 'ollama pull {self.model_name}' iniciado.")

            full_output = []

            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                # print(f"[ui/model_manager_widget.py] -> InstallWorker.run -> Línea recibida: {line.strip()}") # Descomentar para depuración muy detallada
                full_output.append(line)
                progress_match = re.search(r'(\d+)%', line)
                if progress_match:
                    percentage = int(progress_match.group(1))
                    size_match = re.search(r'(\d+\.?\d*\s[KMGT]?B\s*/\s*\d+\.?\d*\s[KMGT]?B)', line)
                    status_text = size_match.group(1) if size_match else "Descargando..."
                    # print(f"[ui/model_manager_widget.py] -> InstallWorker.run -> Emitiendo progreso: {percentage}%, {status_text}")
                    self.progress_updated.emit(percentage, status_text)
                elif "pulling" in line or "verifying" in line or "writing" in line or "success" in line.lower():
                    # print(f"[ui/model_manager_widget.py] -> InstallWorker.run -> Emitiendo estado: {line}")
                    self.progress_updated.emit(-1, line)
            
            process.stdout.close()
            return_code = process.wait()
            print(f"PASO 7: [ui/model_manager_widget.py] -> InstallWorker.run -> Proceso finalizado con código: {return_code}")

            if return_code == 0:
                print(f"PASO 8: [ui/model_manager_widget.py] -> InstallWorker.run -> Emitiendo señal 'finished' para {self.model_name}")
                self.finished.emit(self.model_name)
            else:
                error_details = f"El proceso 'ollama pull' falló con código {return_code}.\n\nÚltimas líneas:\n{''.join(full_output[-5:])}"
                print(f"PASO 8 (ERROR): [ui/model_manager_widget.py] -> InstallWorker.run -> Emitiendo señal 'error': {error_details}")
                self.error.emit(error_details, self.model_name)
        except Exception as e:
            self.error.emit(str(e), self.model_name)

class ModelManagerWidget(QDialog):
    """Ventana de gestión de modelos en PyQt6"""
    
    # Señales
    model_selected = pyqtSignal(str)  # Emitida cuando se selecciona un modelo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[DEBUG] Creando ModelManagerWidget")
        
        self.setWindowTitle("Gestión de Modelos")
        self.setMinimumSize(500, 400)
              
        # Variables para arrastrar ventana
        self.drag_position = QPoint()
        
        self.selected_model_name = None
        self.install_threads = {}
        self.install_workers = {} # Para mantener una referencia a los workers
        self.install_buttons = []
        
        self.setup_ui()
        self.load_models()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        print("[DEBUG] ModelManagerWidget.setup_ui llamado")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
                
        # Frame principal
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(10)
        
        # Etiqueta de instrucciones
        instruction_label = QLabel("Selecciona modelo:")
        instruction_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        frame_layout.addWidget(instruction_label)
        
        # Lista de modelos
        self.model_list = QListWidget()
        self.model_list.setObjectName("modelList")
        self.model_list.setMinimumHeight(250)
        
        # Conectar eventos
        self.model_list.currentItemChanged.connect(self.on_model_select)
        
        frame_layout.addWidget(self.model_list)
        
        main_layout.addWidget(main_frame)
        
    def load_models(self):
        """Inicia la carga de modelos en un hilo de trabajo."""
        print("[DEBUG] ModelManagerWidget.load_models llamado (iniciando worker)")
        self.model_list.clear()
        self.install_buttons.clear()
        
        # Mostrar un mensaje de carga
        loading_item = QListWidgetItem("Cargando modelos...")
        loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_list.addItem(loading_item)
        self.model_list.setEnabled(False)

        # Crear y ejecutar el worker
        self.loader_thread = QThread()
        self.loader_worker = ModelLoaderWorker()
        self.loader_worker.moveToThread(self.loader_thread)

        self.loader_worker.finished.connect(self.on_models_loaded)
        self.loader_thread.started.connect(self.loader_worker.run)
        
        # Limpieza de recursos
        self.loader_worker.finished.connect(self.loader_thread.quit)
        self.loader_worker.finished.connect(self.loader_worker.deleteLater)
        self.loader_thread.finished.connect(self.loader_thread.deleteLater)

        self.loader_thread.start()

    def on_models_loaded(self, local_gguf_models, ollama_models_details, online_models_names, error_string):
        """Puebla la lista de modelos cuando el worker ha terminado."""
        print("[DEBUG] ModelManagerWidget.on_models_loaded llamado")
        self.model_list.clear()
        self.model_list.setEnabled(True)

        if error_string:
            # No mostrar como error crítico si solo falla la conexión a Ollama pero hay modelos locales
            if not local_gguf_models and not ollama_models_details:
                 QMessageBox.warning(self, "Error de Carga", error_string)

        # --- Añadir modelos locales GGUF ---
        for model_path in sorted(local_gguf_models):
            size_bytes = os.path.getsize(model_path)
            size_gb = size_bytes / (1024**3)
            self.add_model_widget(model_path, is_local=True, size=f"{size_gb:.1f} GB")

        # --- Añadir modelos de Ollama instalados ---
        for model_info in sorted(ollama_models_details, key=lambda x: x['name']):
            self.add_model_widget(model_info['name'], is_local=True, size=model_info['size'])

        # --- Añadir modelos online que no están en local ---
        installed_ollama_names = {m['name'] for m in ollama_models_details}
        installed_ollama_base_names = {m['name'].split(':')[0] for m in ollama_models_details}

        for model_name in sorted(online_models_names):
            # No mostrar un modelo online si ya está instalado exactamente con el mismo nombre/tag
            if model_name in installed_ollama_names:
                continue

            # Evitar mostrar alias genéricos (sin tag) si ya tenemos cualquier versión de ese modelo
            is_alias = ':' not in model_name
            if is_alias and model_name in installed_ollama_base_names:
                continue
            
            self.add_model_widget(model_name, is_local=False, size="Remoto")
        
        if self.model_list.count() == 0 and not error_string:
            no_models_item = QListWidgetItem("No se encontraron modelos.")
            no_models_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_list.addItem(no_models_item)

    def start_model_installation(self, model_name, install_button, progress_bar):
        """Inicia la instalación de un modelo en un hilo de trabajo."""
        print(f"PASO 1: [ui/model_manager_widget.py] -> ModelManagerWidget.start_model_installation -> Botón 'Instalar' para '{model_name}' presionado.")
        install_button.setVisible(False)
        progress_bar.setVisible(True)
        self.set_install_buttons_enabled(False)
        print(f"PASO 2: [ui/model_manager_widget.py] -> ModelManagerWidget.start_model_installation -> Creando QThread y InstallWorker para '{model_name}'.")

        thread = QThread()
        worker = InstallWorker(model_name)
        worker.moveToThread(thread)

        worker.progress_updated.connect(
            lambda p, s, pb=progress_bar: self.update_progress(pb, p, s)
        )
        worker.finished.connect(self.on_install_finished)
        worker.error.connect(self.on_install_error)
        print(f"PASO 2.1: [ui/model_manager_widget.py] -> ModelManagerWidget.start_model_installation -> Conectando señales del worker para '{model_name}'.")
        thread.started.connect(worker.run)
        
        # Conectar para limpieza de recursos
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        self.install_threads[model_name] = thread # Guardar referencia
        self.install_workers[model_name] = worker # Guardar referencia
        thread.start()
        print(f"PASO 3: [ui/model_manager_widget.py] -> ModelManagerWidget.start_model_installation -> Hilo iniciado para '{model_name}'.")

    def update_progress(self, progress_bar, percentage, status_text):
        """Actualiza una barra de progreso específica."""
        # print(f"PASO 6: [ui/model_manager_widget.py] -> ModelManagerWidget.update_progress -> Actualizando barra: {percentage}%, {status_text}")
        if percentage >= 0:
            progress_bar.setValue(percentage)
            progress_bar.setFormat(f"{status_text} ({percentage}%)")
        else:
            progress_bar.setFormat(status_text)

    def on_install_finished(self, model_name):
        """Se ejecuta cuando la instalación finaliza con éxito."""
        print(f"PASO 9: [ui/model_manager_widget.py] -> ModelManagerWidget.on_install_finished -> Instalación de {model_name} finalizada con éxito.")
        QMessageBox.information(self, "Éxito", f"Modelo {model_name} instalado.")
        self.set_install_buttons_enabled(True)
        print(f"PASO 10: [ui/model_manager_widget.py] -> ModelManagerWidget.on_install_finished -> Recargando lista de modelos...")
        # Limpiar referencias para permitir la recolección de basura
        if model_name in self.install_threads:
            del self.install_threads[model_name]
        if model_name in self.install_workers:
            del self.install_workers[model_name]
        self.load_models()

    def on_install_error(self, error_msg, model_name):
        """Se ejecuta si hay un error en la instalación."""
        print(f"PASO 9 (ERROR): [ui/model_manager_widget.py] -> ModelManagerWidget.on_install_error -> Error de instalación: {error_msg}")
        QMessageBox.critical(self, "Error de Instalación", f"No se pudo instalar el modelo '{model_name}':\n{error_msg}")
        self.set_install_buttons_enabled(True)
        print(f"PASO 10 (ERROR): [ui/model_manager_widget.py] -> ModelManagerWidget.on_install_error -> Recargando lista de modelos...")
        # Limpiar referencias para permitir la recolección de basura
        if model_name in self.install_threads:
            del self.install_threads[model_name]
        if model_name in self.install_workers:
            del self.install_workers[model_name]
        self.load_models()

    def use_model(self, model_name):
        """Emite la señal para usar el modelo seleccionado y cierra el diálogo."""
        print(f"[DEBUG] Usando modelo {model_name}")
        self.selected_model_name = model_name
        self.model_selected.emit(model_name)
        self.close()

    def uninstall_model_action(self, model_name):
        """Maneja la lógica para desinstalar un modelo."""
        reply = QMessageBox.question(self, "Confirmar Desinstalación",
                                     f"¿Estás seguro de que quieres desinstalar el modelo {model_name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                ollama_manager = OllamaManager()
                if ollama_manager.uninstall_model(model_name):
                    QMessageBox.information(self, "Éxito", f"Modelo {model_name} desinstalado.")
                    # Recargar la lista para reflejar el cambio
                    self.load_models()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo desinstalar el modelo")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo desinstalar el modelo:\n{e}")
            finally:
                QApplication.restoreOverrideCursor()


    def add_model_widget(self, model_identifier, is_local, size=""):
        """Agrega un widget personalizado para cada fila de la lista."""
        item = QListWidgetItem()

        # 💾 Guardamos el nombre del modelo en el item, ya que no usaremos .text()
        item.setData(Qt.ItemDataRole.UserRole, model_identifier)

        # El widget contenedor para cada fila
        row_widget = QWidget()
        row_widget.setObjectName("modelRowWidget")
        # Forzar una altura mínima para la fila para asegurar que el contenido no se corte
        row_widget.setMinimumHeight(45)
        # El estilo de fondo y borde se controla desde qt_styles.py

        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Mostrar solo el nombre base para rutas de archivo
        display_name = os.path.basename(model_identifier)
        label = QLabel(display_name)
        label.setFont(QFont("Segoe UI", 11))

        # Etiqueta para el tamaño
        size_label = QLabel(size)
        size_label.setFont(QFont("Segoe UI", 10))
        size_label.setStyleSheet("color: #a0aec0;")
        size_label.setFixedWidth(80)
        size_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()
        layout.addWidget(size_label, 0, Qt.AlignmentFlag.AlignVCenter)

        if is_local:
            is_gguf = model_identifier.lower().endswith('.gguf')

            # El botón de desinstalar solo tiene sentido para modelos de Ollama
            if not is_gguf:
                uninstall_button = QPushButton("Desinstalar")
                uninstall_button.setFixedWidth(90)
                uninstall_button.setMinimumHeight(30)
                uninstall_button.setObjectName("uninstallModelButton")
                uninstall_button.clicked.connect(lambda checked=False, mn=model_identifier: self.uninstall_model_action(mn))
                layout.addWidget(uninstall_button, 0, Qt.AlignmentFlag.AlignVCenter)

            # --- Botón Usar ---
            use_button = QPushButton("Usar")
            use_button.setFixedWidth(90)
            use_button.setMinimumHeight(30)
            use_button.setObjectName("useModelButton")
            # Conectar el botón para usar cualquier modelo local (GGUF u Ollama)
            use_button.clicked.connect(lambda checked=False, mi=model_identifier: self.use_model(mi))
            layout.addWidget(use_button, 0, Qt.AlignmentFlag.AlignVCenter)
        else:
            # --- Botón Instalar ---
            install_button = QPushButton("Instalar")
            install_button.setFixedWidth(90)
            install_button.setMinimumHeight(30)
            self.install_buttons.append(install_button)

            # --- Barra de Progreso ---
            progress_bar = QProgressBar()
            progress_bar.setObjectName("downloadProgressBar")
            progress_bar.setFixedWidth(190)
            progress_bar.setMinimumHeight(30)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat("%p%")
            progress_bar.setVisible(False)

            # Conectar el botón a un método de la clase usando lambda para pasar los argumentos correctos
            install_button.clicked.connect(
                lambda checked=False, mn=model_identifier, btn=install_button, pb=progress_bar:
                    self.start_model_installation(mn, btn, pb)
            )

            layout.addWidget(install_button, 0, Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(progress_bar, 0, Qt.AlignmentFlag.AlignVCenter)
        # Establecer un tamaño adecuado para la fila
        item.setSizeHint(row_widget.sizeHint())
        self.model_list.addItem(item)
        self.model_list.setItemWidget(item, row_widget)

    def on_model_select(self, current_item, previous_item):
        """Maneja la selección de un modelo"""
        # El argumento `previous_item` es requerido por la señal, pero no lo usamos.
        item = current_item
        if not item:
            return
            
        # Se obtiene el nombre del modelo de los datos del item, no del texto.
        model_name = item.data(Qt.ItemDataRole.UserRole)
        if not model_name:
            return

        self.selected_model_name = model_name
        print(f"[DEBUG] Fila seleccionada: {model_name}")
        
    def set_install_buttons_enabled(self, enabled):
        """Habilita o deshabilita todos los botones de instalación."""
        for button in self.install_buttons:
            button.setEnabled(enabled)
                
    def get_selected_model(self):
        """Retorna el modelo seleccionado"""
        return self.selected_model_name
        
    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        print("[DEBUG] ModelManagerWidget.closeEvent llamado")
        if self.install_threads: # Si el diccionario no está vacío, hay descargas.
            reply = QMessageBox.question(
                self,
                "Descarga en Progreso",
                "Hay descargas de modelos en curso. ¿Estás seguro de que quieres cerrar esta ventana y cancelarlas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()  # Aceptar el cierre, se cancelarán las descargas.
            else:
                event.ignore()  # Ignorar el cierre, la ventana permanece abierta.
        else:
            event.accept() # No hay descargas, cerrar normalmente.
