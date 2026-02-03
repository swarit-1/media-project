import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.models.portfolio_item import PortfolioItem
from tests.conftest import FREELANCER_ID


@pytest.mark.asyncio
async def test_list_my_portfolio(
    freelancer_client: AsyncClient,
    sample_portfolio_items: list[PortfolioItem],
):
    """Test listing portfolio items for the current freelancer."""
    response = await freelancer_client.get("/api/v1/portfolio/my")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) == 2


@pytest.mark.asyncio
async def test_get_portfolio_item(
    freelancer_client: AsyncClient,
    sample_portfolio_items: list[PortfolioItem],
):
    """Test getting a specific portfolio item."""
    item = sample_portfolio_items[0]
    response = await freelancer_client.get(f"/api/v1/portfolio/{item.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item.id)
    assert data["title"] == item.title
    assert data["outlet_tier"] == "tier1"
    assert data["verification_status"] == "verified"


@pytest.mark.asyncio
async def test_get_nonexistent_portfolio_item(
    freelancer_client: AsyncClient,
):
    """Test getting a nonexistent portfolio item."""
    response = await freelancer_client.get(f"/api/v1/portfolio/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_freelancer_portfolio_public(
    freelancer_client: AsyncClient,
    sample_portfolio_items: list[PortfolioItem],
):
    """Test listing portfolio for a specific freelancer (public endpoint)."""
    response = await freelancer_client.get(
        f"/api/v1/portfolio/freelancer/{FREELANCER_ID}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
