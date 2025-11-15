# -*- coding: utf-8 -*-
# ui/conversation_load_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                             QDialogButtonBox, QListWidgetItem, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from .custom_widgets import show_warning_message

class ConversationLoadDialog(QDialog):
    """Dialog to select and load a conversation."""
    
    conversation_selected = pyqtSignal(str)

    def __init__(self, conversations, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cargar Conversación")
        self.setMinimumSize(450, 350)
        
        self.conversations = conversations
        self.selected_conv_id = None
        
        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Haz doble clic en una conversación para cargarla.")
        info_label.setStyleSheet("color: #90cdf4; margin-bottom: 5px;")
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_list(self):
        """Llena la lista con las conversaciones."""
        self.list_widget.clear()
        # Ordenar conversaciones por fecha, de más reciente a más antigua
        sorted_convs = sorted(self.conversations, key=lambda x: x.get('timestamp', datetime.min), reverse=True)

        for conv in sorted_convs:
            title = conv.get("title", "Sin título")
            timestamp = conv.get("timestamp", datetime.now())
            
            if isinstance(timestamp, datetime):
                date_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = "Fecha desconocida"

            item_text = f"{date_str} - {title}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, str(conv.get("_id")))
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        """Guarda el ID de la conversación seleccionada."""
        self.selected_conv_id = item.data(Qt.ItemDataRole.UserRole)

    def accept(self):
        """Confirma la selección."""
        if not self.selected_conv_id and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            self.selected_conv_id = self.list_widget.currentItem().data(Qt.ItemDataRole.UserRole)

        if not self.selected_conv_id:
            show_warning_message(self, "Sin selección", "Por favor, selecciona una conversación.")
            return
            
        super().accept()

    def get_selected_conversation_id(self):
        """Devuelve el ID de la conversación seleccionada."""
        return self.selected_conv_id