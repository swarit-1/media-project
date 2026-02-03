import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Numeric, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class LedgerEntryType(str, enum.Enum):
    """Ledger entry type enumeration."""

    PAYMENT = "payment"
    KILL_FEE = "kill_fee"
    BONUS = "bonus"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class VendorLedgerEntry(Base):
    """Vendor ledger entry for tracking freelancer payments."""

    __tablename__ = "vendor_ledger"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    payment_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )
    freelancer_id: Mapped[UUID] = mapped_column(
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

    # Entry details
    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType, name="ledger_entry_type", create_constraint=True),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    running_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
    )

    def __repr__(self) -> str:
        return f"<VendorLedger {self.entry_type.value} ${self.amount}>"
