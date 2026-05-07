from functools import lru_cache
from typing import Any, Optional

import anthropic

from app.config import get_settings


@lru_cache
def get_anthropic_client() -> anthropic.AsyncAnthropic:
    """Retorna el cliente Anthropic async. La API key viene solo de variables de entorno."""
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def call_claude(
    system_prompt: str,
    user_content: str,
    tools: Optional[list] = None,
) -> Any:
    """Realiza una llamada async a Claude.

    Sin tools: retorna el texto de la respuesta como str.
    Con tools: retorna el dict de inputs del bloque tool_use (ya estructurado).
    """
    settings = get_settings()
    client = get_anthropic_client()
    kwargs: dict = {
        "model": settings.anthropic_model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = {"type": "any"}

    message = await client.messages.create(**kwargs)

    if tools:
        for block in message.content:
            if block.type == "tool_use":
                return block.input
        # Fallback: Claude no usó la tool (no debería ocurrir con tool_choice=any)
        return message.content[0].text

    return message.content[0].text
