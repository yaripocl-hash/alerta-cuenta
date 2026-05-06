"""
STUB — Integración con CSIRT (Equipo de Respuesta ante Incidentes de Seguridad)

Estado: NO IMPLEMENTADO. Placeholder para futura integración.

El CSIRT del Gobierno de Chile tiene canal de reporte en csirt.gob.cl.
Relevante para fraudes con componente de ciberseguridad (phishing, malware).
"""


def get_csirt_report_url() -> str:
    return "https://www.csirt.gob.cl/reportar/"


def format_for_csirt(case_data: dict) -> dict:
    """Placeholder: formatea el caso para el CSIRT."""
    raise NotImplementedError("Integración CSIRT no implementada")
