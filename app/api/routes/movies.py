from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import CategorySchema
from app.core.security import get_current_user
from app.schemas.content import ContentItemSchema
from app.services.mappers.movie_mapper import normalize_movie
from app.core.config import setting

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

# -------------------------
# Endpoints
# -------------------------
@router.get("/categories", response_model=List[CategorySchema])
async def get_movie_categories(
    current_user: str = Depends(get_current_user)
):
    client = XtreamClient()
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
async def get_movies(current_user: str = Depends(get_current_user), limit: int = 50):
    """
    Trae películas normalizadas para frontend, con límite opcional.
    """
    client = XtreamClient()

    try:
        raw_objects = await client.get_movies(limit=limit)
        # Normaliza cada película usando normalize_movie
        normalized = [
            normalize_movie(obj.model_dump(), extra_info=obj.model_dump().get("info"))
            for obj in raw_objects
        ]

        return normalized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo películas: {str(e)}")
    finally:
        await client.close()


@router.get("/{movie_id}", response_model=ContentItemSchema, response_model_exclude_none=True)
async def get_movie_by_id(
    movie_id: int, 
    current_user: str = Depends(get_current_user)
):
    """
    Detalle de película por ID. Incluye info extra (plot, poster, etc.)
    """
    client = XtreamClient()
    try:
        data = await client.get_movie_info(movie_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="Película no encontrada")

        movie_data = data.get("movie_data", {})
        info = data.get("info", {})

        # Normaliza incluyendo info extra
        normalized = normalize_movie(movie_data, extra_info=info)
        return normalized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo película: {str(e)}")
    finally:
        await client.close()


@router.get("/{movie_id}/play")
async def get_movie_play_url(movie_id: int, current_user: str = Depends(get_current_user)):
    """
    Devuelve la URL de reproducción para la película seleccionada.
    """
    client = XtreamClient()

    try:
        data = await client.get_movie_info(movie_id)

        if not data:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        movie_data = data.get("movie_data", {})
        container_extension = movie_data.get("container_extension")

        if not container_extension:
            raise HTTPException(status_code=400, detail="No se encontró formato de reproducción")
        
        play_url = (
            f"{setting.xtream_host}"
            f"/movie/{setting.xtream_username}/{setting.xtream_password}"
            f"/{movie_id}.{container_extension}"
        )

        return {"play_url": play_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando URL de reproducción: {str(e)}")
    finally:
        await client.close()
    