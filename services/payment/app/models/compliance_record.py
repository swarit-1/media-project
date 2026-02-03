import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Numeric, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class ComplianceRecord(Base):
    """Tax compliance record for 1099 reporting."""

    __tablename__ = "compliance_records"

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
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Amounts
    total_gross_payments: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    total_platform_fees: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    total_net_payments: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    payment_count: Mapped[int] = mapped_column(Integer, default=0)

    # Tax info
    w9_received: Mapped[bool] = mapped_column(default=False)
    tin_last_four: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    form_1099_generated: Mapped[bool] = mapped_column(default=False)
    form_1099_sent: Mapped[bool] = mapped_column(default=False)

    # Threshold
    threshold_1099: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("600.00")
    )
    exceeds_threshold: Mapped[bool] = mapped_column(default=False)

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

    def __repr__(self) -> str:
        return f"<ComplianceRecord freelancer={self.freelancer_id} year={self.tax_year}>"
