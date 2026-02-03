from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FreelancerProfileCreate(BaseModel):
    """Schema for creating freelancer profile."""

    display_name: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    avatar_url: Optional[str] = Field(None, max_length=500)

    # Location
    home_zip: Optional[str] = Field(None, max_length=10)
    home_city: Optional[str] = Field(None, max_length=100)
    home_state: Optional[str] = Field(None, max_length=50)
    home_country: str = Field(default="US", max_length=50)
    willing_to_travel_miles: int = Field(default=50, ge=0, le=5000)

    # Beats & expertise
    primary_beats: Optional[list[str]] = None
    secondary_beats: Optional[list[str]] = None
    languages: list[str] = Field(default=["en"])

    # Availability
    availability_status: str = Field(default="available")
    weekly_capacity_hours: int = Field(default=40, ge=0, le=168)

    # Rates
    hourly_rate_min: Optional[Decimal] = Field(None, ge=0, le=10000)
    hourly_rate_max: Optional[Decimal] = Field(None, ge=0, le=10000)
    per_word_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    day_rate: Optional[Decimal] = Field(None, ge=0, le=50000)


class FreelancerProfileUpdate(BaseModel):
    """Schema for updating freelancer profile."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    avatar_url: Optional[str] = Field(None, max_length=500)

    # Location
    home_zip: Optional[str] = Field(None, max_length=10)
    home_city: Optional[str] = Field(None, max_length=100)
    home_state: Optional[str] = Field(None, max_length=50)
    home_country: Optional[str] = Field(None, max_length=50)
    willing_to_travel_miles: Optional[int] = Field(None, ge=0, le=5000)

    # Beats & expertise
    primary_beats: Optional[list[str]] = None
    secondary_beats: Optional[list[str]] = None
    languages: Optional[list[str]] = None

    # Availability
    availability_status: Optional[str] = None
    weekly_capacity_hours: Optional[int] = Field(None, ge=0, le=168)

    # Rates
    hourly_rate_min: Optional[Decimal] = Field(None, ge=0, le=10000)
    hourly_rate_max: Optional[Decimal] = Field(None, ge=0, le=10000)
    per_word_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    day_rate: Optional[Decimal] = Field(None, ge=0, le=50000)


class FreelancerProfileResponse(BaseModel):
    """Schema for freelancer profile response."""

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
    primary_beats: Optional[list[str]] = None
    secondary_beats: Optional[list[str]] = None
    languages: list[str]

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

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability status."""

    availability_status: str = Field(..., pattern="^(available|limited|unavailable)$")
    weekly_capacity_hours: Optional[int] = Field(None, ge=0, le=168)
