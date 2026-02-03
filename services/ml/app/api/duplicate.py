from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.duplicate import (
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    SimilarItem,
)
from ..services.duplicate_service import DuplicateService
from .deps import require_freelancer

router = APIRouter()
duplicate_service = DuplicateService()


@router.post("/check", response_model=DuplicateCheckResponse)
async def check_duplicate(
    data: DuplicateCheckRequest,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Check if a pitch is a duplicate of existing content.

    Embeds the pitch headline + summary and searches for:
    1. Similar existing pitches for the same newsroom
    2. Similar published articles in portfolio database

    Returns similarity scores and warnings.
    """
    result = await duplicate_service.check_duplicate(
        db, data.headline, data.summary, data.newsroom_id,
    )

    return DuplicateCheckResponse(
        duplicate_score=result["duplicate_score"],
        duplicate_warning=result["duplicate_warning"],
        style_match_score=result["style_match_score"],
        similar_pitches=[
            SimilarItem(**p) for p in result["similar_pitches"]
        ],
        competing_coverage=[
            SimilarItem(**c) for c in result["competing_coverage"]
        ],
    )
