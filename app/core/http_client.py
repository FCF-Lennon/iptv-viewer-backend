import httpx
from typing import Optional
from app.core.config import setting

# Cliente global
_http_client: Optional[httpx.AsyncClient] = None

def start_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": setting.xtream_user_agent},
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

async def stop_http_client():
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        # Fallback en caso de que se llame fuera del lifespan (p.ej. tests sueltos)
        start_http_client()
    return _http_client
