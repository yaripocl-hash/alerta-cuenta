from fastapi import APIRouter, HTTPException
from app.schemas.tracking import TrackingQuery, TrackingResponse

router = APIRouter()


@router.post("/lookup", response_model=TrackingResponse)
async def lookup_case(query: TrackingQuery):
    # TODO: implementar en Fase 3
    # 1. Buscar caso por tracking_code + email
    # 2. Verificar HMAC del tracking_code
    # 3. Retornar estado y resumen del caso
    raise HTTPException(status_code=501, detail="Not implemented yet")
