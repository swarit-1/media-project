import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..config import get_settings
from ..schemas.assignment import (
    AssignmentResponse,
    CMSWebhookPayload,
    CMSWebhookResponse,
)
from ..services.assignment_service import AssignmentService
from ..services.cms_webhook_service import CMSWebhookService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()
assignment_service = AssignmentService()
cms_webhook_service = CMSWebhookService()


@router.post("/cms/webhook", response_model=CMSWebhookResponse)
async def handle_cms_webhook(
    payload: CMSWebhookPayload,
    request: Request,
    x_webhook_signature: str = Header(None, alias="X-Webhook-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle CMS webhook events (article published, updated, etc.).

    CMS systems call this endpoint when articles are published.
    On publication, this triggers payment release for the assignment.
    """
    # Verify webhook signature if configured
    if settings.cms_webhook_secret and settings.cms_webhook_secret != "disabled":
        if not x_webhook_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "MISSING_SIGNATURE", "message": "Webhook signature required"},
            )
        body = await request.body()
        if not cms_webhook_service.verify_signature(
            body, x_webhook_signature, settings.cms_webhook_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_SIGNATURE", "message": "Invalid webhook signature"},
            )

    # Look up the assignment
    assignment = await assignment_service.get_assignment_by_id(db, payload.assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Assignment not found"},
        )

    payment_release_triggered = False

    if payload.event == "article.published":
        try:
            assignment = await cms_webhook_service.handle_article_published(
                db=db,
                assignment=assignment,
                cms_post_id=payload.cms_post_id,
                published_url=payload.published_url,
                published_at=payload.published_at,
                metadata=payload.metadata,
            )
            payment_release_triggered = True
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATE", "message": str(e)},
            )

    elif payload.event == "article.updated":
        try:
            assignment = await cms_webhook_service.handle_article_updated(
                db=db,
                assignment=assignment,
                published_url=payload.published_url,
                metadata=payload.metadata,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATE", "message": str(e)},
            )

    elif payload.event == "article.unpublished":
        logger.warning(
            "Article unpublished event received",
            extra={
                "assignment_id": str(payload.assignment_id),
                "cms_post_id": payload.cms_post_id,
            },
        )

    await db.commit()

    return CMSWebhookResponse(
        status="processed",
        assignment_id=assignment.id,
        assignment_status=assignment.status.value,
        payment_release_triggered=payment_release_triggered,
    )
