import pytest
import json
from unittest.mock import MagicMock

# This is needed to make sure the app modules can be imported
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Martin_LLM'))

from app.agent import Agent
from app.reasoner import Reasoner
from app.llm_providers import BaseLLMProvider
from app.tools import tool_registry, BaseTool

@pytest.fixture
def mock_provider():
    """Fixture to create a mock LLM provider."""
    provider = MagicMock(spec=BaseLLMProvider)
    return provider

@pytest.fixture
def mock_tool():
    """Fixture for a generic mock tool."""
    tool = MagicMock(spec=BaseTool)
    tool.name = "mock_tool"
    tool.description = "A tool for testing."
    tool.run.return_value = "Tool executed successfully."
    return tool

def test_agent_parses_valid_json_and_calls_tool(mock_provider, mock_tool):
    """Test that the agent correctly parses a valid JSON response and calls the right tool."""
    # Register the mock tool for this test
    tool_registry.register(mock_tool)
    
    # The response the mock LLM will give
    llm_response = {
        "thought": "I should use the mock tool.",
        "action": {
            "tool_name": "mock_tool",
            "args": "some arguments"
        }
    }
    # El agente verá el resultado de la herramienta y decidirá terminar
    finish_response = {
        "thought": "La herramienta funcionó, ahora he terminado.",
        "action": {
            "tool_name": "finish",
            "args": "La respuesta final se basa en el resultado de la herramienta."
        }
    }
    mock_provider.query.side_effect = [json.dumps(llm_response), json.dumps(finish_response)]

    mock_provider.query.return_value = json.dumps(llm_response)

    agent = Agent(provider=mock_provider)
    final_answer = agent.run("some objective")

    # Afirmar que el proveedor fue llamado dos veces
    assert mock_provider.query.call_count == 2
    # Afirmar que la herramienta correcta fue llamada con los argumentos correctos
    mock_tool.run.assert_called_once_with("some arguments")
    # Afirmar que la respuesta final es correcta
    assert final_answer == "La respuesta final se basa en el resultado de la herramienta."
    # Anular el registro de la herramienta para no afectar a otras pruebas
    tool_registry._tools.pop("mock_tool", None)

def test_agent_handles_finish_action(mock_provider):
    """Test that the agent correctly handles the 'finish' action."""
    llm_response = {
        "thought": "I am done.",
        "action": {
            "tool_name": "finish",
            "args": "This is the final answer."
        }
    }
    mock_provider.query.return_value = json.dumps(llm_response)

    agent = Agent(provider=mock_provider)
    final_answer = agent.run("some objective")

    assert final_answer == "This is the final answer."
    mock_provider.query.assert_called_once()

def test_agent_handles_invalid_json(mock_provider):
    """Prueba que el agente puede recuperarse de una respuesta JSON inválida del LLM."""
    invalid_json_response = "esto no es json"
    valid_finish_response = {
        "thought": "Fallé antes, pero ahora terminaré.",
        "action": {"tool_name": "finish", "args": "Respuesta final después de la recuperación."}
    }
    
    # El proveedor simulado primero devolverá JSON inválido, luego JSON válido
    mock_provider.query.side_effect = [invalid_json_response, json.dumps(valid_finish_response)]
    
    agent = Agent(provider=mock_provider)
    final_answer = agent.run("some objective")

    assert mock_provider.query.call_count == 2
    assert final_answer == "Respuesta final después de la recuperación."
    # Comprobar que el agente envió la observación de error de vuelta al LLM
    history = agent.history
    assert "Observation: Error: Your last response was not a valid JSON object." in history[-2]['content']

def test_agent_handles_unknown_tool(mock_provider):
    """Prueba que el agente maneja que se le diga que use una herramienta que no existe."""
    unknown_tool_response = {
        "thought": "Usaré una herramienta que no existe.",
        "action": {"tool_name": "non_existent_tool", "args": "algunos argumentos"}
    }
    valid_finish_response = {
        "thought": "Esa herramienta no existía, terminaré ahora.",
        "action": {"tool_name": "finish", "args": "Terminado después de intentar una herramienta desconocida."}
    }
    mock_provider.query.side_effect = [json.dumps(unknown_tool_response), json.dumps(valid_finish_response)]

    agent = Agent(provider=mock_provider)
    final_answer = agent.run("some objective")

    assert mock_provider.query.call_count == 2
    assert final_answer == "Terminado después de intentar una herramienta desconocida."
    # Comprobar que el agente envió la observación de error de vuelta al LLM
    history = agent.history
    assert "Error: Herramienta desconocida: 'non_existent_tool'" in history[-2]['content']

def test_reasoner_generates_valid_plan(mock_provider):
    """Prueba que el razonador puede generar un plan válido a partir de una respuesta del LLM."""
    plan_response = {
        "plan": [
            "Paso 1: Haz esto.",
            "Paso 2: Haz aquello.",
            "Paso 3: Termina."
        ]
    }
    mock_provider.query.return_value = json.dumps(plan_response)

    reasoner = Reasoner(provider=mock_provider)
    plan = reasoner.generate_plan("algún objetivo complejo")

    assert plan is not None
    assert isinstance(plan, list)
    assert len(plan) == 3
    assert plan[0] == "Paso 1: Haz esto."
    mock_provider.query.assert_called_once()

def test_reasoner_handles_invalid_plan_json(mock_provider):
    """Prueba que el razonador devuelve None si la respuesta del LLM no es un JSON válido."""
    mock_provider.query.return_value = "esto no es un plan"

    reasoner = Reasoner(provider=mock_provider)
    plan = reasoner.generate_plan("algún objetivo complejo")

    assert plan is None
    mock_provider.query.assert_called_once()