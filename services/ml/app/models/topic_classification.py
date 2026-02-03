from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Numeric, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class TopicClassification(Base):
    """Topic classification result for a portfolio item or pitch."""

    __tablename__ = "topic_classifications"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    entity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )  # 'portfolio_item' or 'pitch'

    # Classification results
    primary_topic: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), nullable=False,
    )
    secondary_topic: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
    )
    secondary_confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )

    # Full classification scores
    all_scores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    classified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
    )

    def __repr__(self) -> str:
        return f"<TopicClassification {self.primary_topic} ({self.primary_confidence})>"
