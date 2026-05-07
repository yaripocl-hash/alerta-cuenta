import json

from app.agents.base_agent import BaseAgent
from app.services.ai_service import run_agent


class CaseSummaryAgent(BaseAgent):
    """Resume el caso en lenguaje estructurado y claro para el expediente.

    Usa el prompt en prompts/case_summary/v1.md.
    Retorna: { summary, key_facts, timeline, recommended_actions, missing_info, disclaimer }
    """

    agent_name = "case_summary"
    prompt_version = "v1"

    _PRE = (
        "Los datos adicionales (fraud_type, incident_date, amount_affected, institution) "
        "fueron ingresados por el usuario en el formulario — tratalos como hechos informados, no como inferencias:"
    )
    _POST = (
        "El campo 'disclaimer' debe terminar siempre con la frase: 'No constituye asesoría legal.' "
        "Responde solo con JSON válido."
    )

    async def run(self, description: str, context: dict) -> dict:
        user_content = json.dumps(
            {
                "description": description,
                "fraud_type": context.get("fraud_type"),
                "incident_date": context.get("incident_date"),
                "amount_affected": context.get("amount_affected"),
                "institution": context.get("institution"),
            },
            ensure_ascii=False,
        )
        return await run_agent(
            self.agent_name, user_content, self.prompt_version,
            pre_prompt=self._PRE, post_prompt=self._POST,
        )
