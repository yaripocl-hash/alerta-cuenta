import os
import tempfile
import threading
import time

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents.case_summary_agent import CaseSummaryAgent
from app.agents.fraud_classifier_agent import FraudClassifierAgent
from app.config import get_settings
from app.db.supabase import get_supabase
from app.schemas.ai import AIRequest, AIResponse
from app.services.audit_service import log_action
from app.services.phishtank_service import check_urls_in_description

router = APIRouter()

# Mapeo de texto libre de Claude → enum del schema
_FRAUD_KEYWORDS = [
    ("vishing", "vishing"),
    ("smishing", "smishing"),
    ("whatsapp", "whatsapp_impersonation"),
    ("cuento del tío", "whatsapp_impersonation"),
    ("suplantación de identidad", "whatsapp_impersonation"),
    ("suplantación", "whatsapp_impersonation"),
    ("phishing", "phishing"),
    ("transferencia engañosa", "deceptive_transfer"),
    ("engañosa", "deceptive_transfer"),
    ("compra", "fake_online_purchase"),
    ("marketplace", "fake_online_purchase"),
    ("acceso no autorizado", "unauthorized_account_access"),
    ("acceso", "unauthorized_account_access"),
]


def _normalize_fraud_type(raw: str | None) -> str | None:
    if not raw:
        return None
    raw_lower = raw.lower()
    for keyword, enum_val in _FRAUD_KEYWORDS:
        if keyword in raw_lower:
            return enum_val
    return "other"


def _extract_fraud_type(output: dict) -> str | None:
    raw = (
        output.get("fraud_type")
        or output.get("classification", {}).get("fraud_type")
        or output.get("fraud_classification", {}).get("primary_type")
        or output.get("fraud_classification", {}).get("primary_category")
        or output.get("fraud_classification", {}).get("subcategory")
    )
    return _normalize_fraud_type(raw)


def _needs_clarification(output: dict) -> bool:
    val = (
        output.get("needs_clarification")
        or output.get("fraud_classification", {}).get("needs_clarification", False)
    )
    if isinstance(val, list):
        return len(val) > 0
    return bool(val)


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

    context = dict(payload.additional_context or {})
    urlhaus_results = await check_urls_in_description(payload.description)
    if urlhaus_results:
        context["urlhaus_results"] = urlhaus_results

    t0 = time.monotonic()
    try:
        output = await agent.run(payload.description, context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    latency_ms = int((time.monotonic() - t0) * 1000)

    await _persist_ai_output(payload.case_id, agent, output, latency_ms)

    fraud_type = _extract_fraud_type(output)
    if fraud_type and not _needs_clarification(output):
        get_supabase().table("cases").update({"fraud_type": fraud_type}).eq("id", payload.case_id).execute()

    return AIResponse(
        agent=agent.agent_name,
        prompt_version=agent.prompt_version,
        output=output,
        model_used=settings.anthropic_model,
        url_checks=urlhaus_results or None,
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


# ── Transcripción de audio con Whisper local ─────────────────────────────────

_whisper_lock = threading.Lock()
_whisper_model = None

_AUDIO_EXTS = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
}
_MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        with _whisper_lock:
            if _whisper_model is None:
                try:
                    import whisper as _whisper
                except ImportError as exc:
                    raise HTTPException(
                        status_code=503,
                        detail="Servicio de transcripción no disponible. Instala openai-whisper.",
                    ) from exc
                settings = get_settings()
                _whisper_model = _whisper.load_model(settings.whisper_model)
    return _whisper_model


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    content = await audio.read()

    if len(content) > _MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio demasiado grande (máx. 10 MB).")
    if len(content) < 2000:
        raise HTTPException(status_code=400, detail="Audio demasiado corto o vacío.")

    ct = (audio.content_type or "audio/webm").split(";")[0].strip().lower()
    ext = _AUDIO_EXTS.get(ct, ".webm")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(content)
            tmp_path = f.name

        model = _get_whisper()
        result = model.transcribe(tmp_path, language="es")
        text = (result.get("text") or "").strip()

        if not text:
            raise HTTPException(
                status_code=422,
                detail="No se detectó texto en el audio. Habla más cerca del micrófono e intenta de nuevo.",
            )
        return {"text": text}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al transcribir el audio.") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
