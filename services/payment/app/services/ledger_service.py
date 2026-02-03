from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.vendor_ledger import VendorLedgerEntry, LedgerEntryType
from ..models.payment import Payment


class LedgerService:
    """Service for managing vendor ledger entries."""

    async def get_freelancer_balance(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> Decimal:
        """Get the current balance for a freelancer."""
        result = await db.execute(
            select(VendorLedgerEntry.running_balance)
            .where(VendorLedgerEntry.freelancer_id == freelancer_id)
            .order_by(VendorLedgerEntry.created_at.desc())
            .limit(1)
        )
        balance = result.scalar_one_or_none()
        return balance if balance is not None else Decimal("0.00")

    async def create_entry(
        self,
        db: AsyncSession,
        payment: Payment,
        entry_type: LedgerEntryType,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> VendorLedgerEntry:
        """Create a new ledger entry."""
        current_balance = await self.get_freelancer_balance(
            db, payment.freelancer_id
        )
        new_balance = current_balance + amount

        entry = VendorLedgerEntry(
            payment_id=payment.id,
            freelancer_id=payment.freelancer_id,
            newsroom_id=payment.newsroom_id,
            entry_type=entry_type,
            amount=amount,
            running_balance=new_balance,
            description=description or f"{entry_type.value} for payment {payment.id}",
        )
        db.add(entry)
        await db.flush()
        await db.refresh(entry)
        return entry

    async def record_payment_completed(
        self, db: AsyncSession, payment: Payment
    ) -> VendorLedgerEntry:
        """Record a completed payment in the ledger."""
        entry_type_map = {
            "assignment": LedgerEntryType.PAYMENT,
            "kill_fee": LedgerEntryType.KILL_FEE,
            "bonus": LedgerEntryType.BONUS,
        }
        entry_type = entry_type_map.get(
            payment.payment_type.value, LedgerEntryType.PAYMENT
        )

        return await self.create_entry(
            db,
            payment,
            entry_type=entry_type,
            amount=payment.net_amount,
            description=f"{payment.payment_type.value} payment completed",
        )

    async def record_refund(
        self, db: AsyncSession, payment: Payment
    ) -> VendorLedgerEntry:
        """Record a refund in the ledger (negative entry)."""
        return await self.create_entry(
            db,
            payment,
            entry_type=LedgerEntryType.REFUND,
            amount=-payment.net_amount,
            description=f"Refund for payment {payment.id}",
        )

    async def list_freelancer_entries(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[VendorLedgerEntry], int]:
        """List ledger entries for a freelancer."""
        query = select(VendorLedgerEntry).where(
            VendorLedgerEntry.freelancer_id == freelancer_id
        )
        count_query = select(func.count(VendorLedgerEntry.id)).where(
            VendorLedgerEntry.freelancer_id == freelancer_id
        )

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(VendorLedgerEntry.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        entries = list(result.scalars().all())

        return entries, total
