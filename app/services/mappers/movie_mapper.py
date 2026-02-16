from typing import Optional, Dict

from app.schemas.content import ContentItemSchema
from app.schemas.xtream import MovieSchema, RawMovieSchema
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
        rating=rating
    )

def clean_movie_data(raw: 'RawMovieSchema') -> dict:
    """
    Convierte un RawMovieSchema en un dict seguro para normalize_movie.
    Convierte rating a float, maneja valores faltantes.
    """
    rating = raw.rating
    try:
        rating = float(rating) if rating not in (None, "") else None
    except (ValueError, TypeError):
        rating = None

    return {
        "stream_id": int(raw.stream_id) if raw.stream_id else None,
        "name": raw.name or "",
        "category_id": raw.category_id,
        "stream_icon": raw.stream_icon,
        "rating": rating,
        "added": raw.added,
        "container_extension": raw.container_extension,
        "is_adult": raw.is_adult
    }