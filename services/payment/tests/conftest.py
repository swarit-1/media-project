import asyncio
from datetime import datetime, timezone
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
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.compliance_record import ComplianceRecord
from app.models.vendor_ledger import VendorLedgerEntry

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test user IDs
FREELANCER_ID = uuid4()
EDITOR_ID = uuid4()
ADMIN_ID = uuid4()
NEWSROOM_ID = uuid4()
ASSIGNMENT_ID = uuid4()


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


def mock_verify_token_admin(token, expected_type="access"):
    """Mock token verification returning an admin."""
    from unittest.mock import MagicMock
    payload = MagicMock()
    payload.sub = str(ADMIN_ID)
    payload.role = "admin"
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


@pytest_asyncio.fixture(scope="function")
async def admin_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client authenticated as an admin."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.deps.verify_token", side_effect=mock_verify_token_admin):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": "Bearer test-admin-token"},
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_payment(db_session: AsyncSession) -> Payment:
    """Create a sample pending payment."""
    payment = Payment(
        id=uuid4(),
        assignment_id=ASSIGNMENT_ID,
        newsroom_id=NEWSROOM_ID,
        freelancer_id=FREELANCER_ID,
        payment_type=PaymentType.ASSIGNMENT,
        gross_amount=Decimal("1200.00"),
        platform_fee=Decimal("120.00"),
        net_amount=Decimal("1080.00"),
        currency="USD",
        description="Payment for article assignment",
        status=PaymentStatus.PENDING,
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    return payment


@pytest_asyncio.fixture
async def sample_escrow_payment(db_session: AsyncSession) -> Payment:
    """Create a sample payment in escrow."""
    payment = Payment(
        id=uuid4(),
        assignment_id=ASSIGNMENT_ID,
        newsroom_id=NEWSROOM_ID,
        freelancer_id=FREELANCER_ID,
        payment_type=PaymentType.ASSIGNMENT,
        gross_amount=Decimal("800.00"),
        platform_fee=Decimal("80.00"),
        net_amount=Decimal("720.00"),
        currency="USD",
        stripe_payment_intent_id="pi_test_escrow123",
        status=PaymentStatus.ESCROW_HELD,
        escrow_held_at=datetime.now(timezone.utc),
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    return payment
