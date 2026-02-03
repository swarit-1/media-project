import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
sys.path.insert(0, "/app")

from shared.db import Base, get_db
from shared.auth import hash_password
from app.main import app
from app.models import User, FreelancerProfile, EditorProfile
from app.models.user import UserRole, UserStatus

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database session override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_freelancer(db_session: AsyncSession) -> User:
    """Create a test freelancer user."""
    user = User(
        id=uuid4(),
        email="freelancer@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.FREELANCER,
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)

    profile = FreelancerProfile(
        id=uuid4(),
        user_id=user.id,
        display_name="Test Freelancer",
        bio="A test freelancer bio",
        home_city="San Francisco",
        home_state="CA",
        home_country="US",
        primary_beats=["politics", "tech"],
        availability_status="available",
        trust_score=0.75,
        quality_score=0.80,
        reliability_score=0.85,
    )
    db_session.add(profile)

    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_editor(db_session: AsyncSession) -> User:
    """Create a test editor user."""
    user = User(
        id=uuid4(),
        email="editor@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.EDITOR,
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)

    profile = EditorProfile(
        id=uuid4(),
        user_id=user.id,
        display_name="Test Editor",
        title="Senior Editor",
    )
    db_session.add(profile)

    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def freelancer_token(test_freelancer: User) -> str:
    """Get JWT token for test freelancer."""
    from shared.auth import create_access_token
    return create_access_token(
        user_id=test_freelancer.id,
        email=test_freelancer.email,
        role=test_freelancer.role.value,
    )


@pytest_asyncio.fixture
async def editor_token(test_editor: User) -> str:
    """Get JWT token for test editor."""
    from shared.auth import create_access_token
    return create_access_token(
        user_id=test_editor.id,
        email=test_editor.email,
        role=test_editor.role.value,
    )
