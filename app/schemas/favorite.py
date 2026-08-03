from pydantic import BaseModel
from typing import Literal


class FavoriteCreate(BaseModel):
    content_type: Literal["movie", "series", "live"]
    content_id: int
    name: str


class FavoriteResponse(BaseModel):
    id: int
    content_type: str
    content_id: int
    name: str

    model_config = {"from_attributes": True}
