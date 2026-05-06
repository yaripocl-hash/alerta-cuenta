from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class CaseCreate(BaseModel):
    description: str = Field(..., min_length=20, max_length=5000)
    incident_date: Optional[date] = None
    amount_affected: Optional[float] = None
    currency: str = "CLP"
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    target_institution: Optional[str] = None


class CaseResponse(BaseModel):
    id: str
    tracking_code: str
    status: str
    fraud_type: Optional[str] = None
    created_at: str
