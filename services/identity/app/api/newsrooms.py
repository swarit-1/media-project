from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db
from shared.errors import NotFoundError, ConflictError, AuthorizationError

from ..models import User
from ..schemas import (
    NewsroomCreate,
    NewsroomResponse,
    NewsroomUpdate,
    MembershipCreate,
    MembershipResponse,
)
from ..services import NewsroomService
from .deps import get_current_editor, get_current_active_user

router = APIRouter()


@router.post("", response_model=NewsroomResponse, status_code=status.HTTP_201_CREATED)
async def create_newsroom(
    data: NewsroomCreate,
    current_user: User = Depends(get_current_editor),
    db: AsyncSession = Depends(get_db),
) -> NewsroomResponse:
    """
    Create a new newsroom.

    Creates a newsroom and adds the creator as owner.
    Only editors can create newsrooms.
    """
    newsroom_service = NewsroomService()
    try:
        newsroom = await newsroom_service.create_newsroom(db, current_user, data)
        await db.commit()
        return NewsroomResponse.model_validate(newsroom)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message},
        )


@router.get("/{newsroom_id}", response_model=NewsroomResponse)
async def get_newsroom(
    newsroom_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> NewsroomResponse:
    """
    Get a newsroom by ID.

    Returns the newsroom's public information.
    """
    newsroom_service = NewsroomService()
    newsroom = await newsroom_service.get_newsroom_by_id(db, newsroom_id)

    if not newsroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Newsroom not found"},
        )

    return NewsroomResponse.model_validate(newsroom)


@router.patch("/{newsroom_id}", response_model=NewsroomResponse)
async def update_newsroom(
    newsroom_id: UUID,
    data: NewsroomUpdate,
    current_user: User = Depends(get_current_editor),
    db: AsyncSession = Depends(get_db),
) -> NewsroomResponse:
    """
    Update a newsroom.

    Requires owner or admin role in the newsroom.
    """
    newsroom_service = NewsroomService()
    try:
        newsroom = await newsroom_service.update_newsroom(db, newsroom_id, current_user, data)
        await db.commit()
        return NewsroomResponse.model_validate(newsroom)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message},
        )


@router.post("/{newsroom_id}/members", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_newsroom_member(
    newsroom_id: UUID,
    data: MembershipCreate,
    current_user: User = Depends(get_current_editor),
    db: AsyncSession = Depends(get_db),
) -> MembershipResponse:
    """
    Add a member to a newsroom.

    Requires owner or admin role in the newsroom.
    """
    newsroom_service = NewsroomService()
    try:
        membership = await newsroom_service.add_member(db, newsroom_id, current_user, data)
        await db.commit()
        return MembershipResponse.model_validate(membership)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message},
        )
