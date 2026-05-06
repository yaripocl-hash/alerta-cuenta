from app.db.supabase import get_supabase
from app.config import get_settings


async def upload_file(bucket: str, path: str, data: bytes, content_type: str) -> str:
    """Sube un archivo a Supabase Storage. Retorna la ruta del archivo."""
    # TODO: implementar en Fase 3
    raise NotImplementedError


async def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    """Genera una URL firmada temporal para acceder a un archivo."""
    # TODO: implementar en Fase 3
    raise NotImplementedError
