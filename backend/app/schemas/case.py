from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class CaseCreate(BaseModel):
    # ── Relato ────────────────────────────────────────────────────────────────
    description: str = Field(..., min_length=20, max_length=5000)

    # ── Clasificación (se puede enviar o dejar que Claude la infiera luego) ──
    fraud_type: Optional[str] = None
    channel: Optional[str] = None

    # ── Fecha/hora del incidente ──────────────────────────────────────────────
    incident_date: Optional[date] = None
    incident_occurred_at: Optional[datetime] = None
    incident_time_precision: Optional[str] = None

    # ── Monto ────────────────────────────────────────────────────────────────
    amount_affected: Optional[float] = Field(default=None, ge=0)
    currency: str = "CLP"

    # ── Institución ──────────────────────────────────────────────────────────
    target_institution: Optional[str] = None

    # ── Persona / contacto (van a case_people) ───────────────────────────────
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    person_role: str = "victim"
    victim_age: Optional[int] = Field(default=None, ge=0, le=130)
    victim_age_range: Optional[str] = None
    is_foreign_person: bool = False
    identity_type: Optional[str] = None
    identity_last4: Optional[str] = Field(default=None, max_length=6)


class CaseResponse(BaseModel):
    id: str
    tracking_code: str
    status: str
    fraud_type: Optional[str] = None
    created_at: str
