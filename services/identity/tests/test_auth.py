import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_freelancer(client: AsyncClient):
    """Test freelancer registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newfreelancer@test.com",
            "password": "securepassword123",
            "role": "freelancer",
            "display_name": "New Freelancer",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newfreelancer@test.com"
    assert data["role"] == "freelancer"
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_editor(client: AsyncClient):
    """Test editor registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "neweditor@test.com",
            "password": "securepassword123",
            "role": "editor",
            "display_name": "New Editor",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "neweditor@test.com"
    assert data["role"] == "editor"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email fails."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "securepassword123",
            "role": "freelancer",
            "display_name": "First User",
        },
    )

    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "differentpassword",
            "role": "freelancer",
            "display_name": "Second User",
        },
    )

    assert response.status_code == 409
    data = response.json()
    assert data["detail"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_invalid_role(client: AsyncClient):
    """Test registration with invalid role fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "password": "securepassword123",
            "role": "invalid_role",
            "display_name": "Test User",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "password": "short",  # Less than 8 chars
            "role": "freelancer",
            "display_name": "Test User",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # First register a user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logintest@test.com",
            "password": "securepassword123",
            "role": "freelancer",
            "display_name": "Login Test",
        },
    )

    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "logintest@test.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900  # 15 minutes


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password fails."""
    # First register a user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpasstest@test.com",
            "password": "securepassword123",
            "role": "freelancer",
            "display_name": "Wrong Pass Test",
        },
    )

    # Try login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpasstest@test.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent user fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "somepassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refreshtest@test.com",
            "password": "securepassword123",
            "role": "freelancer",
            "display_name": "Refresh Test",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "refreshtest@test.com",
            "password": "securepassword123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    # Refresh the token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token fails."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )

    assert response.status_code == 401
