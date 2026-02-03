from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TrustScoreComponents(BaseModel):
    """Breakdown of trust score components."""

    identity_verification: float
    portfolio_quality: float
    on_time_delivery: float
    acceptance_rate: float
    editor_ratings: float
    platform_tenure: float
    response_time: float


class TrustScoreResponse(BaseModel):
    """Schema for trust score response."""

    freelancer_id: UUID
    trust_score: float
    previous_score: Optional[float] = None
    components: TrustScoreComponents
    computed_at: str


class TrustScoreComputeRequest(BaseModel):
    """Schema for requesting trust score computation."""

    freelancer_id: UUID
    force_recompute: bool = False
