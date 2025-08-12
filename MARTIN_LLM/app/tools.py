# -*- coding: utf-8 -*-
# app/tools.py
import requests
from bs4 import BeautifulSoup

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
    description = "A simple calculator. Use this to perform mathematical calculations. The argument should be a mathematical expression (e.g., '2+2', '10 * (4/2)')."

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
    def __init__(self):
        self._tools = {}
        self.register(WebSearchTool())
        self.register(CalculatorTool())

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_tool_descriptions(self) -> str:
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self._tools.values()])

# Global instance
tool_registry = ToolRegistry()
