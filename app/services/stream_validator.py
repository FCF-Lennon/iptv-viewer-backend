import httpx
import asyncio
import time
from typing import Dict

_validation_semaphore = asyncio.Semaphore(5)
_stream_cache: Dict[str, Dict] = {}

TTL_CONFIG = {
    "live": 900,       # 15 min
    "movie": 86400,    # 24h
    "series": 86400
}

# -------------------------
# CACHE HELPERS
# -------------------------

def _cache_key(stream_type: str, stream_id: int) -> str:
    return f"{stream_type}:{stream_id}"

def _cache_valid(entry: Dict, ttl: int) -> bool:
    return (time.time() - entry["checked_at"]) < ttl


# -------------------------
# VALIDADORES INTERNOS
# -------------------------

async def _check_vod(url: str) -> bool:
    timeout = httpx.Timeout(5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.head(url)

            if response.status_code not in (200, 206):
                return False

            content_type = response.headers.get("content-type", "")
            if not (
                content_type.startswith("video/") or
                content_type.startswith("application/octet-stream")
            ):
                return False

            return True

        except Exception:
            return False


async def _check_live(url: str) -> bool:
    timeout = httpx.Timeout(4.0)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.head(url)

            if response.status_code not in (200, 206):
                return False

            content_type = response.headers.get("content-type", "")

            if not (
                content_type.startswith("video/") or
                content_type.startswith("application/vnd.apple.mpegurl") or
                content_type.startswith("application/octet-stream")
            ):
                return False

            return True

        except Exception:
            return False


# -------------------------
# FUNCIÓN PÚBLICA ÚNICA
# -------------------------

async def validate_stream(stream_type: str, stream_id: int, url: str) -> bool:
    key = _cache_key(stream_type, stream_id)
    ttl = TTL_CONFIG.get(stream_type, 3600)

    # 🔹 1️⃣ Cache hit
    if key in _stream_cache:
        entry = _stream_cache[key]
        if _cache_valid(entry, ttl):
            return entry["valid"]

    # 🔹 2️⃣ Validación controlada por semaphore
    async with _validation_semaphore:

        if stream_type == "live":
            is_valid = await _check_live(url)
        else:
            is_valid = await _check_vod(url)

        _stream_cache[key] = {
            "valid": is_valid,
            "checked_at": time.time()
        }

        return is_valid