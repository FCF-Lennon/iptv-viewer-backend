from fastapi import APIRouter, HTTPException
from typing import List

from app.services.xtream_service import XtreamClient
from app.schemas.xtream import MovieSchema, CategorySchema

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

@router.get("/categories", response_model=List[CategorySchema])
async def get_movie_categories():
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

@router.get("/", response_model=List[MovieSchema])
async def get_movies():
    client = XtreamClient()
    try:
        movies = await client.get_movies()
        return movies
    except Exception:
        raise HTTPException(status_code=500, detail="Error obteniendo películas")
    finally:
        await client.close()


@router.get("/{movie_id}", response_model=MovieSchema)
async def get_movie_by_id(movie_id: int):
    client = XtreamClient()
    try:
        movies = await client.get_movies()
        for movie in movies:
            if int(movie.stream_id) == movie_id:
                return movie
        raise HTTPException(status_code=404, detail="Película no encontrada")
    finally:
        await client.close()


