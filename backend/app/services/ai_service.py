import json
import re
from pathlib import Path
from typing import Optional

from app.integrations.anthropic_client import call_claude


def load_prompt(agent_name: str, version: str = "v1") -> str:
    """Carga el prompt versionado desde prompts/<agent_name>/<version>.md"""
    prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / agent_name / f"{version}.md"
    return prompt_path.read_text(encoding="utf-8")


def _extract_system_prompt(markdown: str) -> str:
    match = re.search(r"## System Prompt\s+```\s*(.*?)```", markdown, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown.strip()


def _extract_json(text: str) -> str:
    """Extrae el objeto JSON de la respuesta, tolerando texto adicional o code fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text


def _load_tool_for_agent(agent_name: str) -> Optional[dict]:
    """Carga la definición de tool del agente desde tools.json en la raíz del proyecto."""
    tools_path = Path(__file__).parent.parent.parent.parent / "tools.json"
    if not tools_path.exists():
        return None
    tools = json.loads(tools_path.read_text(encoding="utf-8"))
    for tool in tools:
        if tool.get("name") == agent_name:
            return tool
    return None


async def run_agent(agent_name: str, user_content: str, version: str = "v1") -> dict:
    """Ejecuta un agente Claude con el prompt versionado correspondiente.

    Usa tool_use si el agente tiene tool definida en tools.json,
    garantizando output estructurado sin parseo de texto libre.
    Cae a parseo de JSON si no existe tool para el agente.
    """
    markdown = load_prompt(agent_name, version)
    system_prompt = _extract_system_prompt(markdown)
    tool = _load_tool_for_agent(agent_name)

    if tool:
        result = await call_claude(system_prompt, user_content, tools=[tool])
        if isinstance(result, dict):
            return result
        # Fallback: call_claude retornó texto (no debería ocurrir con tool_choice=any)
        return json.loads(_extract_json(result))

    raw = await call_claude(system_prompt, user_content)
    return json.loads(_extract_json(raw))
