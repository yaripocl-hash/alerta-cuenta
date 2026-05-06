from app.agents.base_agent import BaseAgent


class FraudClassifierAgent(BaseAgent):
    """Clasifica el tipo de fraude según el relato del usuario.

    Usa el prompt en prompts/fraud_classifier/v1.md.
    Retorna: { fraud_type, confidence, reasoning }
    """

    agent_name = "fraud_classifier"
    prompt_version = "v1"

    async def run(self, description: str, context: dict) -> dict:
        # TODO: implementar en Fase 2
        # 1. Cargar prompt via ai_service.load_prompt(self.agent_name, self.prompt_version)
        # 2. Construir user_content con description + context
        # 3. Llamar a ai_service.run_agent(...)
        # 4. Parsear y retornar output JSON
        raise NotImplementedError
