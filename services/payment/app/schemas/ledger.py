from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VendorLedgerResponse(BaseModel):
    """Schema for vendor ledger entry response."""

    id: UUID
    payment_id: Optional[UUID] = None
    freelancer_id: UUID
    newsroom_id: UUID
    entry_type: str
    amount: Decimal
    running_balance: Decimal
    currency: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total_results: int
    total_pages: int


class LedgerListResponse(BaseModel):
    """Schema for paginated ledger list."""

    results: list[VendorLedgerResponse]
    pagination: PaginationMeta
