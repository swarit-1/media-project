import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..models.pitch_window import PitchWindowStatus
from ..schemas.pitch_window import (
    PitchWindowCreate,
    PitchWindowUpdate,
    PitchWindowResponse,
    PitchWindowListResponse,
    PaginationMeta,
)
from ..services.pitch_window_service import PitchWindowService
from .deps import require_editor, require_newsroom_id, get_current_user_id

router = APIRouter()
window_service = PitchWindowService()


@router.post("", response_model=PitchWindowResponse, status_code=status.HTTP_201_CREATED)
async def create_pitch_window(
    data: PitchWindowCreate,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pitch window. Requires editor role."""
    if data.closes_at <= data.opens_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_DATES", "message": "closes_at must be after opens_at"},
        )

    window = await window_service.create_window(db, data, editor_id, newsroom_id)
    return window


@router.get("", response_model=PitchWindowListResponse)
async def list_pitch_windows(
    newsroom_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    beats: Optional[str] = Query(None, description="Comma-separated beats"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List pitch windows with optional filters."""
    pw_status = None
    if status_filter:
        try:
            pw_status = PitchWindowStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    beats_list = beats.split(",") if beats else None

    windows, total = await window_service.list_windows(
        db, newsroom_id=newsroom_id, status=pw_status, beats=beats_list,
        page=page, per_page=per_page,
    )

    return PitchWindowListResponse(
        results=[PitchWindowResponse.model_validate(w) for w in windows],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/{window_id}", response_model=PitchWindowResponse)
async def get_pitch_window(
    window_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific pitch window."""
    window = await window_service.get_window_by_id(db, window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch window not found"},
        )
    return window


@router.patch("/{window_id}", response_model=PitchWindowResponse)
async def update_pitch_window(
    window_id: UUID,
    data: PitchWindowUpdate,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update a pitch window. Only the creating editor can update."""
    window = await window_service.get_window_by_id(db, window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch window not found"},
        )
    if window.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Only the creating editor can update this window"},
        )
    if window.status not in (PitchWindowStatus.DRAFT, PitchWindowStatus.OPEN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "WINDOW_NOT_EDITABLE", "message": "Closed or cancelled windows cannot be edited"},
        )

    updated = await window_service.update_window(db, window, data)
    return updated


@router.post("/{window_id}/open", response_model=PitchWindowResponse)
async def open_pitch_window(
    window_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Open a draft pitch window for submissions."""
    window = await window_service.get_window_by_id(db, window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch window not found"},
        )
    if window.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Only the creating editor can open this window"},
        )
    if window.status != PitchWindowStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATUS", "message": "Only draft windows can be opened"},
        )

    opened = await window_service.open_window(db, window)
    return opened


@router.post("/{window_id}/close", response_model=PitchWindowResponse)
async def close_pitch_window(
    window_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Close an open pitch window."""
    window = await window_service.get_window_by_id(db, window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Pitch window not found"},
        )
    if window.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Only the creating editor can close this window"},
        )
    if window.status != PitchWindowStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATUS", "message": "Only open windows can be closed"},
        )

    closed = await window_service.close_window(db, window)
    return closed
