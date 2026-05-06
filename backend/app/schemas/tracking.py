from pydantic import BaseModel, EmailStr


class TrackingQuery(BaseModel):
    tracking_code: str
    email: EmailStr


class TrackingResponse(BaseModel):
    tracking_code: str
    status: str
    fraud_type: str | None
    summary: str | None
    created_at: str
    updated_at: str
