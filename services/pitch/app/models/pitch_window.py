import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Numeric, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.db import Base

if TYPE_CHECKING:
    from .pitch import Pitch


class PitchWindowStatus(str, enum.Enum):
    """Pitch window status enumeration."""

    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PitchWindow(Base):
    """Pitch window representing an open opportunity from a newsroom."""

    __tablename__ = "pitch_windows"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("newsrooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    editor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Window details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    beats: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
    )
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Budget
    budget_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    budget_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    rate_type: Mapped[str] = mapped_column(String(20), default="per_word")

    # Window constraints
    max_pitches: Mapped[int] = mapped_column(Integer, default=50)
    current_pitch_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Status
    status: Mapped[PitchWindowStatus] = mapped_column(
        Enum(PitchWindowStatus, name="pitch_window_status", create_constraint=True),
        default=PitchWindowStatus.DRAFT,
    )

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

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
    pitches: Mapped[list["Pitch"]] = relationship(
        "Pitch",
        back_populates="pitch_window",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PitchWindow {self.title[:50]}>"
