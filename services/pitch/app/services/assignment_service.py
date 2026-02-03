from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.assignment import Assignment, AssignmentStatus
from ..schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentStatusUpdate


class AssignmentService:
    """Service for managing assignments."""

    async def create_assignment(
        self,
        db: AsyncSession,
        data: AssignmentCreate,
    ) -> Assignment:
        """Create a new assignment from an accepted pitch."""
        assignment = Assignment(
            pitch_id=data.pitch_id,
            freelancer_id=data.freelancer_id,
            editor_id=data.editor_id,
            newsroom_id=data.newsroom_id,
            agreed_rate=data.agreed_rate,
            rate_type=data.rate_type,
            word_count_target=data.word_count_target,
            deadline=data.deadline,
            kill_fee_percentage=data.kill_fee_percentage,
            status=AssignmentStatus.ASSIGNED,
        )
        db.add(assignment)
        await db.flush()
        await db.refresh(assignment)
        return assignment

    async def get_assignment_by_id(
        self, db: AsyncSession, assignment_id: UUID
    ) -> Optional[Assignment]:
        """Get an assignment by ID."""
        result = await db.execute(
            select(Assignment).where(Assignment.id == assignment_id)
        )
        return result.scalar_one_or_none()

    async def get_assignment_by_pitch_id(
        self, db: AsyncSession, pitch_id: UUID
    ) -> Optional[Assignment]:
        """Get an assignment by pitch ID."""
        result = await db.execute(
            select(Assignment).where(Assignment.pitch_id == pitch_id)
        )
        return result.scalar_one_or_none()

    async def list_freelancer_assignments(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        status: Optional[AssignmentStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Assignment], int]:
        """List assignments for a freelancer."""
        query = select(Assignment).where(Assignment.freelancer_id == freelancer_id)
        count_query = select(func.count(Assignment.id)).where(
            Assignment.freelancer_id == freelancer_id
        )

        if status:
            query = query.where(Assignment.status == status)
            count_query = count_query.where(Assignment.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Assignment.deadline.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        assignments = list(result.scalars().all())

        return assignments, total

    async def list_newsroom_assignments(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        status: Optional[AssignmentStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Assignment], int]:
        """List assignments for a newsroom."""
        query = select(Assignment).where(Assignment.newsroom_id == newsroom_id)
        count_query = select(func.count(Assignment.id)).where(
            Assignment.newsroom_id == newsroom_id
        )

        if status:
            query = query.where(Assignment.status == status)
            count_query = count_query.where(Assignment.status == status)

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Assignment.deadline.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        assignments = list(result.scalars().all())

        return assignments, total

    async def update_assignment(
        self,
        db: AsyncSession,
        assignment: Assignment,
        data: AssignmentUpdate,
    ) -> Assignment:
        """Update assignment details."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assignment, field, value)
        await db.flush()
        await db.refresh(assignment)
        return assignment

    async def update_status(
        self,
        db: AsyncSession,
        assignment: Assignment,
        data: AssignmentStatusUpdate,
    ) -> Assignment:
        """Update assignment status with state machine validation."""
        new_status = AssignmentStatus(data.status)

        # Validate state transitions
        valid_transitions = {
            AssignmentStatus.ASSIGNED: [AssignmentStatus.IN_PROGRESS, AssignmentStatus.KILLED],
            AssignmentStatus.IN_PROGRESS: [AssignmentStatus.SUBMITTED, AssignmentStatus.KILLED],
            AssignmentStatus.SUBMITTED: [
                AssignmentStatus.REVISION_REQUESTED,
                AssignmentStatus.APPROVED,
                AssignmentStatus.KILLED,
            ],
            AssignmentStatus.REVISION_REQUESTED: [
                AssignmentStatus.SUBMITTED,
                AssignmentStatus.KILLED,
            ],
            AssignmentStatus.APPROVED: [],
            AssignmentStatus.KILLED: [],
        }

        if new_status not in valid_transitions.get(assignment.status, []):
            raise ValueError(
                f"Invalid status transition from {assignment.status.value} to {new_status.value}"
            )

        now = datetime.now(timezone.utc)
        assignment.status = new_status

        if new_status == AssignmentStatus.IN_PROGRESS:
            assignment.started_at = now
        elif new_status == AssignmentStatus.SUBMITTED:
            assignment.submitted_at = now
            if data.content_url:
                assignment.content_url = data.content_url
            if data.final_word_count:
                assignment.final_word_count = data.final_word_count
        elif new_status == AssignmentStatus.REVISION_REQUESTED:
            assignment.revision_count += 1
            if data.revision_notes:
                assignment.revision_notes = data.revision_notes
        elif new_status == AssignmentStatus.APPROVED:
            assignment.completed_at = now
        elif new_status == AssignmentStatus.KILLED:
            assignment.completed_at = now

        await db.flush()
        await db.refresh(assignment)
        return assignment
