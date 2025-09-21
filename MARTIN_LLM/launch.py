# -*- coding: utf-8 -*-
# launch.py - Lanzador principal de MARTIN LLM con interfaz gráfica

"""
MARTIN LLM - Lanzador Principal
==============================

Este es el punto de entrada principal para MARTIN LLM.
Proporciona una experiencia de usuario simplificada con:

- Configuración automática de hardware
- Interfaz gráfica intuitiva 
- Detección inteligente de GPU/CPU
- Instalación automática de dependencias

Uso:
    python launch.py

Para usuarios finales, simplemente hacer doble clic en este archivo.
"""

import sys
import os
from pathlib import Path

# Configurar path del proyecto
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def check_dependencies():
    """Verifica dependencias básicas."""
    missing_deps = []
    
    # Verificar PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PyQt6")
    
    # Verificar llama-cpp-python
    try:
        from llama_cpp import Llama
    except ImportError:
        missing_deps.append("llama-cpp-python")
    
    return missing_deps

def show_welcome_gui():
    """Muestra ventana de bienvenida y configuración."""
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                                    QVBoxLayout, QLabel, QPushButton, 
                                    QMessageBox, QProgressBar, QFrame)
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QFont, QPalette, QColor
        
        class WelcomeWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("🚀 MARTIN LLM - Bienvenido")
                self.setFixedSize(600, 400)
                self.setStyleSheet(self.get_style())
                
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)
                layout.setContentsMargins(40, 40, 40, 40)
                layout.setSpacing(20)
                
                # Header
                header = QFrame()
                header.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #2196F3, stop:1 #1976D2);
                        border-radius: 15px;
                        padding: 20px;
                    }
                """)
                header_layout = QVBoxLayout(header)
                
                title = QLabel("🚀 MARTIN LLM")
                title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
                title.setStyleSheet("color: white; background: transparent;")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                subtitle = QLabel("Asistente de Lenguaje Inteligente")
                subtitle.setFont(QFont("Segoe UI", 14))
                subtitle.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
                subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                header_layout.addWidget(title)
                header_layout.addWidget(subtitle)
                layout.addWidget(header)
                
                # Descripción
                desc = QLabel(
                    "🎯 MARTIN LLM detectará automáticamente su hardware y "
                    "configurará la mejor experiencia para su sistema.\\n\\n"
                    "✅ Detección automática de GPU/CPU\\n"
                    "⚡ Configuración optimizada\\n"
                    "🔧 Instalación automática de dependencias"
                )
                desc.setFont(QFont("Segoe UI", 12))
                desc.setStyleSheet("color: #333; padding: 20px; background: #f5f5f5; border-radius: 10px;")
                desc.setWordWrap(True)
                layout.addWidget(desc)
                
                # Botones
                self.config_btn = QPushButton("🔧 Configurar Hardware")
                self.config_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self.config_btn.setStyleSheet(self.get_button_style("#2196F3"))
                self.config_btn.clicked.connect(self.launch_config)
                
                self.direct_btn = QPushButton("🚀 Inicio Directo")
                self.direct_btn.setFont(QFont("Segoe UI", 12))
                self.direct_btn.setStyleSheet(self.get_button_style("#4CAF50"))
                self.direct_btn.clicked.connect(self.direct_launch)
                
                layout.addWidget(self.config_btn)
                layout.addWidget(self.direct_btn)
                
                # Info
                info = QLabel("💡 Sugerencia: Use 'Configurar Hardware' en la primera ejecución")
                info.setFont(QFont("Segoe UI", 10))
                info.setStyleSheet("color: #666; font-style: italic;")
                info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(info)
            
            def get_style(self):
                return """
                    QMainWindow {
                        background-color: #ffffff;
                    }
                    QWidget {
                        background-color: #ffffff;
                        color: #333333;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }
                """
            
            def get_button_style(self, color):
                return f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        border-radius: 10px;
                        font-size: 14px;
                        min-height: 20px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.darken_color(color)};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.darken_color(color, 0.8)};
                    }}
                """
            
            def darken_color(self, color, factor=0.9):
                color = color.lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                rgb = tuple(int(c * factor) for c in rgb)
                return '#%02x%02x%02x' % rgb
            
            def launch_config(self):
                """Lanza el configurador de hardware."""
                try:
                    from hardware_config_gui_v4 import HardwareConfigDialog as HardwareConfigGUI
                    from ui.qt_styles import apply_futuristic_theme
                    self.hide()
                    config_window = HardwareConfigGUI()
                    config_window.show()
                    # No cerrar esta ventana, por si el usuario cancela
                except Exception as e:
                    QMessageBox.critical(self, "Error", 
                        f"No se pudo cargar el configurador:\\n{str(e)}")
            
            def direct_launch(self):
                """Lanza directamente la aplicación."""
                try:
                    from smart_start import SmartStart
                    self.close()
                    starter = SmartStart()
                    starter.start_application()
                except Exception as e:
                    QMessageBox.critical(self, "Error", 
                        f"No se pudo iniciar la aplicación:\\n{str(e)}")
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = WelcomeWindow()
        window.show()
        
        return app.exec()
        
    except ImportError:
        return None

def show_welcome_console():
    """Muestra bienvenida en consola si no hay GUI disponible."""
    print("="*60)
    print("🚀 MARTIN LLM - Asistente de Lenguaje Inteligente")
    print("="*60)
    print()
    print("🎯 MARTIN LLM detectará su hardware automáticamente")
    print("   y configurará la mejor experiencia para su sistema.")
    print()
    print("✅ Detección automática de GPU/CPU")
    print("⚡ Configuración optimizada") 
    print("🔧 Instalación automática de dependencias")
    print()
    print("="*60)
    
    choice = input("¿Continuar? (S/n): ").strip().lower()
    if choice in ['n', 'no']:
        print("👋 ¡Hasta luego!")
        return False
    
    return True

def main():
    """Función principal del lanzador."""
    print("🚀 Iniciando MARTIN LLM...")
    
    # Verificar dependencias críticas
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Faltan dependencias: {', '.join(missing)}")
        print("📦 Ejecute: pip install -r requirements.txt")
        
        install = input("¿Intentar instalar automáticamente? (s/N): ").strip().lower()
        if install in ['s', 'si', 'sí', 'y', 'yes']:
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True)
                print("✅ Dependencias instaladas. Reiniciando...")
            except Exception as e:
                print(f"❌ Error instalando dependencias: {e}")
                return 1
        else:
            return 1
    
    # Intentar mostrar interfaz gráfica
    if 'PyQt6' not in missing:
        print("🎨 Cargando interfaz gráfica...")
        result = show_welcome_gui()
        if result is not None:
            return 0
    
    # Fallback a interfaz de consola
    print("🖥️  Usando interfaz de consola...")
    if not show_welcome_console():
        return 0
    
    try:
        from smart_start import SmartStart
        starter = SmartStart()
        success = starter.start_application()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n👋 Cancelado por el usuario.")
        return 0
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
        return 1

if __name__ == "__main__":
    sys.exit(main())