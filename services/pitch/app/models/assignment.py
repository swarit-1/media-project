import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Numeric, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.db import Base

if TYPE_CHECKING:
    from .pitch import Pitch


class AssignmentStatus(str, enum.Enum):
    """Assignment status enumeration."""

    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"
    PUBLISHED = "published"
    KILLED = "killed"


class Assignment(Base):
    """Assignment created when a pitch is accepted."""

    __tablename__ = "assignments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    pitch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pitches.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    freelancer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    editor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("newsrooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Assignment details
    agreed_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rate_type: Mapped[str] = mapped_column(String(20), nullable=False)
    word_count_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Deadline
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Status
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status", create_constraint=True),
        default=AssignmentStatus.ASSIGNED,
    )

    # Revision tracking
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    max_revisions: Mapped[int] = mapped_column(Integer, default=2)
    revision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Content delivery
    content_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    final_word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # CMS integration
    draft_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    final_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cms_post_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Kill fee
    kill_fee_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("25.00")
    )

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
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
    pitch: Mapped["Pitch"] = relationship(
        "Pitch",
        back_populates="assignment",
    )

    def __repr__(self) -> str:
        return f"<Assignment pitch={self.pitch_id} status={self.status.value}>"
