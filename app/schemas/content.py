from pydantic import BaseModel
from typing import Optional, List

class ContentItemSchema(BaseModel):
    id: int
    title: str
    type: str 
    description: Optional[str] = None  
    year: Optional[int] = None
    poster: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    quality: Optional[str] = None
    language: Optional[str] = None
    rating: Optional[float] = None

     # Campos extra para películas
    actors: Optional[str] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[str] = None
    trailer: Optional[str] = None


class EpisodeSchema(BaseModel):
    id: int
    title: Optional[str] = None
    episode_num: Optional[int] = None
    season: Optional[int] = None
    rating: Optional[float] = None
    container_extension: Optional[str] = None


class SeasonSchema(BaseModel):
    season_number: int
    episode_count: int
    episodes: List[EpisodeSchema]


class SeriesDetailSchema(ContentItemSchema):
    seasons: List[SeasonSchema] = []
    total_seasons: Optional[int] = None
    total_episodes: Optional[int] = None
    