from app.config import get_settings


async def send_tracking_code(email: str, tracking_code: str) -> None:
    """Envía el código de seguimiento al email del usuario."""
    settings = get_settings()
    if settings.email_provider == "console":
        print(f"[EMAIL] Para: {email} | Código: {tracking_code}")
        return
    # TODO: implementar SMTP en Fase 2
    raise NotImplementedError(f"Email provider '{settings.email_provider}' no implementado")
