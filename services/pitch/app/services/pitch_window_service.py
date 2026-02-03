import math
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.pitch_window import PitchWindow, PitchWindowStatus
from ..schemas.pitch_window import PitchWindowCreate, PitchWindowUpdate


class PitchWindowService:
    """Service for managing pitch windows."""

    async def create_window(
        self,
        db: AsyncSession,
        data: PitchWindowCreate,
        editor_id: UUID,
        newsroom_id: UUID,
    ) -> PitchWindow:
        """Create a new pitch window."""
        window = PitchWindow(
            newsroom_id=newsroom_id,
            editor_id=editor_id,
            title=data.title,
            description=data.description,
            beats=data.beats,
            requirements=data.requirements,
            budget_min=data.budget_min,
            budget_max=data.budget_max,
            rate_type=data.rate_type,
            max_pitches=data.max_pitches,
            opens_at=data.opens_at,
            closes_at=data.closes_at,
            status=PitchWindowStatus.DRAFT,
        )
        db.add(window)
        await db.flush()
        await db.refresh(window)
        return window

    async def get_window_by_id(
        self, db: AsyncSession, window_id: UUID
    ) -> Optional[PitchWindow]:
        """Get a pitch window by ID."""
        result = await db.execute(
            select(PitchWindow).where(PitchWindow.id == window_id)
        )
        return result.scalar_one_or_none()

    async def list_windows(
        self,
        db: AsyncSession,
        newsroom_id: Optional[UUID] = None,
        status: Optional[PitchWindowStatus] = None,
        beats: Optional[list[str]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PitchWindow], int]:
        """List pitch windows with optional filters."""
        query = select(PitchWindow)
        count_query = select(func.count(PitchWindow.id))

        if newsroom_id:
            query = query.where(PitchWindow.newsroom_id == newsroom_id)
            count_query = count_query.where(PitchWindow.newsroom_id == newsroom_id)

        if status:
            query = query.where(PitchWindow.status == status)
            count_query = count_query.where(PitchWindow.status == status)

        if beats:
            query = query.where(PitchWindow.beats.overlap(beats))
            count_query = count_query.where(PitchWindow.beats.overlap(beats))

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(PitchWindow.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        windows = list(result.scalars().all())

        return windows, total

    async def update_window(
        self,
        db: AsyncSession,
        window: PitchWindow,
        data: PitchWindowUpdate,
    ) -> PitchWindow:
        """Update a pitch window."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(window, field, value)
        await db.flush()
        await db.refresh(window)
        return window

    async def open_window(
        self, db: AsyncSession, window: PitchWindow
    ) -> PitchWindow:
        """Open a pitch window for submissions."""
        window.status = PitchWindowStatus.OPEN
        await db.flush()
        await db.refresh(window)
        return window

    async def close_window(
        self, db: AsyncSession, window: PitchWindow
    ) -> PitchWindow:
        """Close a pitch window."""
        window.status = PitchWindowStatus.CLOSED
        await db.flush()
        await db.refresh(window)
        return window

    async def cancel_window(
        self, db: AsyncSession, window: PitchWindow
    ) -> PitchWindow:
        """Cancel a pitch window."""
        window.status = PitchWindowStatus.CANCELLED
        await db.flush()
        await db.refresh(window)
        return window

    def is_window_accepting_pitches(self, window: PitchWindow) -> bool:
        """Check if a window is currently accepting pitches."""
        now = datetime.now(timezone.utc)
        return (
            window.status == PitchWindowStatus.OPEN
            and window.opens_at <= now <= window.closes_at
            and window.current_pitch_count < window.max_pitches
        )
