import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient

from app.models.compliance_record import ComplianceRecord
from tests.conftest import FREELANCER_ID, ADMIN_ID


@pytest.fixture
async def sample_compliance_record(db_session) -> ComplianceRecord:
    """Create a sample compliance record."""
    record = ComplianceRecord(
        id=uuid4(),
        freelancer_id=FREELANCER_ID,
        tax_year=datetime.now().year,
        total_gross_payments=Decimal("5000.00"),
        total_platform_fees=Decimal("500.00"),
        total_net_payments=Decimal("4500.00"),
        payment_count=5,
        w9_received=True,
        tin_last_four="1234",
        exceeds_threshold=True,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record


@pytest.mark.asyncio
async def test_get_my_compliance(
    freelancer_client: AsyncClient,
    sample_compliance_record: ComplianceRecord,
):
    """Test getting compliance record for the current freelancer."""
    response = await freelancer_client.get(
        f"/api/v1/compliance/my?tax_year={datetime.now().year}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["freelancer_id"] == str(FREELANCER_ID)
    assert float(data["total_gross_payments"]) == 5000.00
    assert data["exceeds_threshold"] is True


@pytest.mark.asyncio
async def test_get_compliance_summary(
    admin_client: AsyncClient,
    sample_compliance_record: ComplianceRecord,
):
    """Test getting compliance summary as admin."""
    response = await admin_client.get(
        f"/api/v1/compliance/summary?tax_year={datetime.now().year}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_freelancers"] >= 1
    assert data["freelancers_exceeding_threshold"] >= 1


@pytest.mark.asyncio
async def test_compliance_no_record(freelancer_client: AsyncClient):
    """Test getting compliance when no record exists."""
    response = await freelancer_client.get(
        "/api/v1/compliance/my?tax_year=2020"
    )

    assert response.status_code == 404
