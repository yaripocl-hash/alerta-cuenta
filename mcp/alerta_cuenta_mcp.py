"""
MCP Server — Alerta Cuenta
Expone herramientas de fraude financiero para Claude Desktop / Claude Code.

Herramientas:
  verificar_url        → Análisis heurístico de URL (dominios chilenos + patrones de fraude)
  ejemplos_fraude      → Dataset sintético de fraudes chilenos
  patrones_smishing    → Patrones conocidos de SMS fraudulentos en Chile
  indicadores_vishing  → Señales de alerta en llamadas telefónicas fraudulentas
"""

from mcp.server.fastmcp import FastMCP
from urllib.parse import urlparse
import json

mcp = FastMCP("alerta-cuenta")

# ─── Tool 1: Análisis heurístico de URL ───────────────────────────────────────

DOMINIOS_OFICIALES = {
    "bancoestado.cl", "bci.cl", "santander.cl", "scotiabank.cl",
    "bancochile.cl", "itau.cl", "security.cl", "falabella.com",
    "ripley.cl", "mercadopago.cl", "mercadopago.com", "tenpo.cl",
    "fintual.cl", "fintual.com", "correos.cl", "cmfchile.cl",
    "sii.cl", "registrocivil.cl", "carabineros.cl", "pdi.cl",
    "bcn.cl", "clave.cl", "previred.com", "fonasa.cl",
}

INSTITUCIONES_CONOCIDAS = [
    "bancoestado", "bancochile", "santander", "scotiabank", "bci",
    "itau", "security", "falabella", "ripley", "mercadopago", "tenpo",
    "fintual", "correos", "cmf", "sii", "carabineros", "pdi", "clave",
    "fonasa", "previred", "afp",
]

TLDS_SOSPECHOSOS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click",
    ".loan", ".win", ".bid", ".stream", ".download", ".faith",
    ".review", ".trade", ".webcam", ".accountant", ".date",
}

KEYWORDS_FRAUDE = [
    "verificar", "confirmar", "reactivar", "activar", "alerta",
    "seguro", "pago", "arancel", "premio", "ganador", "suspendida",
    "bloqueada", "validar", "cuenta-segura", "rut", "clave",
    "ingreso", "acceso-seguro",
]


@mcp.tool()
def verificar_url(url: str) -> str:
    """
    Analiza una URL con heurísticas para detectar fraude financiero en Chile.
    Detecta dominios lookalike de bancos e instituciones chilenas, TLDs sospechosos
    y palabras clave típicas de phishing/smishing.
    Útil para analizar links recibidos por SMS, WhatsApp o correo sospechoso.
    """
    try:
        parsed = urlparse(url if "://" in url else "http://" + url)
        dominio = parsed.netloc.lower().lstrip("www.")
        ruta = parsed.path.lower()
        url_completa = (dominio + ruta).lower()
    except Exception:
        return json.dumps({
            "url": url,
            "estado": "error",
            "mensaje": "No se pudo analizar la URL. Verifique que esté bien escrita.",
            "riesgo": "desconocido",
        }, ensure_ascii=False)

    alertas = []
    puntos_riesgo = 0

    # 1. Dominio oficial conocido → seguro
    if dominio in DOMINIOS_OFICIALES:
        return json.dumps({
            "url": url,
            "dominio": dominio,
            "estado": "dominio_oficial",
            "mensaje": f"El dominio '{dominio}' corresponde a un sitio oficial conocido en Chile.",
            "riesgo": "BAJO",
            "alertas": [],
        }, ensure_ascii=False, indent=2)

    # 2. Lookalike: contiene nombre de institución pero no es el dominio oficial
    for institucion in INSTITUCIONES_CONOCIDAS:
        if institucion in dominio:
            alertas.append(f"El dominio contiene '{institucion}' pero NO es el sitio oficial.")
            puntos_riesgo += 4
            break

    # 3. TLD sospechoso
    for tld in TLDS_SOSPECHOSOS:
        if dominio.endswith(tld):
            alertas.append(f"TLD '{tld}' es frecuentemente usado en sitios fraudulentos.")
            puntos_riesgo += 3
            break

    # 4. Keywords de fraude en la URL
    encontradas = [kw for kw in KEYWORDS_FRAUDE if kw in url_completa]
    if encontradas:
        alertas.append(f"La URL contiene palabras asociadas a fraude: {', '.join(encontradas)}.")
        puntos_riesgo += len(encontradas)

    # 5. Guiones en el dominio (táctica común: banco-estado-cl.xyz)
    guiones = dominio.count("-")
    if guiones >= 2:
        alertas.append(f"El dominio tiene {guiones} guiones — táctica común en dominios falsos.")
        puntos_riesgo += 2
    elif guiones == 1:
        puntos_riesgo += 1

    # 6. HTTP sin HTTPS
    if url.startswith("http://"):
        alertas.append("La URL usa HTTP (sin cifrado). Sitios legítimos usan HTTPS.")
        puntos_riesgo += 1

    # Clasificar riesgo
    if puntos_riesgo >= 5:
        nivel_riesgo = "ALTO"
        estado = "sospechosa"
        mensaje = "Esta URL tiene múltiples señales de fraude. No la visites ni entregues datos."
    elif puntos_riesgo >= 2:
        nivel_riesgo = "MEDIO"
        estado = "dudosa"
        mensaje = "Esta URL tiene características sospechosas. Verifica el dominio oficial antes de continuar."
    else:
        nivel_riesgo = "BAJO"
        estado = "sin_alertas"
        mensaje = "No se detectaron señales claras de fraude, pero esto no garantiza que sea segura."

    return json.dumps({
        "url": url,
        "dominio": dominio,
        "estado": estado,
        "riesgo": nivel_riesgo,
        "puntos_riesgo": puntos_riesgo,
        "alertas": alertas,
        "mensaje": mensaje,
    }, ensure_ascii=False, indent=2)


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
def senales_de_alerta(tipo_fraude: str) -> str:
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
