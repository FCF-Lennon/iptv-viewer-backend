from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.xtream_service import XtreamClient
from app.schemas.content import ContentItemSchema, SeriesDetailSchema
from app.core.config import setting
from app.core.security import get_current_user
from app.services.mappers.series_mapper import normalize_series, normalize_series_detail
from app.services.xtream_credentials_service import get_active_xtream_credentials_by_email
from app.db.session import get_db

router = APIRouter(
    prefix="/series",
    tags=["series"]
)

@router.get("/categories")
async def get_series_categories(
    current_user: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    creds = get_active_xtream_credentials_by_email(db, current_user)

    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds['host'],
        creds['username'],
        creds['password']
    )
    try:
        return await client.get_series_categories()
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo categorias de series")
    finally:
        await client.close()


@router.get("/", response_model=List[ContentItemSchema], response_model_exclude_none=True)
async def get_series(
    current_user: str = Depends(get_current_user), 
    db: Session = Depends(get_db),
    limit: int = 50, 
    category_id: Optional[str] = None
):
    creds = get_active_xtream_credentials_by_email(db, current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds['host'],
        creds['username'],
        creds['password']
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
async def get_series_by_id(
    series_id: int, 
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    creds = get_active_xtream_credentials_by_email(db, current_user)
    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds['host'],
        creds['username'],
        creds['password']
    )
    try:
        data = await client.get_series_info(series_id)
        if not data:
            raise HTTPException(status_code=404, detail="Serie no encontrada")

        return normalize_series_detail(data, series_id)

    finally:
        await client.close()
