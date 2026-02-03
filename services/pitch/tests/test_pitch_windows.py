import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

from app.models.pitch_window import PitchWindow, PitchWindowStatus
from tests.conftest import NEWSROOM_ID, EDITOR_ID


@pytest.mark.asyncio
async def test_create_pitch_window(editor_client: AsyncClient):
    """Test creating a pitch window."""
    now = datetime.now(timezone.utc)
    response = await editor_client.post(
        "/api/v1/pitch-windows",
        json={
            "title": "Health Policy Series",
            "description": "We need investigative stories about healthcare policy changes.",
            "beats": ["health", "policy"],
            "budget_min": 500,
            "budget_max": 1500,
            "rate_type": "flat",
            "max_pitches": 30,
            "opens_at": (now + timedelta(hours=1)).isoformat(),
            "closes_at": (now + timedelta(days=14)).isoformat(),
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Health Policy Series"
    assert data["beats"] == ["health", "policy"]
    assert data["status"] == "draft"
    assert data["newsroom_id"] == str(NEWSROOM_ID)
    assert data["editor_id"] == str(EDITOR_ID)
    assert data["current_pitch_count"] == 0


@pytest.mark.asyncio
async def test_create_pitch_window_invalid_dates(editor_client: AsyncClient):
    """Test that closes_at must be after opens_at."""
    now = datetime.now(timezone.utc)
    response = await editor_client.post(
        "/api/v1/pitch-windows",
        json={
            "title": "Bad Dates Window",
            "description": "This should fail due to invalid dates.",
            "beats": ["tech"],
            "opens_at": (now + timedelta(days=14)).isoformat(),
            "closes_at": (now + timedelta(hours=1)).isoformat(),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_DATES"


@pytest.mark.asyncio
async def test_list_pitch_windows(
    editor_client: AsyncClient,
    sample_pitch_window: PitchWindow,
):
    """Test listing pitch windows."""
    response = await editor_client.get("/api/v1/pitch-windows")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_get_pitch_window(
    editor_client: AsyncClient,
    sample_pitch_window: PitchWindow,
):
    """Test getting a specific pitch window."""
    response = await editor_client.get(
        f"/api/v1/pitch-windows/{sample_pitch_window.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_pitch_window.id)
    assert data["title"] == sample_pitch_window.title


@pytest.mark.asyncio
async def test_get_nonexistent_pitch_window(editor_client: AsyncClient):
    """Test getting a nonexistent pitch window returns 404."""
    from uuid import uuid4
    response = await editor_client.get(
        f"/api/v1/pitch-windows/{uuid4()}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_open_pitch_window(
    editor_client: AsyncClient,
    db_session,
):
    """Test opening a draft pitch window."""
    from uuid import uuid4
    now = datetime.now(timezone.utc)

    # Create a draft window
    window = PitchWindow(
        id=uuid4(),
        newsroom_id=NEWSROOM_ID,
        editor_id=EDITOR_ID,
        title="Draft Window",
        description="A draft window to be opened.",
        beats=["tech"],
        max_pitches=20,
        opens_at=now,
        closes_at=now + timedelta(days=7),
        status=PitchWindowStatus.DRAFT,
    )
    db_session.add(window)
    await db_session.commit()

    response = await editor_client.post(
        f"/api/v1/pitch-windows/{window.id}/open"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_close_pitch_window(
    editor_client: AsyncClient,
    sample_pitch_window: PitchWindow,
):
    """Test closing an open pitch window."""
    response = await editor_client.post(
        f"/api/v1/pitch-windows/{sample_pitch_window.id}/close"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
