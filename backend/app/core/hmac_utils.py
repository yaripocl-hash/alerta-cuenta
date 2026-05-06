import hmac
import hashlib
from app.config import get_settings


def sign_tracking_code(tracking_code: str) -> str:
    """Firma un tracking_code con HMAC-SHA256 usando APP_SECRET."""
    settings = get_settings()
    return hmac.new(
        settings.app_secret.encode(),
        tracking_code.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_tracking_code(tracking_code: str, signature: str) -> bool:
    """Verifica que la firma de un tracking_code sea válida."""
    expected = sign_tracking_code(tracking_code)
    return hmac.compare_digest(expected, signature)
