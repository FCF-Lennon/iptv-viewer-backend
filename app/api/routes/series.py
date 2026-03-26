from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.services.xtream_service import XtreamClient
from app.services.stream_validator import validate_stream
from app.schemas.content import ContentItemSchema, SeriesDetailSchema
from app.core.config import setting
from app.core.security import get_current_user
from app.services.mappers.series_mapper import normalize_series, normalize_series_detail
from app.core.xtream_store import user_xtream_credentials

router = APIRouter(
    prefix="/series",
    tags=["series"]
)

@router.get("/categories")
async def get_series_categories(current_user: str = Depends(get_current_user)):
    creds = user_xtream_credentials.get(current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds.host,
        creds.username,
        creds.password
    )
    try:
        return await client.get_series_categories()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo categorias de series")
    finally:
        await client.close()


@router.get("/", response_model=List[ContentItemSchema], response_model_exclude_none=True)
async def get_series(current_user: str = Depends(get_current_user), limit: int = 50, category_id: Optional[str] = None):
    creds = user_xtream_credentials.get(current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds.host,
        creds.username,
        creds.password
    )
    try:
        raw_data = await client.get_series(limit=limit, category_id=category_id)

        normalized = [normalize_series(obj.model_dump()) for obj in raw_data]

        return normalized
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo series: {str(e)}")
    finally:
        await client.close()


@router.get("/{series_id}", response_model=SeriesDetailSchema, response_model_exclude_none=True)
async def get_series_by_id(series_id: int, current_user: str = Depends(get_current_user)):
    creds = user_xtream_credentials.get(current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds.host,
        creds.username,
        creds.password
    )
    try:
        data = await client.get_series_info(series_id)
        if not data:
            raise HTTPException(status_code=404, detail="Serie no encontrada")

        return normalize_series_detail(data, series_id)

    finally:
        await client.close()



@router.get("/{series_id}/{episode_id}/play")
async def get_episode_play_url(series_id: int, episode_id: int, current_user: str = Depends(get_current_user)):
    creds = user_xtream_credentials.get(current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds.host,
        creds.username,
        creds.password
    )
    try:
        series_data = await client.get_series_info(series_id)
        if not series_data:
            raise HTTPException(status_code=404, detail="Serie no encontrada")

        # Buscar el episodio dentro de la serie
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

        play_url = f"{creds.host}/series/{creds.username}/{creds.password}/{episode_id}.{container_ext}"
        
        is_valid = await validate_stream("series", episode_id, play_url)

        if not is_valid:
            raise HTTPException(status_code=404, detail="Stream not available")
        
        return {"play_url": play_url}

    finally:
        await client.close()