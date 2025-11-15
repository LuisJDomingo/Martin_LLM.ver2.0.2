# -*- coding: utf-8 -*-
# test_loader.py

import os
from llama_cpp import Llama

# --- CONFIGURACIÓN ---
# Asegúrate de que esta ruta apunta a tu archivo de modelo.
# ¡Prueba con el modelo que ya tienes Y con uno nuevo que descargues!
MODEL_PATH = "models/model.gguf"

def test_model_loading():
    """Intenta cargar el modelo de forma aislada para un diagnóstico preciso."""
    print("--- INICIANDO PRUEBA DE CARGA DE MODELO ---")
    
    model_abs_path = os.path.abspath(MODEL_PATH)
    if not os.path.exists(model_abs_path):
        print(f"❌ ERROR: No se encuentra el archivo del modelo en: {model_abs_path}")
        return

    print(f"Intentando cargar el modelo desde: {model_abs_path}")
    
    try:
        llm = Llama(
            model_path=model_abs_path,
            n_gpu_layers=0,  # Forzando CPU
            verbose=True     # ¡Muy importante para obtener más detalles!
        )
        print("\n✅ ¡ÉXITO! El modelo se ha cargado correctamente en memoria.")
    except Exception as e:
        print(f"\n💥 ERROR FATAL DURANTE LA CARGA: {e}")

if __name__ == "__main__":
    test_model_loading()