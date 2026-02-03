import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
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
from app.models.pitch_window import PitchWindow, PitchWindowStatus
from app.models.pitch import Pitch, PitchStatus
from app.models.assignment import Assignment, AssignmentStatus

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
            headers={
                "Authorization": "Bearer test-editor-token",
                "X-Newsroom-ID": str(NEWSROOM_ID),
            },
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_pitch_window(db_session: AsyncSession) -> PitchWindow:
    """Create a sample open pitch window."""
    now = datetime.now(timezone.utc)
    window = PitchWindow(
        id=uuid4(),
        newsroom_id=NEWSROOM_ID,
        editor_id=EDITOR_ID,
        title="Tech Investigative Series",
        description="Looking for investigative pieces on big tech companies and their impact on privacy.",
        beats=["tech", "privacy", "investigations"],
        requirements="Must include at least 3 on-record sources.",
        budget_min=Decimal("500.00"),
        budget_max=Decimal("2000.00"),
        rate_type="flat",
        max_pitches=50,
        current_pitch_count=0,
        opens_at=now - timedelta(hours=1),
        closes_at=now + timedelta(days=7),
        status=PitchWindowStatus.OPEN,
    )
    db_session.add(window)
    await db_session.commit()
    await db_session.refresh(window)
    return window


@pytest_asyncio.fixture
async def sample_draft_pitch(
    db_session: AsyncSession,
    sample_pitch_window: PitchWindow,
) -> Pitch:
    """Create a sample draft pitch."""
    pitch = Pitch(
        id=uuid4(),
        pitch_window_id=sample_pitch_window.id,
        freelancer_id=FREELANCER_ID,
        headline="Big Tech's Secret Data Deals",
        summary="An investigation into undisclosed data sharing agreements between major tech companies and data brokers.",
        approach="I will use FOIA requests and interviews with former employees to uncover the scope of data sharing.",
        estimated_word_count=3000,
        proposed_rate=Decimal("1500.00"),
        proposed_rate_type="flat",
        estimated_delivery_days=21,
        status=PitchStatus.DRAFT,
    )
    db_session.add(pitch)
    await db_session.commit()
    await db_session.refresh(pitch)
    return pitch


@pytest_asyncio.fixture
async def sample_submitted_pitch(
    db_session: AsyncSession,
    sample_pitch_window: PitchWindow,
) -> Pitch:
    """Create a sample submitted pitch."""
    pitch = Pitch(
        id=uuid4(),
        pitch_window_id=sample_pitch_window.id,
        freelancer_id=FREELANCER_ID,
        headline="AI Ethics in Newsrooms",
        summary="Exploring how news organizations are grappling with the ethical implications of AI-generated content.",
        approach="Interviews with editors at 10 major publications plus analysis of their published AI policies.",
        estimated_word_count=2500,
        proposed_rate=Decimal("1200.00"),
        proposed_rate_type="flat",
        estimated_delivery_days=14,
        status=PitchStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )
    db_session.add(pitch)

    # Increment window count
    sample_pitch_window.current_pitch_count += 1
    await db_session.commit()
    await db_session.refresh(pitch)
    return pitch
