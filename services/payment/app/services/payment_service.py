import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.payment import Payment, PaymentStatus, PaymentType
from ..schemas.payment import PaymentCreate
from .stripe_service import StripeService

settings = get_settings()


class PaymentService:
    """Service for managing payments with escrow state machine."""

    def __init__(self):
        self.stripe = StripeService()

    def _calculate_fees(self, gross_amount: Decimal) -> tuple[Decimal, Decimal]:
        """Calculate platform fee and net amount."""
        fee_rate = Decimal(str(settings.platform_fee_percentage)) / Decimal("100")
        platform_fee = (gross_amount * fee_rate).quantize(Decimal("0.01"))
        net_amount = gross_amount - platform_fee
        return platform_fee, net_amount

    async def create_payment(
        self,
        db: AsyncSession,
        data: PaymentCreate,
    ) -> Payment:
        """Create a new payment record."""
        platform_fee, net_amount = self._calculate_fees(data.gross_amount)

        payment = Payment(
            assignment_id=data.assignment_id,
            newsroom_id=data.newsroom_id,
            freelancer_id=data.freelancer_id,
            payment_type=PaymentType(data.payment_type),
            gross_amount=data.gross_amount,
            platform_fee=platform_fee,
            net_amount=net_amount,
            description=data.description,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        await db.flush()
        await db.refresh(payment)
        return payment

    async def get_payment_by_id(
        self, db: AsyncSession, payment_id: UUID
    ) -> Optional[Payment]:
        """Get a payment by ID."""
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def list_payments_for_assignment(
        self, db: AsyncSession, assignment_id: UUID
    ) -> list[Payment]:
        """List all payments for an assignment."""
        result = await db.execute(
            select(Payment)
            .where(Payment.assignment_id == assignment_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_payments_for_freelancer(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        status: Optional[PaymentStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Payment], int]:
        """List payments for a freelancer."""
        query = select(Payment).where(Payment.freelancer_id == freelancer_id)
        count_query = select(func.count(Payment.id)).where(
            Payment.freelancer_id == freelancer_id
        )

        if status:
            query = query.where(Payment.status == status)
            count_query = count_query.where(Payment.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Payment.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        payments = list(result.scalars().all())

        return payments, total

    async def list_payments_for_newsroom(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        status: Optional[PaymentStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Payment], int]:
        """List payments for a newsroom."""
        query = select(Payment).where(Payment.newsroom_id == newsroom_id)
        count_query = select(func.count(Payment.id)).where(
            Payment.newsroom_id == newsroom_id
        )

        if status:
            query = query.where(Payment.status == status)
            count_query = count_query.where(Payment.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Payment.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        payments = list(result.scalars().all())

        return payments, total

    async def hold_escrow(
        self, db: AsyncSession, payment: Payment
    ) -> Payment:
        """Hold funds in escrow via Stripe."""
        if payment.status != PaymentStatus.PENDING:
            raise ValueError(
                f"Cannot hold escrow: payment is {payment.status.value}, expected pending"
            )

        amount_cents = int(payment.gross_amount * 100)

        # Create Stripe PaymentIntent with manual capture
        intent = await self.stripe.create_payment_intent(
            amount_cents=amount_cents,
            metadata={
                "payment_id": str(payment.id),
                "assignment_id": str(payment.assignment_id),
                "freelancer_id": str(payment.freelancer_id),
            },
        )

        payment.stripe_payment_intent_id = intent["id"]
        payment.status = PaymentStatus.ESCROW_HELD
        payment.escrow_held_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(payment)
        return payment

    async def release_payment(
        self, db: AsyncSession, payment: Payment
    ) -> Payment:
        """Release payment from escrow (trigger capture)."""
        if payment.status != PaymentStatus.ESCROW_HELD:
            raise ValueError(
                f"Cannot release: payment is {payment.status.value}, expected escrow_held"
            )

        payment.status = PaymentStatus.RELEASE_TRIGGERED
        payment.release_triggered_at = datetime.now(timezone.utc)

        # Capture the payment intent
        if payment.stripe_payment_intent_id:
            await self.stripe.capture_payment_intent(
                payment.stripe_payment_intent_id,
                amount_cents=int(payment.gross_amount * 100),
            )

        payment.status = PaymentStatus.PROCESSING

        await db.flush()
        await db.refresh(payment)
        return payment

    async def complete_payment(
        self, db: AsyncSession, payment: Payment
    ) -> Payment:
        """Mark payment as completed after transfer succeeds."""
        if payment.status != PaymentStatus.PROCESSING:
            raise ValueError(
                f"Cannot complete: payment is {payment.status.value}, expected processing"
            )

        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(payment)
        return payment

    async def fail_payment(
        self, db: AsyncSession, payment: Payment, reason: Optional[str] = None
    ) -> Payment:
        """Mark payment as failed."""
        payment.status = PaymentStatus.FAILED
        if reason:
            payment.metadata_json = payment.metadata_json or {}
            payment.metadata_json["failure_reason"] = reason

        await db.flush()
        await db.refresh(payment)
        return payment

    async def refund_payment(
        self, db: AsyncSession, payment: Payment
    ) -> Payment:
        """Refund a payment."""
        if payment.status not in (
            PaymentStatus.ESCROW_HELD,
            PaymentStatus.COMPLETED,
        ):
            raise ValueError(
                f"Cannot refund: payment is {payment.status.value}"
            )

        if payment.stripe_payment_intent_id:
            await self.stripe.create_refund(payment.stripe_payment_intent_id)

        payment.status = PaymentStatus.REFUNDED
        payment.completed_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(payment)
        return payment
