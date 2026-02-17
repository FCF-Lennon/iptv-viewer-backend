from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union

class RawMovieSchema(BaseModel):
    stream_id: Optional[Union[int, str]] = None  # acepta int o str
    name: Optional[str] = None
    category_id: Optional[str] = None
    stream_icon: Optional[str] = None
    rating: Optional[Union[float, str]] = None  # acepta float o str
    added: Optional[str] = None
    container_extension: Optional[str] = None
    is_adult: Optional[str] = None

    model_config = ConfigDict(extra="ignore")
 
class RawSeriesSchema(BaseModel):
    series_id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    cover: Optional[str] = None
    plot: Optional[str] = None
    rating: Optional[Union[str, float]] = None
    category_id: Optional[Union[str, int]] = None

    model_config = ConfigDict(extra="ignore")

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




