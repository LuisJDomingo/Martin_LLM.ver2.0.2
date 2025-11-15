# -*- coding: utf-8 -*-
# app/reasoner.py

import json
from app.llm_providers import BaseLLMProvider
from app.tools import tool_registry

REASONER_SYSTEM_PROMPT_TEMPLATE = """
# Core Persona
{custom_prompt}

# Your Mission
You are a master planner. Your role is to break down a complex user objective into a series of simple, sequential steps.
Each step must be a clear, self-contained instruction that can be executed by an agent with a specific set of tools.

# Available Tools for the Executor Agent
{tools}

Your response MUST be a JSON object containing a single key "plan", which is a list of strings.
Each string in the list is a single step or task for the executor agent.

User Objective: "Investiga en la web qué es la API de Llama.cpp, busca un ejemplo de uso en Python y explícamelo."

Example of your output:
{{
    "plan": [
        "Use the web_search tool to find a good explanation of what the Llama.cpp API is. A good starting point could be its official GitHub repository or documentation.",
        "Use the web_search tool again on a relevant page to find a code example of how to use the Llama.cpp Python bindings to get a chat completion.",
        "Based on the information gathered from the previous steps, formulate a clear and concise explanation of the API and the code example for the user."
    ]
}}

Now, generate a plan for the user's objective.
"""

class Reasoner:
    """
    El Planificador. Su única función es crear un plan de acción.
    """
    def __init__(self, provider: BaseLLMProvider, custom_prompt: str = None):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("El proveedor debe ser una instancia de BaseLLMProvider.")
        self.provider = provider

        if not custom_prompt:
            custom_prompt = "You are a helpful and strategic master planner."

        self.system_prompt = REASONER_SYSTEM_PROMPT_TEMPLATE.format(
            custom_prompt=custom_prompt,
            tools=tool_registry.get_tool_descriptions()
        )

    def generate_plan(self, user_objective: str) -> list[str] | None:
        """
        Llama al LLM para generar un plan y lo devuelve como una lista de pasos.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"User Objective: \"{user_objective}\""}
        ]
        
        try:
            response_text = self.provider.query(messages, format="json")
            response_data = json.loads(response_text)
            plan = response_data.get("plan")
            if isinstance(plan, list):
                return plan
            return None
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            print(f"[Reasoner] Error al generar o parsear el plan: {e}")
            return None