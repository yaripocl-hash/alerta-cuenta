from fastapi import APIRouter, HTTPException
from app.schemas.ai import AIRequest, AIResponse

router = APIRouter()


@router.post("/classify", response_model=AIResponse)
async def classify_fraud(payload: AIRequest):
    # TODO: implementar en Fase 2
    # Llama a fraud_classifier_agent
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/summarize", response_model=AIResponse)
async def summarize_case(payload: AIRequest):
    # TODO: implementar en Fase 2
    # Llama a case_summary_agent
    raise HTTPException(status_code=501, detail="Not implemented yet")
