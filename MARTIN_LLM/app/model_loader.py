# -*- coding: utf-8 -*-
import requests
import socket
import psutil

def get_process_info(port: int = 11434) -> str:
    """Obtiene información del proceso que está usando un puerto TCP específico."""
    print("Obteniendo información del proceso en el puerto", port)
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                pid = conn.pid
                if pid:
                    proc = psutil.Process(pid)
                    return f"\nProceso: {proc.name()} (PID: {pid})"
        return "\nNo se encontró proceso escuchando en el puerto"
    except Exception as e:
        return "\nError obteniendo información del proceso: " + str(e)
def is_port_in_use(port: int = 11434) -> tuple[bool, str]:
   """Check if port is in use"""
   """Check if a specific port is in use and return process info if available"""
   print(f"iniciando la función is_port_in_use")
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print(sock)
   try:
       print("Intentando conectar al puerto desde is_port_in_use", port)
       sock.settimeout(1)  # Timeout de 1 segundo para evitar bloqueos
       # Intentar conectar al puerto especificado
       print("Conectando al puerto", port)
       result = sock.connect_ex(('127.0.0.1', port))
       sock.close()
       print("Resultado de la conexión:", result)
       if result == 0:
           process_info = get_process_info(port)
           print("conexion exitosa al puerto", port)
           return True, "Puerto " + str(port) + " en uso" + process_info
       
       return False, "Puerto " + str(port) + " libre"
   except Exception as e:
       return False, "Error al verificar puerto: " + str(e)
   finally:
       sock.close()
       print("finalizando is_port_in_use...")
def trim_context(context: list, max_length: int = 1000) -> list:
    """Limita el tamano del contexto para mejorar el rendimiento"""
    if context and len(context) > max_length:
        return context[-max_length:]
    return context
def check_system_resources():
    """Verifica recursos del sistema"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        print(f"\nRecursos del sistema:")
        print(f"CPU: {cpu_percent}%")
        print(f"Memoria: {memory.percent}% usado ({memory.available // (1024*1024)} MB libre)")
        return True
    except ImportError:
        print("Instala 'psutil' para monitorear recursos: pip install psutil")
        return False

# Código de prueba solo cuando se ejecuta directamente
if __name__ == "__main__":
    check_system_resources()
    print("=== Diagnostico de Ollama ===")
    port_used, port_msg = is_port_in_use()
    print("Estado del puerto: " + port_msg)
    if port_used:
        ok, msg = verify_ollama_connection()
        print("Estado de conexion: " + msg)