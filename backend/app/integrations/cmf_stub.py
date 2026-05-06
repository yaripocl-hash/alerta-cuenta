"""
STUB — Integración con CMF (Comisión para el Mercado Financiero)

Estado: NO IMPLEMENTADO. Placeholder para futura integración.

La CMF tiene un portal de denuncias en cmfchile.cl.
En producción, requeriría acuerdo institucional.

Por ahora, Alerta Cuenta orienta al usuario hacia el canal correcto.
"""


def get_cmf_complaint_url() -> str:
    return "https://www.cmfchile.cl/portal/principal/613/w3-article-10254.html"


def format_for_cmf(case_data: dict) -> dict:
    """Placeholder: formatea el caso para la CMF."""
    raise NotImplementedError("Integración CMF no implementada")
