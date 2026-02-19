from app.schemas.content import ContentItemSchema
from app.utils.text_cleaner import (
    normalize_whitespace,
    extract_country,
    extract_quality,
    clean_special_chars, 
    remove_country,
    remove_quality,
    safe_int
)

def normalize_live(item: dict) -> ContentItemSchema:
    stream_id = item.get("stream_id")

    if not stream_id:
        raise ValueError("normalize_live recibió item sin stream_id")

    raw_title = item.get("name", "")

    country = extract_country(raw_title)
    quality = extract_quality(raw_title)

    # Limpieza consistente
    cleaned_title = clean_special_chars(raw_title)
    cleaned_title = normalize_whitespace(cleaned_title)
    cleaned_title = remove_quality(cleaned_title)
    cleaned_title = remove_country(cleaned_title)

    return ContentItemSchema(
        id=safe_int(stream_id),
        title=cleaned_title,
        type="live",
        description=None,
        year=None,
        poster=item.get("stream_icon"),
        category=item.get("category_id"),
        country=country,
        quality=quality,
        rating=None,
        actors=None,
        director=None,
        genre=None,
        duration=None,
        trailer=None
    )
