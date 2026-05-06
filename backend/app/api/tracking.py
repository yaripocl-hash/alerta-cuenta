from fastapi import APIRouter, HTTPException

from app.db.supabase import get_supabase
from app.schemas.tracking import TrackingQuery, TrackingResponse
from app.services.audit_service import log_action

router = APIRouter()


@router.post("/lookup", response_model=TrackingResponse)
async def lookup_case(query: TrackingQuery):
    supabase = get_supabase()

    result = (
        supabase.table("cases")
        .select("*")
        .eq("tracking_code", query.tracking_code)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        await log_action(action="tracking_lookup_failed", metadata={"reason": "not_found"})
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    case = result.data[0]
    case_id: str = case["id"]

    people = (
        supabase.table("case_people")
        .select("contact_email")
        .eq("case_id", case_id)
        .execute()
    )
    emails = [p["contact_email"].lower() for p in people.data if p.get("contact_email")]
    if str(query.email).lower() not in emails:
        await log_action(
            case_id=case_id,
            action="tracking_lookup_failed",
            metadata={"reason": "email_mismatch"},
        )
        raise HTTPException(status_code=403, detail="No autorizado")

    supabase.table("case_events").insert({
        "case_id": case_id,
        "event_type": "tracking_lookup",
        "actor": "backend",
    }).execute()
    await log_action(case_id=case_id, action="tracking_lookup")

    ai_result = (
        supabase.table("case_ai_outputs")
        .select("output_json")
        .eq("case_id", case_id)
        .eq("agent_name", "case_summary")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    summary = None
    if ai_result.data:
        out = ai_result.data[0]["output_json"]
        summary = (
            out.get("summary")
            or out.get("caso_resumen", {}).get("tipo_fraude", {}).get("descripcion")
        )

    return TrackingResponse(
        tracking_code=case["tracking_code"],
        status=case["status"],
        fraud_type=case.get("fraud_type"),
        summary=summary,
        created_at=case["created_at"],
        updated_at=case["updated_at"],
    )
