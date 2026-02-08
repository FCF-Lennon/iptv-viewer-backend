from fastapi import APIRouter, HTTPException
from typing import List

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import LiveTVSchema, CategorySchema

router = APIRouter(
    prefix="/live",
    tags=["live"]
)

@router.get("/categories", response_model=List[CategorySchema])
async def get_live_categories():
    client = XtreamClient()
    try:
        return await client.get_live_categories()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo categorias")
    finally:
        await client.close()
        
@router.get("/", response_model=List[LiveTVSchema])
async def get_live_streams():
    client = XtreamClient()
    try:
        return await client.get_live_tv()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo live tv")
    finally:
        await client.close()
