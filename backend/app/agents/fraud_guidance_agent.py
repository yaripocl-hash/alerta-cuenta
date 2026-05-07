import json

from app.agents.base_agent import BaseAgent
from app.services.ai_service import run_agent


class FraudGuidanceAgent(BaseAgent):
    """Evalúa si una situación descrita tiene señales de fraude y entrega orientación.

    Usa el prompt en prompts/fraud_guidance/v1.md.
    Retorna: { assessment, assessment_label, red_flags, immediate_actions,
               recommended_steps, institutions, should_file_case, disclaimer }
    """

    agent_name = "fraud_guidance"
    prompt_version = "v1"

    async def run(self, description: str, context: dict = None) -> dict:
        user_content = json.dumps(
            {
                "description": description,
                "additional_context": context or {},
            },
            ensure_ascii=False,
        )
        return await run_agent(self.agent_name, user_content, self.prompt_version)
