# 🚀 MARTIN LLM - Configurador Inteligente de Hardware

## ¿Qué es esto?

El **Configurador Inteligente de Hardware** es una nueva funcionalidad que permite a MARTIN LLM detectar automáticamente tu hardware (CPU/GPU) y configurarse para obtener el **máximo rendimiento** posible en tu sistema.

## ✨ Características Principales

- **🔍 Detección Automática**: Detecta GPU NVIDIA, Intel, AMD y configuración de CPU
- **⚡ Optimización Inteligente**: Recomienda la mejor configuración para tu hardware
- **🎨 Interfaz Gráfica**: Interfaz moderna y fácil de usar
- **💾 Configuración Persistente**: Recuerda tu configuración para futuras ejecuciones
- **🔧 Sin Instalaciones Manuales**: Todo se configura automáticamente

## 🚀 Cómo Usar

### Opción 1: Lanzador Gráfico (Recomendado)
```bash
python launch.py
```
Esta es la forma más fácil de usar MARTIN LLM. El lanzador:
1. Muestra una ventana de bienvenida
2. Te permite elegir entre configuración automática o configurar hardware
3. Lanza la aplicación con la configuración óptima

### Opción 2: Configurador Directo
```bash
python hardware_config_gui_v2.py
```
Abre directamente el configurador de hardware para ajustar la configuración.

### Opción 3: Inicio Inteligente
```bash
python smart_start.py
```
Inicio inteligente con opciones tanto gráficas como de terminal.

## 🖥️ Tipos de Hardware Soportados

### ✅ CPU (Siempre Disponible)
- **Detección**: Número de núcleos del procesador
- **Optimización**: Configuración automática de threads
- **Compatibilidad**: 100% - Funciona en cualquier sistema

### 🎮 GPU NVIDIA (Rendimiento Máximo)
- **Detección**: GPU NVIDIA + Drivers CUDA
- **Optimización**: Uso de GPU para acelerar el procesamiento
- **Beneficio**: 5-10x más rápido que CPU
- **Requisito**: Drivers CUDA instalados

### 💎 GPU Intel/AMD (Detectado pero no utilizado)
- **Detección**: Reconoce GPU integradas Intel y dedicadas AMD
- **Estado**: Detectado para información, no usado actualmente
- **Futuro**: Soporte planeado en futuras versiones

## ⚙️ Opciones de Configuración

### 1. 🎯 Automática (Recomendada)
- El sistema elige la mejor configuración para tu hardware
- **Para GPU NVIDIA**: Usa GPU + CPU para máximo rendimiento
- **Para solo CPU**: Optimiza threads según núcleos disponibles
- **Recomendado para**: Todos los usuarios

### 2. 🖥️ Solo CPU
- Fuerza el uso únicamente del procesador
- **Ventaja**: Máxima compatibilidad
- **Desventaja**: Menor rendimiento si tienes GPU NVIDIA
- **Recomendado para**: Sistemas con problemas de GPU o testing

### 3. 🎮 GPU NVIDIA (Solo si disponible)
- Fuerza el uso de GPU NVIDIA con máximas capas
- **Ventaja**: Máximo rendimiento posible
- **Requisito**: Drivers CUDA funcionando correctamente
- **Recomendado para**: Usuarios avanzados con GPU NVIDIA

## 📊 Indicadores de Estado

En el configurador verás badges de colores:

- 🟢 **Verde**: Hardware disponible y funcionando
- 🟡 **Amarillo**: Hardware detectado pero no optimizado
- 🔴 **Rojo**: Hardware no disponible

## 🛠️ Resolución de Problemas

### Problema: "No se detecta GPU NVIDIA"
**Causa**: Drivers CUDA no instalados o GPU no compatible
**Solución**: 
1. Instalar [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
2. Usar configuración "Solo CPU" mientras tanto

### Problema: "Error al cargar configuración"
**Causa**: Archivo de configuración corrupto
**Solución**:
1. Eliminar `hardware_config.json`
2. Volver a ejecutar el configurador

### Problema: "La aplicación va lenta"
**Causa**: Configuración no óptima
**Solución**:
1. Ejecutar `python hardware_config_gui_v2.py`
2. Seleccionar configuración "Automática"
3. Verificar que se detecte tu hardware correctamente

## 📁 Archivos Importantes

- `hardware_config.json`: Configuración guardada automáticamente
- `hardware_detector.py`: Lógica de detección de hardware
- `hardware_config_gui_v2.py`: Interfaz gráfica del configurador
- `launch.py`: Lanzador principal recomendado
- `smart_start.py`: Inicio inteligente con opciones

## 🔄 Actualizar Configuración

Si cambias tu hardware (nueva GPU, más RAM, etc.):

1. Ejecuta: `python hardware_config_gui_v2.py`
2. Haz clic en "Detectar de Nuevo"
3. Selecciona nueva configuración
4. Haz clic en "Aplicar y Continuar"

## 💡 Consejos de Rendimiento

### Para Usuarios con GPU NVIDIA:
- Asegúrate de tener la última versión de drivers
- Usa configuración "Automática" o "GPU NVIDIA"
- El rendimiento puede ser 5-10x más rápido

### Para Usuarios Solo CPU:
- La configuración automática optimizará el número de threads
- En CPUs de 8+ núcleos verás mejoras significativas
- Cierra otras aplicaciones pesadas durante el uso

### Para Todos:
- La primera configuración toma más tiempo (detección de hardware)
- Las siguientes ejecuciones son instantáneas
- La configuración se guarda automáticamente

## 🎯 Integración con MARTIN LLM

Esta funcionalidad está **completamente integrada** con MARTIN LLM:

1. **Transparente**: No cambia la forma de usar la aplicación
2. **Automática**: Se aplica automáticamente al iniciar
3. **Persistente**: Recuerda tu configuración
4. **Compatible**: Funciona con todas las características existentes

## 🚀 Para Desarrolladores

Si quieres integrar esto en tu propia aplicación:

```python
from hardware_detector import HardwareDetector
from hardware_config_gui_v2 import HardwareConfigGUI

# Detección programática
detector = HardwareDetector()
config = detector.get_user_choice()

# Interfaz gráfica
app = QApplication(sys.argv)
window = HardwareConfigGUI()
window.show()
```

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `python hardware_detector.py` para ver la detección en terminal
2. Revisa que tengas todas las dependencias: `pip install -r requirements.txt`
3. Para GPU NVIDIA, verifica CUDA: `nvidia-smi`

---

**¡Disfruta del poder de MARTIN LLM optimizado para tu hardware! 🚀**