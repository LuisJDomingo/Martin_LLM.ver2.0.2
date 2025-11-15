#!/usr/bin/env python3
"""
Script para verificar que todas las dependencias offline estén disponibles
"""
import sys
import importlib
from pathlib import Path

def check_module(module_name, description=""):
    """Verifica si un módulo está disponible"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError:
        print(f"❌ {module_name} - {description} - NO ENCONTRADO")
        return False

def check_file(file_path, description=""):
    """Verifica si un archivo existe"""
    if Path(file_path).exists():
        print(f"✅ {file_path} - {description}")
        return True
    else:
        print(f"❌ {file_path} - {description} - NO ENCONTRADO")
        return False

def main():
    print("🔍 Verificando dependencias para aplicación offline...")
    print("=" * 60)
    
    all_ok = True
    
    # Dependencias críticas para funcionamiento offline
    critical_modules = [
        ("llama_cpp", "Motor de inferencia local"),
        ("PySide6", "Interfaz gráfica"),
        ("sqlite3", "Base de datos local"),
        ("numpy", "Operaciones matemáticas"),
    ]
    
    print("\n📋 Módulos críticos:")
    for module, desc in critical_modules:
        if not check_module(module, desc):
            all_ok = False
    
    # Archivos críticos
    critical_files = [
        ("run.py", "Archivo principal"),
        ("app/", "Código de aplicación"),
        ("ui/", "Interfaz de usuario"),
        (".env", "Variables de entorno"),
    ]
    
    print("\n📁 Archivos críticos:")
    for file_path, desc in critical_files:
        if not check_file(file_path, desc):
            all_ok = False
    
    # Verificar modelos locales
    print("\n🤖 Modelos locales:")
    models_dir = Path("models")
    if models_dir.exists():
        gguf_files = list(models_dir.glob("*.gguf"))
        if gguf_files:
            print(f"✅ Encontrados {len(gguf_files)} modelos .gguf")
            for model in gguf_files:
                print(f"   - {model.name}")
        else:
            print("⚠️  No se encontraron modelos .gguf")
    else:
        print("❌ Carpeta models/ no existe")
        all_ok = False
    
    # Verificar llama_cpp específicamente
    print("\n🦙 Verificación específica de llama_cpp:")
    try:
        import llama_cpp
        llama_path = Path(llama_cpp.__file__).parent
        print(f"✅ llama_cpp ubicado en: {llama_path}")
        
        # Verificar librerías nativas
        lib_path = llama_path / "lib"
        if lib_path.exists():
            dll_files = list(lib_path.glob("*.dll")) + list(lib_path.glob("*.so"))
            print(f"✅ Encontradas {len(dll_files)} librerías nativas")
        else:
            print("⚠️  Carpeta lib/ no encontrada en llama_cpp")
            
    except ImportError:
        print("❌ llama_cpp no está instalado")
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 ¡Todo listo para construir la aplicación offline!")
        print("📦 Ejecuta: python setup.py build")
    else:
        print("⚠️  Hay dependencias faltantes. Instálalas antes de continuar.")
        print("📥 Ejecuta: pip install llama-cpp-python PySide6 numpy")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)