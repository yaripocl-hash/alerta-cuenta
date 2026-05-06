from app.agents.base_agent import BaseAgent


class EvidenceGapAgent(BaseAgent):
    """Identifica qué evidencia falta para fortalecer el caso.

    Usa el prompt en prompts/evidence_gap/v1.md.
    Retorna: { missing_evidence: [], priority: "high|medium|low", tips: [] }
    """

    agent_name = "evidence_gap"
    prompt_version = "v1"

    async def run(self, description: str, context: dict) -> dict:
        # TODO: implementar en Fase 3
        raise NotImplementedError
