import httpx
import logging
from typing import Any, Optional, List, Dict
from app.core.config import setting
from app.schemas.xtream import RawLiveSchema, CategorySchema, RawMovieSchema, RawSeriesSchema
from app.utils.text_cleaner import remove_emojis, normalize_whitespace, clean_category_name


logger = logging.getLogger(__name__)

class XtreamClient:
    """Cliente para consumir la API de Xtream Codes de manera segura. con cache de episodios."""

    def __init__(self):
        self.host = setting.xtream_host
        self.username = setting.xtream_username
        self.password = setting.xtream_password
        self.user_agent = setting.xtream_user_agent

        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": self.user_agent}
        )

    async def _get(self, action: str, extra_params: Optional[dict] = None) -> Optional[Any]:
        params = {
            "username": self.username,
            "password": self.password,
            "action": action,
        }

        if extra_params:
            params.update(extra_params)

        url = f"{self.host}/player_api.php"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Solo validamos si la API devuelve error explícito
            if isinstance(data, dict) and "error" in data:
                logger.warning(f"API devolvió error: {data['error']}")
                return None

            return data  # ← sin forzar tipo

        except httpx.RequestError as e:
            logger.error(f"Error de conexión a Xtream Codes: {e}")
            return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return None


    async def get_movies(self, limit: int = 50, category_id: Optional[str] = None) -> List[RawMovieSchema]:
        """
        Trae la lista de películas desde Xtream como RawMovieSchema,
        valida y aplica un límite opcional.
        """
        extra = {"category_id": category_id} if category_id else None
        data = await self._get("get_vod_streams", extra)
        if not data:
            return []

        # Aplica límite
        data = data[:limit]

        # Convierte a RawMovieSchema
        return [
            RawMovieSchema.model_validate(item)
            for item in data
            if isinstance(item, dict)
        ]


    async def get_movie_info(self, vod_id: int) -> Dict:
        """
        Trae la info detallada de una película por ID.
        """
        data = await self._get("get_vod_info", {"vod_id": vod_id})
        return data or {}
    

    async def get_series(self, limit: int = 50, category_id: Optional[str] = None) -> List[RawSeriesSchema]:
        """
        Trae la lista de series desde Xtream como RawSeriesSchema,
        valida y aplica un límite opcional.
        """
        extra = {"category_id": category_id} if category_id else None
        data = await self._get("get_series", extra)
        if not data:
            return []

        # Aplica límite
        data = data[:limit]

        # Convierte a RawSeriesSchema
        return [
            RawSeriesSchema.model_validate(item)
            for item in data
            if isinstance(item, dict)
        ]

    
    async def get_series_info(self, series_id: int) -> Dict:
        """
        Trae la info detallada de una serie por ID.
        """
        data = await self._get("get_series_info", {"series_id": series_id})
        return data or {}

    async def get_live_tv(self, limit: int = 50, category_id: Optional[str] = None) -> List[RawLiveSchema]:
        
        extra = {"category_id": category_id} if category_id else None
        data = await self._get("get_live_streams", extra)

        if not data:
            return []
        
        data = data[:limit]
        
        return [
            RawLiveSchema.model_validate(item)
            for item in data
            if isinstance(item, dict)
        ]
    
    async def get_movie_categories(self) -> List[CategorySchema]:
    
        data = await self._get("get_vod_categories")
        if not data:
            return []

        categories = []

        for item in data:
            if not isinstance(item, dict):
                continue

            raw_name = item.get("category_name") or ""
            clean_name = normalize_whitespace(remove_emojis(raw_name))

            categories.append(
                CategorySchema(
                    category_id=item.get("category_id"),
                    category_name=clean_name
                )
            )

        return categories
    
    async def get_series_categories(self) -> List[CategorySchema]:
        data = await self._get("get_series_categories")
        if not data:
            return []

        categories = []

        for item in data:
            if not isinstance(item, dict):
                continue

            raw_name = item.get("category_name") or ""
            clean_name = normalize_whitespace(remove_emojis(raw_name))

            categories.append(
                CategorySchema(
                    category_id=item.get("category_id"),
                    category_name=clean_name
                )
            )

        return categories
       
    
    async def get_live_categories(self) -> List[CategorySchema]:
        data = await self._get("get_live_categories")
        print(f"2. Petición terminada. Datos recibidos: {len(data) if data else 0} items")
        if not data:
            return []

        categories = []

        for item in data:
            if not isinstance(item, dict):
                continue

            raw_name = item.get("category_name") or ""
            clean_name = normalize_whitespace(clean_category_name(raw_name))

            categories.append(
                CategorySchema(
                    category_id=item.get("category_id"),
                    category_name=clean_name
                )
            )

        return categories

    async def close(self):
        """Cerrar sesión del cliente HTTP."""
        await self.client.aclose()

    
    
