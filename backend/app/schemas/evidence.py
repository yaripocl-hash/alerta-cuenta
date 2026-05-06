from pydantic import BaseModel
from typing import Optional


class EvidenceMetadata(BaseModel):
    case_id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    description: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: str
    case_id: str
    filename: str
    content_type: str
    created_at: str
