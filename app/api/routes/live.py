from fastapi import APIRouter, HTTPException
from typing import List, Optional
from fastapi import Depends

from app.services.xtream_service import XtreamClient
from app.services.stream_validator import validate_stream
from app.schemas.xtream import CategorySchema
from app.schemas.content import ContentItemSchema
from app.core.security import get_current_user, setting
from app.services.mappers.live_mapper import normalize_live

router = APIRouter(
    prefix="/live",
    tags=["live"]
)

@router.get("/categories", response_model=List[CategorySchema])
async def get_live_categories(current_user: str = Depends(get_current_user), limit: int = 50):
    client = XtreamClient()
    try:
        return await client.get_live_categories()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo categorias")
    finally:
        await client.close()
        
@router.get("/", response_model=List[ContentItemSchema], response_model_exclude_none=True)
async def get_live_streams(current_user: str = Depends(get_current_user), limit: int = 50, category_id: Optional[str] = None):
    client = XtreamClient()
    try:
        print("A → llamando get_live_tv")

        raw_objects = await client.get_live_tv(limit=limit, category_id=category_id)

        print("B → recibidos objetos:", len(raw_objects))

        normalized = [normalize_live(obj.model_dump()) for obj in raw_objects]

        print("C → normalización terminada")

        return normalized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo canales: {str(e)}")
    finally:
        await client.close()

@router.get("/{live_id}/play")
async def get_live_play_url(
    live_id: int,
    current_user: str = Depends(get_current_user)
):
    play_url = (
        f"{setting.xtream_host}"
        f"/live/{setting.xtream_username}/{setting.xtream_password}"
        f"/{live_id}.ts"
    )

    is_valid = await validate_stream("live", live_id, play_url)

    if not is_valid:
        raise HTTPException(status_code=404, detail="Stream not available")

    return {"play_url": play_url}