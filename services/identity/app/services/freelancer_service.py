from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import sys
sys.path.insert(0, "/app")
from shared.errors import NotFoundError, AuthorizationError

from ..models import User, FreelancerProfile
from ..models.user import UserRole
from ..schemas import FreelancerProfileUpdate, AvailabilityUpdate


class FreelancerService:
    """Service for freelancer profile management."""

    async def get_profile_by_id(
        self,
        db: AsyncSession,
        profile_id: UUID,
    ) -> Optional[FreelancerProfile]:
        """Get a freelancer profile by ID."""
        result = await db.execute(
            select(FreelancerProfile)
            .options(selectinload(FreelancerProfile.user))
            .where(FreelancerProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[FreelancerProfile]:
        """Get a freelancer profile by user ID."""
        result = await db.execute(
            select(FreelancerProfile)
            .options(selectinload(FreelancerProfile.user))
            .where(FreelancerProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: FreelancerProfileUpdate,
    ) -> FreelancerProfile:
        """Update a freelancer's profile."""
        profile = await self.get_profile_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError("FreelancerProfile", user_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(profile)
        return profile

    async def update_availability(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: AvailabilityUpdate,
    ) -> FreelancerProfile:
        """Update a freelancer's availability status."""
        profile = await self.get_profile_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError("FreelancerProfile", user_id)

        profile.availability_status = data.availability_status
        if data.weekly_capacity_hours is not None:
            profile.weekly_capacity_hours = data.weekly_capacity_hours

        profile.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(profile)
        return profile

    def verify_freelancer_role(self, user: User) -> None:
        """Verify that the user is a freelancer."""
        if user.role != UserRole.FREELANCER:
            raise AuthorizationError("This action requires a freelancer account")
