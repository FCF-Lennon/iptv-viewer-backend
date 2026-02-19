from app.schemas.content import ContentItemSchema
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
def normalize_movie(item: dict) -> ContentItemSchema:
    stream_id = item.get("stream_id")
    if not stream_id:
        raise ValueError("Movie sin stream_id")

    raw_title = item.get("name", "")
    year = extract_year(raw_title)
    title = normalize_whitespace(remove_emojis(remove_year(raw_title)))
    

    return ContentItemSchema(
        id=int(stream_id),
        title=title,
        type="movie",
        year=year,
        poster=item.get("stream_icon"),
        category=item.get("category_id"),
        rating=safe_float(item.get("rating"))
    )

def normalize_movie_detail(raw: dict, movie_id: int) -> ContentItemSchema:
    movie_data = raw.get("movie_data", {})
    info = raw.get("info", {})

    raw_title = movie_data.get("name", "")
    year = extract_year(raw_title)
    title = normalize_whitespace(remove_emojis(remove_year(raw_title)))

    return ContentItemSchema(
        id=movie_id,
        title=title,
        type="movie",
        description=normalize_whitespace(remove_emojis(info.get("plot"))) if info.get("plot") else None,
        year=year,
        poster=info.get("movie_image") or info.get("cover"),
        category=movie_data.get("category_id"),
        country=info.get("country"),
        quality=movie_data.get("container_extension"),
        rating=safe_float(info.get("rating")),
        actors=info.get("actors"),
        director=info.get("director"),
        genre=info.get("genre"),
        duration=info.get("duration"),
        trailer=info.get("youtube_trailer"),
    )