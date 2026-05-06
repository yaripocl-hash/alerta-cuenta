from functools import lru_cache

import anthropic

from app.config import get_settings


@lru_cache
def get_anthropic_client() -> anthropic.AsyncAnthropic:
    """Retorna el cliente Anthropic async. La API key viene solo de variables de entorno."""
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def call_claude(system_prompt: str, user_content: str) -> str:
    """Realiza una llamada async a Claude y retorna el texto de la respuesta."""
    settings = get_settings()
    client = get_anthropic_client()
    message = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text
