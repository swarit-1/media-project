from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Text, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.db import Base

if TYPE_CHECKING:
    from .user import User


class Newsroom(Base):
    """Newsroom model representing a media organization."""

    __tablename__ = "newsrooms"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Configuration
    cms_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cms_webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)

    # Compliance
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    billing_address: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Style configuration
    style_guide_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="active")

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
    memberships: Mapped[list["NewsroomMembership"]] = relationship(
        "NewsroomMembership",
        back_populates="newsroom",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Newsroom {self.name}>"


class NewsroomMembership(Base):
    """Newsroom membership model for editors belonging to newsrooms."""

    __tablename__ = "newsroom_memberships"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("newsrooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # owner, admin, editor, viewer
    permissions: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
    )

    # Relationships
    newsroom: Mapped["Newsroom"] = relationship("Newsroom", back_populates="memberships")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        # Unique constraint on newsroom_id and user_id
        {"schema": None},
    )

    def __repr__(self) -> str:
        return f"<NewsroomMembership {self.user_id} -> {self.newsroom_id}>"
