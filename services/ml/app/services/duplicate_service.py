import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.portfolio_item import PortfolioItem
from ..pipeline.embeddings import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()


class DuplicateService:
    """Service for detecting duplicate or similar pitches and content."""

    def __init__(self):
        self.embeddings = EmbeddingService()

    async def check_duplicate(
        self,
        db: AsyncSession,
        headline: str,
        summary: str,
        newsroom_id: UUID,
    ) -> dict:
        """Check if a pitch is a duplicate of existing content.

        Embeds the pitch headline + summary and searches for:
        1. Similar existing pitches for the same newsroom
        2. Similar published articles in the portfolio database
        """
        # Generate embedding for the pitch
        pitch_text = f"{headline}. {summary}"
        pitch_embedding = self.embeddings.encode(pitch_text)

        # Check against existing pitches (using raw SQL for pgvector)
        similar_pitches = await self._find_similar_pitches(
            db, pitch_embedding, newsroom_id
        )

        # Check against published portfolio items
        competing_coverage = await self._find_similar_articles(
            db, pitch_embedding
        )

        # Calculate overall duplicate score
        max_pitch_score = max(
            (p["overlap_score"] for p in similar_pitches), default=0.0
        )
        max_article_score = max(
            (a["overlap_score"] for a in competing_coverage), default=0.0
        )
        duplicate_score = max(max_pitch_score, max_article_score * 0.7)

        # Generate warning if high similarity found
        duplicate_warning = None
        if duplicate_score >= 0.8:
            duplicate_warning = "Very similar content already exists. Consider a different angle."
        elif duplicate_score >= settings.similarity_threshold:
            duplicate_warning = "Moderately similar content found. Ensure your pitch offers a unique perspective."

        return {
            "duplicate_score": round(duplicate_score, 2),
            "duplicate_warning": duplicate_warning,
            "style_match_score": None,
            "similar_pitches": similar_pitches,
            "competing_coverage": competing_coverage,
        }

    async def _find_similar_pitches(
        self,
        db: AsyncSession,
        embedding: list[float],
        newsroom_id: UUID,
    ) -> list[dict]:
        """Find similar pitches for the same newsroom.

        In production, this would query the pitches table with pgvector.
        For now, we use a simplified approach querying recent pitches.
        """
        # This is a simplified version - in production you would:
        # 1. Store pitch embeddings in a pitch_embeddings table
        # 2. Use pgvector cosine distance to find similar ones
        #
        # For now, return empty list as pitch embeddings storage
        # would require modifying the pitch service
        return []

    async def _find_similar_articles(
        self,
        db: AsyncSession,
        embedding: list[float],
    ) -> list[dict]:
        """Find similar published articles in the portfolio database.

        Computes similarity against portfolio item excerpts.
        """
        # Get recent portfolio items with excerpts
        result = await db.execute(
            select(PortfolioItem)
            .where(PortfolioItem.excerpt.isnot(None))
            .order_by(PortfolioItem.published_date.desc().nullslast())
            .limit(100)
        )
        items = list(result.scalars().all())

        similar = []
        for item in items:
            if item.excerpt:
                item_embedding = self.embeddings.encode(item.excerpt)
                score = self.embeddings.cosine_similarity(embedding, item_embedding)

                if score >= settings.similarity_threshold:
                    similar.append({
                        "id": str(item.id),
                        "title": item.title,
                        "entity_type": "article",
                        "overlap_score": round(score, 4),
                        "publication": item.publication,
                        "published_date": (
                            item.published_date.isoformat()
                            if item.published_date else None
                        ),
                    })

        # Sort by score descending
        similar.sort(key=lambda x: x["overlap_score"], reverse=True)
        return similar[:10]
