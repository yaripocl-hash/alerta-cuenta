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
    prompt_version = "v2"

    _PRE = (
        "El siguiente relato fue escrito por una persona que puede estar en estado de angustia. "
        "Léelo con cuidado antes de estructurarlo:"
    )
    _POST = (
        "Antes de responder verifica: "
        "(1) Solo incluye en key_facts lo que el usuario mencionó explícitamente. "
        "(2) Si detectas datos sensibles (RUT, número de tarjeta, clave), enmascáralos en el output. "
        "(3) El disclaimer debe ser exactamente el texto especificado en las instrucciones, sin modificaciones. "
        "(4) Tu respuesta debe comenzar con { y terminar con }."
    )

    async def run(self, description: str, context: dict = None) -> dict:
        user_content = json.dumps(
            {
                "description": description,
                "additional_context": context or {},
            },
            ensure_ascii=False,
        )
        return await run_agent(
            self.agent_name, user_content, self.prompt_version,
            pre_prompt=self._PRE, post_prompt=self._POST,
        )
