from app.db.supabase import get_supabase


async def upload_file(bucket: str, path: str, data: bytes, content_type: str) -> str:
    """Sube un archivo a Supabase Storage. Retorna la ruta del archivo."""
    supabase = get_supabase()
    supabase.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"contentType": content_type},
    )
    return path


async def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    """Genera una URL firmada temporal para acceder a un archivo."""
    supabase = get_supabase()
    response = supabase.storage.from_(bucket).create_signed_url(path=path, expires_in=expires_in)
    # storage3 returns a TypedDict with key "signedURL"
    if isinstance(response, dict):
        return response.get("signedURL") or response.get("signed_url", "")
    return getattr(response, "signed_url", "") or getattr(response, "signedURL", "")
