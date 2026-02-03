from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.style import (
    StyleFingerprintResponse,
    StyleMatchRequest,
    StyleMatchResult,
)
from ..services.style_service import StyleService
from .deps import require_freelancer, require_editor, get_current_user_id

router = APIRouter()
style_service = StyleService()


@router.post("/compute", response_model=StyleFingerprintResponse)
async def compute_style_fingerprint(
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Compute/update style fingerprint for the current freelancer.

    Analyzes all verified portfolio items and generates aggregate
    style metrics and a 384-dimensional embedding.
    """
    fingerprint = await style_service.compute_fingerprint(
        db, freelancer_id, "freelancer"
    )
    if not fingerprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NO_PORTFOLIO",
                "message": "No verified portfolio items found. Add and verify portfolio URLs first.",
            },
        )
    return fingerprint


@router.get("/fingerprint/{entity_type}/{entity_id}", response_model=StyleFingerprintResponse)
async def get_style_fingerprint(
    entity_type: str,
    entity_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a style fingerprint for a freelancer or newsroom."""
    if entity_type not in ("freelancer", "newsroom"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TYPE", "message": "Entity type must be 'freelancer' or 'newsroom'"},
        )

    fingerprint = await style_service.get_fingerprint(db, entity_id, entity_type)
    if not fingerprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Style fingerprint not found"},
        )
    return fingerprint


@router.post("/match", response_model=list[StyleMatchResult])
async def find_style_matches(
    data: StyleMatchRequest,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Find freelancers whose writing style matches a newsroom.

    Uses pgvector cosine similarity on 384-dim style embeddings.
    Requires editor role.
    """
    matches = await style_service.find_style_matches(
        db, data.newsroom_id, limit=data.limit, min_score=data.min_score,
    )

    return [
        StyleMatchResult(
            freelancer_id=m["freelancer_id"],
            display_name="",  # Would be populated from freelancer profile
            style_score=m["style_score"],
        )
        for m in matches
    ]
