from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PitchWindowCreate(BaseModel):
    """Schema for creating a pitch window."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10)
    beats: list[str] = Field(..., min_length=1)
    requirements: Optional[str] = None
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    rate_type: str = Field(default="per_word", pattern="^(per_word|hourly|flat|day_rate)$")
    max_pitches: int = Field(default=50, ge=1, le=500)
    opens_at: datetime
    closes_at: datetime


class PitchWindowUpdate(BaseModel):
    """Schema for updating a pitch window."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    beats: Optional[list[str]] = None
    requirements: Optional[str] = None
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    max_pitches: Optional[int] = Field(None, ge=1, le=500)
    closes_at: Optional[datetime] = None


class PitchWindowResponse(BaseModel):
    """Schema for pitch window response."""

    id: UUID
    newsroom_id: UUID
    editor_id: UUID
    title: str
    description: str
    beats: list[str]
    requirements: Optional[str] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    rate_type: str
    max_pitches: int
    current_pitch_count: int
    opens_at: datetime
    closes_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total_results: int
    total_pages: int


class PitchWindowListResponse(BaseModel):
    """Schema for paginated pitch window list."""

    results: list[PitchWindowResponse]
    pagination: PaginationMeta
