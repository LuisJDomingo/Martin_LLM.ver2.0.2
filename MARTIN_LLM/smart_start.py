# -*- coding: utf-8 -*-
# smart_start.py - Inicio inteligente con detección automática de hardware

import sys
import os
from pathlib import Path

# Añadir la raíz del proyecto al path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from hardware_detector import HardwareDetector

class SmartStart:
    """Sistema de inicio inteligente para MARTIN LLM."""
    
    def __init__(self):
        self.detector = HardwareDetector()
        self.config = None
        
    def initialize(self):
        """Inicializa el sistema con la configuración apropiada."""
        print("🚀 MARTIN LLM - Inicio Inteligente")
        print("="*50)
        
        # Verificar si ya existe configuración
        saved_config = self.detector.load_saved_config()
        
        if saved_config:
            print(f"📋 Configuración existente encontrada: {saved_config.get('description', 'N/A')}")
            
            # Ofrecer opciones: usar existente, reconfigurar, o usar GUI
            print("\n🔧 Opciones:")
            print("   [1] Usar configuración existente")
            print("   [2] Reconfigurar (terminal)")
            print("   [3] Configurador gráfico")
            
            choice = input("\n👆 Seleccione una opción (1/2/3): ").strip()
            
            if choice == '1':
                self.config = saved_config
                print("✅ Usando configuración existente.")
            elif choice == '3':
                self.config = self._launch_gui_config()
            else:
                self.config = self._get_new_config()
        else:
            print("🔧 Primera ejecución - Configurando sistema...")
            print("\n🎨 ¿Cómo desea configurar el sistema?")
            print("   [1] Configurador gráfico (recomendado)")
            print("   [2] Configurador de terminal")
            
            choice = input("\n👆 Seleccione una opción (1/2): ").strip()
            
            if choice == '1' or choice == '':
                self.config = self._launch_gui_config()
            else:
                self.config = self._get_new_config()
        
        return self.config
    
    def _get_new_config(self):
        """Obtiene nueva configuración del usuario."""
        config = self.detector.get_user_choice()
        
        # Guardar configuración
        save_config = input("\n💾 ¿Guardar esta configuración? (S/n): ").strip().lower()
        if save_config not in ['n', 'no']:
            self.detector.save_config(config)
        
        return config
    
    def _launch_gui_config(self, app):
        """Lanza el configurador gráfico."""
        print("🎨 Iniciando configurador gráfico...")
        
        try:
            from hardware_config_gui_v2 import HardwareConfigGUI
            from ui.qt_styles import apply_futuristic_theme
            
            # Crear y mostrar ventana de configuración
            config_window = HardwareConfigGUI()
            config_window.show()
            
            # Ejecutar el diálogo
            config_window.exec()
            
            # Cargar configuración guardada
            saved_config = self.detector.load_saved_config()
            if saved_config:
                print("✅ Configuración guardada desde interfaz gráfica.")
                return saved_config
            else:
                print("⚠️  No se guardó configuración. Usando configuración por defecto.")
                return self._get_default_config()
                
        except ImportError as e:
            print(f"❌ Error: No se pudo cargar la interfaz gráfica: {e}")
            print(f"🔄 Usando configurador de terminal...")
            return self._get_new_config()
        except Exception as e:
            print(f"❌ Error inesperado en interfaz gráfica: {e}")
            print(f"🔄 Usando configurador de terminal...")
            return self._get_new_config()
    
    def _get_default_config(self):
        """Retorna configuración por defecto."""
        return {
            'type': 'default_cpu',
            'n_gpu_layers': 0,
            'n_threads': os.cpu_count(),
            'requires_cuda_build': False,
            'description': 'Configuración por defecto (CPU)'
        }
    
    def start_application(self, app):
        """Inicia la aplicación principal con la configuración seleccionada."""
        config = self.initialize()
        
        print(f"\n🎯 Iniciando MARTIN LLM con configuración:")
        print(f"   • Tipo: {config.get('type', 'unknown')}")
        print(f"   • GPU Layers: {config.get('n_gpu_layers', 0)}")
        print(f"   • CPU Threads: {config.get('n_threads', 'auto')}")
        
        # Verificar si se requiere build CUDA
        if config.get('requires_cuda_build', False) and config.get('n_gpu_layers', 0) > 0:
            print(f"\n⚠️  Esta configuración requiere llama-cpp-python con soporte CUDA")
            self._check_cuda_availability()
        
        # Importar y ejecutar la aplicación principal
        try:
            print(f"\n🚀 Iniciando aplicación principal...")
            
            # Establecer variables de entorno para la configuración
            os.environ['MARTIN_GPU_LAYERS'] = str(config.get('n_gpu_layers', 0))
            os.environ['MARTIN_CPU_THREADS'] = str(config.get('n_threads', os.cpu_count()))
            os.environ['MARTIN_HARDWARE_TYPE'] = config.get('type', 'unknown')
            
            # Importar y ejecutar main_qt (interfaz principal)
            import main_qt
            main_qt.main(app)
            
        except ImportError as e:
            print(f"❌ Error importando la aplicación principal: {e}")
            print(f"   Verificar que todos los archivos estén presentes.")
            return False
        except Exception as e:
            print(f"❌ Error iniciando la aplicación: {e}")
            return False
        
        return True
    
    def _check_cuda_availability(self):
        """Verifica si CUDA está disponible y ofrece ayuda."""
        try:
            # Intentar importar llama_cpp y verificar capacidades
            from llama_cpp import Llama
            
            # Crear una instancia temporal con 1 capa GPU para probar
            test_model_path = "test"  # Solo para verificar importación
            print("✅ llama-cpp-python parece tener soporte GPU")
            
        except Exception as e:
            print(f"\n❌ Problema detectado con soporte GPU: {e}")
            print(f"\n🔧 Para habilitar GPU, ejecute:")
            print(f"   pip uninstall llama-cpp-python")
            print(f"   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")
            
            # Ofrecer continuar con CPU
            continue_cpu = input(f"\n¿Continuar con solo CPU? (S/n): ").strip().lower()
            if continue_cpu in ['n', 'no']:
                print(f"👋 Saliendo... Instale soporte CUDA y vuelva a intentar.")
                sys.exit(0)
            else:
                # Cambiar configuración a solo CPU
                self.config['n_gpu_layers'] = 0
                self.config['type'] = 'fallback_cpu'
                print(f"⚠️  Cambiando a modo CPU únicamente.")

def main():
    """Función principal del inicio inteligente."""
    try:
        starter = SmartStart()
        success = starter.start_application()
        
        if not success:
            print(f"\n❌ La aplicación no pudo iniciarse correctamente.")
            input(f"Presione Enter para salir...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Inicio cancelado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico durante el inicio: {e}")
        import traceback
        traceback.print_exc()
        input(f"Presione Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()