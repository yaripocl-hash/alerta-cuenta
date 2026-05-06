from fastapi import APIRouter, HTTPException
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
    raise HTTPException(status_code=501, detail="Not implemented yet")
