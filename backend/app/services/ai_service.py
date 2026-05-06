from app.integrations.anthropic_client import get_anthropic_client
from app.config import get_settings
from pathlib import Path


def load_prompt(agent_name: str, version: str = "v1") -> str:
    """Carga el prompt versionado desde prompts/<agent_name>/<version>.md"""
    prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / agent_name / f"{version}.md"
    return prompt_path.read_text(encoding="utf-8")


async def run_agent(agent_name: str, user_content: str, version: str = "v1") -> dict:
    """Ejecuta un agente Claude con el prompt versionado correspondiente."""
    # TODO: implementar en Fase 2
    raise NotImplementedError
