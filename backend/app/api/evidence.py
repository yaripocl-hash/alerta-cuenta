from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf", "text/plain"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/{case_id}")
async def upload_evidence(case_id: str, file: UploadFile = File(...)):
    # TODO: implementar en Fase 3
    # 1. Validar content_type y tamaño
    # 2. Subir a Supabase Storage via storage_service
    # 3. Persistir metadatos en case_evidence
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Tipo de archivo no permitido")
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{case_id}")
async def list_evidence(case_id: str):
    # TODO: implementar en Fase 3
    raise HTTPException(status_code=501, detail="Not implemented yet")
