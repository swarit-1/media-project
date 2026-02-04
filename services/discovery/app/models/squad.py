import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class SquadMemberStatus(str, enum.Enum):
    """Status of a squad member invitation."""

    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REMOVED = "removed"


class SquadInstanceStatus(str, enum.Enum):
    """Status of a squad instance."""

    FORMING = "forming"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISBANDED = "disbanded"


class SquadTemplate(Base):
    """Reusable squad template defining team composition needs."""

    __tablename__ = "squad_templates"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Required roles/beats for the squad
    required_beats: Mapped[list] = mapped_column(ARRAY(Text), nullable=False)
    required_roles: Mapped[list] = mapped_column(ARRAY(Text), nullable=False)
    min_members: Mapped[int] = mapped_column(Integer, default=2)
    max_members: Mapped[int] = mapped_column(Integer, default=10)

    # Filters for auto-matching
    min_trust_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    preferred_tiers: Mapped[Optional[list]] = mapped_column(ARRAY(Text), nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"),
        onupdate=datetime.utcnow,
    )

    # Relationships
    instances: Mapped[list["SquadInstance"]] = relationship(
        "SquadInstance", back_populates="template",
    )

    def __repr__(self) -> str:
        return f"<SquadTemplate name={self.name}>"


class SquadInstance(Base):
    """Active squad assembled from a template for a specific project."""

    __tablename__ = "squad_instances"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    template_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("squad_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_brief: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[SquadInstanceStatus] = mapped_column(
        Enum(SquadInstanceStatus, name="squad_instance_status", create_constraint=True),
        default=SquadInstanceStatus.FORMING,
    )

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"),
        onupdate=datetime.utcnow,
    )

    # Relationships
    template: Mapped["SquadTemplate"] = relationship(
        "SquadTemplate", back_populates="instances",
    )
    members: Mapped[list["SquadMember"]] = relationship(
        "SquadMember", back_populates="squad",
    )

    def __repr__(self) -> str:
        return f"<SquadInstance name={self.name} status={self.status.value}>"


class SquadMember(Base):
    """A freelancer member of a squad instance."""

    __tablename__ = "squad_members"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    squad_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("squad_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    freelancer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Role within the squad
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    beats: Mapped[Optional[list]] = mapped_column(ARRAY(Text), nullable=True)

    # Status
    status: Mapped[SquadMemberStatus] = mapped_column(
        Enum(SquadMemberStatus, name="squad_member_status", create_constraint=True),
        default=SquadMemberStatus.INVITED,
    )

    # Invitation
    invited_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    invitation_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"),
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationships
    squad: Mapped["SquadInstance"] = relationship(
        "SquadInstance", back_populates="members",
    )

    def __repr__(self) -> str:
        return f"<SquadMember squad={self.squad_id} freelancer={self.freelancer_id}>"
