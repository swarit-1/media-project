from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StyleFingerprintResponse(BaseModel):
    """Schema for style fingerprint response."""

    id: UUID
    entity_id: UUID
    entity_type: str
    avg_sentence_length: Optional[Decimal] = None
    passive_voice_ratio: Optional[Decimal] = None
    narrative_score: Optional[Decimal] = None
    analytical_score: Optional[Decimal] = None
    explanatory_score: Optional[Decimal] = None
    citation_density: Optional[Decimal] = None
    headline_style: Optional[str] = None
    similar_to_outlets: Optional[list[str]] = None
    sample_size: int
    computed_at: datetime

    class Config:
        from_attributes = True


class StyleMatchRequest(BaseModel):
    """Schema for requesting style matching."""

    newsroom_id: UUID
    limit: int = 20
    min_score: float = 0.5
    beats: Optional[list[str]] = None


class StyleMatchResult(BaseModel):
    """Schema for a style match result."""

    freelancer_id: UUID
    display_name: str
    style_score: float
    beats: Optional[list[str]] = None
    trust_score: Optional[float] = None
    availability: Optional[str] = None
