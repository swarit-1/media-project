import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.squad import (
    SquadTemplate,
    SquadInstance,
    SquadInstanceStatus,
    SquadMember,
    SquadMemberStatus,
)
from ..schemas.squad import (
    SquadTemplateCreate,
    SquadTemplateUpdate,
    SquadInstanceCreate,
    SquadMemberInvite,
)

logger = logging.getLogger(__name__)


class SquadService:
    """Service for managing squad templates, instances, and members."""

    # --- Template Methods ---

    async def create_template(
        self,
        db: AsyncSession,
        data: SquadTemplateCreate,
        newsroom_id: UUID,
        editor_id: UUID,
    ) -> SquadTemplate:
        """Create a new squad template."""
        template = SquadTemplate(
            newsroom_id=newsroom_id,
            created_by=editor_id,
            name=data.name,
            description=data.description,
            required_beats=data.required_beats,
            required_roles=data.required_roles,
            min_members=data.min_members,
            max_members=data.max_members,
            min_trust_score=data.min_trust_score,
            preferred_tiers=data.preferred_tiers,
        )
        db.add(template)
        await db.flush()
        await db.refresh(template)
        return template

    async def get_template_by_id(
        self, db: AsyncSession, template_id: UUID
    ) -> Optional[SquadTemplate]:
        """Get a squad template by ID."""
        result = await db.execute(
            select(SquadTemplate).where(SquadTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[SquadTemplate], int]:
        """List squad templates for a newsroom."""
        query = select(SquadTemplate).where(
            SquadTemplate.newsroom_id == newsroom_id
        )
        count_query = select(func.count(SquadTemplate.id)).where(
            SquadTemplate.newsroom_id == newsroom_id
        )

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(SquadTemplate.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        templates = list(result.scalars().all())
        return templates, total

    async def update_template(
        self,
        db: AsyncSession,
        template: SquadTemplate,
        data: SquadTemplateUpdate,
    ) -> SquadTemplate:
        """Update a squad template."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        await db.flush()
        await db.refresh(template)
        return template

    async def delete_template(
        self, db: AsyncSession, template: SquadTemplate
    ) -> None:
        """Delete a squad template."""
        await db.delete(template)
        await db.flush()

    # --- Instance Methods ---

    async def create_instance(
        self,
        db: AsyncSession,
        data: SquadInstanceCreate,
        template: SquadTemplate,
        editor_id: UUID,
    ) -> SquadInstance:
        """Create a squad instance from a template."""
        instance = SquadInstance(
            template_id=template.id,
            newsroom_id=template.newsroom_id,
            created_by=editor_id,
            name=data.name,
            description=data.description,
            project_brief=data.project_brief,
            status=SquadInstanceStatus.FORMING,
        )
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def get_instance_by_id(
        self, db: AsyncSession, instance_id: UUID
    ) -> Optional[SquadInstance]:
        """Get a squad instance by ID with members loaded."""
        result = await db.execute(
            select(SquadInstance)
            .options(selectinload(SquadInstance.members))
            .where(SquadInstance.id == instance_id)
        )
        return result.scalar_one_or_none()

    async def list_instances(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        status: Optional[SquadInstanceStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[SquadInstance], int]:
        """List squad instances for a newsroom."""
        query = select(SquadInstance).where(
            SquadInstance.newsroom_id == newsroom_id
        )
        count_query = select(func.count(SquadInstance.id)).where(
            SquadInstance.newsroom_id == newsroom_id
        )

        if status:
            query = query.where(SquadInstance.status == status)
            count_query = count_query.where(SquadInstance.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.options(selectinload(SquadInstance.members))
        query = query.order_by(SquadInstance.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        instances = list(result.scalars().all())
        return instances, total

    async def activate_instance(
        self, db: AsyncSession, instance: SquadInstance
    ) -> SquadInstance:
        """Activate a squad instance (all minimum slots filled)."""
        if instance.status != SquadInstanceStatus.FORMING:
            raise ValueError(
                f"Cannot activate: squad is {instance.status.value}, expected forming"
            )

        accepted_count = sum(
            1 for m in instance.members if m.status == SquadMemberStatus.ACCEPTED
        )
        template = await self.get_template_by_id(db, instance.template_id)
        if template and accepted_count < template.min_members:
            raise ValueError(
                f"Cannot activate: need at least {template.min_members} accepted members, have {accepted_count}"
            )

        instance.status = SquadInstanceStatus.ACTIVE
        instance.activated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def complete_instance(
        self, db: AsyncSession, instance: SquadInstance
    ) -> SquadInstance:
        """Mark a squad instance as completed."""
        if instance.status != SquadInstanceStatus.ACTIVE:
            raise ValueError(
                f"Cannot complete: squad is {instance.status.value}, expected active"
            )
        instance.status = SquadInstanceStatus.COMPLETED
        instance.completed_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def disband_instance(
        self, db: AsyncSession, instance: SquadInstance
    ) -> SquadInstance:
        """Disband a squad instance."""
        if instance.status in (
            SquadInstanceStatus.COMPLETED,
            SquadInstanceStatus.DISBANDED,
        ):
            raise ValueError(f"Cannot disband: squad is already {instance.status.value}")

        instance.status = SquadInstanceStatus.DISBANDED
        instance.completed_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(instance)
        return instance

    # --- Member Methods ---

    async def invite_member(
        self,
        db: AsyncSession,
        instance: SquadInstance,
        data: SquadMemberInvite,
        invited_by: UUID,
    ) -> SquadMember:
        """Invite a freelancer to a squad."""
        if instance.status != SquadInstanceStatus.FORMING:
            raise ValueError(
                f"Cannot invite: squad is {instance.status.value}, expected forming"
            )

        # Check if freelancer is already in the squad
        existing = await db.execute(
            select(SquadMember).where(
                SquadMember.squad_id == instance.id,
                SquadMember.freelancer_id == data.freelancer_id,
                SquadMember.status.in_([
                    SquadMemberStatus.INVITED,
                    SquadMemberStatus.ACCEPTED,
                ]),
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Freelancer is already invited or a member of this squad")

        member = SquadMember(
            squad_id=instance.id,
            freelancer_id=data.freelancer_id,
            role=data.role,
            beats=data.beats,
            invited_by=invited_by,
            invitation_message=data.invitation_message,
            status=SquadMemberStatus.INVITED,
        )
        db.add(member)
        await db.flush()
        await db.refresh(member)
        return member

    async def respond_to_invitation(
        self,
        db: AsyncSession,
        member: SquadMember,
        action: str,
    ) -> SquadMember:
        """Accept or decline a squad invitation."""
        if member.status != SquadMemberStatus.INVITED:
            raise ValueError(
                f"Cannot respond: invitation is {member.status.value}, expected invited"
            )

        now = datetime.now(timezone.utc)
        member.responded_at = now

        if action == "accept":
            member.status = SquadMemberStatus.ACCEPTED
        elif action == "decline":
            member.status = SquadMemberStatus.DECLINED

        await db.flush()
        await db.refresh(member)
        return member

    async def remove_member(
        self, db: AsyncSession, member: SquadMember
    ) -> SquadMember:
        """Remove a member from a squad."""
        member.status = SquadMemberStatus.REMOVED
        member.responded_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(member)
        return member

    async def get_member_by_id(
        self, db: AsyncSession, member_id: UUID
    ) -> Optional[SquadMember]:
        """Get a squad member by ID."""
        result = await db.execute(
            select(SquadMember).where(SquadMember.id == member_id)
        )
        return result.scalar_one_or_none()

    async def get_freelancer_invitations(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        status: Optional[SquadMemberStatus] = None,
    ) -> list[SquadMember]:
        """Get all squad invitations for a freelancer."""
        query = select(SquadMember).where(
            SquadMember.freelancer_id == freelancer_id
        )
        if status:
            query = query.where(SquadMember.status == status)
        query = query.order_by(SquadMember.invited_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())
