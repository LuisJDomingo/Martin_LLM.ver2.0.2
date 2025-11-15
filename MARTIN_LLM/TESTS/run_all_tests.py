# -*- coding: utf-8 -*-
# run_all_tests.py

import pytest
import json
import os
import sys
from datetime import datetime
from collections import defaultdict

# --- CONFIGURACIÓN ---
# Número de veces que se ejecutará la suite de pruebas completa.
NUM_RUNS = 10

# --- RUTAS (Paths) ---
# Se determina la ruta del directorio de pruebas basándose en la ubicación de este script.
# Esto hace que el script funcione sin importar desde dónde se ejecute.
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
# Directorio donde se encuentran las pruebas.
# Nombre del archivo de reporte.
REPORT_FILE = os.path.join(PROJECT_ROOT, "test_stress_report.txt")
# Archivo temporal para el reporte JSON de pytest.
JSON_REPORT_TEMP_FILE = os.path.join(TEST_DIR, "temp_report.json")

def run_tests():
    """
    Ejecuta la suite de pruebas y recopila los resultados.
    """
    # Usamos defaultdict para facilitar la inicialización de contadores.
    # La estructura será: { 'test_node_id': {'passed': 0, 'failed': 0, 'skipped': 0} }
    results = defaultdict(lambda: defaultdict(int))
    
    print(f"Iniciando {NUM_RUNS} ejecuciones de la suite de pruebas...")
    print("Esto puede tardar varios minutos.")

    for i in range(NUM_RUNS):
        print(f"\n--- Ejecución {i + 1}/{NUM_RUNS} ---")
        
        # Ejecutar pytest programáticamente.
        # -q para modo silencioso, --json-report para generar el reporte que necesitamos.
        pytest.main([
            '-q', 
            '--json-report', 
            f'--json-report-file={JSON_REPORT_TEMP_FILE}',
            TEST_DIR
        ])

        # Verificar si el reporte JSON se creó.
        if not os.path.exists(JSON_REPORT_TEMP_FILE):
            print(f"ERROR: No se pudo generar el archivo de reporte JSON en la ejecución {i+1}. Abortando.")
            sys.exit(1)

        # Procesar el reporte JSON.
        with open(JSON_REPORT_TEMP_FILE, 'r', encoding='utf-8') as f:
            try:
                report_data = json.load(f)
                if 'tests' not in report_data:
                    print(f"ADVERTENCIA: El reporte JSON de la ejecución {i+1} no contiene la clave 'tests'.")
                    continue
                    
                for test in report_data['tests']:
                    node_id = test['nodeid']
                    outcome = test['outcome'] # 'passed', 'failed', 'skipped'
                    results[node_id][outcome] += 1
            except json.JSONDecodeError:
                print(f"ADVERTENCIA: No se pudo decodificar el reporte JSON de la ejecución {i+1}.")
                continue
    
    # Limpiar el archivo temporal.
    if os.path.exists(JSON_REPORT_TEMP_FILE):
        os.remove(JSON_REPORT_TEMP_FILE)
        
    return results

def generate_report(results):
    """
    Genera un archivo de texto con el resumen de los resultados.
    """
    # Agrupar resultados por archivo (módulo).
    # { 'module_path': { 'test_name': {'passed': ...} } }
    grouped_results = defaultdict(dict)
    total_tests_run = 0
    total_passes = 0
    total_failures = 0

    for node_id, outcomes in results.items():
        module_path, test_name = node_id.split("::")
        grouped_results[module_path][test_name] = outcomes
        total_passes += outcomes.get('passed', 0)
        total_failures += outcomes.get('failed', 0)
        total_tests_run += sum(outcomes.values())

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(" " * 15 + "INFORME DE PRUEBAS DE ESTRÉS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de Ejecuciones por Prueba: {NUM_RUNS}\n\n")

        # Ordenar módulos por nombre de archivo.
        for module_path in sorted(grouped_results.keys()):
            f.write(f"--- Módulo: {module_path} ---\n")
            
            module_results = grouped_results[module_path]
            # Ordenar pruebas por nombre.
            for test_name in sorted(module_results.keys()):
                outcomes = module_results[test_name]
                passes = outcomes.get('passed', 0)
                failures = outcomes.get('failed', 0)
                skipped = outcomes.get('skipped', 0)
                
                test_display = f"  - {test_name}:".ljust(65)
                f.write(f"{test_display} Éxitos: {passes}, Fallos: {failures}\n")
            f.write("\n")
            
        f.write("=" * 60 + "\n")
        f.write("Resumen General:\n")
        f.write(f"  - Total de Pruebas Ejecutadas (incluye repeticiones): {total_tests_run}\n")
        f.write(f"  - Total de Éxitos: {total_passes}\n")
        f.write(f"  - Total de Fallos: {total_failures}\n")
        
        success_rate = (total_passes / total_tests_run) * 100 if total_tests_run > 0 else 0
        f.write(f"  - Tasa de Éxito General: {success_rate:.2f}%\n")
        f.write("=" * 60 + "\n")

    print(f"\n✅ Reporte completo guardado en: {os.path.abspath(REPORT_FILE)}")

def main():
    """Función principal del script."""
    try:
        import pytest_jsonreport
    except ImportError:
        print("❌ ERROR: El paquete 'pytest-json-report' es necesario para este script.")
        print("   Por favor, instálalo ejecutando: pip install pytest-json-report")
        sys.exit(1)
        
    test_results = run_tests()
    if test_results:
        generate_report(test_results)
    else:
        print("No se obtuvieron resultados de las pruebas.")

if __name__ == "__main__":
    main()