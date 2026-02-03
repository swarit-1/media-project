from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.compliance import ComplianceRecordResponse, ComplianceSummary
from ..services.compliance_service import ComplianceService
from .deps import require_admin, require_freelancer

router = APIRouter()
compliance_service = ComplianceService()


@router.get("/my", response_model=ComplianceRecordResponse)
async def get_my_compliance(
    tax_year: int = Query(default_factory=lambda: datetime.now().year),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Get compliance record for the current freelancer."""
    record = await compliance_service.get_compliance_record(
        db, freelancer_id, tax_year
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "No compliance record found for this year"},
        )
    return record


@router.get("/summary", response_model=ComplianceSummary)
async def get_compliance_summary(
    tax_year: int = Query(default_factory=lambda: datetime.now().year),
    admin_id: UUID = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get compliance summary for a tax year. Requires admin role."""
    summary = await compliance_service.get_compliance_summary(db, tax_year)
    return ComplianceSummary(**summary)


@router.get("/{freelancer_id}", response_model=ComplianceRecordResponse)
async def get_freelancer_compliance(
    freelancer_id: UUID,
    tax_year: int = Query(default_factory=lambda: datetime.now().year),
    admin_id: UUID = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get compliance record for a specific freelancer. Requires admin role."""
    record = await compliance_service.get_compliance_record(
        db, freelancer_id, tax_year
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "No compliance record found"},
        )
    return record
