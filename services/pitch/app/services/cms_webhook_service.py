import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.assignment import Assignment, AssignmentStatus
from ..schemas.assignment import AssignmentStatusUpdate

logger = logging.getLogger(__name__)


class CMSWebhookService:
    """Service for handling CMS webhook events."""

    def verify_signature(
        self,
        payload_body: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify HMAC-SHA256 webhook signature."""
        expected = hmac.new(
            secret.encode("utf-8"),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_article_published(
        self,
        db: AsyncSession,
        assignment: Assignment,
        cms_post_id: str,
        published_url: str,
        published_at: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> Assignment:
        """Handle article.published event from CMS."""
        if assignment.status != AssignmentStatus.APPROVED:
            raise ValueError(
                f"Cannot publish: assignment is {assignment.status.value}, expected approved"
            )

        now = published_at or datetime.now(timezone.utc)

        assignment.status = AssignmentStatus.PUBLISHED
        assignment.cms_post_id = cms_post_id
        assignment.final_url = published_url
        assignment.published_at = now

        if metadata:
            existing_meta = assignment.metadata_json or {}
            existing_meta["cms_metadata"] = metadata
            assignment.metadata_json = existing_meta

        await db.flush()
        await db.refresh(assignment)

        logger.info(
            "Assignment published via CMS webhook",
            extra={
                "assignment_id": str(assignment.id),
                "cms_post_id": cms_post_id,
                "published_url": published_url,
            },
        )

        return assignment

    async def handle_article_updated(
        self,
        db: AsyncSession,
        assignment: Assignment,
        published_url: str,
        metadata: Optional[dict] = None,
    ) -> Assignment:
        """Handle article.updated event from CMS."""
        if assignment.status != AssignmentStatus.PUBLISHED:
            raise ValueError(
                f"Cannot update published article: assignment is {assignment.status.value}"
            )

        assignment.final_url = published_url

        if metadata:
            existing_meta = assignment.metadata_json or {}
            existing_meta["cms_metadata"] = metadata
            assignment.metadata_json = existing_meta

        await db.flush()
        await db.refresh(assignment)
        return assignment
