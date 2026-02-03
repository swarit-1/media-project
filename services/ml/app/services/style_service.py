import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.portfolio_item import PortfolioItem, VerificationStatus
from ..models.style_fingerprint import StyleFingerprint
from ..pipeline.nlp import NLPPipeline
from ..pipeline.embeddings import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()


class StyleService:
    """Service for computing and querying style fingerprints."""

    def __init__(self):
        self.nlp = NLPPipeline()
        self.embeddings = EmbeddingService()

    async def compute_fingerprint(
        self,
        db: AsyncSession,
        entity_id: UUID,
        entity_type: str = "freelancer",
    ) -> Optional[StyleFingerprint]:
        """Compute or update a style fingerprint from portfolio items.

        Analyzes all verified portfolio items for a freelancer and
        generates aggregate style metrics and an embedding.
        """
        if entity_type == "freelancer":
            # Get verified portfolio items
            result = await db.execute(
                select(PortfolioItem)
                .where(
                    PortfolioItem.freelancer_id == entity_id,
                    PortfolioItem.verification_status == VerificationStatus.VERIFIED,
                )
                .order_by(PortfolioItem.published_date.desc().nullslast())
                .limit(50)
            )
            items = list(result.scalars().all())
        else:
            items = []

        if not items:
            logger.info(f"No verified items for {entity_type}:{entity_id}")
            return None

        # Aggregate style metrics from tone profiles
        metrics = {
            "avg_sentence_length": [],
            "passive_voice_ratio": [],
            "narrative_score": [],
            "analytical_score": [],
            "explanatory_score": [],
            "citation_density": [],
        }

        texts = []
        for item in items:
            if item.tone_profile:
                for key in metrics:
                    if key in item.tone_profile:
                        metrics[key].append(float(item.tone_profile[key]))
            if item.excerpt:
                texts.append(item.excerpt)

        # Compute averages
        avg_metrics = {}
        for key, values in metrics.items():
            if values:
                avg_metrics[key] = Decimal(str(round(sum(values) / len(values), 4)))
            else:
                avg_metrics[key] = None

        # Generate aggregate style embedding from excerpts
        style_embedding = None
        if texts:
            embeddings = self.embeddings.encode_batch(texts)
            # Average the embeddings
            import numpy as np
            avg_embedding = np.mean(embeddings, axis=0)
            norm = np.linalg.norm(avg_embedding)
            if norm > 0:
                avg_embedding = avg_embedding / norm
            style_embedding = avg_embedding.tolist()

        # Get or create fingerprint
        existing = await self._get_fingerprint(db, entity_id, entity_type)

        if existing:
            fingerprint = existing
            fingerprint.avg_sentence_length = avg_metrics.get("avg_sentence_length")
            fingerprint.passive_voice_ratio = avg_metrics.get("passive_voice_ratio")
            fingerprint.narrative_score = avg_metrics.get("narrative_score")
            fingerprint.analytical_score = avg_metrics.get("analytical_score")
            fingerprint.explanatory_score = avg_metrics.get("explanatory_score")
            fingerprint.citation_density = avg_metrics.get("citation_density")
            fingerprint.style_embedding = style_embedding
            fingerprint.sample_size = len(items)
            fingerprint.computed_at = datetime.now(timezone.utc)
        else:
            fingerprint = StyleFingerprint(
                entity_id=entity_id,
                entity_type=entity_type,
                avg_sentence_length=avg_metrics.get("avg_sentence_length"),
                passive_voice_ratio=avg_metrics.get("passive_voice_ratio"),
                narrative_score=avg_metrics.get("narrative_score"),
                analytical_score=avg_metrics.get("analytical_score"),
                explanatory_score=avg_metrics.get("explanatory_score"),
                citation_density=avg_metrics.get("citation_density"),
                style_embedding=style_embedding,
                sample_size=len(items),
                computed_at=datetime.now(timezone.utc),
            )
            db.add(fingerprint)

        await db.flush()
        await db.refresh(fingerprint)
        return fingerprint

    async def get_fingerprint(
        self,
        db: AsyncSession,
        entity_id: UUID,
        entity_type: str = "freelancer",
    ) -> Optional[StyleFingerprint]:
        """Get a style fingerprint."""
        return await self._get_fingerprint(db, entity_id, entity_type)

    async def find_style_matches(
        self,
        db: AsyncSession,
        newsroom_id: UUID,
        limit: int = 20,
        min_score: float = 0.5,
    ) -> list[dict]:
        """Find freelancers whose style matches a newsroom's fingerprint.

        Uses pgvector cosine distance for approximate nearest neighbor search.
        """
        # Get newsroom fingerprint
        newsroom_fp = await self._get_fingerprint(db, newsroom_id, "newsroom")
        if not newsroom_fp or newsroom_fp.style_embedding is None:
            return []

        # Query freelancer fingerprints by embedding similarity
        # Using pgvector's <=> operator for cosine distance
        try:
            query = sa_text("""
                SELECT
                    sf.entity_id as freelancer_id,
                    1 - (sf.style_embedding <=> :embedding) as style_score
                FROM style_fingerprints sf
                WHERE sf.entity_type = 'freelancer'
                    AND sf.style_embedding IS NOT NULL
                    AND 1 - (sf.style_embedding <=> :embedding) >= :min_score
                ORDER BY sf.style_embedding <=> :embedding
                LIMIT :limit
            """)

            result = await db.execute(
                query,
                {
                    "embedding": str(newsroom_fp.style_embedding),
                    "min_score": min_score,
                    "limit": limit,
                },
            )

            matches = []
            for row in result:
                matches.append({
                    "freelancer_id": row.freelancer_id,
                    "style_score": round(float(row.style_score), 4),
                })

            return matches

        except Exception as e:
            logger.error(f"Style match query failed: {e}")
            # Fallback: compute manually if pgvector query fails
            return await self._fallback_style_match(
                db, newsroom_fp, limit, min_score
            )

    async def _get_fingerprint(
        self,
        db: AsyncSession,
        entity_id: UUID,
        entity_type: str,
    ) -> Optional[StyleFingerprint]:
        """Get a fingerprint by entity."""
        result = await db.execute(
            select(StyleFingerprint).where(
                StyleFingerprint.entity_id == entity_id,
                StyleFingerprint.entity_type == entity_type,
            )
        )
        return result.scalar_one_or_none()

    async def _fallback_style_match(
        self,
        db: AsyncSession,
        newsroom_fp: StyleFingerprint,
        limit: int,
        min_score: float,
    ) -> list[dict]:
        """Fallback style matching without pgvector operators."""
        result = await db.execute(
            select(StyleFingerprint).where(
                StyleFingerprint.entity_type == "freelancer",
                StyleFingerprint.style_embedding.isnot(None),
            )
        )
        freelancer_fps = list(result.scalars().all())

        matches = []
        for fp in freelancer_fps:
            if fp.style_embedding is not None and newsroom_fp.style_embedding is not None:
                score = self.embeddings.cosine_similarity(
                    newsroom_fp.style_embedding,
                    fp.style_embedding,
                )
                if score >= min_score:
                    matches.append({
                        "freelancer_id": fp.entity_id,
                        "style_score": round(score, 4),
                    })

        matches.sort(key=lambda x: x["style_score"], reverse=True)
        return matches[:limit]
