import requests
from bs4 import BeautifulSoup
import subprocess
def get_online_ollama_models():
    url = 'https://ollama.com/search'
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10) # Timeout de 10 segundos
        if response.status_code != 200:
            print(f"Error HTTP {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar los span que contienen el nombre del modelo
        span_tags = soup.find_all('span', attrs={"x-test-search-response-title": True})
        modelos = [span.get_text(strip=True) for span in span_tags]

        return sorted(set(modelos))  # Eliminar duplicados si los hay y los ordena alfabeticamente

    except Exception as e:
        print(f"Error al hacer scraping de la libreria online: {e}")
        return []
def get_local_ollama_models_subprocess():
    """
    Usa 'ollama list' desde CLI para obtener modelos locales.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")[1:]  # Saltar encabezado
        modelos = [line.split()[0] for line in lines if line.strip()]
        return sorted(set(modelos))
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al ejecutar 'ollama list': {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return []

'''
# Ejemplo de uso
modelos = get_online_ollama_models()
print("Modelos disponibles online:")
for modelo in modelos:
    print(f"- {modelo}")
'''