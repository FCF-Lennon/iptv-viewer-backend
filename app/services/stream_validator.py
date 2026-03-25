import httpx
import asyncio
import time
from typing import Dict

_validation_semaphore = asyncio.Semaphore(5)
_stream_cache: Dict[str, Dict] = {}
_pending_revalidations: set[str] = set()

TTL_VALID = {
    "live": 900,    # 15 min
    "movie": 86400, # 24h
    "series": 86400
}

TTL_INVALID = {
    "live": 300,
    "movie": 1800,
    "series": 1800
}

# -------------------------
# CACHE HELPERS
# -------------------------

def _cache_key(stream_type: str, stream_id: int) -> str:
    return f"{stream_type}:{stream_id}"

def _cache_valid(entry: Dict, stream_type: str) -> bool:
    ttl = _get_ttl(stream_type, entry["valid"])
    return (time.time() - entry["checked_at"]) < ttl

def _get_ttl(stream_type: str, is_valid: bool) -> int:
    if is_valid:
        return TTL_VALID.get(stream_type, 36000)
    return TTL_INVALID.get(stream_type, 600)

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

            content_type = response.headers.get("content-type", "").lower()

            if not (
                content_type.startswith("video/") or
                "mpegurl" in content_type or
                content_type.startswith("application/octet-stream")
            ):
                return False

            return True

        except Exception:
            return False


# -------------------------
# BACKGROUND REVALIDATION
# -------------------------

async def _background_revalidate(key: str, stream_type: str, url: str):
    try:
        async with _validation_semaphore:
            if stream_type == "live":
                is_valid = await _check_live(url)
            else:
                is_valid = await _check_vod(url)
            
            _stream_cache[key] = {
                "valid": is_valid,
                "checked_at": time.time()
            }
    finally:
        _pending_revalidations.discard(key)


# -------------------------
# FUNCIÓN PÚBLICA ÚNICA
# -------------------------

async def validate_stream(stream_type: str, stream_id: int, url: str) -> bool:
    key = _cache_key(stream_type, stream_id)

    entry = _stream_cache.get(key)

    # 1️⃣ CACHE MISS
    if not entry:

        # Si ya hay validación en curso, esperar resultado
        if key in _pending_revalidations:
            while key in _pending_revalidations:
                await asyncio.sleep(0.01)
            return _stream_cache[key]["valid"]

        _pending_revalidations.add(key)

        try:
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
        finally:
            _pending_revalidations.discard(key)

    # 2️⃣ CACHE VÁLIDO
    if _cache_valid(entry, stream_type):
        return entry["valid"]

    # 3️⃣ CACHE EXPIRADO → Stale-While-Revalidate
    if key not in _pending_revalidations:
        _pending_revalidations.add(key)
        asyncio.create_task(
            _background_revalidate(key, stream_type, url)
        )

    return entry["valid"]