import logging
from decimal import Decimal
from typing import Optional

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StripeService:
    """Service for interacting with the Stripe API.

    In production, this would use the stripe Python SDK.
    For development, it provides mock implementations.
    """

    def __init__(self):
        self._is_test_mode = settings.stripe_secret_key.startswith("sk_test")

    async def create_payment_intent(
        self,
        amount_cents: int,
        currency: str = "usd",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create a Stripe PaymentIntent for escrow hold.

        Args:
            amount_cents: Amount in cents
            currency: Currency code (default: usd)
            metadata: Additional metadata for the payment intent

        Returns:
            Dict with payment intent details
        """
        if self._is_test_mode:
            # Mock response for test/development
            import uuid
            return {
                "id": f"pi_test_{uuid.uuid4().hex[:24]}",
                "amount": amount_cents,
                "currency": currency,
                "status": "requires_capture",
                "metadata": metadata or {},
            }

        # Production: use stripe SDK
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                capture_method="manual",  # For escrow-style hold
                metadata=metadata or {},
            )
            return {
                "id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status,
                "metadata": intent.metadata,
            }
        except Exception as e:
            logger.error(f"Stripe PaymentIntent creation failed: {e}")
            raise

    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount_cents: Optional[int] = None,
    ) -> dict:
        """Capture (settle) a previously authorized PaymentIntent.

        Args:
            payment_intent_id: The Stripe PaymentIntent ID
            amount_cents: Optional amount to capture (for partial captures)

        Returns:
            Dict with capture details
        """
        if self._is_test_mode:
            return {
                "id": payment_intent_id,
                "status": "succeeded",
                "amount_captured": amount_cents or 0,
            }

        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key

            params = {}
            if amount_cents:
                params["amount_to_capture"] = amount_cents

            intent = stripe.PaymentIntent.capture(payment_intent_id, **params)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount_captured": intent.amount_received,
            }
        except Exception as e:
            logger.error(f"Stripe capture failed: {e}")
            raise

    async def create_transfer(
        self,
        amount_cents: int,
        destination_account_id: str,
        transfer_group: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create a transfer to a connected account (freelancer payout).

        Args:
            amount_cents: Amount in cents
            destination_account_id: Stripe connected account ID
            transfer_group: Optional transfer group for linking
            metadata: Additional metadata

        Returns:
            Dict with transfer details
        """
        if self._is_test_mode:
            import uuid
            return {
                "id": f"tr_test_{uuid.uuid4().hex[:24]}",
                "amount": amount_cents,
                "destination": destination_account_id,
                "status": "paid",
            }

        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key

            params = {
                "amount": amount_cents,
                "currency": "usd",
                "destination": destination_account_id,
                "metadata": metadata or {},
            }
            if transfer_group:
                params["transfer_group"] = transfer_group

            transfer = stripe.Transfer.create(**params)
            return {
                "id": transfer.id,
                "amount": transfer.amount,
                "destination": transfer.destination,
                "status": "paid",
            }
        except Exception as e:
            logger.error(f"Stripe transfer failed: {e}")
            raise

    async def create_refund(
        self,
        payment_intent_id: str,
        amount_cents: Optional[int] = None,
        reason: str = "requested_by_customer",
    ) -> dict:
        """Create a refund for a payment.

        Args:
            payment_intent_id: The Stripe PaymentIntent ID to refund
            amount_cents: Optional amount for partial refund
            reason: Refund reason

        Returns:
            Dict with refund details
        """
        if self._is_test_mode:
            import uuid
            return {
                "id": f"re_test_{uuid.uuid4().hex[:24]}",
                "payment_intent": payment_intent_id,
                "amount": amount_cents or 0,
                "status": "succeeded",
            }

        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key

            params = {
                "payment_intent": payment_intent_id,
                "reason": reason,
            }
            if amount_cents:
                params["amount"] = amount_cents

            refund = stripe.Refund.create(**params)
            return {
                "id": refund.id,
                "payment_intent": refund.payment_intent,
                "amount": refund.amount,
                "status": refund.status,
            }
        except Exception as e:
            logger.error(f"Stripe refund failed: {e}")
            raise

    def verify_webhook_signature(
        self, payload: bytes, sig_header: str
    ) -> dict:
        """Verify a Stripe webhook signature.

        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header value

        Returns:
            Parsed webhook event
        """
        if self._is_test_mode:
            import json
            return json.loads(payload)

        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            raise
