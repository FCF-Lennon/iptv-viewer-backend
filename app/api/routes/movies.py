from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from app.services.xtream_service import XtreamClient
from app.services.stream_validator import validate_stream
from app.schemas.xtream import CategorySchema
from app.core.security import get_current_user
from app.schemas.content import ContentItemSchema
from app.services.mappers.movie_mapper import normalize_movie, normalize_movie_detail
from app.services.xtream_credentials_service import get_active_xtream_credentials_by_email
from app.db.session import get_db

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

# -------------------------
# Endpoints
# -------------------------
@router.get("/categories", response_model=List[CategorySchema])
async def get_movie_categories(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    creds = get_active_xtream_credentials_by_email(db, current_user)

    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds["host"],
        creds["username"],
        creds["password"]
    )

    try:
        return await client.get_movie_categories()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo categorías de películas"
        )
    finally:
        await client.close()


@router.get("/", response_model=List[ContentItemSchema], response_model_exclude_none=True)
async def get_movies(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    category_id: Optional[str] = None
):
    creds = get_active_xtream_credentials_by_email(db, current_user)

    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds["host"],
        creds["username"],
        creds["password"]
    )

    try:
        raw_objects = await client.get_movies(limit=limit, category_id=category_id)
        normalized = [normalize_movie(obj.model_dump()) for obj in raw_objects]
        return normalized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo películas: {str(e)}")
    finally:
        await client.close()


@router.get("/{movie_id}", response_model=ContentItemSchema, response_model_exclude_none=True)
async def get_movie_by_id(
    movie_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    creds = get_active_xtream_credentials_by_email(db, current_user)

    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds["host"],
        creds["username"],
        creds["password"]
    )

    try:
        raw = await client.get_movie_info(movie_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Película no encontrada")

        return normalize_movie_detail(raw, movie_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo película: {str(e)}")
    finally:
        await client.close()


@router.get("/{movie_id}/play")
async def get_movie_play_url(
    movie_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    creds = get_active_xtream_credentials_by_email(db, current_user)

    if not creds:
        raise HTTPException(status_code=400, detail="Credenciales Xtream no configuradas")

    client = XtreamClient(
        creds["host"],
        creds["username"],
        creds["password"]
    )

    try:
        data = await client.get_movie_info(movie_id)

        if not data:
            raise HTTPException(status_code=404, detail="Película no encontrada")

        movie_data = data.get("movie_data", {})
        container_extension = movie_data.get("container_extension")

        if not container_extension:
            raise HTTPException(status_code=400, detail="No se encontró formato de reproducción")

        play_url = (
            f"{creds['host']}"
            f"/movie/{creds['username']}/{creds['password']}"
            f"/{movie_id}.{container_extension}"
        )

        is_valid = await validate_stream("movie", movie_id, play_url)

        if not is_valid:
            raise HTTPException(status_code=404, detail="Stream not available")

        return {"play_url": play_url}

    finally:
        await client.close()
