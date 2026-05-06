"""
STUB — Integración con Bancos y Fintechs

Estado: NO IMPLEMENTADO. Placeholder para futura integración.

Cada banco o fintech tiene su propio proceso de denuncia.
No existe API pública estándar para reportar fraudes en Chile.

En producción, esto podría ser:
- Lista de URLs de denuncia por banco/fintech
- Formulario de contacto específico
- Número de urgencias del banco

Por ahora, Alerta Cuenta orienta al usuario a contactar directamente
a su banco o fintech según el caso.
"""

BANK_CONTACTS: dict[str, dict] = {
    "banco_estado": {
        "fraud_phone": "600 200 7000",
        "web": "https://www.bancoestado.cl",
    },
    "banco_de_chile": {
        "fraud_phone": "600 637 3737",
        "web": "https://portales.bancochile.cl",
    },
    # Agregar más bancos según se identifiquen
}


def get_bank_contact(bank_id: str) -> dict | None:
    """Retorna datos de contacto de un banco dado su identificador."""
    return BANK_CONTACTS.get(bank_id)
