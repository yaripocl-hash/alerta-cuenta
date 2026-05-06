import time

from fastapi import APIRouter, HTTPException

from app.agents.case_summary_agent import CaseSummaryAgent
from app.agents.fraud_classifier_agent import FraudClassifierAgent
from app.config import get_settings
from app.db.supabase import get_supabase
from app.schemas.ai import AIRequest, AIResponse
from app.services.audit_service import log_action

router = APIRouter()


async def _persist_ai_output(case_id: str, agent, output: dict, latency_ms: int) -> None:
    settings = get_settings()
    supabase = get_supabase()
    supabase.table("case_ai_outputs").insert({
        "case_id": case_id,
        "agent_name": agent.agent_name,
        "prompt_version": agent.prompt_version,
        "model": settings.anthropic_model,
        "output_json": output,
        "latency_ms": latency_ms,
    }).execute()
    supabase.table("case_events").insert({
        "case_id": case_id,
        "event_type": "ai_output_generated",
        "description": agent.agent_name,
        "actor": "backend",
    }).execute()
    await log_action(
        case_id=case_id,
        action="ai_agent_called",
        metadata={"agent": agent.agent_name, "latency_ms": latency_ms},
    )


@router.post("/classify", response_model=AIResponse)
async def classify_fraud(payload: AIRequest):
    settings = get_settings()
    agent = FraudClassifierAgent()
    t0 = time.monotonic()
    try:
        output = await agent.run(payload.description, payload.additional_context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    latency_ms = int((time.monotonic() - t0) * 1000)

    await _persist_ai_output(payload.case_id, agent, output, latency_ms)

    fraud_type = output.get("fraud_type") or output.get("classification", {}).get("fraud_type")
    if fraud_type and not output.get("needs_clarification"):
        get_supabase().table("cases").update({"fraud_type": fraud_type}).eq("id", payload.case_id).execute()

    return AIResponse(
        agent=agent.agent_name,
        prompt_version=agent.prompt_version,
        output=output,
        model_used=settings.anthropic_model,
    )


@router.post("/summarize", response_model=AIResponse)
async def summarize_case(payload: AIRequest):
    settings = get_settings()
    agent = CaseSummaryAgent()
    t0 = time.monotonic()
    try:
        output = await agent.run(payload.description, payload.additional_context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    latency_ms = int((time.monotonic() - t0) * 1000)

    await _persist_ai_output(payload.case_id, agent, output, latency_ms)

    return AIResponse(
        agent=agent.agent_name,
        prompt_version=agent.prompt_version,
        output=output,
        model_used=settings.anthropic_model,
    )
