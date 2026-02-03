from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    """Schema for creating an assignment (internal, from pitch acceptance)."""

    pitch_id: UUID
    freelancer_id: UUID
    editor_id: UUID
    newsroom_id: UUID
    agreed_rate: Decimal = Field(..., ge=0)
    rate_type: str = Field(..., pattern="^(per_word|hourly|flat|day_rate)$")
    word_count_target: Optional[int] = Field(None, ge=100)
    deadline: datetime
    kill_fee_percentage: Decimal = Field(default=Decimal("25.00"), ge=0, le=100)


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""

    deadline: Optional[datetime] = None
    word_count_target: Optional[int] = Field(None, ge=100)
    revision_notes: Optional[str] = None


class AssignmentStatusUpdate(BaseModel):
    """Schema for updating assignment status."""

    status: str = Field(
        ...,
        pattern="^(in_progress|submitted|revision_requested|approved|killed)$",
    )
    content_url: Optional[str] = None
    final_word_count: Optional[int] = None
    revision_notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment response."""

    id: UUID
    pitch_id: UUID
    freelancer_id: UUID
    editor_id: UUID
    newsroom_id: UUID
    agreed_rate: Decimal
    rate_type: str
    word_count_target: Optional[int] = None
    deadline: datetime
    status: str
    revision_count: int
    max_revisions: int
    revision_notes: Optional[str] = None
    content_url: Optional[str] = None
    final_word_count: Optional[int] = None
    kill_fee_percentage: Decimal
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
