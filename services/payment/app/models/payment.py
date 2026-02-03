import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, Numeric, Text, Enum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

import sys
sys.path.insert(0, "/app")
from shared.db import Base


class PaymentStatus(str, enum.Enum):
    """Payment status following the escrow state machine."""

    PENDING = "pending"
    ESCROW_HELD = "escrow_held"
    RELEASE_TRIGGERED = "release_triggered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentType(str, enum.Enum):
    """Payment type enumeration."""

    ASSIGNMENT = "assignment"
    KILL_FEE = "kill_fee"
    BONUS = "bonus"
    REFUND = "refund"


class Payment(Base):
    """Payment record with escrow state machine."""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    assignment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    newsroom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("newsrooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    freelancer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payment details
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType, name="payment_type", create_constraint=True),
        nullable=False,
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Stripe references
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_transfer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Status
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", create_constraint=True),
        default=PaymentStatus.PENDING,
    )

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    escrow_held_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    release_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
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
        return f"<Payment {self.id} {self.status.value} ${self.gross_amount}>"
