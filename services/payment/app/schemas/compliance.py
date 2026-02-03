from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ComplianceRecordResponse(BaseModel):
    """Schema for compliance record response."""

    id: UUID
    freelancer_id: UUID
    tax_year: int
    total_gross_payments: Decimal
    total_platform_fees: Decimal
    total_net_payments: Decimal
    payment_count: int
    w9_received: bool
    tin_last_four: Optional[str] = None
    form_1099_generated: bool
    form_1099_sent: bool
    threshold_1099: Decimal
    exceeds_threshold: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceSummary(BaseModel):
    """Schema for compliance summary across freelancers."""

    tax_year: int
    total_freelancers: int
    freelancers_exceeding_threshold: int
    total_gross_paid: Decimal
    total_platform_fees: Decimal
    w9_pending_count: int
    form_1099_pending_count: int
