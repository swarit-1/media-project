from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""

    assignment_id: UUID
    newsroom_id: UUID
    freelancer_id: UUID
    payment_type: str = Field(..., pattern="^(assignment|kill_fee|bonus)$")
    gross_amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None


class EscrowHoldRequest(BaseModel):
    """Schema for holding funds in escrow."""

    payment_id: UUID


class ReleasePaymentRequest(BaseModel):
    """Schema for releasing payment from escrow."""

    payment_id: UUID


class PaymentResponse(BaseModel):
    """Schema for payment response."""

    id: UUID
    assignment_id: UUID
    newsroom_id: UUID
    freelancer_id: UUID
    payment_type: str
    gross_amount: Decimal
    platform_fee: Decimal
    net_amount: Decimal
    currency: str
    stripe_payment_intent_id: Optional[str] = None
    status: str
    description: Optional[str] = None
    escrow_held_at: Optional[datetime] = None
    release_triggered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total_results: int
    total_pages: int


class PaymentListResponse(BaseModel):
    """Schema for paginated payment list."""

    results: list[PaymentResponse]
    pagination: PaginationMeta
