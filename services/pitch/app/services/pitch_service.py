from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.pitch import Pitch, PitchStatus
from ..models.pitch_window import PitchWindow
from ..schemas.pitch import PitchCreate, PitchUpdate


class PitchService:
    """Service for managing pitches."""

    async def create_pitch(
        self,
        db: AsyncSession,
        data: PitchCreate,
        freelancer_id: UUID,
    ) -> Pitch:
        """Create a new pitch."""
        pitch = Pitch(
            pitch_window_id=data.pitch_window_id,
            freelancer_id=freelancer_id,
            headline=data.headline,
            summary=data.summary,
            approach=data.approach,
            estimated_word_count=data.estimated_word_count,
            proposed_rate=data.proposed_rate,
            proposed_rate_type=data.proposed_rate_type,
            estimated_delivery_days=data.estimated_delivery_days,
            status=PitchStatus.DRAFT,
        )
        db.add(pitch)
        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def get_pitch_by_id(
        self, db: AsyncSession, pitch_id: UUID
    ) -> Optional[Pitch]:
        """Get a pitch by ID."""
        result = await db.execute(
            select(Pitch).where(Pitch.id == pitch_id)
        )
        return result.scalar_one_or_none()

    async def get_freelancer_pitch_for_window(
        self, db: AsyncSession, freelancer_id: UUID, window_id: UUID
    ) -> Optional[Pitch]:
        """Check if a freelancer already has a pitch in a window."""
        result = await db.execute(
            select(Pitch).where(
                and_(
                    Pitch.freelancer_id == freelancer_id,
                    Pitch.pitch_window_id == window_id,
                    Pitch.status != PitchStatus.WITHDRAWN,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_pitches_for_window(
        self,
        db: AsyncSession,
        window_id: UUID,
        status: Optional[PitchStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Pitch], int]:
        """List pitches for a specific window."""
        query = select(Pitch).where(Pitch.pitch_window_id == window_id)
        count_query = select(func.count(Pitch.id)).where(
            Pitch.pitch_window_id == window_id
        )

        if status:
            query = query.where(Pitch.status == status)
            count_query = count_query.where(Pitch.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Pitch.submitted_at.desc().nullslast(), Pitch.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        pitches = list(result.scalars().all())

        return pitches, total

    async def list_freelancer_pitches(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        status: Optional[PitchStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Pitch], int]:
        """List all pitches by a freelancer."""
        query = select(Pitch).where(Pitch.freelancer_id == freelancer_id)
        count_query = select(func.count(Pitch.id)).where(
            Pitch.freelancer_id == freelancer_id
        )

        if status:
            query = query.where(Pitch.status == status)
            count_query = count_query.where(Pitch.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Pitch.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        pitches = list(result.scalars().all())

        return pitches, total

    async def update_pitch(
        self,
        db: AsyncSession,
        pitch: Pitch,
        data: PitchUpdate,
    ) -> Pitch:
        """Update a draft pitch."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pitch, field, value)
        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def submit_pitch(
        self, db: AsyncSession, pitch: Pitch
    ) -> Pitch:
        """Submit a draft pitch."""
        pitch.status = PitchStatus.SUBMITTED
        pitch.submitted_at = datetime.now(timezone.utc)

        # Increment pitch window counter
        await db.execute(
            PitchWindow.__table__.update()
            .where(PitchWindow.id == pitch.pitch_window_id)
            .values(current_pitch_count=PitchWindow.current_pitch_count + 1)
        )

        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def accept_pitch(
        self,
        db: AsyncSession,
        pitch: Pitch,
        editor_notes: Optional[str] = None,
    ) -> Pitch:
        """Accept a submitted pitch."""
        pitch.status = PitchStatus.ACCEPTED
        pitch.reviewed_at = datetime.now(timezone.utc)
        if editor_notes:
            pitch.editor_notes = editor_notes
        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def reject_pitch(
        self,
        db: AsyncSession,
        pitch: Pitch,
        rejection_reason: Optional[str] = None,
        editor_notes: Optional[str] = None,
    ) -> Pitch:
        """Reject a submitted pitch."""
        pitch.status = PitchStatus.REJECTED
        pitch.reviewed_at = datetime.now(timezone.utc)
        if rejection_reason:
            pitch.rejection_reason = rejection_reason
        if editor_notes:
            pitch.editor_notes = editor_notes
        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def withdraw_pitch(
        self, db: AsyncSession, pitch: Pitch
    ) -> Pitch:
        """Withdraw a pitch."""
        pitch.status = PitchStatus.WITHDRAWN

        # Decrement pitch window counter if it was submitted
        if pitch.submitted_at:
            await db.execute(
                PitchWindow.__table__.update()
                .where(PitchWindow.id == pitch.pitch_window_id)
                .values(current_pitch_count=PitchWindow.current_pitch_count - 1)
            )

        await db.flush()
        await db.refresh(pitch)
        return pitch

    async def count_freelancer_pitches_this_week(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> int:
        """Count pitches submitted by a freelancer in the current week."""
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        result = await db.execute(
            select(func.count(Pitch.id)).where(
                and_(
                    Pitch.freelancer_id == freelancer_id,
                    Pitch.submitted_at >= week_start,
                    Pitch.status != PitchStatus.WITHDRAWN,
                )
            )
        )
        return result.scalar() or 0
