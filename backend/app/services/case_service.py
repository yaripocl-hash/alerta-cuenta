from app.db.supabase import get_supabase
from app.core.tracking_code import generate_tracking_code
from app.schemas.case import CaseCreate
from app.services.audit_service import log_action


async def create_case(payload: CaseCreate) -> dict:
    """Crea un caso en Supabase. No llama a agentes Claude."""
    supabase = get_supabase()
    tracking_code = generate_tracking_code()

    # ── 1. Insertar en public.cases ───────────────────────────────────────────
    case_data: dict = {
        "tracking_code": tracking_code,
        "status": "submitted",
        "description": payload.description,
        "currency": payload.currency,
    }
    if payload.fraud_type is not None:
        case_data["fraud_type"] = payload.fraud_type
    if payload.channel is not None:
        case_data["channel"] = payload.channel
    if payload.incident_date is not None:
        case_data["incident_date"] = payload.incident_date.isoformat()
    if payload.incident_occurred_at is not None:
        case_data["incident_occurred_at"] = payload.incident_occurred_at.isoformat()
    if payload.incident_time_precision is not None:
        case_data["incident_time_precision"] = payload.incident_time_precision
    if payload.amount_affected is not None:
        case_data["amount_affected"] = payload.amount_affected
    if payload.target_institution is not None:
        case_data["target_institution"] = payload.target_institution

    result = supabase.table("cases").insert(case_data).execute()
    case: dict = result.data[0]
    case_id: str = case["id"]

    # ── 2. Insertar en public.case_people (si hay datos de persona) ───────────
    has_person_data = any([
        payload.contact_email,
        payload.contact_phone,
        payload.victim_age is not None,
        payload.victim_age_range,
        payload.identity_type,
        payload.identity_last4,
    ])
    if has_person_data:
        person_data: dict = {
            "case_id": case_id,
            "person_role": payload.person_role,
            "is_foreign_person": payload.is_foreign_person,
        }
        if payload.contact_email is not None:
            person_data["contact_email"] = str(payload.contact_email)
        if payload.contact_phone is not None:
            person_data["contact_phone"] = payload.contact_phone
        if payload.victim_age is not None:
            person_data["victim_age"] = payload.victim_age
        if payload.victim_age_range is not None:
            person_data["victim_age_range"] = payload.victim_age_range
        if payload.identity_type is not None:
            person_data["identity_type"] = payload.identity_type
        if payload.identity_last4 is not None:
            person_data["identity_last4"] = payload.identity_last4
        supabase.table("case_people").insert(person_data).execute()

    # ── 3. Insertar evento inicial en public.case_events ─────────────────────
    supabase.table("case_events").insert({
        "case_id": case_id,
        "event_type": "case_created",
        "actor": "backend",
    }).execute()

    # ── 4. Registrar en audit_log sin PII ────────────────────────────────────
    await log_action(
        case_id=case_id,
        action="case_created",
        actor="backend",
        metadata={"has_contact": bool(payload.contact_email or payload.contact_phone)},
    )

    return case


async def get_case_by_tracking(tracking_code: str, email: str) -> dict | None:
    """Busca un caso por tracking_code y email. Retorna None si no existe."""
    # TODO: implementar en Fase 3
    raise NotImplementedError
