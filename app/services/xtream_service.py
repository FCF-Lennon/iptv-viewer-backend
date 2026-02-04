import httpx
from typing import Any, Optional, List, Dict
from app.core.config import setting
from app.schemas.xtream import MovieSchema, SeriesSchema, LiveTVSchema, CategorySchema
import logging

logger = logging.getLogger(__name__)

class XtreamClient:
    """Cliente para consumir la API de Xtream Codes de manera segura."""

    def __init__(self):
        self.host = setting.xtream_host
        self.username = setting.xtream_username
        self.password = setting.xtream_password
        self.user_agent = setting.xtream_user_agent

        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": self.user_agent}
        )

    async def _get(self, action: str, extra_params: Optional[dict] = None) -> Optional[List[Dict]]:
        params = {"username": self.username, "password": self.password, "action": action}
        if extra_params:
            params.update(extra_params)
        url = f"{self.host}/player_api.php"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, dict) and "error" in data:
                logger.warning(f"API devolvió error: {data['error']}")
                return None
            if not isinstance(data, list):
                logger.warning(f"Formato inesperado: {data}")
                return None
            return data

        except httpx.RequestError as e:
            logger.error(f"Error de conexión a Xtream Codes: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return None

    async def get_movies(self) -> List[MovieSchema]:
        data = await self._get("get_vod_streams")
        if not data:
            return []

        return [
            MovieSchema(**item)
            for item in data[:50]   # límite SOLO para dev
            if isinstance(item, dict)
        ]

    async def get_series(self) -> List[SeriesSchema]:
        data = await self._get("get_series")
        if data:
            return [SeriesSchema(**item) for item in data if isinstance(item, dict)]
        return []

    async def get_live_tv(self) -> List[LiveTVSchema]:
        data = await self._get("get_live_streams")
        if data:
            return [LiveTVSchema(**item) for item in data if isinstance(item, dict)]
        return []

    async def get_categories(self, content_type: str) -> List[CategorySchema]:
        if content_type not in ("movies", "series", "live"):
            raise ValueError("Tipo de contenido inválido")
        data = await self._get(f"get_{content_type}_categories")
        if data:
            return [CategorySchema(**item) for item in data if isinstance(item, dict)]
        return []
    
    async def get_movie_categories(self) -> List[CategorySchema]:
        data = await self._get("get_vod_categories")
        if data:
            return [CategorySchema(**item) for item in data if isinstance(item, dict)]
        return []


    async def close(self):
        """Cerrar sesión del cliente HTTP."""
        await self.client.aclose()
