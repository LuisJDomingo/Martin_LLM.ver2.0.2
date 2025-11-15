import os
from llama_cpp import Llama

# --- CONFIGURACIÓN ---
# Asegúrate de que esta ruta apunta a tu modelo GGUF.
# Cambia la ruta si es necesario.
MODEL_GGUF_PATH = os.path.join(os.path.dirname(__file__), "models", "model.gguf")

print("--- INICIANDO PRUEBA DE DIAGNÓSTICO DE LLAMA.CPP ---")
print(f"Ruta del modelo: {MODEL_GGUF_PATH}")

if not os.path.exists(MODEL_GGUF_PATH):
    print("\nERROR CRÍTICO: No se encontró el archivo del modelo en la ruta especificada.")
    print("Por favor, verifica que la ruta en la variable MODEL_GGUF_PATH es correcta.")
    exit()

try:
    print("\n[Paso 1/3] Creando instancia de Llama...")
    
    # Creamos la instancia con los parámetros más seguros y compatibles
    llm = Llama(
        model_path=MODEL_GGUF_PATH,
        n_gpu_layers=0,      # Forzar CPU
        verbose=True,        # Máxima información de salida
        n_ctx=512            # Un contexto pequeño para la prueba
    )
    
    print("\n[Paso 2/3] ¡ÉXITO! La instancia de Llama se ha creado y el modelo se ha cargado.")
    
    prompt = "Hello, world!"
    print(f"\n[Paso 3/3] Intentando generar una respuesta para el prompt: '{prompt}'")
    
    output = llm(prompt, max_tokens=5)
    
    print("\n--- ¡PRUEBA COMPLETADA CON ÉXITO! ---")
    print("Respuesta del modelo:")
    print(output)

except Exception as e:
    print("\n--- LA PRUEBA HA FALLADO ---")
    print("Se ha producido un error durante la inicialización o ejecución de Llama.cpp.")
    import traceback
    traceback.print_exc()

