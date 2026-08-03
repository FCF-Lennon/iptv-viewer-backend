import httpx
import logging
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import setting
from app.core.security import get_current_user, oauth2_scheme
from app.db.session import get_db
from app.services.xtream_credentials_service import get_active_xtream_credentials_by_email
from app.services.xtream_service import XtreamClient
from app.services.stream_validator import validate_stream
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stream",
    tags=["stream"]
)


# ---------------------------------------------------------------------------
# Auth flexible: acepta JWT en header Authorization O en ?token= query param
# Necesario para media players (VLC, etc.) que no soportan headers custom
# ---------------------------------------------------------------------------

async def get_stream_user(
    request: Request,
    token: Optional[str] = None,        # ?token=<jwt>
) -> str:
    """
    Resuelve el usuario actual aceptando el JWT de dos formas:
    1. Header:  Authorization: Bearer <token>   (frontend web)
    2. Query:   ?token=<token>                  (VLC y otros media players)
    """
    # Prioridad: header > query param
    bearer = request.headers.get("Authorization", "")
    if bearer.startswith("Bearer "):
        raw_token = bearer[7:]
    elif token:
        raw_token = token
    else:
        raise HTTPException(
            status_code=401,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(raw_token, setting.jwt_secret, algorithms=["HS256"])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CHUNK_SIZE = 1024 * 64  # 64 KB por chunk
PROXY_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


# ---------------------------------------------------------------------------
# Helper: genera chunks desde la respuesta httpx
# ---------------------------------------------------------------------------

async def _iter_chunks(response: httpx.Response) -> AsyncGenerator[bytes, None]:
    """Itera la respuesta de Xtream en chunks y los retransmite al cliente."""
    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
        yield chunk


# ---------------------------------------------------------------------------
# Helper: construye headers de proxy (Range y Content-*)
# ---------------------------------------------------------------------------

def _build_request_headers(request: Request) -> dict:
    """Reenvía el header Range del cliente y agrega User-Agent del proveedor IPTV."""
    headers = {
        # Usamos el mismo User-Agent que XtreamClient para no ser bloqueados
        "User-Agent": setting.xtream_user_agent,
    }
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header
    return headers


def _build_response_headers(xtream_response: httpx.Response) -> dict:
    """Extrae los headers relevantes de la respuesta de Xtream para el cliente."""
    passthrough = [
        "content-type",
        "content-length",
        "content-range",
        "accept-ranges",
        "cache-control",
    ]
    return {
        k: v
        for k, v in xtream_response.headers.items()
        if k.lower() in passthrough
    }


# ---------------------------------------------------------------------------
# Helper: realiza el proxy de stream
# ---------------------------------------------------------------------------

async def _proxy(
    xtream_url: str,
    request: Request,
    default_media_type: str = "video/mp4",
) -> StreamingResponse:
    """
    Abre una conexión streaming a la URL de Xtream y retransmite los bytes
    al cliente. Soporta Range requests para seeking.
    Las credenciales Xtream NUNCA se incluyen en la respuesta al cliente.
    """
    request_headers = _build_request_headers(request)
    has_range = "Range" in request_headers

    try:
        client = httpx.AsyncClient(timeout=PROXY_TIMEOUT)
        xtream_response = await client.send(
            httpx.Request("GET", xtream_url, headers=request_headers),
            stream=True,
            follow_redirects=True,  # explícito: httpx requiere esto en send() para redirigir
        )

        if xtream_response.status_code not in (200, 206):
            logger.error(
                f"[proxy] Xtream devolvió status={xtream_response.status_code} "
                f"headers={dict(xtream_response.headers)}"
            )
            await xtream_response.aclose()
            await client.aclose()
            raise HTTPException(
                status_code=xtream_response.status_code,
                detail="El stream no está disponible en el servidor IPTV"
            )

        response_headers = _build_response_headers(xtream_response)
        media_type = (
            xtream_response.headers.get("content-type") or default_media_type
        )
        status_code = 206 if has_range else 200

        async def stream_and_close():
            try:
                async for chunk in xtream_response.aiter_bytes(chunk_size=CHUNK_SIZE):
                    yield chunk
            finally:
                await xtream_response.aclose()
                await client.aclose()

        return StreamingResponse(
            content=stream_and_close(),
            status_code=status_code,
            media_type=media_type,
            headers=response_headers,
        )

    except httpx.RequestError as exc:
        logger.error(f"Error de conexión al servidor IPTV: {exc}")
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar al servidor IPTV"
        )


# ---------------------------------------------------------------------------
# Endpoint: Movie
# ---------------------------------------------------------------------------

@router.get("/movie/{movie_id}", summary="Proxy de stream para películas")
async def stream_movie(
    movie_id: int,
    request: Request,
    current_user: str = Depends(get_stream_user),
    db: Session = Depends(get_db),
):
    """
    Retransmite el stream de una película directamente desde el servidor Xtream.
    Las credenciales del proveedor IPTV nunca se exponen al cliente.
    Soporta Range requests para seeking.
    """
    creds = get_active_xtream_credentials_by_email(db, current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    # Obtener el container_extension desde la API de Xtream
    client = XtreamClient(creds["host"], creds["username"], creds["password"])
    try:
        data = await client.get_movie_info(movie_id)
    finally:
        await client.close()

    if not data:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    movie_data = data.get("movie_data", {})
    container_ext = movie_data.get("container_extension")
    if not container_ext:
        raise HTTPException(status_code=400, detail="No se encontró formato de reproducción")

    # Construir la URL internamente — nunca se devuelve al cliente
    xtream_url = (
        f"{creds['host']}"
        f"/movie/{creds['username']}/{creds['password']}"
        f"/{movie_id}.{container_ext}"
    )

    # Validar disponibilidad antes de hacer proxy
    is_valid = await validate_stream("movie", movie_id, xtream_url)
    if not is_valid:
        raise HTTPException(status_code=404, detail="Stream no disponible")

    return await _proxy(xtream_url, request, default_media_type="video/mp4")


# ---------------------------------------------------------------------------
# Endpoint: Live TV
# ---------------------------------------------------------------------------

@router.get("/live/{live_id}", summary="Proxy de stream para TV en vivo")
async def stream_live(
    live_id: int,
    request: Request,
    current_user: str = Depends(get_stream_user),
    db: Session = Depends(get_db),
):
    """
    Retransmite el stream de un canal de TV en vivo desde el servidor Xtream.
    Las credenciales del proveedor IPTV nunca se exponen al cliente.
    """
    creds = get_active_xtream_credentials_by_email(db, current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    # Construir la URL internamente — nunca se devuelve al cliente
    xtream_url = (
        f"{creds['host']}"
        f"/live/{creds['username']}/{creds['password']}"
        f"/{live_id}.ts"
    )

    # Validar disponibilidad antes de hacer proxy
    is_valid = await validate_stream("live", live_id, xtream_url)
    logger.info(f"[stream/live/{live_id}] validate_stream={is_valid}")
    if not is_valid:
        raise HTTPException(status_code=404, detail="Stream no disponible")

    logger.info(f"[stream/live/{live_id}] iniciando proxy")
    return await _proxy(xtream_url, request, default_media_type="video/MP2T")


# ---------------------------------------------------------------------------
# Endpoint: Series / Episode
# ---------------------------------------------------------------------------

@router.get("/series/{series_id}/{episode_id}", summary="Proxy de stream para episodios")
async def stream_episode(
    series_id: int,
    episode_id: int,
    request: Request,
    current_user: str = Depends(get_stream_user),
    db: Session = Depends(get_db),
):
    """
    Retransmite el stream de un episodio directamente desde el servidor Xtream.
    Las credenciales del proveedor IPTV nunca se exponen al cliente.
    Soporta Range requests para seeking.
    """
    creds = get_active_xtream_credentials_by_email(db, current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    # Obtener info de la serie para encontrar el container_extension del episodio
    client = XtreamClient(creds["host"], creds["username"], creds["password"])
    try:
        series_data = await client.get_series_info(series_id)
    finally:
        await client.close()

    if not series_data:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    # Buscar el episodio dentro de todas las temporadas
    episode_found = None
    for eps_list in series_data.get("episodes", {}).values():
        for ep in eps_list:
            if ep.get("id") == str(episode_id):
                episode_found = ep
                break
        if episode_found:
            break

    if not episode_found:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")

    container_ext = episode_found.get("container_extension")
    if not container_ext:
        raise HTTPException(status_code=400, detail="No se encontró formato de reproducción")

    # Construir la URL internamente — nunca se devuelve al cliente
    xtream_url = (
        f"{creds['host']}"
        f"/series/{creds['username']}/{creds['password']}"
        f"/{episode_id}.{container_ext}"
    )

    # Validar disponibilidad antes de hacer proxy
    is_valid = await validate_stream("series", episode_id, xtream_url)
    if not is_valid:
        raise HTTPException(status_code=404, detail="Stream no disponible")

    return await _proxy(xtream_url, request, default_media_type="video/mp4")
