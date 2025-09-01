# -*- coding: utf-8 -*-
# app/tool_generator.py

import os
import re
import importlib.util
from app.tools import BaseTool
from app.llm_providers import BaseLLMProvider

GENERATOR_PROMPT_TEMPLATE = """
You are an expert Python programmer. Your task is to generate the code for a new tool for an AI agent.
The tool must be a single Python class that inherits from 'BaseTool'.
The class must have 'name' and 'description' attributes.
The 'name' must be a short, snake_case identifier.
The 'description' must clearly explain what the tool does and what its arguments are.
The class must implement a 'run(self, args: str) -> str' method.

Your output MUST be ONLY the Python code for the class, without any explanations, comments, or markdown fences like ```python.

Here is the user's request for the new tool:
"{tool_description}"

Example of a valid output for a "text reverser" tool:

import os

class TextReverserTool(BaseTool):
    name = "text_reverser"
    description = "Reverses the provided text string. The argument is the text to reverse."

    def run(self, args: str) -> str:
        return args[::-1]

Now, generate the Python code for the requested tool.
"""

class ToolGeneratorTool(BaseTool):
    name = "tool_generator"
    description = (
        "Creates a new tool and saves it for future use. "
        "Use this when the user asks to create a new, permanent capability. "
        "The argument should be a clear description of what the new tool must do."
    )

    def __init__(self, provider: BaseLLMProvider, registry):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("ToolGeneratorTool requires a valid LLM provider.")
        
        # Importar aquí para evitar una dependencia circular a nivel de módulo
        from app.tools import ToolRegistry
        if not isinstance(registry, ToolRegistry):
            raise TypeError("ToolGeneratorTool requires a valid ToolRegistry instance.")
            
        self.provider = provider
        self.registry = registry # Guardar la instancia del registro
        # Define el directorio donde se guardarán las nuevas herramientas
        self.tools_dir = os.path.join(os.path.dirname(__file__), "generated_tools")
        os.makedirs(self.tools_dir, exist_ok=True)

    def _detect_imports(self, code: str) -> set[str]:
        """Detecta importaciones de nivel superior en el código generado."""
        import_pattern = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z0-9_.]+)", re.MULTILINE)
        found_modules = import_pattern.findall(code)
        base_modules = {module.split('.')[0] for module in found_modules}
        # Excluir librerías estándar y las que ya usa el proyecto
        standard_libs = {'os', 'sys', 're', 'json', 'datetime', 'math', 'collections', 'inspect', 'importlib', 'requests', 'bs4', 'app'}
        return base_modules - standard_libs

    def _verify_imports(self, modules: set[str]) -> list[str]:
        """Verifica si una lista de módulos se puede importar. Devuelve una lista de los que faltan."""
        missing = []
        for module_name in modules:
            if importlib.util.find_spec(module_name) is None:
                missing.append(module_name)
        return missing

    def run(self, args: str) -> str:
        """Genera, valida, guarda y carga una nueva herramienta."""
        prompt = GENERATOR_PROMPT_TEMPLATE.format(tool_description=args)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            generated_code = self.provider.query(messages)

            required_modules = self._detect_imports(generated_code)
            if required_modules:
                missing_modules = self._verify_imports(required_modules)
                if missing_modules:
                    return (f"Error: Cannot create tool. The generated code requires the following "
                            f"libraries which are not installed: {', '.join(missing_modules)}. "
                            f"Please ask a developer to install them.")

            class_name_match = re.search(r"class\s+(\w+)\(BaseTool\):", generated_code)
            tool_name_match = re.search(r"name\s*=\s*['\"]([\w_]+)['\"]", generated_code)

            if not class_name_match or not tool_name_match:
                return "Error: The generated code is not a valid tool. Could not find class name or tool name."

            tool_name = tool_name_match.group(1)
            file_path = os.path.join(self.tools_dir, f"{tool_name}.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generated_code)

            self.registry.load_newly_created_tool(tool_name)
            return f"Successfully created and loaded new tool '{tool_name}'. It is now available for use in the next step."
        except Exception as e:
            return f"An error occurred while generating the tool: {e}"