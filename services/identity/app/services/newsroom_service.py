from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import sys
sys.path.insert(0, "/app")
from shared.errors import NotFoundError, ConflictError, AuthorizationError

from ..models import User, Newsroom, NewsroomMembership
from ..models.user import UserRole
from ..schemas import NewsroomCreate, NewsroomUpdate, MembershipCreate


class NewsroomService:
    """Service for newsroom management."""

    async def create_newsroom(
        self,
        db: AsyncSession,
        user: User,
        data: NewsroomCreate,
    ) -> Newsroom:
        """Create a new newsroom."""
        # Verify user is an editor
        if user.role != UserRole.EDITOR:
            raise AuthorizationError("Only editors can create newsrooms")

        # Check for slug uniqueness
        existing = await self.get_newsroom_by_slug(db, data.slug)
        if existing:
            raise ConflictError("A newsroom with this slug already exists")

        # Create newsroom
        newsroom = Newsroom(
            name=data.name,
            slug=data.slug.lower(),
            domain=data.domain,
            logo_url=data.logo_url,
            cms_type=data.cms_type,
            cms_webhook_url=data.cms_webhook_url,
            payment_terms_days=data.payment_terms_days,
            style_guide_url=data.style_guide_url,
        )
        db.add(newsroom)
        await db.flush()

        # Add creator as owner
        membership = NewsroomMembership(
            newsroom_id=newsroom.id,
            user_id=user.id,
            role="owner",
            permissions=["approve_pitches", "trigger_payments", "manage_squads", "manage_members"],
        )
        db.add(membership)

        await db.flush()
        await db.refresh(newsroom)
        return newsroom

    async def get_newsroom_by_id(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
    ) -> Optional[Newsroom]:
        """Get a newsroom by ID."""
        result = await db.execute(
            select(Newsroom)
            .options(selectinload(Newsroom.memberships))
            .where(Newsroom.id == newsroom_id)
        )
        return result.scalar_one_or_none()

    async def get_newsroom_by_slug(
        self,
        db: AsyncSession,
        slug: str,
    ) -> Optional[Newsroom]:
        """Get a newsroom by slug."""
        result = await db.execute(
            select(Newsroom).where(Newsroom.slug == slug.lower())
        )
        return result.scalar_one_or_none()

    async def update_newsroom(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        user: User,
        data: NewsroomUpdate,
    ) -> Newsroom:
        """Update a newsroom."""
        newsroom = await self.get_newsroom_by_id(db, newsroom_id)
        if not newsroom:
            raise NotFoundError("Newsroom", newsroom_id)

        # Check user has permission
        await self._verify_membership_permission(db, newsroom_id, user.id, ["owner", "admin"])

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(newsroom, field, value)

        newsroom.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(newsroom)
        return newsroom

    async def add_member(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        user: User,
        data: MembershipCreate,
    ) -> NewsroomMembership:
        """Add a member to a newsroom."""
        newsroom = await self.get_newsroom_by_id(db, newsroom_id)
        if not newsroom:
            raise NotFoundError("Newsroom", newsroom_id)

        # Check user has permission to add members
        await self._verify_membership_permission(db, newsroom_id, user.id, ["owner", "admin"])

        # Check if user is already a member
        existing = await self._get_membership(db, newsroom_id, data.user_id)
        if existing:
            raise ConflictError("User is already a member of this newsroom")

        membership = NewsroomMembership(
            newsroom_id=newsroom_id,
            user_id=data.user_id,
            role=data.role,
            permissions=data.permissions,
        )
        db.add(membership)
        await db.flush()
        await db.refresh(membership)
        return membership

    async def get_user_newsrooms(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Newsroom]:
        """Get all newsrooms a user is a member of."""
        result = await db.execute(
            select(Newsroom)
            .join(NewsroomMembership)
            .where(NewsroomMembership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def _get_membership(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        user_id: UUID,
    ) -> Optional[NewsroomMembership]:
        """Get a membership record."""
        result = await db.execute(
            select(NewsroomMembership).where(
                NewsroomMembership.newsroom_id == newsroom_id,
                NewsroomMembership.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def _verify_membership_permission(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        user_id: UUID,
        allowed_roles: list[str],
    ) -> NewsroomMembership:
        """Verify user has required role in newsroom."""
        membership = await self._get_membership(db, newsroom_id, user_id)
        if not membership:
            raise AuthorizationError("You are not a member of this newsroom")
        if membership.role not in allowed_roles:
            raise AuthorizationError(f"Requires one of these roles: {', '.join(allowed_roles)}")
        return membership
