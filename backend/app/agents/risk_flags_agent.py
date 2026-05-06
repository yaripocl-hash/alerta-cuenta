from app.agents.base_agent import BaseAgent


class RiskFlagsAgent(BaseAgent):
    """Detecta señales de alerta o inconsistencias en el relato del usuario.

    Usa el prompt en prompts/risk_flags/v1.md.
    Retorna: { flags: [], risk_level: "high|medium|low", notes: [] }
    """

    agent_name = "risk_flags"
    prompt_version = "v1"

    async def run(self, description: str, context: dict) -> dict:
        # TODO: implementar en Fase 2
        raise NotImplementedError
