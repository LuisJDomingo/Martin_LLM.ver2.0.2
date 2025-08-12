# -*- coding: utf-8 -*-
# app/agent.py
import json
from app.llm_providers import BaseLLMProvider
from app.tools import tool_registry

AGENT_SYSTEM_PROMPT_TEMPLATE = """
# Core Persona
{custom_prompt}

# Your Mission
You are an autonomous agent. Your goal is to achieve the user's objective by using the tools available to you.
You must respond in a specific JSON format. On each step, you must think about your next action and then produce a JSON object with the action to take.

# Available Tools
You have the following tools at your disposal:
{tools}

Your response MUST be a JSON object with two keys: 'thought' and 'action'.
The 'action' key must contain a dictionary with 'tool_name' and 'args'.
The 'tool_name' must be one of the available tools or 'finish' if you have completed the objective.
The 'args' for the 'finish' tool should be your final answer to the user.

Example:
{{
    "thought": "I need to find out what's on the main page of Wikipedia. I will use the web_search tool.",
    "action": {{
        "tool_name": "web_search",
        "args": "https://www.wikipedia.org"
    }}
}}

If you are finished, respond like this:
{{
    "thought": "I have found the answer and will now provide it to the user.",
    "action": {{
        "tool_name": "finish",
        "args": "The main page of Wikipedia contains a lot of information about current events."
    }}
}}
"""

class Agent:
    """
    Clase que implementa la lógica de un agente autónomo con un bucle de
    Pensamiento -> Acción -> Observación.
    """
    def __init__(self, provider: BaseLLMProvider, custom_prompt: str = None):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("El proveedor debe ser una instancia de BaseLLMProvider.")
        self.provider = provider
        self.history = []
        self.report_step_callback = None # Para reportar progreso a la UI
        
        if not custom_prompt:
            custom_prompt = "You are a helpful and efficient autonomous agent."
            
        self.system_prompt = AGENT_SYSTEM_PROMPT_TEMPLATE.format(
            custom_prompt=custom_prompt,
            tools=tool_registry.get_tool_descriptions()
        )

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
            print(f"[Agent] Error: No se pudo parsear la respuesta JSON: {response_text}")
            return None

    def run(self, user_message: str) -> str:
        """
        Ejecuta el bucle del agente: Pensar -> Actuar -> Observar.
        Devuelve la respuesta final del agente al usuario.
        """
        # El historial del agente mantiene el estado completo de la conversación.
        self.history.append({"role": "user", "content": f"User objective: {user_message}"})

        for i in range(5):  # Límite de seguridad de 5 pasos para evitar bucles infinitos
            print(f"\n--- AGENT STEP {i+1} ---")
            
            # 1. PENSAR: El LLM decide la siguiente acción.
            messages_for_provider = [{"role": "system", "content": self.system_prompt}] + self.history
            
            try:
                # Forzar formato JSON para que el modelo se comporte
                response_text = self.provider.query(messages_for_provider, format="json")
            except Exception as e:
                return f"Error en el bucle del agente: {e}"

            self.history.append({"role": "assistant", "content": response_text})
            action_data = self._parse_llm_response(response_text)

            if not action_data:
                observation = "Error: Your last response was not a valid JSON object. You MUST respond with a valid JSON object containing 'thought' and 'action' keys. Please try again."
                print(f"Observation: {observation}")
                self.history.append({"role": "system", "content": f"Observation: {observation}"})
                continue

            thought = action_data.get("thought", "(sin pensamiento)")
            action = action_data.get("action", {})
            tool_name = action.get("tool_name")
            args = action.get("args", "")
            
            # Reportar el paso a la UI si hay un callback
            if self.report_step_callback:
                self.report_step_callback(thought, tool_name, args)
            
            print(f"Thought: {thought}")

            # 2. ACTUAR: ejecutar la herramienta o terminar
            if not tool_name:
                observation = "Error: El modelo no especificó un 'tool_name' en su acción."
            elif tool_name == "finish":
                print(f"--- AGENT FINISHED ---")
                final_answer = args
                # Asegurarse de que la respuesta final siempre sea un string
                if not isinstance(final_answer, str):
                    final_answer = str(final_answer)
                print(f"Final Answer: {final_answer}")
                return final_answer

            tool = tool_registry.get_tool(tool_name)
            if not tool:
                observation = f"Error: Herramienta desconocida: '{tool_name}'. Las herramientas disponibles son: {tool_registry.get_tool_descriptions()}"
            else:
                print(f"Action: Executing tool '{tool_name}' with args: '{args}'")
                # 3. OBSERVAR: obtener el resultado de la herramienta
                try:
                    observation = tool.run(args)
                except Exception as e:
                    observation = f"Error executing tool {tool_name}: {e}"
            
            print(f"Observation: {observation[:200]}...") # Imprimir los primeros 200 caracteres de la observación
            self.history.append({"role": "system", "content": f"Observation: {observation}"})

        return "El agente no pudo completar la tarea en el número máximo de pasos."

    def execute_task(self, task_description: str) -> str:
        """
        Ejecuta una única tarea bien definida. Es un alias para run().
        Esto hace que la intención del código sea más clara cuando se usa como ejecutor.
        """
        return self.run(task_description)