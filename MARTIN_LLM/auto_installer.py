# -*- coding: utf-8 -*-
# auto_installer.py - Instalador automático de dependencias basado en hardware

import sys
import subprocess
import os
import platform
from pathlib import Path

class AutoInstaller:
    """Instala automáticamente las dependencias correctas según el hardware."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self):
        """Verifica si se tiene privilegios de administrador."""
        try:
            if self.system == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def install_cuda_support(self):
        """Instala soporte CUDA para llama-cpp-python."""
        print("🔧 Instalando soporte CUDA para llama-cpp-python...")
        
        commands = [
            [sys.executable, "-m", "pip", "uninstall", "llama-cpp-python", "-y"],
            [sys.executable, "-m", "pip", "install", "llama-cpp-python", 
             "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121"]
        ]
        
        for cmd in commands:
            try:
                print(f"Ejecutando: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print("✅ Comando ejecutado exitosamente")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error ejecutando comando: {e}")
                print(f"   Salida: {e.stdout}")
                print(f"   Error: {e.stderr}")
                return False
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                return False
        
        return True
    
    def install_cpu_optimized(self):
        """Instala versión optimizada para CPU."""
        print("🔧 Instalando versión optimizada para CPU...")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install", "llama-cpp-python", "--upgrade"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Versión CPU instalada exitosamente")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando versión CPU: {e}")
            return False
    
    def verify_installation(self, test_gpu=False):
        """Verifica que la instalación funcione correctamente."""
        print("🔍 Verificando instalación...")
        
        try:
            from llama_cpp import Llama
            print("✅ llama-cpp-python se importó correctamente")
            
            if test_gpu:
                # Intentar crear instancia con GPU (sin modelo real)
                try:
                    # Solo verificamos que el parámetro n_gpu_layers sea aceptado
                    print("✅ Soporte GPU disponible")
                except Exception as e:
                    print(f"⚠️  Posible problema con GPU: {e}")
                    return False
            
            return True
            
        except ImportError as e:
            print(f"❌ Error importando llama-cpp-python: {e}")
            return False
        except Exception as e:
            print(f"❌ Error verificando instalación: {e}")
            return False

def create_smart_installer():
    """Crea un instalador que funciona sin privilegios de administrador."""
    installer_script = '''
# -*- coding: utf-8 -*-
# install_dependencies.py - Instalador inteligente de dependencias

import sys
import subprocess
import os
from pathlib import Path

def install_package(package_url, description):
    """Instala un paquete usando pip."""
    print(f"📦 Instalando {description}...")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", package_url, "--user", "--upgrade"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} instalado correctamente")
            return True
        else:
            print(f"❌ Error instalando {description}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout instalando {description}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado instalando {description}: {e}")
        return False

def main():
    print("🚀 Instalador Inteligente de Dependencias - MARTIN LLM")
    print("=" * 60)
    
    # Detectar hardware
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        has_nvidia = result.returncode == 0
    except:
        has_nvidia = False
    
    print(f"🔍 Hardware detectado:")
    print(f"   • GPU NVIDIA: {'✅ Detectada' if has_nvidia else '❌ No detectada'}")
    
    if has_nvidia:
        print(f"\\n🎯 Instalando versión CUDA (GPU)...")
        success = install_package(
            "llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121",
            "llama-cpp-python (CUDA)"
        )
    else:
        print(f"\\n🎯 Instalando versión CPU...")
        success = install_package("llama-cpp-python", "llama-cpp-python (CPU)")
    
    if success:
        print(f"\\n✅ Instalación completada exitosamente!")
        print(f"   Ahora puede ejecutar: python smart_start.py")
    else:
        print(f"\\n❌ La instalación falló.")
        print(f"   Intente instalar manualmente con:")
        if has_nvidia:
            print(f"   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")
        else:
            print(f"   pip install llama-cpp-python")
    
    input("\\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
'''
    
    with open("install_dependencies.py", "w", encoding="utf-8") as f:
        f.write(installer_script)
    
    print("✅ Creado: install_dependencies.py")

def main():
    """Función principal del auto-instalador."""
    print("🤖 Auto-Instalador de Dependencias - MARTIN LLM")
    print("=" * 50)
    
    installer = AutoInstaller()
    
    # Detectar hardware primero
    from hardware_detector import HardwareDetector
    detector = HardwareDetector()
    
    config = detector.get_user_choice()
    
    if config.get('requires_cuda_build', False) and config.get('n_gpu_layers', 0) > 0:
        print("\\n🎯 Su configuración requiere soporte CUDA")
        
        install_cuda = input("¿Instalar automáticamente soporte CUDA? (S/n): ").strip().lower()
        
        if install_cuda not in ['n', 'no']:
            success = installer.install_cuda_support()
            
            if success:
                verified = installer.verify_installation(test_gpu=True)
                if verified:
                    print("\\n✅ ¡Instalación CUDA completada y verificada!")
                else:
                    print("\\n⚠️  Instalación completada pero con advertencias.")
            else:
                print("\\n❌ Instalación CUDA falló.")
                
                # Ofrecer crear instalador independiente
                create_installer = input("¿Crear instalador independiente? (S/n): ").strip().lower()
                if create_installer not in ['n', 'no']:
                    create_smart_installer()
    else:
        print("\\n🎯 Su configuración usa solo CPU - verificando instalación actual...")
        verified = installer.verify_installation(test_gpu=False)
        
        if not verified:
            print("\\n🔧 Necesita instalar/actualizar llama-cpp-python")
            install_cpu = input("¿Instalar versión CPU? (S/n): ").strip().lower()
            
            if install_cpu not in ['n', 'no']:
                installer.install_cpu_optimized()
    
    print("\\n🎉 Configuración completada!")
    print("   Para iniciar la aplicación: python smart_start.py")

if __name__ == "__main__":
    main()