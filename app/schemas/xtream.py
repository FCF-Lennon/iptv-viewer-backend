from pydantic import BaseModel, ConfigDict
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
    stream_id: int
    num: int
    name: str
    stream_type: Optional[str] = None
    category_id: Optional[str] = None
    container_extension: Optional[str] = None
    stream_icon: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class CategorySchema(BaseModel):
    category_id: str
    category_name: str




