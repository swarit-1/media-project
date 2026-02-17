from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import sys
sys.path.insert(0, "/app")
from shared.db import get_db
from shared.errors import ConflictError, NotFoundError

from ..models import User
from ..schemas import UserResponse, UserUpdate
from ..services import UserService
from .deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get current user's profile.

    Returns the authenticated user's basic information including display_name.
    """
    stmt = select(User).where(User.id == current_user.id).options(
        selectinload(User.freelancer_profile),
        selectinload(User.editor_profile),
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    display_name = None
    if user.freelancer_profile:
        display_name = user.freelancer_profile.display_name
    elif user.editor_profile:
        display_name = user.editor_profile.display_name

    resp = UserResponse.model_validate(user)
    resp.display_name = display_name
    return resp


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update current user's profile.

    Updates the authenticated user's basic information.
    """
    user_service = UserService()
    try:
        user = await user_service.update_user(db, current_user.id, data)
        await db.commit()
        return UserResponse.model_validate(user)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
