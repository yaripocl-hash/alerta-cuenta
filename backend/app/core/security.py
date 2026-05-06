from fastapi import HTTPException, Header
from typing import Optional


async def require_app_token(x_app_token: Optional[str] = Header(None)) -> None:
    """Placeholder para autenticación futura entre frontend y backend."""
    # En MVP no se requiere token. En producción, implementar aquí.
    pass
