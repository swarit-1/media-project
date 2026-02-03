import pytest
from httpx import AsyncClient

from app.models.portfolio_item import PortfolioItem
from tests.conftest import FREELANCER_ID


@pytest.mark.asyncio
async def test_compute_trust_score(
    freelancer_client: AsyncClient,
    sample_portfolio_items: list[PortfolioItem],
):
    """Test computing trust score for a freelancer."""
    response = await freelancer_client.post(
        "/api/v1/trust-score/compute",
        json={"freelancer_id": str(FREELANCER_ID)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["freelancer_id"] == str(FREELANCER_ID)
    assert 0 <= data["trust_score"] <= 1
    assert "components" in data
    assert "identity_verification" in data["components"]
    assert "portfolio_quality" in data["components"]
    assert "on_time_delivery" in data["components"]


@pytest.mark.asyncio
async def test_get_my_trust_score(
    freelancer_client: AsyncClient,
    sample_portfolio_items: list[PortfolioItem],
):
    """Test getting trust score for the current freelancer."""
    response = await freelancer_client.get("/api/v1/trust-score/my")

    assert response.status_code == 200
    data = response.json()
    assert data["freelancer_id"] == str(FREELANCER_ID)
    assert 0 <= data["trust_score"] <= 1
    assert data["computed_at"] is not None
