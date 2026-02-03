import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models.payment import Payment, PaymentStatus
from tests.conftest import FREELANCER_ID, EDITOR_ID, NEWSROOM_ID, ASSIGNMENT_ID


@pytest.mark.asyncio
async def test_create_payment(editor_client: AsyncClient):
    """Test creating a payment as an editor."""
    response = await editor_client.post(
        "/api/v1/payments",
        json={
            "assignment_id": str(ASSIGNMENT_ID),
            "newsroom_id": str(NEWSROOM_ID),
            "freelancer_id": str(FREELANCER_ID),
            "payment_type": "assignment",
            "gross_amount": "1500.00",
            "description": "Payment for investigative article",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert float(data["gross_amount"]) == 1500.00
    assert float(data["platform_fee"]) == 150.00  # 10% fee
    assert float(data["net_amount"]) == 1350.00
    assert data["status"] == "pending"
    assert data["freelancer_id"] == str(FREELANCER_ID)


@pytest.mark.asyncio
async def test_get_payment(
    freelancer_client: AsyncClient,
    sample_payment: Payment,
):
    """Test getting a specific payment."""
    response = await freelancer_client.get(
        f"/api/v1/payments/{sample_payment.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_payment.id)
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_my_payments(
    freelancer_client: AsyncClient,
    sample_payment: Payment,
):
    """Test listing payments for the current freelancer."""
    response = await freelancer_client.get("/api/v1/payments/my")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_hold_escrow(
    editor_client: AsyncClient,
    sample_payment: Payment,
):
    """Test holding funds in escrow."""
    response = await editor_client.post(
        f"/api/v1/payments/{sample_payment.id}/escrow"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "escrow_held"
    assert data["escrow_held_at"] is not None
    assert data["stripe_payment_intent_id"] is not None


@pytest.mark.asyncio
async def test_release_payment(
    editor_client: AsyncClient,
    sample_escrow_payment: Payment,
):
    """Test releasing payment from escrow."""
    response = await editor_client.post(
        f"/api/v1/payments/{sample_escrow_payment.id}/release"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["release_triggered_at"] is not None


@pytest.mark.asyncio
async def test_complete_payment(
    editor_client: AsyncClient,
    sample_escrow_payment: Payment,
    db_session,
):
    """Test completing a payment after processing."""
    # Move to processing state
    sample_escrow_payment.status = PaymentStatus.PROCESSING
    await db_session.commit()

    response = await editor_client.post(
        f"/api/v1/payments/{sample_escrow_payment.id}/complete"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_refund_payment(
    editor_client: AsyncClient,
    sample_escrow_payment: Payment,
):
    """Test refunding a payment in escrow."""
    response = await editor_client.post(
        f"/api/v1/payments/{sample_escrow_payment.id}/refund"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "refunded"


@pytest.mark.asyncio
async def test_invalid_escrow_transition(
    editor_client: AsyncClient,
    sample_escrow_payment: Payment,
):
    """Test that invalid state transitions are rejected."""
    # Trying to hold escrow on a payment already in escrow
    response = await editor_client.post(
        f"/api/v1/payments/{sample_escrow_payment.id}/escrow"
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_STATE"


@pytest.mark.asyncio
async def test_payment_not_found(editor_client: AsyncClient):
    """Test getting a nonexistent payment."""
    from uuid import uuid4
    response = await editor_client.get(
        f"/api/v1/payments/{uuid4()}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_newsroom_payments(
    editor_client: AsyncClient,
    sample_payment: Payment,
):
    """Test listing payments for a newsroom."""
    response = await editor_client.get("/api/v1/payments/newsroom")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
