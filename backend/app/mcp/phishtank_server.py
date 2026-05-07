"""Servidor MCP standalone para verificación de URLs maliciosas vía URLhaus.

Uso:
    cd backend
    python -m app.mcp.phishtank_server
"""

from mcp.server.fastmcp import FastMCP

from app.services.phishtank_service import check_url, check_urls_in_description

mcp = FastMCP(
    "alerta-cuenta-urlhaus",
    instructions=(
        "Verifica URLs contra URLhaus (abuse.ch) para detectar sitios de phishing "
        "y malware reportados en el contexto de fraudes financieros digitales en Chile."
    ),
)


@mcp.tool()
async def verificar_url_maliciosa(url: str) -> dict:
    """Verifica si una URL está reportada como maliciosa en URLhaus (abuse.ch).

    Retorna el estado de la URL: si está en la base de datos, tipo de amenaza
    (phishing, malware) y si sigue activa.
    """
    return await check_url(url)


@mcp.tool()
async def verificar_urls_en_texto(texto: str) -> list:
    """Extrae todas las URLs de un texto y las verifica en URLhaus.

    Útil para analizar el relato completo de una víctima y detectar
    automáticamente si mencionó algún link malicioso.
    """
    return await check_urls_in_description(texto)


if __name__ == "__main__":
    mcp.run()
