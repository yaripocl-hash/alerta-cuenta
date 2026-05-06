import secrets
import string


def generate_tracking_code(length: int = 12) -> str:
    """Genera un código de seguimiento alfanumérico legible."""
    alphabet = string.ascii_uppercase + string.digits
    # Excluir caracteres ambiguos (0, O, I, 1)
    alphabet = alphabet.translate(str.maketrans("", "", "0OI1"))
    return "AC-" + "".join(secrets.choice(alphabet) for _ in range(length))
