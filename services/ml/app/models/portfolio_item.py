import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class VerificationStatus(str, enum.Enum):
    """Portfolio item verification status."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DISPUTED = "disputed"


class OutletTier(str, enum.Enum):
    """Publication outlet tier classification."""

    TIER1 = "tier1"
    TIER2 = "tier2"
    TIER3 = "tier3"
    UNKNOWN = "unknown"


class PortfolioItem(Base):
    """Portfolio item representing a freelancer's published work."""

    __tablename__ = "portfolio_items"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    freelancer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Article metadata
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    publication: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    byline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Content analysis
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topics: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    tone_profile: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Classification
    outlet_tier: Mapped[OutletTier] = mapped_column(
        Enum(OutletTier, name="outlet_tier", create_constraint=True),
        default=OutletTier.UNKNOWN,
    )
    geo_focus: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)

    # Verification
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status", create_constraint=True),
        default=VerificationStatus.PENDING,
    )
    verification_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    scraped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<PortfolioItem {self.title[:50]}>"
