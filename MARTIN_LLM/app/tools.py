# -*- coding: utf-8 -*-
# app/tools.py
import requests
from bs4 import BeautifulSoup

# Imports para carga dinámica
import os
import importlib
import inspect
class BaseTool:
    name: str = "base_tool"
    description: str = "This is a base tool."

    def run(self, args: str) -> str:
        raise NotImplementedError("The run method must be implemented by a subclass.")

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Searches a given URL and returns the clean text content. Use this to get information from a webpage. Argument should be a valid URL."

    def run(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            return f"Successfully retrieved content from {url}. Content (first 2000 chars):\n{clean_text[:2000]}"
        except Exception as e:
            return f"Error searching web for {url}: {e}"

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "A simple calculator. Use this to perform mathematical calculations. The argument MUST be ONLY the mathematical expression to evaluate (e.g., '2+2', '10 * (4/2)'). Do NOT include the answer or any extra text in the arguments."

    def run(self, expression: str) -> str:
        try:
            # Usar un entorno seguro para eval(). Solo permite operaciones matemáticas básicas.
            allowed_names = {
                "abs": abs, "pow": pow, "round": round,
                # Puedes añadir más funciones seguras si es necesario
            }
            code = compile(expression, "<string>", "eval")
            result = eval(code, {"__builtins__": {}}, allowed_names)
            return f"The result of '{expression}' is {result}."
        except Exception as e:
            return f"Error calculating '{expression}': {e}. Please provide a valid and safe mathematical expression."

class ToolRegistry:
    def __init__(self, provider=None): # Acepta un proveedor opcional
        self._tools = {}
        self.provider = provider

        # Registrar herramientas estáticas
        self.register(WebSearchTool())
        self.register(CalculatorTool())

        # Registrar la meta-herramienta si se proporciona un proveedor
        if self.provider:
            # Importar aquí para evitar dependencias circulares
            from app.tool_generator import ToolGeneratorTool
            # Pasar la instancia del registro (self) a la herramienta generadora
            self.register(ToolGeneratorTool(self.provider, self))

        # Cargar herramientas generadas dinámicamente
        self.load_tools_from_directory()

    def _load_and_register_from_module(self, module_name: str) -> bool:
        """
        Helper interno para cargar, registrar y recargar un módulo de herramienta.
        Devuelve True si tiene éxito, False en caso contrario.
        """
        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)  # Recargar por si el archivo acaba de ser escrito
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    self.register(obj())
                    print(f"[ToolRegistry] Herramienta '{obj.name}' cargada y registrada dinámicamente.")
                    return True
        except Exception as e:
            print(f"Error al cargar la herramienta desde el módulo {module_name}: {e}")
        return False

    def load_tools_from_directory(self):
        """Carga dinámicamente herramientas desde el directorio 'generated_tools'."""
        tools_dir = os.path.join(os.path.dirname(__file__), "generated_tools")
        if not os.path.exists(tools_dir):
            return

        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"app.generated_tools.{filename[:-3]}"
                self._load_and_register_from_module(module_name)

    def load_newly_created_tool(self, tool_name: str):
        """Carga una única herramienta recién creada en el registro."""
        module_name = f"app.generated_tools.{tool_name}"
        self._load_and_register_from_module(module_name)
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_tool_descriptions(self) -> str:
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self._tools.values()])

# La instancia global ahora se crea donde se tiene acceso al proveedor,
# por ejemplo, en el constructor del Agente.
# Esto evita la dependencia circular y permite inyectar el proveedor.

# Dejamos una instancia por defecto para compatibilidad, pero el Agente debería crear la suya.
tool_registry = ToolRegistry()


# y que pasa con las librerias que las nuevas herramientas necesitan y no estan instaladas en el entorno virtual del proyecto