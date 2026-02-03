import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..models.assignment import AssignmentStatus
from ..schemas.assignment import (
    AssignmentResponse,
    AssignmentUpdate,
    AssignmentStatusUpdate,
)
from ..schemas.pitch import PaginationMeta
from ..services.assignment_service import AssignmentService
from .deps import require_freelancer, require_editor, get_current_user_role, require_newsroom_id

router = APIRouter()
assignment_service = AssignmentService()


@router.get("/my", response_model=dict)
async def list_my_assignments(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List assignments for the current freelancer."""
    a_status = None
    if status_filter:
        try:
            a_status = AssignmentStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    assignments, total = await assignment_service.list_freelancer_assignments(
        db, freelancer_id, status=a_status, page=page, per_page=per_page,
    )

    return {
        "results": [AssignmentResponse.model_validate(a) for a in assignments],
        "pagination": PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ).model_dump(),
    }


@router.get("/newsroom", response_model=dict)
async def list_newsroom_assignments(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """List assignments for a newsroom. Requires editor role."""
    a_status = None
    if status_filter:
        try:
            a_status = AssignmentStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    assignments, total = await assignment_service.list_newsroom_assignments(
        db, newsroom_id, status=a_status, page=page, per_page=per_page,
    )

    return {
        "results": [AssignmentResponse.model_validate(a) for a in assignments],
        "pagination": PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ).model_dump(),
    }


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific assignment."""
    assignment = await assignment_service.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Assignment not found"},
        )
    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    data: AssignmentUpdate,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update assignment details. Requires editor role."""
    assignment = await assignment_service.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Assignment not found"},
        )
    if assignment.editor_id != editor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "You can only update your own assignments"},
        )

    updated = await assignment_service.update_assignment(db, assignment, data)
    return updated


@router.post("/{assignment_id}/status", response_model=AssignmentResponse)
async def update_assignment_status(
    assignment_id: UUID,
    data: AssignmentStatusUpdate,
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    """Update assignment status. Validates state machine transitions."""
    user_id, role = user_info

    assignment = await assignment_service.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Assignment not found"},
        )

    # Validate who can make which transitions
    freelancer_transitions = {"in_progress", "submitted"}
    editor_transitions = {"revision_requested", "approved", "killed"}

    if role == "freelancer":
        if assignment.freelancer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "NOT_OWNER", "message": "You can only update your own assignments"},
            )
        if data.status not in freelancer_transitions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN_TRANSITION", "message": "Freelancers cannot make this status change"},
            )
    elif role == "editor":
        if assignment.editor_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "NOT_OWNER", "message": "You can only update assignments you manage"},
            )
        if data.status not in editor_transitions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN_TRANSITION", "message": "Editors cannot make this status change"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "UNAUTHORIZED", "message": "Invalid role for this action"},
        )

    try:
        updated = await assignment_service.update_status(db, assignment, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TRANSITION", "message": str(e)},
        )

    return updated
