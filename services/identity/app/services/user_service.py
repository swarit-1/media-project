from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.auth import hash_password
from shared.errors import NotFoundError, ConflictError, ValidationError

from ..models import User, FreelancerProfile, EditorProfile
from ..models.user import UserRole, UserStatus
from ..schemas import UserCreate, UserUpdate


class UserService:
    """Service for user management."""

    async def create_user(
        self,
        db: AsyncSession,
        data: UserCreate,
    ) -> User:
        """Create a new user with appropriate profile."""
        # Check for existing user
        existing = await self.get_user_by_email(db, data.email)
        if existing:
            raise ConflictError("A user with this email already exists")

        # Create user
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role=UserRole(data.role),
            status=UserStatus.ACTIVE,  # For MVP, auto-activate
        )
        db.add(user)
        await db.flush()

        # Create appropriate profile
        if data.role == "freelancer":
            profile = FreelancerProfile(
                user_id=user.id,
                display_name=data.display_name,
            )
            db.add(profile)
        elif data.role == "editor":
            profile = EditorProfile(
                user_id=user.id,
                display_name=data.display_name,
            )
            db.add(profile)

        await db.flush()
        await db.refresh(user)
        return user

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: UserUpdate,
    ) -> User:
        """Update a user's information."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            # Check if new email is already taken
            existing = await self.get_user_by_email(db, update_data["email"])
            if existing and existing.id != user_id:
                raise ConflictError("A user with this email already exists")
            update_data["email"] = update_data["email"].lower()

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(user)
        return user

    async def update_last_login(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> None:
        """Update the user's last login timestamp."""
        user = await self.get_user_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await db.flush()
