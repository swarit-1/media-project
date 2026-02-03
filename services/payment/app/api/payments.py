import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..models.payment import PaymentStatus
from ..schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    PaginationMeta,
)
from ..services.payment_service import PaymentService
from ..services.compliance_service import ComplianceService
from ..services.ledger_service import LedgerService
from .deps import require_editor, require_freelancer, get_current_user_role, require_newsroom_id

router = APIRouter()
payment_service = PaymentService()
compliance_service = ComplianceService()
ledger_service = LedgerService()


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new payment. Requires editor role."""
    payment = await payment_service.create_payment(db, data)
    return payment


@router.get("/my", response_model=PaymentListResponse)
async def list_my_payments(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List payments for the current freelancer."""
    p_status = None
    if status_filter:
        try:
            p_status = PaymentStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    payments, total = await payment_service.list_payments_for_freelancer(
        db, freelancer_id, status=p_status, page=page, per_page=per_page,
    )

    return PaymentListResponse(
        results=[PaymentResponse.model_validate(p) for p in payments],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/newsroom", response_model=PaymentListResponse)
async def list_newsroom_payments(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """List payments for a newsroom. Requires editor role."""
    p_status = None
    if status_filter:
        try:
            p_status = PaymentStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    payments, total = await payment_service.list_payments_for_newsroom(
        db, newsroom_id, status=p_status, page=page, per_page=per_page,
    )

    return PaymentListResponse(
        results=[PaymentResponse.model_validate(p) for p in payments],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific payment."""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Payment not found"},
        )
    return payment


@router.post("/{payment_id}/escrow", response_model=PaymentResponse)
async def hold_escrow(
    payment_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Hold payment funds in escrow. Requires editor role."""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Payment not found"},
        )

    try:
        updated = await payment_service.hold_escrow(db, payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    return updated


@router.post("/{payment_id}/release", response_model=PaymentResponse)
async def release_payment(
    payment_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Release payment from escrow. Requires editor role."""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Payment not found"},
        )

    try:
        updated = await payment_service.release_payment(db, payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    return updated


@router.post("/{payment_id}/complete", response_model=PaymentResponse)
async def complete_payment(
    payment_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Mark payment as completed. Creates ledger entry and updates compliance."""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Payment not found"},
        )

    try:
        updated = await payment_service.complete_payment(db, payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    # Create ledger entry
    await ledger_service.record_payment_completed(db, updated)

    # Update compliance record
    await compliance_service.update_compliance_on_payment(db, updated)

    return updated


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Refund a payment. Requires editor role."""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Payment not found"},
        )

    try:
        updated = await payment_service.refund_payment(db, payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    # Create negative ledger entry
    await ledger_service.record_refund(db, updated)

    return updated
