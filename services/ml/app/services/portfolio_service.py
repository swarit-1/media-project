import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.portfolio_item import PortfolioItem, VerificationStatus, OutletTier
from ..models.topic_classification import TopicClassification
from ..pipeline.scraper import ArticleScraper
from ..pipeline.nlp import NLPPipeline
from ..pipeline.embeddings import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()

# Known tier-1 publications
TIER1_PUBLICATIONS = {
    "nytimes", "washingtonpost", "wsj", "reuters", "apnews",
    "bbc", "guardian", "propublica", "theatlantic", "newyorker",
    "economist", "bloomberg", "cnn", "npr",
}

TIER2_PUBLICATIONS = {
    "politico", "axios", "vox", "slate", "salon", "thehill",
    "thedailybeast", "buzzfeed", "vice", "wired", "arstechnica",
    "techcrunch", "theverge", "huffpost", "usatoday",
}


class PortfolioService:
    """Service for managing portfolio items and ingestion pipeline."""

    def __init__(self):
        self.scraper = ArticleScraper()
        self.nlp = NLPPipeline()
        self.embeddings = EmbeddingService()

    async def ingest_url(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        url: str,
        freelancer_name: Optional[str] = None,
    ) -> Optional[PortfolioItem]:
        """Ingest a single URL through the portfolio pipeline."""
        # Check if already exists
        existing = await self._get_by_url(db, freelancer_id, url)
        if existing:
            logger.info(f"Portfolio item already exists: {url}")
            return existing

        # Scrape the article
        article = await self.scraper.scrape(url)
        if not article:
            logger.warning(f"Failed to scrape: {url}")
            return None

        # Run NLP analysis
        analysis = self.nlp.analyze(article.text, article.title)

        # Determine outlet tier
        outlet_tier = self._classify_outlet(url)

        # Determine verification status
        verification_status = VerificationStatus.PENDING
        verification_method = "automated_scrape"
        if freelancer_name and self.scraper.verify_byline(article, freelancer_name):
            verification_status = VerificationStatus.VERIFIED
            verification_method = "automated_scrape"

        # Create portfolio item
        item = PortfolioItem(
            freelancer_id=freelancer_id,
            url=url,
            title=article.title,
            publication=article.publication,
            published_date=article.published_date,
            byline=article.byline,
            word_count=article.word_count,
            excerpt=article.excerpt,
            topics=analysis.topics,
            tone_profile=analysis.tone_profile,
            outlet_tier=outlet_tier,
            verification_status=verification_status,
            verification_method=verification_method,
            scraped_at=datetime.now(timezone.utc),
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)

        # Store topic classification
        if analysis.topics:
            topic = TopicClassification(
                entity_id=item.id,
                entity_type="portfolio_item",
                primary_topic=analysis.topics[0],
                primary_confidence=analysis.topic_scores.get(analysis.topics[0], 0.0),
                secondary_topic=analysis.topics[1] if len(analysis.topics) > 1 else None,
                secondary_confidence=(
                    analysis.topic_scores.get(analysis.topics[1], 0.0)
                    if len(analysis.topics) > 1 else None
                ),
                all_scores=analysis.topic_scores,
            )
            db.add(topic)
            await db.flush()

        return item

    async def get_portfolio_item(
        self, db: AsyncSession, item_id: UUID
    ) -> Optional[PortfolioItem]:
        """Get a portfolio item by ID."""
        result = await db.execute(
            select(PortfolioItem).where(PortfolioItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_freelancer_portfolio(
        self,
        db: AsyncSession,
        freelancer_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PortfolioItem], int]:
        """List portfolio items for a freelancer."""
        query = select(PortfolioItem).where(
            PortfolioItem.freelancer_id == freelancer_id
        )
        count_query = select(func.count(PortfolioItem.id)).where(
            PortfolioItem.freelancer_id == freelancer_id
        )

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(PortfolioItem.published_date.desc().nullslast())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def _get_by_url(
        self, db: AsyncSession, freelancer_id: UUID, url: str
    ) -> Optional[PortfolioItem]:
        """Check if a URL already exists in the portfolio."""
        result = await db.execute(
            select(PortfolioItem).where(
                PortfolioItem.freelancer_id == freelancer_id,
                PortfolioItem.url == url,
            )
        )
        return result.scalar_one_or_none()

    def _classify_outlet(self, url: str) -> OutletTier:
        """Classify the outlet tier based on URL domain."""
        from urllib.parse import urlparse
        import re

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain = re.sub(r'^www\.', '', domain)
        domain_key = domain.split('.')[0] if '.' in domain else domain

        if domain_key in TIER1_PUBLICATIONS:
            return OutletTier.TIER1
        if domain_key in TIER2_PUBLICATIONS:
            return OutletTier.TIER2

        # Check full domain for compound names
        domain_clean = domain.replace('.', '').replace('-', '')
        for t1 in TIER1_PUBLICATIONS:
            if t1 in domain_clean:
                return OutletTier.TIER1
        for t2 in TIER2_PUBLICATIONS:
            if t2 in domain_clean:
                return OutletTier.TIER2

        return OutletTier.TIER3
