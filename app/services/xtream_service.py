import httpx
import logging
from typing import Any, Optional, List, Dict
from app.core.config import setting
from app.core.http_client import get_http_client
from app.schemas.xtream import RawLiveSchema, CategorySchema, RawMovieSchema, RawSeriesSchema, EpgListingSchema
from app.utils.text_cleaner import remove_emojis, normalize_whitespace, clean_category_name

logger = logging.getLogger(__name__)

class XtreamClient:
    """Cliente para consumir la API de Xtream Codes de manera segura. con cache de episodios."""

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.client = get_http_client()

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
        
        except ValueError as e:
            logger.error(f"Error al analizar la respuesta JSON: {e}")
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

        # Ordenar por fecha de agregado (más recientes primero)
        data.sort(key=lambda x: str(x.get("added", "")), reverse=True)

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

        # Ordenar por fecha de agregado/modificado
        data.sort(key=lambda x: str(x.get("last_modified") or x.get("added") or ""), reverse=True)

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
    
    async def get_short_epg(self, stream_id: str, limit: int = 5) -> List[EpgListingSchema]:
        data = await self._get("get_short_epg", {"stream_id": stream_id, "limit": limit})
        if not data or not isinstance(data, dict):
            return []
            
        epg_listings = data.get("epg_listings", [])
        
        return [
            EpgListingSchema.model_validate(item)
            for item in epg_listings
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
        """No hace nada, el cliente HTTP es global y se cierra en el lifespan de la app."""
        pass


    
    
