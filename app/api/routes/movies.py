from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import MovieSchema, CategorySchema, RawMovieSchema
from app.core.security import get_current_user
from app.schemas.content import ContentItemSchema
from app.services.mappers.movie_mapper import normalize_movie, clean_movie_data

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
    limit: int = 50
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


@router.get("/", response_model=List[ContentItemSchema])
async def get_movies(current_user: str = Depends(get_current_user), limit: int = 50):
    """
    Listado profesional de películas:
    - Límite aplicado antes de limpiar
    - Datos crudos de Xtream transformados con RawMovieSchema
    - Limpieza profesional con safe_float
    - Normalización a ContentItemSchema
    """
    client = XtreamClient()
    try:
        # 1️⃣ Traer datos crudos de Xtream
        raw_data = await client._get("get_vod_streams")  # dicts crudos
        if not raw_data:
            return []

        # 2️⃣ Aplicar límite antes de cualquier validación o limpieza
        raw_data = raw_data[:limit]

        # 3️⃣ Convertir a RawMovieSchema (tipo seguro, rating como str)
        raw_objects = [RawMovieSchema.model_validate(item) for item in raw_data if isinstance(item, dict)]

        # 4️⃣ Limpiar datos (rating a float, IDs seguros, etc.)
        cleaned_movies = [clean_movie_data(m) for m in raw_objects]

        # 5️⃣ Normalizar a ContentItemSchema
        normalized_movies = [normalize_movie(m) for m in cleaned_movies]

        return normalized_movies

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo películas: {str(e)}")
    finally:
        await client.close()


@router.get("/{movie_id}", response_model=ContentItemSchema)
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