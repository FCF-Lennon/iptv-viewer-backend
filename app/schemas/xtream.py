from pydantic import BaseModel
from typing import List, Optional

class MovieSchema(BaseModel):
    stream_id: int
    name: str
    category_id: Optional[str]

    class Config:
        from_attributes = True

class SeriesSchema(BaseModel):
    series_id: int
    name: str
    cover: Optional[str] = None
    plot: Optional[str] = None
    rating: Optional[str] = None

class LiveTVSchema(BaseModel):
    id: int
    name:str
    stream_url: str

class CategorySchema(BaseModel):
    category_id: str
    category_name: str




