from pydantic import BaseModel
from typing import Optional

class ContentItemSchema(BaseModel):
    id: int
    title: str
    type: str  # movie | series | live tv
    description: Optional[str] = None  # <- aquí está
    year: Optional[int] = None
    poster: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    quality: Optional[str] = None
    language: Optional[str] = None
    rating: Optional[float] = None

