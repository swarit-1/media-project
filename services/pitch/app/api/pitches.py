import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..config import get_settings
from ..models.pitch import PitchStatus
from ..schemas.pitch import (
    PitchCreate,
    PitchUpdate,
    PitchResponse,
    PitchReview,
    PitchListResponse,
    PaginationMeta,
)
from ..schemas.assignment import AssignmentCreate
from ..services.pitch_service import PitchService
from ..services.pitch_window_service import PitchWindowService
from ..services.assignment_service import AssignmentService
from .deps import require_freelancer, require_editor, get_current_user_id

router = APIRouter()
settings = get_settings()
pitch_service = PitchService()
window_service = PitchWindowService()
assignment_service = AssignmentService()


@router.post("", response_model=PitchResponse, status_code=status.HTTP_201_CREATED)
async def create_pitch(
    data: PitchCreate,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pitch. Requires freelancer role."""
    # Check pitch window exists and is accepting pitches
    window = await window_service.get_window_by_id(db, data.pitch_window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WINDOW_NOT_FOUND", "message": "Pitch window not found"},
        )
    if not window_service.is_window_accepting_pitches(window):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "WINDOW_NOT_ACCEPTING", "message": "This pitch window is not currently accepting pitches"},
        )

    # Check if freelancer already pitched to this window
    existing = await pitch_service.get_freelancer_pitch_for_window(
        db, freelancer_id, data.pitch_window_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "DUPLICATE_PITCH", "message": "You already have a pitch in this window"},
        )

    # Check weekly pitch limit
    weekly_count = await pitch_service.count_freelancer_pitches_this_week(
        db, freelancer_id
    )
    if weekly_count >= settings.default_pitch_limit_per_week:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "WEEKLY_LIMIT_REACHED", "message": "Weekly pitch limit reached"},
        )

    pitch = await pitch_service.create_pitch(db, data, freelancer_id)
    return pitch


@router.get("/my", response_model=PitchListResponse)
async def list_my_pitches(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List pitches for the current freelancer."""
    p_status = None
    if status_filter:
        try:
            p_status = PitchStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    pitches, total = await pitch_service.list_freelancer_pitches(
        db, freelancer_id, status=p_status, page=page, per_page=per_page,
    )

    return PitchListResponse(
        results=[PitchResponse.model_validate(p) for p in pitches],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/window/{window_id}", response_model=PitchListResponse)
async def list_pitches_for_window(
    window_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """List pitches for a window. Requires editor role."""
    window = await window_service.get_window_by_id(db, window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WINDOW_NOT_FOUND", "message": "Pitch window not found"},
        )
    if window.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only view pitches for your own windows"},
        )

    p_status = None
    if status_filter:
        try:
            p_status = PitchStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    pitches, total = await pitch_service.list_pitches_for_window(
        db, window_id, status=p_status, page=page, per_page=per_page,
    )

    return PitchListResponse(
        results=[PitchResponse.model_validate(p) for p in pitches],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/{pitch_id}", response_model=PitchResponse)
async def get_pitch(
    pitch_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific pitch."""
    pitch = await pitch_service.get_pitch_by_id(db, pitch_id)
    if not pitch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch not found"},
        )
    return pitch


@router.patch("/{pitch_id}", response_model=PitchResponse)
async def update_pitch(
    pitch_id: UUID,
    data: PitchUpdate,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft pitch. Only the owning freelancer can update."""
    pitch = await pitch_service.get_pitch_by_id(db, pitch_id)
    if not pitch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch not found"},
        )
    if pitch.freelancer_id != freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only update your own pitches"},
        )
    if pitch.status != PitchStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_DRAFT", "message": "Only draft pitches can be edited"},
        )

    updated = await pitch_service.update_pitch(db, pitch, data)
    return updated


@router.post("/{pitch_id}/submit", response_model=PitchResponse)
async def submit_pitch(
    pitch_id: UUID,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Submit a draft pitch for review."""
    pitch = await pitch_service.get_pitch_by_id(db, pitch_id)
    if not pitch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch not found"},
        )
    if pitch.freelancer_id != freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only submit your own pitches"},
        )
    if pitch.status != PitchStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_DRAFT", "message": "Only draft pitches can be submitted"},
        )

    # Verify window is still accepting
    window = await window_service.get_window_by_id(db, pitch.pitch_window_id)
    if not window or not window_service.is_window_accepting_pitches(window):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "WINDOW_NOT_ACCEPTING", "message": "Pitch window is no longer accepting pitches"},
        )

    submitted = await pitch_service.submit_pitch(db, pitch)
    return submitted


@router.post("/{pitch_id}/review", response_model=PitchResponse)
async def review_pitch(
    pitch_id: UUID,
    data: PitchReview,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Accept or reject a submitted pitch. Requires editor role."""
    pitch = await pitch_service.get_pitch_by_id(db, pitch_id)
    if not pitch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch not found"},
        )
    if pitch.status != PitchStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_SUBMITTED", "message": "Only submitted pitches can be reviewed"},
        )

    # Verify editor owns the window
    window = await window_service.get_window_by_id(db, pitch.pitch_window_id)
    if not window or window.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only review pitches for your own windows"},
        )

    if data.action == "accept":
        if not data.agreed_rate or not data.rate_type or not data.deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "MISSING_FIELDS",
                    "message": "agreed_rate, rate_type, and deadline are required when accepting",
                },
            )

        accepted = await pitch_service.accept_pitch(db, pitch, data.editor_notes)

        # Create assignment
        assignment_data = AssignmentCreate(
            pitch_id=pitch.id,
            freelancer_id=pitch.freelancer_id,
            editor_id=editor_id,
            newsroom_id=window.newsroom_id,
            agreed_rate=data.agreed_rate,
            rate_type=data.rate_type,
            word_count_target=pitch.estimated_word_count,
            deadline=data.deadline,
        )
        await assignment_service.create_assignment(db, assignment_data)

        return accepted

    else:  # reject
        rejected = await pitch_service.reject_pitch(
            db, pitch, data.rejection_reason, data.editor_notes
        )
        return rejected


@router.post("/{pitch_id}/withdraw", response_model=PitchResponse)
async def withdraw_pitch(
    pitch_id: UUID,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Withdraw a pitch."""
    pitch = await pitch_service.get_pitch_by_id(db, pitch_id)
    if not pitch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch not found"},
        )
    if pitch.freelancer_id != freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only withdraw your own pitches"},
        )
    if pitch.status in (PitchStatus.ACCEPTED, PitchStatus.WITHDRAWN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_WITHDRAW", "message": "This pitch cannot be withdrawn"},
        )

    withdrawn = await pitch_service.withdraw_pitch(db, pitch)
    return withdrawn
