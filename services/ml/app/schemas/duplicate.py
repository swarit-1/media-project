from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DuplicateCheckRequest(BaseModel):
    """Schema for checking duplicate pitches."""

    headline: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=10)
    newsroom_id: UUID


class SimilarItem(BaseModel):
    """Schema for a similar item found during duplicate check."""

    id: UUID
    title: str
    entity_type: str  # 'pitch' or 'article'
    overlap_score: float
    publication: Optional[str] = None
    published_date: Optional[str] = None


class DuplicateCheckResponse(BaseModel):
    """Schema for duplicate check response."""

    duplicate_score: float
    duplicate_warning: Optional[str] = None
    style_match_score: Optional[float] = None
    similar_pitches: list[SimilarItem]
    competing_coverage: list[SimilarItem]
