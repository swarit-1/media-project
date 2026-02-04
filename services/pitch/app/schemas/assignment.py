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
        pattern="^(in_progress|submitted|revision_requested|approved|published|killed)$",
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
    draft_url: Optional[str] = None
    final_url: Optional[str] = None
    cms_post_id: Optional[str] = None
    published_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CMSWebhookPayload(BaseModel):
    """Schema for CMS webhook payload."""

    event: str = Field(..., pattern="^(article.published|article.updated|article.unpublished)$")
    cms_post_id: str
    assignment_id: UUID
    published_url: str
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class CMSWebhookResponse(BaseModel):
    """Schema for CMS webhook response."""

    status: str
    assignment_id: UUID
    assignment_status: str
    payment_release_triggered: bool = False
