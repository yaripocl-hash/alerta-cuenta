from fastapi import UploadFile
from app.db.supabase import get_supabase
from app.config import get_settings


async def upload_evidence(case_id: str, file: UploadFile) -> dict:
    """Sube evidencia a Supabase Storage y persiste metadatos."""
    # TODO: implementar en Fase 3
    raise NotImplementedError
