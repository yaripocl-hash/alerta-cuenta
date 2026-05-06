from app.db.supabase import get_supabase
from app.core.tracking_code import generate_tracking_code
from app.schemas.case import CaseCreate


async def create_case(payload: CaseCreate) -> dict:
    """Persiste un caso en Supabase y retorna el registro creado."""
    # TODO: implementar en Fase 2
    raise NotImplementedError


async def get_case_by_tracking(tracking_code: str, email: str) -> dict | None:
    """Busca un caso por tracking_code y email. Retorna None si no existe."""
    # TODO: implementar en Fase 3
    raise NotImplementedError
