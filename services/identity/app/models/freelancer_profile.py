import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, Text, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

import sys
sys.path.insert(0, "/app")
from shared.db import Base

if TYPE_CHECKING:
    from .user import User


class AvailabilityStatus(str, enum.Enum):
    """Freelancer availability status."""

    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"


class FreelancerProfile(Base):
    """Freelancer profile extending user with professional information."""

    __tablename__ = "freelancer_profiles"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Location data
    home_zip: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    home_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    home_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    home_country: Mapped[str] = mapped_column(String(50), default="US")
    geo_point: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    willing_to_travel_miles: Mapped[int] = mapped_column(Integer, default=50)

    # Beats & expertise
    primary_beats: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    secondary_beats: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    languages: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        server_default=text("ARRAY['en']::text[]"),
    )

    # Availability
    availability_status: Mapped[AvailabilityStatus] = mapped_column(
        String(20),
        default=AvailabilityStatus.AVAILABLE.value,
    )
    weekly_capacity_hours: Mapped[int] = mapped_column(Integer, default=40)

    # Rates
    hourly_rate_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    hourly_rate_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    per_word_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 4), nullable=True)
    day_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Verification status
    identity_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    portfolio_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_info_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    bank_info_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Computed scores (updated by ML pipeline)
    trust_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.50"))
    quality_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.50"))
    reliability_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.50"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=datetime.utcnow,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="freelancer_profile")

    def __repr__(self) -> str:
        return f"<FreelancerProfile {self.display_name}>"
