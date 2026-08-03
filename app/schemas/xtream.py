from pydantic import BaseModel, ConfigDict
from typing import Optional, Union

class RawMovieSchema(BaseModel):
    stream_id: Optional[Union[int, str]] = None  
    name: Optional[str] = None
    category_id: Optional[str] = None
    stream_icon: Optional[str] = None
    rating: Optional[Union[float, str]] = None  
    added: Optional[str] = None
    container_extension: Optional[str] = None
    is_adult: Optional[str] = None
    plot: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(extra="ignore")
 
class RawSeriesSchema(BaseModel):
    series_id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    cover: Optional[str] = None
    plot: Optional[str] = None
    rating: Optional[Union[str, float]] = None
    category_id: Optional[Union[str, int]] = None
    last_modified: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class RawLiveSchema(BaseModel):
    num: Optional[int]
    stream_id: Optional[int]
    name: Optional[str]
    stream_type: Optional[str] = None
    stream_icon: Optional[str] 
    epg_channel_id: Optional[str] = None
    added: Optional[str] = None
    category_id: Optional[str] 
    custom_sid: Optional[str] = None
    tv_archive: Optional[int] = None
    direct_source: Optional[str] = None
    tv_archive_duration: Optional[int] = None

    model_config = ConfigDict(extra="ignore")

class CategorySchema(BaseModel):
    category_id: str
    category_name: str


class XtreamCredentials(BaseModel):
    host: str
    username: str
    password: str
    name: str
    is_active: bool = True

class EpgListingSchema(BaseModel):
    id: Optional[str] = None
    epg_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    start_timestamp: Optional[Union[int, str]] = None
    stop_timestamp: Optional[Union[int, str]] = None

    model_config = ConfigDict(extra="ignore")

