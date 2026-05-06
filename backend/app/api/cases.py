from fastapi import APIRouter, HTTPException

from app.db.supabase import get_supabase
from app.schemas.case import CaseCreate, CaseResponse
from app.services.case_service import create_case

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case_endpoint(payload: CaseCreate):
    try:
        case = await create_case(payload)
        return case
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{tracking_code}", response_model=CaseResponse)
async def get_case(tracking_code: str):
    supabase = get_supabase()
    result = (
        supabase.table("cases")
        .select("*")
        .eq("tracking_code", tracking_code)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return result.data[0]
