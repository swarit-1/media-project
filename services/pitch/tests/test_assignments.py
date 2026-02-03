import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient

from app.models.pitch_window import PitchWindow
from app.models.pitch import Pitch, PitchStatus
from app.models.assignment import Assignment, AssignmentStatus
from tests.conftest import FREELANCER_ID, EDITOR_ID, NEWSROOM_ID


@pytest.fixture
async def sample_assignment(
    db_session,
    sample_submitted_pitch: Pitch,
) -> Assignment:
    """Create a sample assignment from an accepted pitch."""
    # Mark pitch as accepted
    sample_submitted_pitch.status = PitchStatus.ACCEPTED
    sample_submitted_pitch.reviewed_at = datetime.now(timezone.utc)

    assignment = Assignment(
        id=uuid4(),
        pitch_id=sample_submitted_pitch.id,
        freelancer_id=FREELANCER_ID,
        editor_id=EDITOR_ID,
        newsroom_id=NEWSROOM_ID,
        agreed_rate=Decimal("1200.00"),
        rate_type="flat",
        word_count_target=2500,
        deadline=datetime.now(timezone.utc) + timedelta(days=21),
        status=AssignmentStatus.ASSIGNED,
        kill_fee_percentage=Decimal("25.00"),
    )
    db_session.add(assignment)
    await db_session.commit()
    await db_session.refresh(assignment)
    return assignment


@pytest.mark.asyncio
async def test_get_assignment(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
):
    """Test getting a specific assignment."""
    response = await freelancer_client.get(
        f"/api/v1/assignments/{sample_assignment.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_assignment.id)
    assert data["status"] == "assigned"
    assert float(data["agreed_rate"]) == 1200.00


@pytest.mark.asyncio
async def test_list_my_assignments(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
):
    """Test listing assignments for the current freelancer."""
    response = await freelancer_client.get("/api/v1/assignments/my")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_start_assignment(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
):
    """Test freelancer starting an assignment."""
    response = await freelancer_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None


@pytest.mark.asyncio
async def test_submit_assignment(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
    db_session,
):
    """Test freelancer submitting an assignment."""
    # First start it
    sample_assignment.status = AssignmentStatus.IN_PROGRESS
    sample_assignment.started_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await freelancer_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={
            "status": "submitted",
            "content_url": "https://docs.example.com/article-draft",
            "final_word_count": 2600,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
    assert data["content_url"] == "https://docs.example.com/article-draft"
    assert data["final_word_count"] == 2600


@pytest.mark.asyncio
async def test_approve_assignment(
    editor_client: AsyncClient,
    sample_assignment: Assignment,
    db_session,
):
    """Test editor approving a submitted assignment."""
    # Progress to submitted state
    sample_assignment.status = AssignmentStatus.SUBMITTED
    sample_assignment.submitted_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await editor_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={"status": "approved"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_request_revision(
    editor_client: AsyncClient,
    sample_assignment: Assignment,
    db_session,
):
    """Test editor requesting a revision."""
    sample_assignment.status = AssignmentStatus.SUBMITTED
    sample_assignment.submitted_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await editor_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={
            "status": "revision_requested",
            "revision_notes": "Please add more sources in section 3.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "revision_requested"
    assert data["revision_count"] == 1
    assert data["revision_notes"] == "Please add more sources in section 3."


@pytest.mark.asyncio
async def test_kill_assignment(
    editor_client: AsyncClient,
    sample_assignment: Assignment,
):
    """Test editor killing an assignment."""
    response = await editor_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={"status": "killed"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "killed"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_invalid_status_transition(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
):
    """Test that invalid state transitions are rejected."""
    # Cannot go from assigned to submitted (must be in_progress first)
    response = await freelancer_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={"status": "submitted"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_TRANSITION"


@pytest.mark.asyncio
async def test_freelancer_cannot_approve(
    freelancer_client: AsyncClient,
    sample_assignment: Assignment,
    db_session,
):
    """Test that freelancers cannot approve assignments."""
    sample_assignment.status = AssignmentStatus.SUBMITTED
    await db_session.commit()

    response = await freelancer_client.post(
        f"/api/v1/assignments/{sample_assignment.id}/status",
        json={"status": "approved"},
    )

    assert response.status_code == 403
