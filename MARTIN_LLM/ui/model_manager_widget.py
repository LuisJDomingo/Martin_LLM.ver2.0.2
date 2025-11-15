# -*- coding: utf-8 -*- 
# ui/model_manager_widget.py
import json
import os
import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QMessageBox, QFrame, QWidget, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont
from ui.custom_widgets import FramelessWindowMixin, CustomTitleBar
from pathlib import Path

class ModelLoaderWorker(QObject):
    """Worker to load model lists in a separate thread."""
    finished = pyqtSignal(list, list, str)  # catalog_models, installed_models, error_string
    

    def run(self):
        """Executes model loading and emits the result."""
        catalog_models = []
        installed_models = []
        error_messages = []

        # 1. Load models from models.json
        try:
            with open('models.json', 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
                catalog_models = catalog_data.get('models', [])
        except FileNotFoundError:
            error_messages.append("El archivo 'models.json' no fue encontrado.")
        except json.JSONDecodeError:
            error_messages.append("Error al decodificar 'models.json'.")
        except Exception as e:
            error_messages.append(f"Error al leer 'models.json': {e}")

        # 2. Load installed models by checking for GGUF files in ./models
        try:
            models_dir = Path("models")
            if models_dir.exists():
                installed_models = [f.name for f in models_dir.iterdir() if f.is_file() and f.suffix.lower() == ".gguf"]
        except Exception as e:
            error_messages.append(f"Error al leer la carpeta de modelos: {e}")

        self.finished.emit(catalog_models, installed_models, "\n".join(error_messages))


class DownloadWorker(QObject):
    """Worker to download models from a URL."""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)

    def __init__(self, model_name, download_url, download_path):
        super().__init__()
        self.model_name = model_name
        self.download_url = download_url
        self.download_path = download_path

    def run(self):
        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded_size = 0

            with open(self.download_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded_size += len(data)
                    f.write(data)
                    if total_size > 0:
                        percentage = int(downloaded_size / total_size * 100)
                        completed_gb = downloaded_size / (1024**3)
                        total_gb = total_size / (1024**3)
                        status_text = f"{completed_gb:.2f} GB / {total_gb:.2f} GB"
                        self.progress_updated.emit(percentage, status_text)
                    else:
                        # indeterminate progress
                        self.progress_updated.emit(-1, f"{downloaded_size / (1024**2):.2f} MB")
            
            self.finished.emit(self.model_name)

        except Exception as e:
            self.error.emit(str(e), self.model_name)


class ModelCard(QFrame):
    """A card widget to display model information."""
    def __init__(self, model_data, is_installed, manager, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.is_installed = is_installed
        self.manager = manager
        self.setObjectName("modelCard")
        self.setup_ui()

    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            #modelCard {
                background-color: #2d3748;
                border-radius: 8px;
                border: 1px solid #4a5568;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Header ---
        header_layout = QHBoxLayout()
        name_label = QLabel(self.model_data.get('name', 'N/A'))
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        tags = self.model_data.get('tags', [])
        for tag in tags:
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("""
                background-color: #63b3ed;
                color: white;
                border-radius: 5px;
                padding: 2px 6px;
                font-size: 9pt;
            """)
            header_layout.addWidget(tag_label)

        main_layout.addLayout(header_layout)

        # --- Description ---
        desc_label = QLabel(self.model_data.get('description', ''))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #e2e8f0;")
        main_layout.addWidget(desc_label)

        # --- Details ---
        details_frame = QFrame()
        details_layout = QHBoxLayout(details_frame)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(20)

        def add_detail(label, value):
            v_layout = QVBoxLayout()
            v_layout.setSpacing(0)
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #a0aec0;")
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 10))
            v_layout.addWidget(lbl)
            v_layout.addWidget(val)
            details_layout.addLayout(v_layout)

        add_detail("Parámetros", self.model_data.get('parameters', 'N/A'))
        add_detail("Tamaño", self.model_data.get('size', 'N/A'))
        add_detail("Cuantización", self.model_data.get('quantization', 'N/A'))
        add_detail("Contexto", self.model_data.get('context_length', 'N/A'))
        
        main_layout.addWidget(details_frame)
        
        # --- Full Details ---
        details_text = QLabel(self.model_data.get('details', ''))
        details_text.setWordWrap(True)
        details_text.setStyleSheet("color: #e2e8f0; font-size: 9pt;")
        main_layout.addWidget(details_text)


        # --- Action Buttons ---
        self.button_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setTextVisible(True)

        self.install_button = QPushButton("Instalar")
        self.install_button.setObjectName("installModelButton")
        self.install_button.clicked.connect(self.install_model)

        self.use_button = QPushButton("Usar")
        self.use_button.setObjectName("useModelButton")
        self.use_button.clicked.connect(self.use_model)
        
        self.uninstall_button = QPushButton("Desinstalar")
        self.uninstall_button.setObjectName("uninstallModelButton")
        self.uninstall_button.clicked.connect(self.uninstall_model)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.progress_bar)
        self.button_layout.addWidget(self.install_button)
        self.button_layout.addWidget(self.use_button)
        self.button_layout.addWidget(self.uninstall_button)
        
        self.update_button_state()

        main_layout.addLayout(self.button_layout)

    def update_button_state(self):
        self.install_button.setVisible(not self.is_installed)
        self.use_button.setVisible(self.is_installed)
        self.uninstall_button.setVisible(self.is_installed)
        self.progress_bar.setVisible(False)

    def install_model(self):
        self.install_button.setVisible(False)
        self.progress_bar.setVisible(True)
        self.manager.start_model_installation(self.model_data, self)

    def use_model(self):
        download_url = self.model_data.get('download_url', '')
        filename = download_url.split('/')[-1]
        model_path = Path("models") / filename
        self.manager.use_model(str(model_path.resolve()))

    def uninstall_model(self):
        self.manager.uninstall_model_action(self.model_data)

    def update_progress(self, percentage, status_text):
        if percentage >= 0:
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{status_text} ({percentage}%)")
        else:
            self.progress_bar.setFormat(status_text)

    def set_installed_state(self, installed):
        self.is_installed = installed
        self.update_button_state()


class ModelManagerWidget(QDialog, FramelessWindowMixin):
    model_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_frameless_mixin()
        self.setMinimumSize(800, 600)
        self.install_threads = {}
        self.install_workers = {}
        self.model_cards = {}
        self.setup_ui()
        self.load_models()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, "Gestión de Modelos", show_max_min=False)
        main_layout.addWidget(self.title_bar)

        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet("background-color: #2d3748; color: white;")
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.scroll_widget = QWidget()
        self.models_layout = QVBoxLayout(self.scroll_widget)
        self.models_layout.setSpacing(15)
        self.models_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.scroll_widget)
        frame_layout.addWidget(scroll_area)
        main_layout.addWidget(main_frame)

    def load_models(self):
        # Clear existing cards
        for i in reversed(range(self.models_layout.count())):
            self.models_layout.itemAt(i).widget().setParent(None)
        self.model_cards.clear()

        loading_label = QLabel("Cargando modelos...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.models_layout.addWidget(loading_label)

        self.loader_thread = QThread()
        self.loader_worker = ModelLoaderWorker()
        self.loader_worker.moveToThread(self.loader_thread)
        self.loader_worker.finished.connect(self.on_models_loaded)
        self.loader_thread.started.connect(self.loader_worker.run)
        self.loader_worker.finished.connect(self.loader_thread.quit)
        self.loader_worker.finished.connect(self.loader_worker.deleteLater)
        self.loader_thread.finished.connect(self.loader_thread.deleteLater)
        self.loader_thread.start()

    def on_models_loaded(self, catalog_models, installed_models, error_string):
        # Clear loading message
        for i in reversed(range(self.models_layout.count())):
            self.models_layout.itemAt(i).widget().setParent(None)

        if error_string and not catalog_models:
            QMessageBox.warning(self, "Error de Carga", error_string)
            error_label = QLabel(error_string)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.models_layout.addWidget(error_label)
            return

        for model_data in catalog_models:
            download_url = model_data.get('download_url', '')
            if not download_url:
                continue # Don't show models without a download url
            
            filename = download_url.split('/')[-1]
            is_installed = filename in installed_models
            
            card = ModelCard(model_data, is_installed, self)
            self.models_layout.addWidget(card)
            self.model_cards[model_data['name']] = card

        if not self.model_cards:
            no_models_label = QLabel("No hay modelos definidos en 'models.json' con URLs de descarga.")
            no_models_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.models_layout.addWidget(no_models_label)

    def start_model_installation(self, model_data, card):
        self.set_all_buttons_enabled(False)
        
        download_url = model_data.get('download_url')
        if not download_url:
            QMessageBox.critical(self, "Error", "No hay URL de descarga para este modelo.")
            self.set_all_buttons_enabled(True)
            return

        model_name = model_data['name']
        filename = download_url.split('/')[-1]
        download_path = Path("models") / filename
        
        # Create models directory if it doesn't exist
        download_path.parent.mkdir(parents=True, exist_ok=True)

        thread = QThread()
        worker = DownloadWorker(model_name, download_url, str(download_path))
        worker.moveToThread(thread)

        worker.progress_updated.connect(card.update_progress)
        worker.finished.connect(lambda model_name: self.on_install_finished(model_name, card))
        worker.error.connect(lambda error_msg, model_name: self.on_install_error(error_msg, model_name, card))
        
        thread.started.connect(worker.run)
        
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        self.install_threads[model_name] = thread
        self.install_workers[model_name] = worker
        thread.start()

    def on_install_finished(self, model_name, card):
        QMessageBox.information(self, "Éxito", f"Modelo {model_name} instalado.")
        card.set_installed_state(True)
        self.cleanup_install_thread(model_name)
        self.set_all_buttons_enabled(True)

    def on_install_error(self, error_msg, model_name, card):
        QMessageBox.critical(self, "Error de Instalación", f"No se pudo instalar el modelo '{model_name}':\n{error_msg}")
        card.update_button_state() # Revert to install button
        self.cleanup_install_thread(model_name)
        self.set_all_buttons_enabled(True)

    def cleanup_install_thread(self, model_name):
        if model_name in self.install_threads:
            del self.install_threads[model_name]
        if model_name in self.install_workers:
            del self.install_workers[model_name]

    def use_model(self, model_path):
        self.model_selected.emit(model_path)
        self.close()

    def uninstall_model_action(self, model_data):
        model_name = model_data['name']
        download_url = model_data.get('download_url', '')
        filename = download_url.split('/')[-1]
        model_path = Path("models") / filename

        reply = QMessageBox.question(self, "Confirmar Desinstalación",
                                     f"¿Estás seguro de que quieres desinstalar el modelo {model_name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                if model_path.exists():
                    model_path.unlink()
                    QMessageBox.information(self, "Éxito", f"Modelo {model_name} desinstalado.")
                    if model_name in self.model_cards:
                        self.model_cards[model_name].set_installed_state(False)
                else:
                    QMessageBox.critical(self, "Error", "El archivo del modelo no existe.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo desinstalar el modelo:\n{e}")
            finally:
                QApplication.restoreOverrideCursor()

    def set_all_buttons_enabled(self, enabled):
        for card in self.model_cards.values():
            card.install_button.setEnabled(enabled)
            card.use_button.setEnabled(enabled)
            card.uninstall_button.setEnabled(enabled)

    def closeEvent(self, event):
        if self.install_threads:
            reply = QMessageBox.question(
                self, "Descarga en Progreso",
                "Hay descargas de modelos en curso. ¿Seguro que quieres cerrar y cancelar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()