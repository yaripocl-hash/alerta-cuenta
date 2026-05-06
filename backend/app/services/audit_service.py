from app.db.supabase import get_supabase


async def log_action(case_id: str, action: str, actor: str = "system", metadata: dict = {}) -> None:
    """Registra una acción en el audit_log. No registrar PII en metadata."""
    # TODO: implementar en Fase 2
    pass
