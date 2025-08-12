# Martin LLM - Aplicación PyQt6 Migrada

## 🎉 Migración Completada Exitosamente

La aplicación ha sido migrada de **Tkinter** a **PyQt6** con todas las características originales mantenidas y mejoradas.

## 📋 Características Implementadas

### ✅ **Ventanas Sin Bordes y Redimensionables**
- Todas las ventanas tienen bordes personalizados con tema sci-fi
- La barra superior cubre todo el ancho de la aplicación
- Las ventanas son completamente redimensionables
- Funcionalidad de arrastre desde la barra superior

### ✅ **Interfaz Moderna**
- Tema sci-fi completo con colores verde neón
- Transiciones suaves y efectos hover
- Tipografía Consolas para efecto terminal
- Widgets personalizados con estilos CSS

### ✅ **Funcionalidad Completa**
- Sistema de login con recordar usuario
- Gestión de modelos Ollama
- Chat con historial persistente
- Autoguardado de conversaciones
- Monitoreo del sistema en tiempo real
- Adjuntar archivos
- Ventana de carga animada

## 🚀 Cómo Ejecutar la Aplicación

### 1. Activar el Entorno Virtual
```bash
# En PowerShell
.\venv\Scripts\Activate.ps1

# En Command Prompt
venv\Scripts\activate.bat
```

### 2. Ejecutar la Aplicación
```bash
python main_pyqt6.py
```

## 📁 Archivos Migrados

### **Archivos Principales**
- `main_pyqt6.py` - Punto de entrada principal
- `Martin_LLM/ui/qt_styles.py` - Sistema de estilos PyQt6
- `Martin_LLM/ui/login_widget.py` - Widget de login
- `Martin_LLM/ui/chat_interface.py` - Interfaz principal de chat
- `Martin_LLM/ui/model_manager_widget.py` - Gestor de modelos
- `Martin_LLM/ui/loading_dialog.py` - Ventana de carga
- `Martin_LLM/ui/popup_window.py` - Ventana emergente

### **Archivos Originales de Tkinter**
Los archivos originales de Tkinter se mantienen intactos:
- `Martin_LLM/app/shortcut_listener.py` - Versión original
- `Martin_LLM/ui/popup_window.py` - Ahora migrado a PyQt6

## 🔧 Dependencias Instaladas

```
PyQt6==6.7.0
PyQt6-Qt6==6.7.0
PyQt6-sip==13.6.0
```

## 🎯 Mejoras Implementadas

### **Interfaz**
- **Barra superior completa**: Ahora cubre todo el ancho de la ventana
- **Redimensionamiento**: Todas las ventanas son redimensionables
- **Arrastre mejorado**: Funcionalidad de arrastre más fluida
- **Estilos consistentes**: Tema sci-fi unificado en toda la aplicación

### **Funcionalidad**
- **Señales PyQt6**: Sistema de comunicación entre widgets más robusto
- **Gestión de recursos**: Mejor manejo de memoria y recursos
- **Eventos de teclado**: Navegación mejorada con teclas
- **Validación**: Mejor validación de entrada de datos

### **Rendimiento**
- **Widgets nativos**: Mejor rendimiento que Tkinter
- **Renderizado**: Gráficos más fluidos y responsive
- **Memoria**: Menor uso de memoria
- **Estabilidad**: Menos propenso a crashes

## 🐛 Solución de Problemas

### **Si la aplicación no inicia:**
1. Verifica que el entorno virtual esté activado
2. Asegúrate de que PyQt6 esté instalado correctamente
3. Verifica que Ollama esté ejecutándose

### **Si hay problemas con las ventanas:**
1. Los bordes personalizados funcionan mejor en Windows 10/11
2. En sistemas más antiguos, algunos efectos pueden verse diferentes

### **Si el chat no funciona:**
1. Verifica que MongoDB esté ejecutándose
2. Asegúrate de que Ollama tenga modelos descargados
3. Revisa los logs en la consola

## 📊 Comparación: Tkinter vs PyQt6

| Característica | Tkinter | PyQt6 |
|---------------|---------|--------|
| **Rendimiento** | Básico | Excelente |
| **Apariencia** | Limitada | Moderna |
| **Redimensionamiento** | Básico | Avanzado |
| **Estilos** | Limitados | CSS completo |
| **Widgets** | Básicos | Avanzados |
| **Estabilidad** | Buena | Excelente |

## 🔮 Próximas Mejoras Sugeridas

1. **Temas múltiples**: Agregar más temas de colores
2. **Animaciones**: Transiciones más sofisticadas
3. **Plugins**: Sistema de plugins para extender funcionalidad
4. **Configuración**: Panel de configuración avanzado
5. **Shortcuts**: Más atajos de teclado personalizables

## 💡 Consejos de Uso

- **Arrastra** desde la barra superior para mover ventanas
- **Redimensiona** desde cualquier esquina o borde
- **Usa Enter** para enviar mensajes (Shift+Enter para nueva línea)
- **Click derecho** en la lista de modelos para opciones
- **Cierra** ventanas con el botón ❌ en la barra superior

---

**¡Disfruta de tu aplicación Martin LLM mejorada con PyQt6!** 🚀
