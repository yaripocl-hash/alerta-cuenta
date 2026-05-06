from abc import ABC, abstractmethod
from app.services.ai_service import load_prompt, run_agent


class BaseAgent(ABC):
    """Clase base para todos los agentes Claude de Alerta Cuenta.

    Cada subclase define su nombre y versión de prompt.
    El método run() envía el caso a Claude y retorna un dict estructurado.
    Los prompts se cargan desde prompts/<agent_name>/<version>.md via ai_service.
    """

    agent_name: str = ""
    prompt_version: str = "v1"

    @abstractmethod
    async def run(self, description: str, context: dict) -> dict:
        """Ejecuta el agente con el relato del usuario y contexto adicional."""
        raise NotImplementedError
