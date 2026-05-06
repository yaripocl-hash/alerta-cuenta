import hashlib
import re
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.db.supabase import get_supabase
from app.services.audit_service import log_action
from app.services.storage_service import upload_file

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf", "text/plain"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w.\-]", "_", name)


@router.post("/{case_id}", status_code=201)
async def upload_evidence(case_id: str, file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Tipo de archivo no permitido")

    data = await file.read()
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (máximo 10 MB)")

    settings = get_settings()
    sha256 = hashlib.sha256(data).hexdigest()
    safe_name = _sanitize_filename(file.filename or "file")
    storage_path = f"{case_id}/{uuid.uuid4().hex}-{safe_name}"

    try:
        await upload_file(settings.supabase_storage_bucket, storage_path, data, file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {exc}") from exc

    supabase = get_supabase()
    supabase.table("case_evidence").insert({
        "case_id": case_id,
        "filename": safe_name,
        "content_type": file.content_type,
        "size_bytes": len(data),
        "storage_path": storage_path,
        "sha256": sha256,
        "scan_status": "skipped",
    }).execute()

    supabase.table("case_events").insert({
        "case_id": case_id,
        "event_type": "evidence_uploaded",
        "actor": "backend",
    }).execute()
    await log_action(
        case_id=case_id,
        action="evidence_uploaded",
        metadata={"content_type": file.content_type, "size_bytes": len(data)},
    )

    return {"storage_path": storage_path, "sha256": sha256, "size_bytes": len(data)}


@router.get("/{case_id}")
async def list_evidence(case_id: str):
    supabase = get_supabase()
    result = (
        supabase.table("case_evidence")
        .select("id, filename, content_type, size_bytes, storage_path, sha256, scan_status, created_at")
        .eq("case_id", case_id)
        .is_("deleted_at", "null")
        .execute()
    )
    return result.data
