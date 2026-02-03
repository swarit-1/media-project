import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.ledger import VendorLedgerResponse, LedgerListResponse, PaginationMeta
from ..services.ledger_service import LedgerService
from .deps import require_freelancer

router = APIRouter()
ledger_service = LedgerService()


@router.get("/my", response_model=LedgerListResponse)
async def list_my_ledger_entries(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List ledger entries for the current freelancer."""
    entries, total = await ledger_service.list_freelancer_entries(
        db, freelancer_id, page=page, per_page=per_page,
    )

    return LedgerListResponse(
        results=[VendorLedgerResponse.model_validate(e) for e in entries],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/balance")
async def get_my_balance(
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Get the current balance for the authenticated freelancer."""
    balance = await ledger_service.get_freelancer_balance(db, freelancer_id)
    return {"freelancer_id": str(freelancer_id), "balance": str(balance), "currency": "USD"}
