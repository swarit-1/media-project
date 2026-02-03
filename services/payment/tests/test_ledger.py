import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient

from app.models.vendor_ledger import VendorLedgerEntry, LedgerEntryType
from tests.conftest import FREELANCER_ID, NEWSROOM_ID


@pytest.fixture
async def sample_ledger_entries(db_session) -> list[VendorLedgerEntry]:
    """Create sample ledger entries."""
    entries = [
        VendorLedgerEntry(
            id=uuid4(),
            payment_id=uuid4(),
            freelancer_id=FREELANCER_ID,
            newsroom_id=NEWSROOM_ID,
            entry_type=LedgerEntryType.PAYMENT,
            amount=Decimal("1080.00"),
            running_balance=Decimal("1080.00"),
            description="Assignment payment completed",
        ),
        VendorLedgerEntry(
            id=uuid4(),
            payment_id=uuid4(),
            freelancer_id=FREELANCER_ID,
            newsroom_id=NEWSROOM_ID,
            entry_type=LedgerEntryType.PAYMENT,
            amount=Decimal("720.00"),
            running_balance=Decimal("1800.00"),
            description="Second assignment payment",
        ),
    ]
    for entry in entries:
        db_session.add(entry)
    await db_session.commit()
    return entries


@pytest.mark.asyncio
async def test_list_my_ledger(
    freelancer_client: AsyncClient,
    sample_ledger_entries: list[VendorLedgerEntry],
):
    """Test listing ledger entries for the current freelancer."""
    response = await freelancer_client.get("/api/v1/ledger/my")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) == 2


@pytest.mark.asyncio
async def test_get_my_balance(
    freelancer_client: AsyncClient,
    sample_ledger_entries: list[VendorLedgerEntry],
):
    """Test getting current balance."""
    response = await freelancer_client.get("/api/v1/ledger/balance")

    assert response.status_code == 200
    data = response.json()
    assert data["freelancer_id"] == str(FREELANCER_ID)
    assert data["currency"] == "USD"


@pytest.mark.asyncio
async def test_empty_ledger(freelancer_client: AsyncClient):
    """Test getting balance with no entries."""
    response = await freelancer_client.get("/api/v1/ledger/balance")

    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "0.00"
