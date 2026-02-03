import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

import sys
sys.path.insert(0, "/app")

from shared.db import Base, get_db
from app.main import app
from app.models.portfolio_item import PortfolioItem, VerificationStatus, OutletTier
from app.models.style_fingerprint import StyleFingerprint
from app.models.topic_classification import TopicClassification

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test user IDs
FREELANCER_ID = uuid4()
EDITOR_ID = uuid4()
NEWSROOM_ID = uuid4()


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


def mock_verify_token_freelancer(token, expected_type="access"):
    """Mock token verification returning a freelancer."""
    from unittest.mock import MagicMock
    payload = MagicMock()
    payload.sub = str(FREELANCER_ID)
    payload.role = "freelancer"
    return payload


def mock_verify_token_editor(token, expected_type="access"):
    """Mock token verification returning an editor."""
    from unittest.mock import MagicMock
    payload = MagicMock()
    payload.sub = str(EDITOR_ID)
    payload.role = "editor"
    return payload


@pytest_asyncio.fixture(scope="function")
async def freelancer_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client authenticated as a freelancer."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.deps.verify_token", side_effect=mock_verify_token_freelancer):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": "Bearer test-freelancer-token"},
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def editor_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client authenticated as an editor."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.deps.verify_token", side_effect=mock_verify_token_editor):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": "Bearer test-editor-token"},
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_portfolio_items(db_session: AsyncSession) -> list[PortfolioItem]:
    """Create sample portfolio items."""
    items = [
        PortfolioItem(
            id=uuid4(),
            freelancer_id=FREELANCER_ID,
            url="https://www.nytimes.com/2026/01/15/tech/ai-journalism.html",
            title="How AI Is Reshaping the Newsroom",
            publication="Nytimes",
            published_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            byline="Test Freelancer",
            word_count=2500,
            excerpt="Artificial intelligence is transforming how newsrooms operate, from story discovery to fact-checking.",
            topics=["tech", "investigations"],
            tone_profile={
                "narrative_score": 0.6,
                "analytical_score": 0.8,
                "explanatory_score": 0.7,
                "passive_voice_ratio": 0.15,
                "citation_density": 0.4,
                "avg_sentence_length": 18.5,
            },
            outlet_tier=OutletTier.TIER1,
            verification_status=VerificationStatus.VERIFIED,
            verification_method="automated_scrape",
            scraped_at=datetime.now(timezone.utc),
        ),
        PortfolioItem(
            id=uuid4(),
            freelancer_id=FREELANCER_ID,
            url="https://www.wired.com/story/privacy-tech-startups/",
            title="The Rise of Privacy-First Tech Startups",
            publication="Wired",
            published_date=datetime(2025, 11, 20, tzinfo=timezone.utc),
            byline="Test Freelancer",
            word_count=3200,
            excerpt="A new wave of startups is building technology that puts user privacy first.",
            topics=["tech", "business"],
            tone_profile={
                "narrative_score": 0.5,
                "analytical_score": 0.7,
                "explanatory_score": 0.8,
                "passive_voice_ratio": 0.1,
                "citation_density": 0.3,
                "avg_sentence_length": 16.2,
            },
            outlet_tier=OutletTier.TIER2,
            verification_status=VerificationStatus.VERIFIED,
            verification_method="automated_scrape",
            scraped_at=datetime.now(timezone.utc),
        ),
    ]

    for item in items:
        db_session.add(item)
    await db_session.commit()
    return items
