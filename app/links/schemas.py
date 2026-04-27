from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional
from uuid import UUID
import re

class ShortenRequest(BaseModel):
    original_url : str


class ShortenResponse(BaseModel):
    short_code : str
    original_url : str
    created_at : datetime
