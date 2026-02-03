from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PitchCreate(BaseModel):
    """Schema for creating a pitch."""

    pitch_window_id: UUID
    headline: str = Field(..., min_length=1, max_length=500)
    summary: str = Field(..., min_length=10)
    approach: Optional[str] = None
    estimated_word_count: Optional[int] = Field(None, ge=100)
    proposed_rate: Optional[Decimal] = Field(None, ge=0)
    proposed_rate_type: Optional[str] = Field(
        None, pattern="^(per_word|hourly|flat|day_rate)$"
    )
    estimated_delivery_days: Optional[int] = Field(None, ge=1)


class PitchUpdate(BaseModel):
    """Schema for updating a draft pitch."""

    headline: Optional[str] = Field(None, min_length=1, max_length=500)
    summary: Optional[str] = Field(None, min_length=10)
    approach: Optional[str] = None
    estimated_word_count: Optional[int] = Field(None, ge=100)
    proposed_rate: Optional[Decimal] = Field(None, ge=0)
    proposed_rate_type: Optional[str] = Field(
        None, pattern="^(per_word|hourly|flat|day_rate)$"
    )
    estimated_delivery_days: Optional[int] = Field(None, ge=1)


class PitchReview(BaseModel):
    """Schema for editor reviewing a pitch."""

    action: str = Field(..., pattern="^(accept|reject)$")
    editor_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    agreed_rate: Optional[Decimal] = Field(None, ge=0)
    rate_type: Optional[str] = Field(
        None, pattern="^(per_word|hourly|flat|day_rate)$"
    )
    deadline: Optional[datetime] = None


class PitchResponse(BaseModel):
    """Schema for pitch response."""

    id: UUID
    pitch_window_id: UUID
    freelancer_id: UUID
    headline: str
    summary: str
    approach: Optional[str] = None
    estimated_word_count: Optional[int] = None
    proposed_rate: Optional[Decimal] = None
    proposed_rate_type: Optional[str] = None
    estimated_delivery_days: Optional[int] = None
    status: str
    editor_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
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


class PitchListResponse(BaseModel):
    """Schema for paginated pitch list."""

    results: list[PitchResponse]
    pagination: PaginationMeta
