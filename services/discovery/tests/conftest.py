import asyncio
from decimal import Decimal
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

import sys
sys.path.insert(0, "/app")

from shared.db import Base, get_db
from app.main import app
from app.services.search_service import FreelancerProfile

# Test database URL
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
async def sample_freelancers(db_session: AsyncSession) -> list[FreelancerProfile]:
    """Create sample freelancers for testing."""
    freelancers = [
        FreelancerProfile(
            id=uuid4(),
            user_id=uuid4(),
            display_name="Alice Tech Writer",
            bio="Technology journalist with 10 years experience",
            home_city="San Francisco",
            home_state="CA",
            home_country="US",
            willing_to_travel_miles=50,
            primary_beats=["tech", "startups"],
            secondary_beats=["finance"],
            languages=["en"],
            availability_status="available",
            weekly_capacity_hours=40,
            per_word_rate=Decimal("0.75"),
            hourly_rate_min=Decimal("75.00"),
            hourly_rate_max=Decimal("125.00"),
            identity_verified=True,
            portfolio_verified=True,
            trust_score=Decimal("0.85"),
            quality_score=Decimal("0.90"),
            reliability_score=Decimal("0.88"),
        ),
        FreelancerProfile(
            id=uuid4(),
            user_id=uuid4(),
            display_name="Bob Politics Reporter",
            bio="Political correspondent covering Washington",
            home_city="Washington",
            home_state="DC",
            home_country="US",
            willing_to_travel_miles=100,
            primary_beats=["politics", "government"],
            secondary_beats=["legal"],
            languages=["en", "es"],
            availability_status="limited",
            weekly_capacity_hours=20,
            per_word_rate=Decimal("1.00"),
            hourly_rate_min=Decimal("100.00"),
            hourly_rate_max=Decimal("150.00"),
            identity_verified=True,
            portfolio_verified=True,
            trust_score=Decimal("0.92"),
            quality_score=Decimal("0.95"),
            reliability_score=Decimal("0.90"),
        ),
        FreelancerProfile(
            id=uuid4(),
            user_id=uuid4(),
            display_name="Carol Health Writer",
            bio="Health and medical journalist",
            home_city="New York",
            home_state="NY",
            home_country="US",
            willing_to_travel_miles=30,
            primary_beats=["health", "science"],
            secondary_beats=["tech"],
            languages=["en"],
            availability_status="unavailable",
            weekly_capacity_hours=0,
            per_word_rate=Decimal("0.50"),
            identity_verified=True,
            portfolio_verified=False,
            trust_score=Decimal("0.70"),
            quality_score=Decimal("0.75"),
            reliability_score=Decimal("0.72"),
        ),
    ]

    for freelancer in freelancers:
        db_session.add(freelancer)

    await db_session.commit()
    return freelancers
