from fastapi import APIRouter, HTTPException
from typing import List
from fastapi import Depends

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import LiveTVSchema, CategorySchema
from app.core.security import get_current_user

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
        
@router.get("/", response_model=List[LiveTVSchema])
async def get_live_streams(current_user: str = Depends(get_current_user), limit: int = 50):
    client = XtreamClient()
    try:
        return await client.get_live_tv()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo live tv")
    finally:
        await client.close()
