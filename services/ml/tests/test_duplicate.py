import pytest
from httpx import AsyncClient
from uuid import uuid4

from tests.conftest import NEWSROOM_ID


@pytest.mark.asyncio
async def test_check_duplicate(
    freelancer_client: AsyncClient,
):
    """Test duplicate check on a pitch."""
    response = await freelancer_client.post(
        "/api/v1/duplicate/check",
        json={
            "headline": "The Impact of AI on Journalism Ethics",
            "summary": "An exploration of how artificial intelligence tools are affecting editorial ethics and accountability in modern newsrooms.",
            "newsroom_id": str(NEWSROOM_ID),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "duplicate_score" in data
    assert 0 <= data["duplicate_score"] <= 1
    assert "similar_pitches" in data
    assert "competing_coverage" in data


@pytest.mark.asyncio
async def test_check_unique_pitch(
    freelancer_client: AsyncClient,
):
    """Test duplicate check on a unique pitch."""
    response = await freelancer_client.post(
        "/api/v1/duplicate/check",
        json={
            "headline": "Underwater Basket Weaving Championship 2026",
            "summary": "Coverage of the first ever international underwater basket weaving championship held in the Mariana Trench.",
            "newsroom_id": str(uuid4()),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["duplicate_score"] == 0
    assert data["duplicate_warning"] is None
