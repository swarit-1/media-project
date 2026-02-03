from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LocationFilter(BaseModel):
    """Location filter for search."""

    type: str = Field(default="radius", pattern="^(radius|state|country)$")
    center_zip: Optional[str] = None
    radius_miles: int = Field(default=50, ge=1, le=500)
    state: Optional[str] = None
    country: Optional[str] = None


class RateFilter(BaseModel):
    """Rate filter for search."""

    type: str = Field(default="per_word", pattern="^(per_word|hourly|day_rate)$")
    min: Optional[Decimal] = Field(None, ge=0)
    max: Optional[Decimal] = Field(None, ge=0)


class StyleMatchConfig(BaseModel):
    """Style matching configuration."""

    newsroom_id: Optional[UUID] = None
    weight: float = Field(default=0.3, ge=0.0, le=1.0)


class SearchQuery(BaseModel):
    """Search query parameters."""

    beats: Optional[list[str]] = None
    location: Optional[LocationFilter] = None
    availability: Optional[str] = Field(None, pattern="^(available|limited|unavailable)$")
    min_trust_score: Optional[Decimal] = Field(None, ge=0.0, le=1.0)
    experience_level: Optional[list[str]] = None
    rate_range: Optional[RateFilter] = None


class PaginationRequest(BaseModel):
    """Pagination request parameters."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SortConfig(BaseModel):
    """Sort configuration."""

    field: str = Field(default="relevance", pattern="^(relevance|trust_score|rate|distance)$")
    order: str = Field(default="desc", pattern="^(asc|desc)$")


class SearchRequest(BaseModel):
    """Full search request body."""

    query: SearchQuery = Field(default_factory=SearchQuery)
    style_match: Optional[StyleMatchConfig] = None
    pagination: PaginationRequest = Field(default_factory=PaginationRequest)
    sort: SortConfig = Field(default_factory=SortConfig)


class FreelancerLocation(BaseModel):
    """Location info in search results."""

    city: Optional[str] = None
    state: Optional[str] = None
    distance_miles: Optional[float] = None


class FreelancerScores(BaseModel):
    """Scores in search results."""

    trust: Decimal
    quality: Decimal
    reliability: Decimal
    style_match: Optional[Decimal] = None


class FreelancerRates(BaseModel):
    """Rates in search results."""

    per_word: Optional[Decimal] = None
    hourly_min: Optional[Decimal] = None
    hourly_max: Optional[Decimal] = None
    day_rate: Optional[Decimal] = None


class PortfolioHighlightBrief(BaseModel):
    """Brief portfolio highlight for search results."""

    title: str
    publication: str
    published_date: Optional[str] = None


class RecentStats(BaseModel):
    """Recent activity stats."""

    articles_last_90_days: int = 0
    on_time_delivery_rate: Optional[Decimal] = None


class FreelancerSearchResult(BaseModel):
    """Single freelancer in search results."""

    freelancer_id: UUID
    display_name: str
    avatar_url: Optional[str] = None
    location: FreelancerLocation
    beats: list[str] = []
    scores: FreelancerScores
    rates: FreelancerRates
    availability: str
    portfolio_highlights: list[PortfolioHighlightBrief] = []
    recent_stats: RecentStats = Field(default_factory=RecentStats)

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination info in response."""

    page: int
    per_page: int
    total_results: int
    total_pages: int


class FacetValue(BaseModel):
    """Single facet value."""

    value: str
    count: int


class SearchFacets(BaseModel):
    """Search facets for filtering UI."""

    beats: list[FacetValue] = []
    experience_level: list[FacetValue] = []
    availability: list[FacetValue] = []


class SearchResponse(BaseModel):
    """Full search response."""

    results: list[FreelancerSearchResult]
    pagination: PaginationInfo
    facets: SearchFacets = Field(default_factory=SearchFacets)
