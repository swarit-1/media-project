from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import sys
sys.path.insert(0, "/app")
from shared.errors import NotFoundError

from ..schemas import (
    SearchRequest,
    SearchResponse,
    FreelancerSearchResult,
    FreelancerLocation,
    FreelancerScores,
    FreelancerRates,
    RecentStats,
    PaginationInfo,
    SearchFacets,
    FacetValue,
    FreelancerDetailResponse,
    PortfolioHighlight,
)

# Import models from identity service's models
# In production, these would be in a shared models package
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.db import Base


class FreelancerProfile(Base):
    """Freelancer profile model (read-only for discovery service)."""

    __tablename__ = "freelancer_profiles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    display_name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Location
    home_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    home_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    home_country: Mapped[str] = mapped_column(String(50))
    willing_to_travel_miles: Mapped[int] = mapped_column(Integer)

    # Beats
    primary_beats: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    secondary_beats: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    languages: Mapped[list[str]] = mapped_column(ARRAY(Text))

    # Availability
    availability_status: Mapped[str] = mapped_column(String(20))
    weekly_capacity_hours: Mapped[int] = mapped_column(Integer)

    # Rates
    hourly_rate_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    hourly_rate_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    per_word_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 4), nullable=True)
    day_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Verification
    identity_verified: Mapped[bool] = mapped_column(Boolean)
    portfolio_verified: Mapped[bool] = mapped_column(Boolean)

    # Scores
    trust_score: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    quality_score: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    reliability_score: Mapped[Decimal] = mapped_column(Numeric(3, 2))

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class SearchService:
    """Service for freelancer search and discovery."""

    async def search(
        self,
        db: AsyncSession,
        request: SearchRequest,
    ) -> SearchResponse:
        """Search for freelancers based on criteria."""
        query = select(FreelancerProfile)
        filters = []

        # Apply filters
        q = request.query

        # Filter by beats
        if q.beats:
            # Match if any primary beat overlaps with requested beats
            filters.append(
                FreelancerProfile.primary_beats.overlap(q.beats)
            )

        # Filter by availability
        if q.availability:
            filters.append(FreelancerProfile.availability_status == q.availability)

        # Filter by minimum trust score
        if q.min_trust_score is not None:
            filters.append(FreelancerProfile.trust_score >= q.min_trust_score)

        # Filter by location (state-based for MVP)
        if q.location:
            if q.location.state:
                filters.append(FreelancerProfile.home_state == q.location.state)
            if q.location.country:
                filters.append(FreelancerProfile.home_country == q.location.country)

        # Filter by rate range
        if q.rate_range:
            if q.rate_range.type == "per_word" and q.rate_range.min is not None:
                filters.append(FreelancerProfile.per_word_rate >= q.rate_range.min)
            if q.rate_range.type == "per_word" and q.rate_range.max is not None:
                filters.append(FreelancerProfile.per_word_rate <= q.rate_range.max)
            if q.rate_range.type == "hourly" and q.rate_range.min is not None:
                filters.append(FreelancerProfile.hourly_rate_min >= q.rate_range.min)
            if q.rate_range.type == "hourly" and q.rate_range.max is not None:
                filters.append(FreelancerProfile.hourly_rate_max <= q.rate_range.max)
            if q.rate_range.type == "day_rate" and q.rate_range.min is not None:
                filters.append(FreelancerProfile.day_rate >= q.rate_range.min)
            if q.rate_range.type == "day_rate" and q.rate_range.max is not None:
                filters.append(FreelancerProfile.day_rate <= q.rate_range.max)

        # Apply filters to query
        if filters:
            query = query.where(and_(*filters))

        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total_count = total_result.scalar() or 0

        # Apply sorting
        sort = request.sort
        if sort.field == "trust_score":
            order_col = FreelancerProfile.trust_score
        elif sort.field == "rate":
            order_col = FreelancerProfile.per_word_rate
        else:
            # Default: sort by trust_score for relevance
            order_col = FreelancerProfile.trust_score

        if sort.order == "desc":
            query = query.order_by(order_col.desc().nulls_last())
        else:
            query = query.order_by(order_col.asc().nulls_last())

        # Apply pagination
        page = request.pagination.page
        per_page = request.pagination.per_page
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        profiles = list(result.scalars().all())

        # Convert to response format
        results = [self._profile_to_search_result(p) for p in profiles]

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

        # Build facets (simplified for MVP)
        facets = await self._build_facets(db, filters)

        return SearchResponse(
            results=results,
            pagination=PaginationInfo(
                page=page,
                per_page=per_page,
                total_results=total_count,
                total_pages=total_pages,
            ),
            facets=facets,
        )

    async def get_freelancer_detail(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
    ) -> FreelancerDetailResponse:
        """Get full freelancer profile for detail view."""
        result = await db.execute(
            select(FreelancerProfile).where(FreelancerProfile.id == freelancer_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise NotFoundError("Freelancer", freelancer_id)

        return FreelancerDetailResponse(
            id=profile.id,
            user_id=profile.user_id,
            display_name=profile.display_name,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            home_city=profile.home_city,
            home_state=profile.home_state,
            home_country=profile.home_country,
            willing_to_travel_miles=profile.willing_to_travel_miles,
            primary_beats=profile.primary_beats or [],
            secondary_beats=profile.secondary_beats or [],
            languages=profile.languages or [],
            availability_status=profile.availability_status,
            weekly_capacity_hours=profile.weekly_capacity_hours,
            hourly_rate_min=profile.hourly_rate_min,
            hourly_rate_max=profile.hourly_rate_max,
            per_word_rate=profile.per_word_rate,
            day_rate=profile.day_rate,
            identity_verified=profile.identity_verified,
            portfolio_verified=profile.portfolio_verified,
            trust_score=profile.trust_score,
            quality_score=profile.quality_score,
            reliability_score=profile.reliability_score,
            portfolio_items=[],  # Will be populated in Phase 3
            total_assignments=0,  # Will be populated when assignments are implemented
            on_time_delivery_rate=None,
            avg_editor_rating=None,
            member_since=profile.created_at,
        )

    def _profile_to_search_result(self, profile: FreelancerProfile) -> FreelancerSearchResult:
        """Convert a profile to a search result."""
        return FreelancerSearchResult(
            freelancer_id=profile.id,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            location=FreelancerLocation(
                city=profile.home_city,
                state=profile.home_state,
                distance_miles=None,  # Will be calculated with PostGIS in future
            ),
            beats=profile.primary_beats or [],
            scores=FreelancerScores(
                trust=profile.trust_score,
                quality=profile.quality_score,
                reliability=profile.reliability_score,
                style_match=None,  # Will be calculated in Phase 3
            ),
            rates=FreelancerRates(
                per_word=profile.per_word_rate,
                hourly_min=profile.hourly_rate_min,
                hourly_max=profile.hourly_rate_max,
                day_rate=profile.day_rate,
            ),
            availability=profile.availability_status,
            portfolio_highlights=[],  # Will be populated in Phase 3
            recent_stats=RecentStats(
                articles_last_90_days=0,
                on_time_delivery_rate=None,
            ),
        )

    async def _build_facets(
        self,
        db: AsyncSession,
        base_filters: list,
    ) -> SearchFacets:
        """Build search facets for filtering UI."""
        # Simplified facets for MVP - just return availability counts
        availability_query = select(
            FreelancerProfile.availability_status,
            func.count(FreelancerProfile.id),
        ).group_by(FreelancerProfile.availability_status)

        result = await db.execute(availability_query)
        availability_facets = [
            FacetValue(value=row[0], count=row[1])
            for row in result.all()
        ]

        return SearchFacets(
            beats=[],  # Will be implemented with more complex aggregation
            experience_level=[],
            availability=availability_facets,
        )
