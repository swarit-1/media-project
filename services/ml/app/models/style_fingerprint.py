from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Numeric, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class StyleFingerprint(Base):
    """Style fingerprint for freelancers or newsrooms.

    Contains computed style metrics and a 384-dimensional embedding
    generated from analyzed portfolio items or newsroom style guides.
    """

    __tablename__ = "style_fingerprints"

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
    )  # 'freelancer' or 'newsroom'

    # Style metrics (0.0 to 1.0 scale)
    avg_sentence_length: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True,
    )
    passive_voice_ratio: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )
    narrative_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )
    analytical_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )
    explanatory_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )
    citation_density: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
    )

    # Headline style classification
    headline_style: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True,
    )  # 'declarative', 'question', 'how_to', 'list'

    # Similar outlets
    similar_to_outlets: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(100)), nullable=True,
    )

    # Embedding vector (384 dimensions from sentence-transformers)
    style_embedding = mapped_column(
        Vector(384), nullable=True,
    )

    # Sample statistics
    sample_size: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
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
        return f"<StyleFingerprint {self.entity_type}:{self.entity_id}>"
