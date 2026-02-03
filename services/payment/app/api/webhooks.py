import logging
from fastapi import APIRouter, Request, HTTPException, status

from ..services.stripe_service import StripeService

router = APIRouter()
stripe_service = StripeService()
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events.

    Stripe sends events for payment status changes, disputes, etc.
    This endpoint verifies the webhook signature and processes events.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe_service.verify_webhook_signature(payload, sig_header)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SIGNATURE", "message": "Invalid webhook signature"},
        )

    event_type = event.get("type", "")

    if event_type == "payment_intent.succeeded":
        logger.info(f"Payment intent succeeded: {event.get('data', {}).get('object', {}).get('id')}")
        # In production: update payment status to completed

    elif event_type == "payment_intent.payment_failed":
        logger.info(f"Payment intent failed: {event.get('data', {}).get('object', {}).get('id')}")
        # In production: update payment status to failed

    elif event_type == "charge.refunded":
        logger.info(f"Charge refunded: {event.get('data', {}).get('object', {}).get('id')}")
        # In production: update payment status to refunded

    elif event_type == "transfer.paid":
        logger.info(f"Transfer paid: {event.get('data', {}).get('object', {}).get('id')}")
        # In production: update freelancer payout status

    elif event_type == "charge.dispute.created":
        logger.warning(f"Dispute created: {event.get('data', {}).get('object', {}).get('id')}")
        # In production: alert team and hold future payments

    else:
        logger.debug(f"Unhandled webhook event type: {event_type}")

    return {"status": "received"}
