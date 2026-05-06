from app.agents.base_agent import BaseAgent


class StatementGeneratorAgent(BaseAgent):
    """Genera una declaración preliminar del caso adaptada a la institución destino.

    Usa el prompt en prompts/statement_generator/v1.md.
    Retorna: { statement_text, institution, format, disclaimer }
    """

    agent_name = "statement_generator"
    prompt_version = "v1"

    async def run(self, description: str, context: dict) -> dict:
        # TODO: implementar en Fase 4
        raise NotImplementedError
