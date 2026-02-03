import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_get_current_user(
    client: AsyncClient,
    test_freelancer: User,
    freelancer_token: str,
):
    """Test getting current user profile."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_freelancer.email
    assert data["role"] == "freelancer"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without auth fails."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token fails."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_current_user(
    client: AsyncClient,
    test_freelancer: User,
    freelancer_token: str,
):
    """Test updating current user profile."""
    response = await client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {freelancer_token}"},
        json={"display_name": "Updated Name"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_freelancer.email


@pytest.mark.asyncio
async def test_update_user_email(
    client: AsyncClient,
    test_freelancer: User,
    freelancer_token: str,
):
    """Test updating user email."""
    response = await client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {freelancer_token}"},
        json={"email": "newemail@test.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@test.com"
