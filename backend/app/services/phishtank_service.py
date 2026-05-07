import re

import httpx

_URL_RE = re.compile(r"https?://[^\s\"'<>]+")
_MAX_URLS = 3
_TIMEOUT = 8.0


def extract_urls(text: str) -> list[str]:
    return _URL_RE.findall(text)[:_MAX_URLS]


async def check_url(url: str) -> dict:
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(
            "https://urlhaus-api.abuse.ch/v1/url/",
            data={"url": url},
        )
        r.raise_for_status()
        return r.json()


async def check_urls_in_description(text: str) -> list[dict]:
    """Extrae URLs del texto y verifica cada una en URLhaus. Retorna [] si no hay URLs."""
    urls = extract_urls(text)
    results = []
    for url in urls:
        try:
            data = await check_url(url)
            results.append({"url": url, "urlhaus": data})
        except Exception:
            results.append({"url": url, "urlhaus": {"error": "no_response"}})
    return results
