from app.schemas.content import ContentItemSchema
from app.utils.text_cleaner import (
    clean_obfuscation,
    extract_prefix,
    extract_strict_country,
    extract_quality,
    remove_quality,
    clean_suffixes_and_noise,
    normalize_whitespace,
    safe_int
)

def normalize_live(item: dict) -> ContentItemSchema:
    stream_id = item.get("stream_id")
    if not stream_id:
        raise ValueError("normalize_live recibió item sin stream_id")

    raw_title = item.get("name", "")

    strict_country = extract_strict_country(raw_title)

    cleaned_title = clean_obfuscation(raw_title)
    prefix, cleaned_title = extract_prefix(cleaned_title)
    
    quality = extract_quality(cleaned_title)

    cleaned_title = remove_quality(cleaned_title)
    cleaned_title = clean_suffixes_and_noise(cleaned_title)
    cleaned_title = normalize_whitespace(cleaned_title or "")

    if not cleaned_title and prefix:
        cleaned_title = clean_suffixes_and_noise(prefix)
        cleaned_title = normalize_whitespace(cleaned_title or "")
        
    if not cleaned_title:
        cleaned_title = raw_title.strip()

    if not cleaned_title:
        cleaned_title = "Unknown Channel"

    cleaned_title = cleaned_title.upper()

    return ContentItemSchema(
        id=safe_int(stream_id),
        title=cleaned_title,
        type="live",
        description=None,
        year=None,
        poster=item.get("stream_icon"),
        category=item.get("category_id") or prefix, 
        country=strict_country, 
        quality=quality,
        rating=None,
        actors=None,
        director=None,
        genre=None,
        duration=None,
        trailer=None
    )