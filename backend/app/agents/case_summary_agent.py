from app.agents.base_agent import BaseAgent


class CaseSummaryAgent(BaseAgent):
    """Resume el caso en lenguaje estructurado y claro para el expediente.

    Usa el prompt en prompts/case_summary/v1.md.
    Retorna: { summary, key_facts, timeline, recommended_actions }
    """

    agent_name = "case_summary"
    prompt_version = "v1"

    async def run(self, description: str, context: dict) -> dict:
        # TODO: implementar en Fase 2
        raise NotImplementedError
