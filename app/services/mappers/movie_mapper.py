from typing import Optional, Dict

from app.schemas.content import ContentItemSchema
from app.schemas.xtream import RawMovieSchema
from app.utils.text_cleaner import safe_float
from app.utils.text_cleaner import (
    remove_emojis,
    remove_year, 
    extract_year,
    normalize_whitespace
)

# -------------------------
# Función de normalización
# -------------------------
def normalize_movie(item: dict, extra_info: Optional[Dict] = None) -> ContentItemSchema:
    """
    Convierte un MovieSchema (Xtream) a ContentItemSchema (normalizado para frontend)
    incluyendo info extra como actores, director, género, duración y trailer.
    """
    stream_id = item.get("stream_id")
    if stream_id is None:
        raise ValueError("normalize_movie recibió un item sin 'stream_id'")

    raw_title = item.get("name", "")
    year = extract_year(raw_title)
    title = normalize_whitespace(remove_emojis(remove_year(raw_title)))

    info = extra_info or {}
    poster = info.get("movie_image") or info.get("cover") or item.get("stream_icon")
    rating = safe_float(item.get("rating") or info.get("rating"))
    country = item.get("country") or info.get("country")
    quality = item.get("container_extension") or info.get("container_extension")
    description = info.get("plot")

    # Campos extras
    actors = info.get("actors")
    director = info.get("director")
    genre = info.get("genre")
    duration = info.get("duration")
    trailer = info.get("youtube_trailer")

    return ContentItemSchema(
        id=int(stream_id),
        title=title,
        type="movie",
        description=normalize_whitespace(remove_emojis(description)) if description else None,
        year=year,
        poster=poster,
        category=item.get("category_id") or info.get("category_id"),
        country=country,
        quality=quality,
        rating=rating,
        actors=actors,
        director=director,
        genre=genre,
        duration=duration,
        trailer=trailer
    )

def clean_movie_data(raw: 'RawMovieSchema', extra_info: Optional[dict] = None) -> dict:
    """
    Convierte un RawMovieSchema en un dict seguro para normalize_movie.
    Maneja rating como float, valores faltantes y agrega info extra opcional.
    """
    rating = raw.rating
    try:
        rating = float(rating) if rating not in (None, "") else None
    except (ValueError, TypeError):
        rating = None

    cleaned = {
        "stream_id": int(raw.stream_id) if raw.stream_id else None,
        "name": raw.name or "",
        "category_id": raw.category_id,
        "stream_icon": raw.stream_icon,
        "rating": rating,
        "added": raw.added,
        "container_extension": raw.container_extension,
        "is_adult": raw.is_adult
    }

    # Añade info extra segura si viene
    if extra_info:
        cleaned.update({
            "description": extra_info.get("plot"),
            "actors": extra_info.get("actors"),
            "director": extra_info.get("director"),
            "genre": extra_info.get("genre"),
            "duration": extra_info.get("duration") or extra_info.get("episode_run_time"),
            "trailer": extra_info.get("youtube_trailer"),
            "country": extra_info.get("country"),
            "poster": extra_info.get("movie_image") or extra_info.get("cover_big")
        })

    return cleaned