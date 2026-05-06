"""
STUB — Integración con SERNAC (Servicio Nacional del Consumidor)

Estado: NO IMPLEMENTADO. Placeholder para futura integración.

SERNAC no tiene API pública documentada a la fecha.
En producción, esta integración requeriría:
- Investigar canales oficiales de SERNAC
- Acuerdo formal con la institución
- Revisión legal del uso de datos

Por ahora, Alerta Cuenta genera el expediente para que el usuario
lo presente manualmente en sernac.cl o en una sucursal.
"""


def get_sernac_complaint_form_url() -> str:
    return "https://www.sernac.cl/portal/604/w3-article-62498.html"


def format_for_sernac(case_data: dict) -> dict:
    """Formatea los datos del caso para el formulario de SERNAC.

    Retorna un dict con los campos del formulario, para que el usuario
    pueda copiar y pegar en el sitio de SERNAC.
    """
    # TODO: mapear campos del caso al formulario de SERNAC cuando se conozca su estructura
    raise NotImplementedError("Integración SERNAC no implementada")
