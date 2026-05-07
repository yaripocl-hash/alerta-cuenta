from pydantic import BaseModel
from typing import Any


class AIRequest(BaseModel):
    case_id: str
    description: str
    additional_context: dict[str, Any] = {}


class AIResponse(BaseModel):
    agent: str
    prompt_version: str
    output: dict[str, Any]
    model_used: str
    url_checks: list[dict[str, Any]] | None = None
