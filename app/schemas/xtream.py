from pydantic import BaseModel
from typing import List, Optional

class MovieSchema(BaseModel):
    id: int
    title: str
    category_id: Optional[int]

class SeriesSchema(BaseModel):
    id: int
    title: str
    category_id: Optional[int]

class LiveTVSchema(BaseModel):
    id: int
    name:str
    stream_url: str

class CategorySchema(BaseModel):
    id: int
    name: str




