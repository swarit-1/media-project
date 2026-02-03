import logging
import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.portfolio_item import PortfolioItem, VerificationStatus, OutletTier

logger = logging.getLogger(__name__)
settings = get_settings()

# Trust score feature weights
WEIGHTS = {
    "identity_verification": 0.15,
    "portfolio_quality": 0.20,
    "on_time_delivery": 0.20,
    "acceptance_rate": 0.15,
    "editor_ratings": 0.15,
    "platform_tenure": 0.05,
    "response_time": 0.10,
}


class TrustScoreService:
    """Service for computing freelancer trust scores.

    Uses a weighted composite model combining multiple signals:
    - Identity verification status
    - Portfolio quality (outlet tier + recency)
    - On-time delivery rate
    - Pitch acceptance rate
    - Editor ratings
    - Platform tenure
    - Response time

    Applies exponential smoothing to prevent score volatility.
    """

    async def compute_trust_score(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        previous_score: Optional[float] = None,
    ) -> dict:
        """Compute a trust score for a freelancer."""
        components = {}

        # 1. Identity verification (from freelancer profile)
        identity_score = await self._compute_identity_score(db, freelancer_id)
        components["identity_verification"] = identity_score

        # 2. Portfolio quality
        portfolio_score = await self._compute_portfolio_quality(db, freelancer_id)
        components["portfolio_quality"] = portfolio_score

        # 3. On-time delivery (from assignments)
        delivery_score = await self._compute_delivery_score(db, freelancer_id)
        components["on_time_delivery"] = delivery_score

        # 4. Acceptance rate (from pitches)
        acceptance_score = await self._compute_acceptance_rate(db, freelancer_id)
        components["acceptance_rate"] = acceptance_score

        # 5. Editor ratings (placeholder - needs feedback system)
        components["editor_ratings"] = 0.5  # Default neutral

        # 6. Platform tenure
        tenure_score = await self._compute_tenure_score(db, freelancer_id)
        components["platform_tenure"] = tenure_score

        # 7. Response time (placeholder - needs notification system)
        components["response_time"] = 0.5  # Default neutral

        # Compute weighted score
        raw_score = sum(
            components[key] * weight
            for key, weight in WEIGHTS.items()
        )

        # Clamp to [0, 1]
        raw_score = max(0.0, min(1.0, raw_score))

        # Apply exponential smoothing if previous score exists
        if previous_score is not None:
            smoothing = settings.trust_score_smoothing_factor
            final_score = (1 - smoothing) * raw_score + smoothing * previous_score
        else:
            final_score = raw_score

        final_score = round(max(0.0, min(1.0, final_score)), 4)

        return {
            "freelancer_id": freelancer_id,
            "trust_score": final_score,
            "previous_score": previous_score,
            "components": components,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _compute_identity_score(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> float:
        """Score based on identity/portfolio verification flags."""
        try:
            result = await db.execute(
                select(
                    func.coalesce(
                        select(func.literal(1)).where(
                            and_(
                                func.literal_column("identity_verified") == True,
                            )
                        ).correlate_except().scalar_subquery(),
                        0,
                    )
                )
            )
        except Exception:
            pass

        # Simplified: check portfolio verification count
        verified_count = await db.execute(
            select(func.count(PortfolioItem.id)).where(
                PortfolioItem.freelancer_id == freelancer_id,
                PortfolioItem.verification_status == VerificationStatus.VERIFIED,
            )
        )
        count = verified_count.scalar() or 0

        if count >= 5:
            return 1.0
        elif count >= 3:
            return 0.8
        elif count >= 1:
            return 0.6
        return 0.2

    async def _compute_portfolio_quality(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> float:
        """Score based on portfolio item quality and outlet tiers."""
        result = await db.execute(
            select(PortfolioItem).where(
                PortfolioItem.freelancer_id == freelancer_id,
                PortfolioItem.verification_status == VerificationStatus.VERIFIED,
            )
        )
        items = list(result.scalars().all())

        if not items:
            return 0.3

        # Score by outlet tier
        tier_scores = {
            OutletTier.TIER1: 1.0,
            OutletTier.TIER2: 0.7,
            OutletTier.TIER3: 0.4,
            OutletTier.UNKNOWN: 0.3,
        }

        total_score = sum(tier_scores.get(item.outlet_tier, 0.3) for item in items)
        avg_tier_score = total_score / len(items)

        # Bonus for recency (articles published in last 6 months)
        recent_count = sum(
            1 for item in items
            if item.published_date
            and (datetime.now(timezone.utc) - item.published_date.replace(tzinfo=timezone.utc)).days < 180
        )
        recency_bonus = min(recent_count * 0.05, 0.2)

        return min(avg_tier_score + recency_bonus, 1.0)

    async def _compute_delivery_score(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> float:
        """Score based on on-time delivery rate (from assignments).

        Queries the assignments table for completed assignments
        and checks deadline compliance.
        """
        try:
            # Query assignments - this accesses the pitch service tables
            from sqlalchemy import text as sa_text

            result = await db.execute(
                sa_text("""
                    SELECT
                        COUNT(*) as total,
                        COUNT(CASE WHEN completed_at <= deadline THEN 1 END) as on_time
                    FROM assignments
                    WHERE freelancer_id = :fid
                        AND status IN ('approved', 'killed')
                        AND completed_at IS NOT NULL
                """),
                {"fid": str(freelancer_id)},
            )
            row = result.first()
            if row and row.total > 0:
                return round(row.on_time / row.total, 4)
        except Exception:
            pass

        # Default: neutral score if no assignments found
        return 0.5

    async def _compute_acceptance_rate(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> float:
        """Score based on pitch acceptance rate."""
        try:
            from sqlalchemy import text as sa_text

            result = await db.execute(
                sa_text("""
                    SELECT
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted
                    FROM pitches
                    WHERE freelancer_id = :fid
                        AND status IN ('accepted', 'rejected')
                """),
                {"fid": str(freelancer_id)},
            )
            row = result.first()
            if row and row.total > 0:
                return round(row.accepted / row.total, 4)
        except Exception:
            pass

        return 0.5

    async def _compute_tenure_score(
        self, db: AsyncSession, freelancer_id: UUID
    ) -> float:
        """Score based on platform tenure (log-scaled months)."""
        try:
            from sqlalchemy import text as sa_text

            result = await db.execute(
                sa_text("""
                    SELECT created_at FROM users WHERE id = :uid
                """),
                {"uid": str(freelancer_id)},
            )
            row = result.first()
            if row and row.created_at:
                created = row.created_at
                if created.tzinfo is None:
                    from datetime import timezone
                    created = created.replace(tzinfo=timezone.utc)
                months = (datetime.now(timezone.utc) - created).days / 30
                # Log-scale: 12 months = ~0.8, 24 months = ~0.9
                return min(math.log1p(months) / math.log1p(24), 1.0)
        except Exception:
            pass

        return 0.1
