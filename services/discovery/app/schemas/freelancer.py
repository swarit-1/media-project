from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PortfolioHighlight(BaseModel):
    """Portfolio item in detail view."""

    id: UUID
    title: str
    publication: str
    published_date: Optional[datetime] = None
    url: str
    word_count: Optional[int] = None
    topics: list[str] = []
    outlet_tier: Optional[str] = None


class FreelancerDetailResponse(BaseModel):
    """Full freelancer profile for detail view."""

    id: UUID
    user_id: UUID
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    # Location
    home_city: Optional[str] = None
    home_state: Optional[str] = None
    home_country: str
    willing_to_travel_miles: int

    # Beats & expertise
    primary_beats: list[str] = []
    secondary_beats: list[str] = []
    languages: list[str] = []

    # Availability
    availability_status: str
    weekly_capacity_hours: int

    # Rates
    hourly_rate_min: Optional[Decimal] = None
    hourly_rate_max: Optional[Decimal] = None
    per_word_rate: Optional[Decimal] = None
    day_rate: Optional[Decimal] = None

    # Verification
    identity_verified: bool
    portfolio_verified: bool

    # Scores
    trust_score: Decimal
    quality_score: Decimal
    reliability_score: Decimal

    # Portfolio
    portfolio_items: list[PortfolioHighlight] = []

    # Stats
    total_assignments: int = 0
    on_time_delivery_rate: Optional[Decimal] = None
    avg_editor_rating: Optional[Decimal] = None

    # Timestamps
    member_since: datetime

    class Config:
        from_attributes = True
