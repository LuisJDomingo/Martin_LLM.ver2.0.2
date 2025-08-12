# -*- coding: utf-8 -*-
# app/workers.py

from PyQt6.QtCore import QObject, pyqtSignal

# --- WORKER PARA CHAT NORMAL ---
class Worker(QObject):
    """Worker para ejecutar una consulta de chat en un hilo separado."""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, chat_engine, user_message, parent=None):
        super().__init__(parent)
        self.chat_engine = chat_engine
        self.user_message = user_message

    def run(self):
        try:
            response = self.chat_engine.ask(self.user_message)
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
        # Conectar el callback del agente a nuestra señal
        self.agent.report_step_callback = self.agent_step.emit

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

            # 1. Planificar
            planner = Reasoner(self.provider, custom_prompt=self.custom_prompt)
            plan = planner.generate_plan(self.user_objective)

            if not plan:
                raise RuntimeError("El razonador no pudo generar un plan.")
            
            self.plan_ready.emit(plan)

            # 2. Ejecutar
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

    def __init__(self, ollama_manager, parent=None):
        super().__init__(parent)
        self.ollama_manager = ollama_manager

    def run(self):
        """
        El método principal que realiza la limpieza.
        """
        print("[CleanupWorker] Iniciando limpieza...")

        if self.ollama_manager:
            self.ollama_manager.stop()
            print("[CleanupWorker] Manager de Ollama detenido.")

        print("[CleanupWorker] Limpieza finalizada.")
        self.finished.emit()

# --- WORKER PARA GESTIÓN DE MODELOS ---
class ModelDeleteWorker(QObject):
    """Worker para eliminar un modelo de Ollama en un hilo separado."""
    finished = pyqtSignal(bool, str, str) # success, model_name, message

    def __init__(self, ollama_manager, model_name, parent=None):
        super().__init__(parent)
        self.ollama_manager = ollama_manager
        self.model_name = model_name

    def run(self):
        """Ejecuta la lógica de eliminación y emite el resultado."""
        try:
            success, message = self.ollama_manager.delete_model(self.model_name)
            self.finished.emit(success, self.model_name, message)
        except Exception as e:
            # Captura cualquier excepción inesperada durante la llamada
            self.finished.emit(False, self.model_name, f"Se produjo un error inesperado en el worker: {e}")