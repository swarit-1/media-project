import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment, AssignmentStatus
from app.models.pitch_window import PitchWindow, PitchWindowStatus
from app.models.pitch import Pitch, PitchStatus
from tests.conftest import FREELANCER_ID, EDITOR_ID, NEWSROOM_ID


@pytest.fixture
async def approved_assignment(db_session: AsyncSession) -> Assignment:
    """Create an approved assignment for CMS webhook tests."""
    now = datetime.now(timezone.utc)

    window = PitchWindow(
        id=uuid4(),
        newsroom_id=NEWSROOM_ID,
        editor_id=EDITOR_ID,
        title="CMS Test Window",
        description="Test window for CMS webhook tests",
        beats=["tech"],
        budget_min=Decimal("500.00"),
        budget_max=Decimal("2000.00"),
        rate_type="flat",
        max_pitches=50,
        current_pitch_count=0,
        opens_at=now - timedelta(hours=1),
        closes_at=now + timedelta(days=7),
        status=PitchWindowStatus.OPEN,
    )
    db_session.add(window)

    pitch = Pitch(
        id=uuid4(),
        pitch_window_id=window.id,
        freelancer_id=FREELANCER_ID,
        headline="CMS Test Article",
        summary="Test article for CMS webhook testing.",
        status=PitchStatus.ACCEPTED,
        submitted_at=now,
        reviewed_at=now,
    )
    db_session.add(pitch)

    assignment = Assignment(
        id=uuid4(),
        pitch_id=pitch.id,
        freelancer_id=FREELANCER_ID,
        editor_id=EDITOR_ID,
        newsroom_id=NEWSROOM_ID,
        agreed_rate=Decimal("1000.00"),
        rate_type="flat",
        word_count_target=2000,
        deadline=now + timedelta(days=14),
        status=AssignmentStatus.APPROVED,
        completed_at=now,
    )
    db_session.add(assignment)
    await db_session.commit()
    await db_session.refresh(assignment)
    return assignment


@pytest.mark.asyncio
async def test_cms_webhook_article_published(
    editor_client: AsyncClient,
    approved_assignment: Assignment,
):
    """Test CMS webhook for article publication."""
    response = await editor_client.post(
        "/api/v1/webhooks/cms/webhook",
        json={
            "event": "article.published",
            "cms_post_id": "cms-12345",
            "assignment_id": str(approved_assignment.id),
            "published_url": "https://example.com/articles/test-article",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"section": "tech", "tags": ["ai", "journalism"]},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["assignment_status"] == "published"
    assert data["payment_release_triggered"] is True


@pytest.mark.asyncio
async def test_cms_webhook_invalid_assignment_state(
    editor_client: AsyncClient,
    db_session: AsyncSession,
    approved_assignment: Assignment,
):
    """Test CMS webhook rejects publication for non-approved assignment."""
    # Change assignment to in_progress (not approved)
    approved_assignment.status = AssignmentStatus.IN_PROGRESS
    approved_assignment.completed_at = None
    await db_session.commit()

    response = await editor_client.post(
        "/api/v1/webhooks/cms/webhook",
        json={
            "event": "article.published",
            "cms_post_id": "cms-12345",
            "assignment_id": str(approved_assignment.id),
            "published_url": "https://example.com/articles/test",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_STATE"


@pytest.mark.asyncio
async def test_cms_webhook_nonexistent_assignment(
    editor_client: AsyncClient,
):
    """Test CMS webhook with nonexistent assignment."""
    response = await editor_client.post(
        "/api/v1/webhooks/cms/webhook",
        json={
            "event": "article.published",
            "cms_post_id": "cms-12345",
            "assignment_id": str(uuid4()),
            "published_url": "https://example.com/articles/test",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cms_webhook_article_updated(
    editor_client: AsyncClient,
    db_session: AsyncSession,
    approved_assignment: Assignment,
):
    """Test CMS webhook for article update after publication."""
    # First publish it
    approved_assignment.status = AssignmentStatus.PUBLISHED
    approved_assignment.published_at = datetime.now(timezone.utc)
    approved_assignment.cms_post_id = "cms-12345"
    approved_assignment.final_url = "https://example.com/articles/test-article"
    await db_session.commit()

    response = await editor_client.post(
        "/api/v1/webhooks/cms/webhook",
        json={
            "event": "article.updated",
            "cms_post_id": "cms-12345",
            "assignment_id": str(approved_assignment.id),
            "published_url": "https://example.com/articles/test-article-v2",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["assignment_status"] == "published"
    assert data["payment_release_triggered"] is False
