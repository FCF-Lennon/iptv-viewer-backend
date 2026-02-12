from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import SeriesSchema
from app.core.security import get_current_user

router = APIRouter(
    prefix="/series",
    tags=["series"]
)


@router.get("/categories")
async def get_series_categories(current_user: str = Depends(get_current_user), limit: int = 50):
    client = XtreamClient()
    try:
        return await client.get_series_categories()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo categorias de series")
    finally:
        await client.close()


@router.get("/", response_model=List[SeriesSchema])
async def get_series(current_user: str = Depends(get_current_user), limit: int = 50):
    client = XtreamClient()
    try:
        return await client.get_series()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo series")
    finally:
        await client.close()


@router.get("/{series_id}", response_model=SeriesSchema)
async def get_series_by_id(series_id: int, current_user: str = Depends(get_current_user), limit: int = 50):
    client = XtreamClient()
    try:
        series_list = await client.get_series()
        for serie in series_list:
            if int(serie.series_id) == series_id:
                return serie
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    finally:
        await client.close()
