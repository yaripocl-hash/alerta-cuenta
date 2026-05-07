import json

from app.agents.base_agent import BaseAgent
from app.services.ai_service import run_agent


class FraudClassifierAgent(BaseAgent):
    """Clasifica el tipo de fraude según el relato del usuario.

    Usa el prompt en prompts/fraud_classifier/v1.md.
    Retorna: { fraud_type, confidence, reasoning, needs_clarification, clarification_question }
    """

    agent_name = "fraud_classifier"
    prompt_version = "v2"

    async def run(self, description: str, context: dict) -> dict:
        user_content = json.dumps(
            {
                "description": description,
                "fraud_type_declared": context.get("fraud_type_declared"),
                "urlhaus_results": context.get("urlhaus_results"),
            },
            ensure_ascii=False,
        )
        return await run_agent(self.agent_name, user_content, self.prompt_version)
