from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.compliance_record import ComplianceRecord
from ..models.payment import Payment, PaymentStatus


class ComplianceService:
    """Service for managing tax compliance records."""

    async def get_or_create_compliance_record(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        tax_year: int,
    ) -> ComplianceRecord:
        """Get or create a compliance record for a freelancer and tax year."""
        result = await db.execute(
            select(ComplianceRecord).where(
                and_(
                    ComplianceRecord.freelancer_id == freelancer_id,
                    ComplianceRecord.tax_year == tax_year,
                )
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            record = ComplianceRecord(
                freelancer_id=freelancer_id,
                tax_year=tax_year,
            )
            db.add(record)
            await db.flush()
            await db.refresh(record)

        return record

    async def update_compliance_on_payment(
        self,
        db: AsyncSession,
        payment: Payment,
    ) -> ComplianceRecord:
        """Update compliance record when a payment is completed."""
        tax_year = payment.completed_at.year if payment.completed_at else datetime.now(timezone.utc).year

        record = await self.get_or_create_compliance_record(
            db, payment.freelancer_id, tax_year
        )

        record.total_gross_payments += payment.gross_amount
        record.total_platform_fees += payment.platform_fee
        record.total_net_payments += payment.net_amount
        record.payment_count += 1

        # Check 1099 threshold
        if record.total_gross_payments >= record.threshold_1099:
            record.exceeds_threshold = True

        await db.flush()
        await db.refresh(record)
        return record

    async def get_compliance_record(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        tax_year: int,
    ) -> Optional[ComplianceRecord]:
        """Get a compliance record."""
        result = await db.execute(
            select(ComplianceRecord).where(
                and_(
                    ComplianceRecord.freelancer_id == freelancer_id,
                    ComplianceRecord.tax_year == tax_year,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_compliance_records_for_year(
        self,
        db: AsyncSession,
        tax_year: int,
        exceeds_threshold_only: bool = False,
    ) -> list[ComplianceRecord]:
        """List all compliance records for a tax year."""
        query = select(ComplianceRecord).where(
            ComplianceRecord.tax_year == tax_year
        )

        if exceeds_threshold_only:
            query = query.where(ComplianceRecord.exceeds_threshold == True)

        query = query.order_by(ComplianceRecord.total_gross_payments.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_compliance_summary(
        self, db: AsyncSession, tax_year: int
    ) -> dict:
        """Get compliance summary for a tax year."""
        records = await self.list_compliance_records_for_year(db, tax_year)

        total_gross = sum(r.total_gross_payments for r in records)
        total_fees = sum(r.total_platform_fees for r in records)
        exceeding = [r for r in records if r.exceeds_threshold]
        w9_pending = [r for r in exceeding if not r.w9_received]
        form_1099_pending = [r for r in exceeding if not r.form_1099_generated]

        return {
            "tax_year": tax_year,
            "total_freelancers": len(records),
            "freelancers_exceeding_threshold": len(exceeding),
            "total_gross_paid": total_gross,
            "total_platform_fees": total_fees,
            "w9_pending_count": len(w9_pending),
            "form_1099_pending_count": len(form_1099_pending),
        }
