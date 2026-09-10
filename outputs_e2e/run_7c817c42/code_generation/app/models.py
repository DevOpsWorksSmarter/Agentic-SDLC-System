import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class CreateUrlRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_in_days: Optional[int] = None

    @field_validator("custom_code")
    @classmethod
    def validate_code(cls, v):
        if v and not v.isalnum():
            raise ValueError("Custom code must be alphanumeric")
        return v


class UrlResponse(BaseModel):
    id: uuid.UUID
    code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool


class StatsResponse(BaseModel):
    code: str
    total_clicks: int
    unique_visitors: int
    clicks_24h: int
    last_clicked_at: Optional[datetime]
    clicks_by_day: list[dict]
