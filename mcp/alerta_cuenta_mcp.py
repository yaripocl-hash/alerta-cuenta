"""
MCP Server — Alerta Cuenta
Expone herramientas de fraude financiero para Claude Desktop / Claude Code.

Herramientas:
  verificar_url        → URLhaus (API pública, sin auth)
  ejemplos_fraude      → Dataset sintético de fraudes chilenos
  patrones_smishing    → Patrones conocidos de SMS fraudulentos en Chile
  indicadores_vishing  → Señales de alerta en llamadas telefónicas fraudulentas
"""

from mcp.server.fastmcp import FastMCP
import httpx
import json

mcp = FastMCP("alerta-cuenta")

# ─── Tool 1: Verificación de URL contra URLhaus ────────────────────────────────

@mcp.tool()
async def verificar_url(url: str) -> str:
    """
    Verifica si una URL está reportada como maliciosa en URLhaus (abuse.ch).
    Útil para analizar links recibidos por SMS, WhatsApp o email sospechosos.
    Retorna el estado de la URL y si está activa en bases de datos de phishing/malware.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://urlhaus-api.abuse.ch/v1/url/",
                data={"url": url},
            )
            data = response.json()

        if data.get("query_status") == "no_results":
            return json.dumps({
                "url": url,
                "estado": "no_encontrada",
                "mensaje": "Esta URL no aparece en la base de datos de URLhaus. Eso no garantiza que sea segura, pero no hay reportes conocidos.",
                "riesgo": "desconocido",
            }, ensure_ascii=False)

        if data.get("query_status") == "is_page":
            return json.dumps({
                "url": url,
                "estado": "REPORTADA_MALICIOSA",
                "fecha_reporte": data.get("date_added"),
                "amenaza": data.get("threat"),  # malware, phishing, etc.
                "activa": data.get("url_status") == "online",
                "mensaje": "⚠️ Esta URL está reportada como maliciosa en URLhaus. No la visites ni la compartas.",
                "riesgo": "ALTO",
            }, ensure_ascii=False)

        return json.dumps({"url": url, "respuesta_raw": data}, ensure_ascii=False)

    except httpx.TimeoutException:
        return json.dumps({
            "url": url,
            "estado": "error",
            "mensaje": "No se pudo consultar URLhaus (timeout). Tratar la URL con precaución.",
        }, ensure_ascii=False)


# ─── Tool 2: Ejemplos de fraudes chilenos ─────────────────────────────────────

EJEMPLOS_FRAUDE = {
    "smishing": [
        {
            "mensaje": "BANCO ESTADO: Detectamos acceso no autorizado a su cuenta. Verifique en: https://bancoestado-seguro.xyz/verificar",
            "señales": ["URL no es bancoestado.cl", "urgencia artificial", "link acortado o dominio sospechoso"],
            "accion": "No hacer clic. Llamar directamente al banco al 600 200 7000.",
        },
        {
            "mensaje": "TENPO: Su cuenta ha sido temporalmente suspendida por seguridad. Reactívela aquí: tenpo-cl.net/reactivar",
            "señales": ["Dominio no oficial", "presión para actuar rápido", "solicita ingresar credenciales"],
            "accion": "Ignorar. Abrir la app oficial de Tenpo para verificar estado real.",
        },
        {
            "mensaje": "Correos Chile: Tiene un paquete retenido. Pague $990 de arancel en: correos-cl.com/pago",
            "señales": ["Cobro pequeño para bajar guardia", "dominio no es correos.cl", "crea urgencia con 'retenido'"],
            "accion": "No pagar. Verificar en correos.cl con el número de seguimiento real.",
        },
        {
            "mensaje": "CMF Chile: Su RUT aparece en alerta por fraude. Consulte en: cmf-alerta.cl/rut",
            "señales": ["CMF no envía SMS", "dominio falso", "usa nombre de institución regulatoria para dar credibilidad"],
            "accion": "Ignorar. La CMF solo publica información en cmfchile.cl.",
        },
    ],
    "vishing": [
        {
            "guion": "Soy del área de seguridad del Banco de Chile. Detectamos una transferencia sospechosa de $850.000 desde su cuenta. Para bloquearla necesito confirmar su número de tarjeta y clave dinámica.",
            "señales": ["Banco real nunca pide clave dinámica por teléfono", "urgencia para que no pienses", "ofrecen 'resolver' si das tus datos"],
            "accion": "Colgar inmediatamente. Llamar al banco al número del reverso de la tarjeta.",
        },
        {
            "guion": "Habla Carabineros de Chile, Unidad de Delitos Económicos. Su RUT está siendo usado en operaciones de lavado de dinero. Para aclarar su situación necesita transferir sus fondos a una 'cuenta segura' mientras investigamos.",
            "señales": ["Carabineros nunca pide transferencias", "uso de autoridad para generar miedo", "solicita acción financiera inmediata"],
            "accion": "Colgar y llamar al 133 para verificar. Nunca transferir dinero por instrucción telefónica.",
        },
        {
            "guion": "Soy ejecutivo de BCI. Ganó un premio. Para transferirle los $2.000.000 necesitamos que primero realice un pago de activación de $50.000.",
            "señales": ["Nadie legítimo pide pagar para recibir un premio", "cifra de 'activación' pequeña para parecer razonable"],
            "accion": "Colgar. El 'cuento del tío' nunca es legítimo.",
        },
    ],
    "phishing": [
        {
            "asunto": "Tu cuenta Mercado Pago fue suspendida - Acción requerida",
            "señales": ["Remitente: soporte@mercadopago-chile.com (dominio falso)", "botón 'Verificar ahora' lleva a sitio clonado", "SSL en el sitio falso (no garantiza legitimidad)"],
            "accion": "No hacer clic. Ir directamente a mercadopago.cl escribiendo la URL en el navegador.",
        },
        {
            "asunto": "Alerta de seguridad: acceso desde dispositivo desconocido - Banco Santander",
            "señales": ["Urgencia + amenaza de bloqueo", "link en el correo no es santander.cl", "pide usuario, contraseña y coordenadas en un solo formulario"],
            "accion": "Ignorar el correo. Ingresar al banco escribiendo la URL directamente.",
        },
    ],
    "whatsapp_impersonation": [
        {
            "mensaje": "Hola mamá, perdí mi teléfono y estoy usando el de una amiga. Necesito que me hagas una transferencia urgente de $200.000 a esta cuenta: 12345678 / BancoEstado / RUT 12.345.678-9",
            "señales": ["Cuenta diferente a la habitual", "urgencia + cambio de dispositivo", "no se puede verificar identidad"],
            "accion": "Llamar directamente a la persona por otro medio antes de transferir. Nunca transferir sin verificar.",
        },
    ],
}

@mcp.tool()
def ejemplos_fraude_chile(tipo: str) -> str:
    """
    Retorna ejemplos reales sintéticos de mensajes y llamadas fraudulentas en Chile.
    Incluye señales de alerta y acciones recomendadas para cada caso.
    Tipos disponibles: smishing, vishing, phishing, whatsapp_impersonation.
    Útil para identificar patrones al analizar el relato de una víctima.
    """
    tipo = tipo.lower().strip()
    if tipo not in EJEMPLOS_FRAUDE:
        disponibles = list(EJEMPLOS_FRAUDE.keys())
        return json.dumps({
            "error": f"Tipo '{tipo}' no disponible.",
            "disponibles": disponibles,
        }, ensure_ascii=False)

    return json.dumps({
        "tipo": tipo,
        "total_ejemplos": len(EJEMPLOS_FRAUDE[tipo]),
        "ejemplos": EJEMPLOS_FRAUDE[tipo],
    }, ensure_ascii=False, indent=2)


# ─── Tool 3: Checklist de señales de alerta ───────────────────────────────────

SEÑALES_POR_TIPO = {
    "smishing": [
        "URL en el mensaje no corresponde al dominio oficial del banco o empresa",
        "Mensaje crea urgencia (cuenta bloqueada, paquete retenido, premio)",
        "Solicita hacer clic para 'verificar', 'activar' o 'confirmar' datos",
        "Número remitente es un celular normal, no un código corto oficial",
        "Monto pequeño de 'arancel' o 'activación' para bajar la guardia",
    ],
    "vishing": [
        "El llamante pide clave dinámica, coordenadas o contraseña completa",
        "Presiona para actuar inmediatamente, sin tiempo para pensar",
        "Ofrece 'resolver un problema' si entregas tus datos",
        "Pide transferir dinero a una 'cuenta segura' o 'cuenta del banco'",
        "Usa nombre de instituciones de autoridad (Carabineros, CMF, SII)",
        "Número que llama no coincide con el oficial (o es número privado)",
    ],
    "phishing": [
        "Dominio del remitente no es el oficial (banco-cl.com vs banco.cl)",
        "Link en el correo lleva a URL diferente al banco",
        "Formulario pide usuario + contraseña + coordenadas en un solo paso",
        "Certificado SSL presente pero dominio es incorrecto (SSL no garantiza legitimidad)",
        "Asunto del correo usa urgencia: 'suspendida', 'bloqueada', 'requerida'",
    ],
    "whatsapp_impersonation": [
        "Número desconocido que dice ser familiar o amigo",
        "Excusa para no poder llamar ('perdí el teléfono', 'batería baja')",
        "Cuenta de destino diferente a la habitual del familiar",
        "Monto de transferencia con urgencia ('es para hoy', 'es emergencia')",
        "No permite verificar por llamada directa",
    ],
}

@mcp.tool()
def señales_de_alerta(tipo_fraude: str) -> str:
    """
    Retorna una checklist de señales de alerta específicas para cada tipo de fraude financiero en Chile.
    Usar para validar si el relato de la víctima coincide con patrones conocidos.
    Tipos: smishing, vishing, phishing, whatsapp_impersonation.
    """
    tipo = tipo_fraude.lower().strip()
    if tipo not in SEÑALES_POR_TIPO:
        return json.dumps({
            "error": f"Tipo '{tipo}' no reconocido.",
            "disponibles": list(SEÑALES_POR_TIPO.keys()),
        }, ensure_ascii=False)

    señales = SEÑALES_POR_TIPO[tipo]
    return json.dumps({
        "tipo_fraude": tipo,
        "total_señales": len(señales),
        "señales_de_alerta": señales,
        "instruccion": f"Si el relato contiene 2 o más de estas señales, la probabilidad de fraude tipo {tipo} es alta.",
    }, ensure_ascii=False, indent=2)


# ─── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
