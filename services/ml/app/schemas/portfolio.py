from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PortfolioItemCreate(BaseModel):
    """Schema for manually adding a portfolio item."""

    url: str = Field(..., max_length=1000)
    title: Optional[str] = Field(None, max_length=500)
    publication: Optional[str] = Field(None, max_length=255)


class PortfolioIngestRequest(BaseModel):
    """Schema for requesting portfolio URL ingestion."""

    urls: list[str] = Field(..., min_length=1, max_length=20)


class PortfolioIngestResponse(BaseModel):
    """Schema for portfolio ingestion response."""

    queued: int
    skipped: int
    errors: list[str]


class PortfolioItemResponse(BaseModel):
    """Schema for portfolio item response."""

    id: UUID
    freelancer_id: UUID
    url: str
    title: str
    publication: Optional[str] = None
    published_date: Optional[datetime] = None
    byline: Optional[str] = None
    word_count: Optional[int] = None
    excerpt: Optional[str] = None
    topics: Optional[list[str]] = None
    tone_profile: Optional[dict] = None
    outlet_tier: str
    geo_focus: Optional[list[str]] = None
    verification_status: str
    verification_method: Optional[str] = None
    scraped_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total_results: int
    total_pages: int


class PortfolioListResponse(BaseModel):
    """Schema for paginated portfolio list."""

    results: list[PortfolioItemResponse]
    pagination: PaginationMeta
