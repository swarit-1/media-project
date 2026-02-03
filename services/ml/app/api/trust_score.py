from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.trust_score import (
    TrustScoreResponse,
    TrustScoreComponents,
    TrustScoreComputeRequest,
)
from ..services.trust_score_service import TrustScoreService
from .deps import require_freelancer, get_current_user_id

router = APIRouter()
trust_score_service = TrustScoreService()


@router.post("/compute", response_model=TrustScoreResponse)
async def compute_trust_score(
    data: TrustScoreComputeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Compute trust score for a freelancer.

    Uses a weighted composite model combining:
    - Identity verification (15%)
    - Portfolio quality (20%)
    - On-time delivery (20%)
    - Acceptance rate (15%)
    - Editor ratings (15%)
    - Platform tenure (5%)
    - Response time (10%)

    Applies exponential smoothing to prevent score volatility.
    """
    result = await trust_score_service.compute_trust_score(
        db, data.freelancer_id,
    )

    return TrustScoreResponse(
        freelancer_id=result["freelancer_id"],
        trust_score=result["trust_score"],
        previous_score=result["previous_score"],
        components=TrustScoreComponents(**result["components"]),
        computed_at=result["computed_at"],
    )


@router.get("/my", response_model=TrustScoreResponse)
async def get_my_trust_score(
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Get trust score for the current freelancer."""
    result = await trust_score_service.compute_trust_score(
        db, freelancer_id,
    )

    return TrustScoreResponse(
        freelancer_id=result["freelancer_id"],
        trust_score=result["trust_score"],
        previous_score=result["previous_score"],
        components=TrustScoreComponents(**result["components"]),
        computed_at=result["computed_at"],
    )
