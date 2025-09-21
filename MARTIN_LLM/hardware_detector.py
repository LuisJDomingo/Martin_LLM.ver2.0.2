# -*- coding: utf-8 -*-
# hardware_detector.py - Detecta hardware y configura automáticamente GPU/CPU

import os
import sys
import subprocess
import platform
import importlib.util
from pathlib import Path

class HardwareDetector:
    """Detecta el hardware disponible y configura la mejor opción para LLM."""
    
    def __init__(self):
        self.system_info = {
            'has_nvidia_gpu': False,
            'has_cuda': False,
            'has_intel_gpu': False,
            'has_amd_gpu': False,
            'cpu_cores': os.cpu_count(),
            'platform': platform.system(),
            'architecture': platform.machine()
        }
        self.recommended_config = None
        self._detect_hardware()
    
    def _detect_hardware(self):
        """Detecta todo el hardware disponible."""
        print("🔍 Detectando hardware disponible...")
        
        # Detectar GPU NVIDIA
        self._detect_nvidia_gpu()
        
        # Detectar otras GPU
        self._detect_other_gpus()
        
        # Determinar configuración recomendada
        self._determine_recommended_config()
    
    def _detect_nvidia_gpu(self):
        """Detecta si hay GPU NVIDIA y drivers CUDA."""
        try:
            # Intentar ejecutar nvidia-smi
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                self.system_info['has_nvidia_gpu'] = True
                # Extraer información de la GPU
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'CUDA Version' in line:
                        self.system_info['has_cuda'] = True
                        break
                print("✅ GPU NVIDIA detectada con drivers CUDA")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Método alternativo: buscar en el registro de Windows (si es Windows)
        if platform.system() == 'Windows':
            try:
                result = subprocess.run([
                    'powershell', '-Command',
                    "Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -like '*NVIDIA*'} | Select-Object Name"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and 'NVIDIA' in result.stdout:
                    self.system_info['has_nvidia_gpu'] = True
                    print("✅ GPU NVIDIA detectada (sin confirmar CUDA)")
                    return True
            except:
                pass
        
        print("❌ No se detectó GPU NVIDIA")
        return False
    
    def _detect_other_gpus(self):
        """Detecta GPU Intel, AMD u otras."""
        if platform.system() == 'Windows':
            try:
                result = subprocess.run([
                    'powershell', '-Command',
                    "Get-WmiObject -Class Win32_VideoController | Select-Object Name"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    if 'intel' in output:
                        self.system_info['has_intel_gpu'] = True
                        print("✅ GPU Intel detectada")
                    if 'amd' in output or 'radeon' in output:
                        self.system_info['has_amd_gpu'] = True
                        print("✅ GPU AMD detectada")
            except:
                pass
    
    def _determine_recommended_config(self):
        """Determina la mejor configuración basada en el hardware."""
        if self.system_info['has_nvidia_gpu'] and self.system_info['has_cuda']:
            self.recommended_config = {
                'type': 'nvidia_gpu',
                'description': 'GPU NVIDIA con CUDA (Máximo rendimiento)',
                'n_gpu_layers': -1,  # Todas las capas en GPU
                'requires_cuda_build': True
            }
        elif self.system_info['has_nvidia_gpu']:
            self.recommended_config = {
                'type': 'nvidia_gpu_no_cuda',
                'description': 'GPU NVIDIA sin CUDA (Requiere instalación de drivers)',
                'n_gpu_layers': 0,  # CPU por ahora
                'requires_cuda_build': True,
                'warning': 'Drivers CUDA no detectados. Instale CUDA Toolkit para mejor rendimiento.'
            }
        elif self.system_info['cpu_cores'] >= 8:
            self.recommended_config = {
                'type': 'high_cpu',
                'description': f'CPU de alto rendimiento ({self.system_info["cpu_cores"]} núcleos)',
                'n_gpu_layers': 0,
                'n_threads': min(self.system_info['cpu_cores'], 16),
                'requires_cuda_build': False
            }
        else:
            self.recommended_config = {
                'type': 'standard_cpu',
                'description': f'CPU estándar ({self.system_info["cpu_cores"]} núcleos)',
                'n_gpu_layers': 0,
                'n_threads': self.system_info['cpu_cores'],
                'requires_cuda_build': False
            }
    
    def get_user_choice(self):
        """Permite al usuario elegir la configuración."""
        print("\n" + "="*60)
        print("🚀 CONFIGURACIÓN DE HARDWARE - MARTIN LLM")
        print("="*60)
        
        print(f"\n📊 Hardware detectado:")
        print(f"   • CPU: {self.system_info['cpu_cores']} núcleos")
        print(f"   • GPU NVIDIA: {'✅' if self.system_info['has_nvidia_gpu'] else '❌'}")
        print(f"   • CUDA: {'✅' if self.system_info['has_cuda'] else '❌'}")
        print(f"   • GPU Intel: {'✅' if self.system_info['has_intel_gpu'] else '❌'}")
        print(f"   • GPU AMD: {'✅' if self.system_info['has_amd_gpu'] else '❌'}")
        
        print(f"\n🎯 Configuración recomendada:")
        print(f"   {self.recommended_config['description']}")
        
        if 'warning' in self.recommended_config:
            print(f"\n⚠️  {self.recommended_config['warning']}")
        
        print(f"\n🔧 Opciones disponibles:")
        options = []
        
        # Opción 1: Configuración recomendada
        options.append({
            'key': '1',
            'name': 'Automática (Recomendada)',
            'description': self.recommended_config['description'],
            'config': self.recommended_config
        })
        
        # Opción 2: Forzar CPU
        options.append({
            'key': '2',
            'name': 'Solo CPU',
            'description': 'Usar solo procesador (máxima compatibilidad)',
            'config': {
                'type': 'force_cpu',
                'n_gpu_layers': 0,
                'n_threads': self.system_info['cpu_cores'],
                'requires_cuda_build': False
            }
        })
        
        # Opción 3: GPU NVIDIA (si está disponible)
        if self.system_info['has_nvidia_gpu']:
            options.append({
                'key': '3',
                'name': 'Forzar GPU NVIDIA',
                'description': 'Intentar usar GPU NVIDIA (puede requerir librerías adicionales)',
                'config': {
                    'type': 'force_nvidia',
                    'n_gpu_layers': -1,
                    'requires_cuda_build': True
                }
            })
        
        # Mostrar opciones
        for option in options:
            print(f"   [{option['key']}] {option['name']}")
            print(f"       {option['description']}")
        
        # Solicitar elección del usuario
        while True:
            try:
                choice = input(f"\n👆 Seleccione una opción (1-{len(options)}): ").strip()
                
                # Buscar la opción seleccionada
                selected_option = None
                for option in options:
                    if option['key'] == choice:
                        selected_option = option
                        break
                
                if selected_option:
                    print(f"\n✅ Configuración seleccionada: {selected_option['name']}")
                    return selected_option['config']
                else:
                    print(f"❌ Opción inválida. Por favor, seleccione entre 1 y {len(options)}")
            
            except KeyboardInterrupt:
                print(f"\n\n👋 Configuración cancelada. Usando CPU por defecto.")
                return {
                    'type': 'default_cpu',
                    'n_gpu_layers': 0,
                    'n_threads': self.system_info['cpu_cores'],
                    'requires_cuda_build': False
                }
            except Exception as e:
                print(f"❌ Error en la entrada: {e}")
                continue
    
    def save_config(self, config, config_file='hardware_config.json'):
        """Guarda la configuración seleccionada."""
        import json
        
        config_data = {
            'hardware_info': self.system_info,
            'selected_config': config,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuración guardada en: {config_file}")
        except Exception as e:
            print(f"⚠️  No se pudo guardar la configuración: {e}")
    
    def load_saved_config(self, config_file='hardware_config.json'):
        """Carga configuración previamente guardada."""
        import json
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('selected_config')
        except:
            pass
        return None

def main():
    """Función principal para ejecutar la detección interactiva."""
    detector = HardwareDetector()
    
    # Intentar cargar configuración previa
    saved_config = detector.load_saved_config()
    
    if saved_config:
        print(f"🔄 Se encontró configuración previa.")
        use_saved = input("¿Usar configuración anterior? (s/N): ").strip().lower()
        
        if use_saved in ['s', 'sí', 'si', 'y', 'yes']:
            print("✅ Usando configuración guardada.")
            return saved_config
    
    # Obtener nueva configuración
    config = detector.get_user_choice()
    
    # Guardar configuración
    save_config = input("\n💾 ¿Guardar esta configuración para futuros usos? (S/n): ").strip().lower()
    
    if save_config not in ['n', 'no']:
        detector.save_config(config)
    
    return config

if __name__ == "__main__":
    config = main()
    print(f"\n🎯 Configuración final: {config}")