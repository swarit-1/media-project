import json
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stripe_webhook_payment_succeeded(editor_client: AsyncClient):
    """Test handling a payment_intent.succeeded webhook."""
    event = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": 120000,
                "currency": "usd",
                "status": "succeeded",
            }
        },
    }

    response = await editor_client.post(
        "/api/v1/webhooks/stripe",
        content=json.dumps(event),
        headers={"stripe-signature": "test_sig"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"


@pytest.mark.asyncio
async def test_stripe_webhook_payment_failed(editor_client: AsyncClient):
    """Test handling a payment_intent.payment_failed webhook."""
    event = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_test_456",
                "amount": 80000,
                "status": "requires_payment_method",
            }
        },
    }

    response = await editor_client.post(
        "/api/v1/webhooks/stripe",
        content=json.dumps(event),
        headers={"stripe-signature": "test_sig"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"


@pytest.mark.asyncio
async def test_stripe_webhook_unknown_event(editor_client: AsyncClient):
    """Test handling an unknown webhook event type."""
    event = {
        "type": "unknown.event",
        "data": {"object": {}},
    }

    response = await editor_client.post(
        "/api/v1/webhooks/stripe",
        content=json.dumps(event),
        headers={"stripe-signature": "test_sig"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"
