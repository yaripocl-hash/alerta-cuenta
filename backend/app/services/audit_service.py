from app.db.supabase import get_supabase


async def log_action(
    action: str,
    case_id: str | None = None,
    actor: str = "system",
    metadata: dict | None = None,
) -> None:
    """Registra una acción en public.audit_log.

    PROHIBIDO incluir en metadata: emails, teléfonos, nombres, RUTs,
    descripciones, tokens, claves bancarias ni ningún dato personal.
    Solo IDs, tipos, conteos y duraciones.
    """
    supabase = get_supabase()
    supabase.table("audit_log").insert({
        "case_id": case_id,
        "action": action,
        "actor": actor,
        "metadata": metadata or {},
    }).execute()
