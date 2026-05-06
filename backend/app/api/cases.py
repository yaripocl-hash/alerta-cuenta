from fastapi import APIRouter, HTTPException
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(payload: CaseCreate):
    # TODO: implementar en Fase 2
    # 1. Validar y persistir caso en Supabase
    # 2. Generar tracking_code via core/tracking_code.py
    # 3. Llamar a fraud_classifier_agent y case_summary_agent
    # 4. Guardar outputs en case_ai_outputs
    # 5. Retornar tracking_code al frontend
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{tracking_code}", response_model=CaseResponse)
async def get_case(tracking_code: str):
    # TODO: implementar en Fase 2
    # Requiere tracking_code + email (verificar con HMAC)
    raise HTTPException(status_code=501, detail="Not implemented yet")
