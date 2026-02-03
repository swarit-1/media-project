import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

from app.models.pitch_window import PitchWindow
from app.models.pitch import Pitch, PitchStatus
from tests.conftest import FREELANCER_ID, EDITOR_ID, NEWSROOM_ID


@pytest.mark.asyncio
async def test_create_pitch(
    freelancer_client: AsyncClient,
    sample_pitch_window: PitchWindow,
    db_session,
):
    """Test creating a pitch as a freelancer."""
    # First remove any existing pitch for this freelancer in this window
    response = await freelancer_client.post(
        "/api/v1/pitches",
        json={
            "pitch_window_id": str(sample_pitch_window.id),
            "headline": "The Rise of Privacy Tech",
            "summary": "An exploration of the growing privacy technology industry and its impact on big tech.",
            "approach": "Interview founders of 5 privacy-focused startups and compare with big tech responses.",
            "estimated_word_count": 2000,
            "proposed_rate": 800,
            "proposed_rate_type": "flat",
            "estimated_delivery_days": 14,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["headline"] == "The Rise of Privacy Tech"
    assert data["status"] == "draft"
    assert data["freelancer_id"] == str(FREELANCER_ID)


@pytest.mark.asyncio
async def test_create_duplicate_pitch(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test that a freelancer cannot create duplicate pitches in the same window."""
    response = await freelancer_client.post(
        "/api/v1/pitches",
        json={
            "pitch_window_id": str(sample_draft_pitch.pitch_window_id),
            "headline": "Another Pitch",
            "summary": "This should fail because we already have a pitch in this window.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "DUPLICATE_PITCH"


@pytest.mark.asyncio
async def test_get_pitch(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test getting a specific pitch."""
    response = await freelancer_client.get(
        f"/api/v1/pitches/{sample_draft_pitch.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_draft_pitch.id)
    assert data["headline"] == sample_draft_pitch.headline


@pytest.mark.asyncio
async def test_update_draft_pitch(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test updating a draft pitch."""
    response = await freelancer_client.patch(
        f"/api/v1/pitches/{sample_draft_pitch.id}",
        json={
            "headline": "Updated Headline",
            "estimated_word_count": 4000,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["headline"] == "Updated Headline"
    assert data["estimated_word_count"] == 4000


@pytest.mark.asyncio
async def test_submit_pitch(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test submitting a draft pitch."""
    response = await freelancer_client.post(
        f"/api/v1/pitches/{sample_draft_pitch.id}/submit"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
    assert data["submitted_at"] is not None


@pytest.mark.asyncio
async def test_cannot_update_submitted_pitch(
    freelancer_client: AsyncClient,
    sample_submitted_pitch: Pitch,
):
    """Test that submitted pitches cannot be edited."""
    response = await freelancer_client.patch(
        f"/api/v1/pitches/{sample_submitted_pitch.id}",
        json={"headline": "Should Fail"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "NOT_DRAFT"


@pytest.mark.asyncio
async def test_accept_pitch(
    editor_client: AsyncClient,
    sample_submitted_pitch: Pitch,
):
    """Test an editor accepting a submitted pitch."""
    deadline = (datetime.now(timezone.utc) + timedelta(days=21)).isoformat()

    response = await editor_client.post(
        f"/api/v1/pitches/{sample_submitted_pitch.id}/review",
        json={
            "action": "accept",
            "editor_notes": "Great angle, let's go with this.",
            "agreed_rate": 1200,
            "rate_type": "flat",
            "deadline": deadline,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["editor_notes"] == "Great angle, let's go with this."


@pytest.mark.asyncio
async def test_reject_pitch(
    editor_client: AsyncClient,
    sample_submitted_pitch: Pitch,
):
    """Test an editor rejecting a submitted pitch."""
    response = await editor_client.post(
        f"/api/v1/pitches/{sample_submitted_pitch.id}/review",
        json={
            "action": "reject",
            "rejection_reason": "We covered this topic recently.",
            "editor_notes": "Good pitch but timing is off.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "We covered this topic recently."


@pytest.mark.asyncio
async def test_withdraw_pitch(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test withdrawing a pitch."""
    response = await freelancer_client.post(
        f"/api/v1/pitches/{sample_draft_pitch.id}/withdraw"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "withdrawn"


@pytest.mark.asyncio
async def test_list_my_pitches(
    freelancer_client: AsyncClient,
    sample_draft_pitch: Pitch,
):
    """Test listing pitches for the current freelancer."""
    response = await freelancer_client.get("/api/v1/pitches/my")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_list_pitches_for_window(
    editor_client: AsyncClient,
    sample_submitted_pitch: Pitch,
):
    """Test listing pitches for a window as an editor."""
    response = await editor_client.get(
        f"/api/v1/pitches/window/{sample_submitted_pitch.pitch_window_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) >= 1
