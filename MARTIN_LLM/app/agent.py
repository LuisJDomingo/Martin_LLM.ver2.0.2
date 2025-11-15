# -*- coding: utf-8 -*- 
# app/agent.py
import json
from app.llm_providers import BaseLLMProvider
from app.tools import ToolRegistry

# ANSI escape codes for colors
class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

class Agent:
    """
    Clase que implementa la lógica de un agente autónomo con un bucle de
    Pensamiento -> Acción -> Observación.
    """
    def __init__(self, provider: BaseLLMProvider, custom_prompt: str = None):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("El proveedor debe ser una instancia de BaseLLMProvider.")
        self.provider = provider
        # Crear una instancia del registro de herramientas específica para este agente,
        # pasándole el proveedor para que la ToolGeneratorTool pueda usarlo.
        self.tool_registry = ToolRegistry(provider=self.provider)
        self.history = []
        self.report_step_callback = None # Para reportar progreso a la UI
        
        if not custom_prompt:
            custom_prompt = "You are a helpful and efficient autonomous agent."
        
        # 🔧 Construir el system_prompt como f-string
        self.system_prompt = f"""
# Core Persona
{custom_prompt}

# Your Mission
You are an autonomous agent. Your goal is to achieve the user's objective by using the tools available to you.
You must respond in a specific JSON format. On each step, you must think about your next action and then produce a JSON object with the action to take.

# Constraints
- You MUST ONLY respond with a single valid JSON object. Do not add any text before or after the JSON object.
- The 'action' field MUST be a dictionary containing 'tool_name' and 'args'.
- The 'tool_name' MUST be one of the available tools or 'finish'.
- The 'args' for the 'calculator' tool MUST be ONLY the mathematical expression to evaluate (e.g., '2+2', '10 * (4/2)'). It MUST NOT contain the answer or any other text.
- The 'args' for the 'finish' tool MUST be the final answer to the user's objective and it MUST be directly related to the user's request. Do not make up unrelated information.

# Learning From Observations
After each action, you will receive an "Observation" message. This message contains the result or an error from the tool you used.
You MUST pay close attention to the Observation. If a tool returns an error, analyze the error message and correct your next action. Do not repeat the same failed action.

# Available Tools
You have the following tools at your disposal:
{self.tool_registry.get_tool_descriptions()}

Your response MUST be a JSON object with two keys: 'thought' and 'action'.
The 'action' key must contain a dictionary with 'tool_name' and 'args'.
The 'tool_name' must be one of the available tools or 'finish' if you have completed the objective.
The 'args' for the 'finish' tool should be your final answer to the user.

**Example 1 (Using Calculator):**
{{
    "thought": "The user is asking for a mathematical calculation. I should use the calculator tool.",
    "action": {{
        "tool_name": "calculator",
        "args": "3 + 4"
    }}
}}

**Example 1b (Incorrect - DO NOT DO THIS):**
{{
    "thought": "The user wants to know what 3+4 is. I will calculate it and put the whole equation in the arguments.",
    "action": {{
        "tool_name": "calculator",
        "args": "3 + 4 = 7"
    }}
}}

**Example 2 (Using Web Search):**
{{
    "thought": "I need to find information on a webpage. I will use the web_search tool.",
    "action": {{
        "tool_name": "web_search",
        "args": "https://www.wikipedia.org"
    }}
}}

**Example 3 (Direct Answer / Finishing Task):**
{{
    "thought": "The user's question can be answered directly without using any tools. I will provide the answer.",
    "action": {{
        "tool_name": "finish",
        "args": "La capital de Francia es París."
    }}
}}

If you are finished, respond like this:
{{
    "thought": "I have calculated the result and will now provide it to the user.",
    "action": {{
        "tool_name": "finish",
        "args": "The result of 2+2 is 4."
    }}
}}
"""

    def _parse_llm_response(self, response_text: str) -> dict | None:
        """Intenta parsear la respuesta del LLM como un objeto JSON.
        A veces los modelos envuelven el JSON en bloques de código, esto intenta manejarlo.
        Devuelve el objeto o None si falla el parseo.
        """
        try:
            # Limpiar si está envuelto en ```json ... ```
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            return json.loads(response_text)
        except json.JSONDecodeError:
            print(f"[agent.py][_parse_llm_response] Error: No se pudo parsear la respuesta JSON: {response_text}")
            return None

    def run(self, user_message: str) -> str:
        """
        Ejecuta el bucle del agente: Pensar -> Actuar -> Observar.
        Devuelve la respuesta final del agente al usuario.
        """
        # El historial del agente mantiene el estado completo de la conversación.
        self.history.append({"role": "user", "content": f"User objective: {user_message}"})

        for i in range(10):  # Límite de seguridad de 10 pasos para evitar bucles infinitos
            print(f"[agent.py][run] --- AGENT STEP {i+1} ---")
            
            # 1. PENSAR: El LLM decide la siguiente acción.
            messages_for_provider = [{"role": "system", "content": self.system_prompt}] + self.history
            
            try:
                # Forzar formato JSON para que el modelo se comporte
                print(f"{Color.GREEN}[Agent]{Color.RESET} -> {Color.YELLOW}run(){Color.RESET}: {Color.BLUE}Querying provider for next action...{Color.RESET}")
                response_text = self.provider.query(messages_for_provider, format="json")
            except Exception as e:
                return f"Error en el bucle del agente: {e}"

            print(f"{Color.GREEN}[Agent]{Color.RESET}    {Color.BLUE}Raw response from provider:{Color.RESET} {response_text}")
            self.history.append({"role": "assistant", "content": response_text})
            action_data = self._parse_llm_response(response_text)

            if not action_data:
                observation = "Error: Your last response was not a valid JSON object. You MUST respond with a valid JSON object containing 'thought' and 'action' keys. Please try again."
                print(f"[agent.py][run] Observation: {observation}")
                self.history.append({"role": "system", "content": f"Observation: {observation}"})
                continue

            thought = action_data.get("thought", "(sin pensamiento)")
            action = action_data.get("action", {})
            if not isinstance(action, dict):
                observation = f"Error: The 'action' field in your JSON response must be a dictionary, but you provided a {type(action).__name__}. Please correct the format and ensure 'action' contains 'tool_name' and 'args'."
                print(f"Observation: {observation}")
                self.history.append({"role": "system", "content": f"Observation: {observation}"})
                continue

            tool_name = action.get("tool_name")
            args = action.get("args", "")
            
            # Reportar el paso a la UI si hay un callback
            if self.report_step_callback:
                self.report_step_callback(thought, tool_name, args)
            
            print(f"{Color.GREEN}[Agent]{Color.RESET}    {Color.YELLOW}Thought:{Color.RESET} {thought}")

            # 2. ACTUAR: ejecutar la herramienta o terminar
            observation = ""
            if not tool_name:
                observation = "Error: El modelo no especificó un 'tool_name' en su acción."
            elif tool_name == "finish":
                if not args:
                    observation = "Error: You used the 'finish' tool without providing a final answer in the 'args'. Please provide the answer in the 'args' field."
                else:
                    print(f"--- AGENT FINISHED ---")
                    final_answer = args
                    # Asegurarse de que la respuesta final siempre sea un string
                    if not isinstance(final_answer, str):
                        final_answer = str(final_answer)
                    print(f"Final Answer: {final_answer}")
                    return final_answer
            else: # It's a tool call
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    observation = f"Error: Herramienta desconocida: '{tool_name}'. Las herramientas disponibles son: {self.tool_registry.get_tool_descriptions()}"
                else:
                    print(f"{Color.GREEN}[Agent]{Color.RESET}    {Color.YELLOW}Action:{Color.RESET} Executing tool '{tool_name}' with args: '{args}'")
                    # 3. OBSERVAR: obtener el resultado de la herramienta
                    try:
                        observation = tool.run(args)
                    except Exception as e:
                        observation = f"Error executing tool {tool_name}: {e}"

            if observation:
                print(f"{Color.GREEN}[Agent]{Color.RESET}    {Color.YELLOW}Observation:{Color.RESET} {observation[:300]}...")
                self.history.append({"role": "system", "content": f"Observation: {observation}"})

        return "El agente no pudo completar la tarea en el número máximo de pasos."

    def execute_task(self, task_description: str) -> str:
        """
        Ejecuta una única tarea bien definida. Es un alias para run().
        Esto hace que la intención del código sea más clara cuando se usa como ejecutor.
        """
        return self.run(task_description)
