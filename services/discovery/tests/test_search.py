import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.services.search_service import FreelancerProfile


@pytest.mark.asyncio
async def test_search_all_freelancers(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching for all freelancers with no filters."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={},
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) == 3  # All sample freelancers


@pytest.mark.asyncio
async def test_search_by_beats(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching for freelancers by beats."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "beats": ["tech"]
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    # Should find Alice (tech, startups) and possibly Carol (health, science, secondary: tech)
    assert len(data["results"]) >= 1
    assert any(
        "tech" in r["beats"]
        for r in data["results"]
    )


@pytest.mark.asyncio
async def test_search_by_availability(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching for freelancers by availability."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "availability": "available"
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1  # Only Alice is available
    assert data["results"][0]["availability"] == "available"


@pytest.mark.asyncio
async def test_search_by_min_trust_score(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching with minimum trust score filter."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "min_trust_score": 0.80
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    # Should find Alice (0.85) and Bob (0.92), not Carol (0.70)
    assert len(data["results"]) == 2
    for result in data["results"]:
        assert float(result["scores"]["trust"]) >= 0.80


@pytest.mark.asyncio
async def test_search_by_location(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching by location (state)."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "location": {
                    "type": "state",
                    "state": "CA"
                }
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1  # Only Alice is in CA
    assert data["results"][0]["location"]["state"] == "CA"


@pytest.mark.asyncio
async def test_search_by_rate_range(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test searching by rate range."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "rate_range": {
                    "type": "per_word",
                    "min": 0.70,
                    "max": 0.80
                }
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    # Should find Alice (0.75)
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_search_pagination(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test search pagination."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "pagination": {
                "page": 1,
                "per_page": 2
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2  # Limited to 2 per page
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 2
    assert data["pagination"]["total_results"] == 3
    assert data["pagination"]["total_pages"] == 2


@pytest.mark.asyncio
async def test_search_sorting(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test search sorting by trust score."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "sort": {
                "field": "trust_score",
                "order": "desc"
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    results = data["results"]

    # Verify descending order by trust score
    trust_scores = [float(r["scores"]["trust"]) for r in results]
    assert trust_scores == sorted(trust_scores, reverse=True)


@pytest.mark.asyncio
async def test_search_combined_filters(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test search with multiple filters combined."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "availability": "available",
                "min_trust_score": 0.80,
                "location": {
                    "type": "country",
                    "country": "US"
                }
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    # Only Alice matches: available, trust 0.85, US
    assert len(data["results"]) == 1
    assert data["results"][0]["display_name"] == "Alice Tech Writer"


@pytest.mark.asyncio
async def test_get_freelancer_detail(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test getting freelancer detail by ID."""
    freelancer = sample_freelancers[0]

    response = await client.get(
        f"/api/v1/discovery/freelancers/{freelancer.id}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(freelancer.id)
    assert data["display_name"] == freelancer.display_name
    assert data["bio"] == freelancer.bio
    assert "trust_score" in data
    assert "portfolio_items" in data


@pytest.mark.asyncio
async def test_get_nonexistent_freelancer(client: AsyncClient):
    """Test getting a nonexistent freelancer returns 404."""
    response = await client.get(
        f"/api/v1/discovery/freelancers/{uuid4()}",
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_search_empty_results(
    client: AsyncClient,
    sample_freelancers: list[FreelancerProfile],
):
    """Test search that returns no results."""
    response = await client.post(
        "/api/v1/discovery/search",
        json={
            "query": {
                "beats": ["nonexistent_beat"]
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0
    assert data["pagination"]["total_results"] == 0
