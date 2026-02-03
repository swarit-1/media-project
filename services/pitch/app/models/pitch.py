import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Numeric, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.db import Base

if TYPE_CHECKING:
    from .pitch_window import PitchWindow
    from .assignment import Assignment


class PitchStatus(str, enum.Enum):
    """Pitch status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Pitch(Base):
    """Pitch submitted by a freelancer to a pitch window."""

    __tablename__ = "pitches"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    pitch_window_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pitch_windows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    freelancer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Pitch content
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    approach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_word_count: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Proposed rates
    proposed_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    proposed_rate_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    estimated_delivery_days: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Status
    status: Mapped[PitchStatus] = mapped_column(
        Enum(PitchStatus, name="pitch_status", create_constraint=True),
        default=PitchStatus.DRAFT,
    )

    # Editor feedback
    editor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    # Relationships
    pitch_window: Mapped["PitchWindow"] = relationship(
        "PitchWindow",
        back_populates="pitches",
    )
    assignment: Mapped[Optional["Assignment"]] = relationship(
        "Assignment",
        back_populates="pitch",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Pitch {self.headline[:50]}>"
