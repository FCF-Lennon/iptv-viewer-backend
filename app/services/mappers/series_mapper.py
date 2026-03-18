from app.schemas.content import ContentItemSchema
from app.utils.text_cleaner import (
    remove_emojis,
    normalize_whitespace,
    extract_year,
    remove_year,
    safe_float,
    safe_int
)

def normalize_series(item: dict) -> ContentItemSchema:
    raw_title = item.get("name", "") or ""

    # Extraer año usando tu función existente
    year = extract_year(raw_title)
    # Quitar año y limpiar título en una sola línea
    title = normalize_whitespace(remove_emojis(remove_year(raw_title)))

    rating = safe_float(item.get("rating"))

    return ContentItemSchema(
        id=int(item.get("series_id")),
        title=title,
        type="series",
        description=None,  # sin descripción
        year=year,
        poster=item.get("cover"),
        category=str(item.get("category_id")) if item.get("category_id") else None,
        rating=rating
    )


def normalize_series_detail(raw: dict, series_id: int) -> dict:
    info = raw.get("info", {})
    seasons_raw = raw.get("seasons", [])
    episodes_raw = raw.get("episodes", {})

    seasons = []
    total_episodes = 0

    for s in seasons_raw:
        season_number = safe_int(s.get("season_number"))
        season_eps = episodes_raw.get(str(season_number), [])

        # Construir lista de episodios de forma más directa
        episode_list = [
            {
                "id": safe_int(ep.get("id")),
                "title": normalize_whitespace(remove_emojis(ep.get("title", ""))),
                "episode_num": safe_int(ep.get("episode_num")),
                "season": season_number,
                "rating": safe_float(ep.get("rating") or ep.get("info", {}).get("rating")),
                "container_extension": ep.get("container_extension"),
            }
            for ep in season_eps
        ]

        if episode_list:
            total_episodes += len(episode_list)
            seasons.append({
                "season_number": season_number,
                "episode_count": len(episode_list),
                "episodes": sorted(episode_list, key=lambda x: x["episode_num"]),
                "air_date": s.get("air_date"),
                "vote_average": safe_float(s.get("vote_average")),
                "cover": s.get("cover")
            })
    
    seasons = sorted(seasons, key=lambda x: x["season_number"])

    return {
        "id": series_id,
        "title": normalize_whitespace(remove_emojis(info.get("name", ""))),
        "type": "series",
        "description": normalize_whitespace(remove_emojis(info.get("plot"))) if info.get("plot") else None,
        "year": safe_int(info.get("releaseDate")),
        "poster": info.get("cover"),
        "rating": safe_float(info.get("rating")),
        "seasons": seasons,
        "total_seasons": len(seasons),
        "total_episodes": total_episodes,
        "category_id": info.get("category_id")
    }
