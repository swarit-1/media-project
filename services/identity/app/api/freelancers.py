from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db
from shared.errors import NotFoundError

from ..models import User
from ..schemas import (
    FreelancerProfileResponse,
    FreelancerProfileUpdate,
    AvailabilityUpdate,
)
from ..services import FreelancerService
from .deps import get_current_freelancer

router = APIRouter()


@router.get("/{freelancer_id}", response_model=FreelancerProfileResponse)
async def get_freelancer_profile(
    freelancer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> FreelancerProfileResponse:
    """
    Get a freelancer's public profile.

    Returns the freelancer's profile information visible to editors.
    """
    freelancer_service = FreelancerService()
    profile = await freelancer_service.get_profile_by_id(db, freelancer_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Freelancer not found"},
        )

    return FreelancerProfileResponse.model_validate(profile)


@router.patch("/me", response_model=FreelancerProfileResponse)
async def update_freelancer_profile(
    data: FreelancerProfileUpdate,
    current_user: User = Depends(get_current_freelancer),
    db: AsyncSession = Depends(get_db),
) -> FreelancerProfileResponse:
    """
    Update current freelancer's profile.

    Updates the authenticated freelancer's profile information.
    """
    freelancer_service = FreelancerService()
    try:
        profile = await freelancer_service.update_profile(db, current_user.id, data)
        await db.commit()
        return FreelancerProfileResponse.model_validate(profile)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.post("/me/availability", response_model=FreelancerProfileResponse)
async def update_availability(
    data: AvailabilityUpdate,
    current_user: User = Depends(get_current_freelancer),
    db: AsyncSession = Depends(get_db),
) -> FreelancerProfileResponse:
    """
    Update freelancer's availability status.

    Sets the freelancer's availability and weekly capacity.
    """
    freelancer_service = FreelancerService()
    try:
        profile = await freelancer_service.update_availability(db, current_user.id, data)
        await db.commit()
        return FreelancerProfileResponse.model_validate(profile)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
