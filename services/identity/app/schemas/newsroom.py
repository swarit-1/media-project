from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NewsroomCreate(BaseModel):
    """Schema for creating a newsroom."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    domain: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)

    # Configuration
    cms_type: Optional[str] = Field(None, max_length=50)
    cms_webhook_url: Optional[str] = Field(None, max_length=500)
    payment_terms_days: int = Field(default=30, ge=0, le=365)

    # Style configuration
    style_guide_url: Optional[str] = Field(None, max_length=500)


class NewsroomUpdate(BaseModel):
    """Schema for updating a newsroom."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    cms_type: Optional[str] = Field(None, max_length=50)
    cms_webhook_url: Optional[str] = Field(None, max_length=500)
    payment_terms_days: Optional[int] = Field(None, ge=0, le=365)
    style_guide_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended)$")


class NewsroomResponse(BaseModel):
    """Schema for newsroom response."""

    id: UUID
    name: str
    slug: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    cms_type: Optional[str] = None
    payment_terms_days: int
    style_guide_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    """Schema for adding a member to a newsroom."""

    user_id: UUID
    role: str = Field(..., pattern="^(owner|admin|editor|viewer)$")
    permissions: Optional[list[str]] = None


class MembershipResponse(BaseModel):
    """Schema for membership response."""

    id: UUID
    newsroom_id: UUID
    user_id: UUID
    role: str
    permissions: Optional[list[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True
