# -*- coding: utf-8 -*-
# app/workers.py

import time
from PyQt6.QtCore import QObject, pyqtSignal

# --- WORKER PARA CHAT NORMAL ---
class Worker(QObject):
    """Worker para ejecutar una consulta de chat en un hilo separado."""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, chat_engine, user_message, parent=None):
        print(f"[workers.py][Worker][__init__] Inicializando Worker con mensaje del usuario: {user_message}")
        super().__init__(parent)
        self.chat_engine = chat_engine
        self.user_message = user_message
        print(f"[workers.py][Worker][__init__] chat_engine.provider: {self.chat_engine.provider}")
        print(f"[workers.py][Worker][__init__] chat_engine.history length: {len(self.chat_engine.history) if self.chat_engine.history else 'N/A'}")

    def run(self):
        try:
            print(f"[Worker] Procesando mensaje del usuario: {self.user_message}")
            if not self.chat_engine.provider:
                raise ValueError("El proveedor del modelo no está configurado en ChatEngine.")
            response = self.chat_engine.provider.query(self.chat_engine.history)
            print(f"[Worker] Respuesta recibida: {response}")
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(f"Error en el worker de chat: {e}")

# --- WORKER PARA MODO AGENTE ---
class AgentWorker(QObject):
    """Worker para ejecutar el agente en un hilo separado."""
    agent_step = pyqtSignal(str, str, str) # thought, tool_name, args
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, agent, objective, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.objective = objective
        self.agent.report_step_callback = self._handle_agent_step

    def _handle_agent_step(self, thought: str, tool_name: str, args):
        import json
        if isinstance(args, dict):
            args_str = json.dumps(args, ensure_ascii=False)
        else:
            args_str = str(args)
        self.agent_step.emit(thought, tool_name, args_str)

    def run(self):
        try:
            final_response = self.agent.run(self.objective)
            self.response_ready.emit(final_response)
        except Exception as e:
            self.error_occurred.emit(f"Error en el worker del agente: {e}")

# --- WORKER PARA MODO RAZONADOR ---
class ReasonerWorker(QObject):
    """Worker para el modo razonador (Plan-and-Execute)."""
    plan_ready = pyqtSignal(list)
    step_result = pyqtSignal(int, str, str) # step_index, task, result
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, provider, user_objective, custom_prompt, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.user_objective = user_objective
        self.custom_prompt = custom_prompt

    def run(self):
        try:
            from app.reasoner import Reasoner
            from app.agent import Agent

            planner = Reasoner(self.provider, custom_prompt=self.custom_prompt)
            plan = planner.generate_plan(self.user_objective)

            if not plan:
                raise RuntimeError("El razonador no pudo generar un plan.")
            
            self.plan_ready.emit(plan)

            executor_agent = Agent(self.provider, custom_prompt=self.custom_prompt)
            final_result = ""
            for i, task in enumerate(plan):
                result = executor_agent.execute_task(task)
                self.step_result.emit(i + 1, task, result)
                final_result += f"Resultado del paso {i+1}: {result}\n\n"
            
            self.response_ready.emit(f"Tarea completada. Resultados combinados:\n{final_result}")

        except Exception as e:
            self.error_occurred.emit(f"Error en el worker del razonador: {e}")

# --- WORKER PARA LIMPIEZA ---
class CleanupWorker(QObject):
    """
    Worker que se ejecuta en un hilo separado para realizar tareas de limpieza
    sin bloquear la interfaz de usuario.
    """
    finished = pyqtSignal()

    def __init__(self, ollama_manager=None, parent=None):
        super().__init__(parent)

    def run(self):
        """
        El método principal que realiza la limpieza.
        """
        print("[CleanupWorker] Iniciando limpieza...")
        # No hay tareas de limpieza activas relacionadas con Ollama.
        # Se mantiene para la fluidez del diálogo de cierre.
        time.sleep(1)
        print("[CleanupWorker] Limpieza finalizada.")
        self.finished.emit()
