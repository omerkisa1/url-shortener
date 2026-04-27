from pydantic import BaseModel, HttpUrl, AnyHttpUrl
from datetime import datetime

class ShortenRequest(BaseModel):
    original_url : AnyHttpUrl


class ShortenResponse(BaseModel):
    short_code : str
    original_url : AnyHttpUrl
    created_at : datetime
