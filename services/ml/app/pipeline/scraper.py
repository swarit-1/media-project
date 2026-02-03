import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ScrapedArticle:
    """Result of scraping an article URL."""

    url: str
    title: str
    text: str
    publication: Optional[str] = None
    published_date: Optional[datetime] = None
    byline: Optional[str] = None
    word_count: int = 0
    excerpt: str = ""


class ArticleScraper:
    """Service for scraping article content from URLs.

    Uses httpx for fetching and basic HTML parsing for extraction.
    In production, this would use Trafilatura or Crawl4AI for better extraction.
    """

    def __init__(self):
        self.timeout = settings.scrape_timeout_seconds
        self.max_retries = settings.max_scrape_retries

    async def scrape(self, url: str) -> Optional[ScrapedArticle]:
        """Scrape an article from the given URL."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "ElasticNewsroom/1.0 (portfolio-verification)"
                },
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            html = response.text
            article = self._extract_article(url, html)

            if article:
                logger.info(f"Successfully scraped: {url} ({article.word_count} words)")
            return article

        except httpx.TimeoutException:
            logger.warning(f"Timeout scraping {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error scraping {url}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def _extract_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Extract article content from HTML.

        Uses basic regex-based extraction. In production, use
        Trafilatura for robust article extraction.
        """
        try:
            # Try to use trafilatura if available
            import trafilatura
            result = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
                output_format="txt",
            )
            metadata = trafilatura.extract_metadata(html)

            if result:
                title = metadata.title if metadata else self._extract_title(html)
                publication = metadata.sitename if metadata else self._extract_publication(url)
                byline = metadata.author if metadata else None
                pub_date = None
                if metadata and metadata.date:
                    try:
                        pub_date = datetime.fromisoformat(metadata.date)
                    except (ValueError, TypeError):
                        pass

                text = result
                word_count = len(text.split())
                excerpt = text[:500] if text else ""

                return ScrapedArticle(
                    url=url,
                    title=title or "Untitled",
                    text=text,
                    publication=publication,
                    published_date=pub_date,
                    byline=byline,
                    word_count=word_count,
                    excerpt=excerpt,
                )
        except ImportError:
            pass

        # Fallback: basic extraction
        title = self._extract_title(html)
        text = self._extract_text(html)
        publication = self._extract_publication(url)
        word_count = len(text.split()) if text else 0
        excerpt = text[:500] if text else ""

        if not text or word_count < 50:
            return None

        return ScrapedArticle(
            url=url,
            title=title or "Untitled",
            text=text,
            publication=publication,
            word_count=word_count,
            excerpt=excerpt,
        )

    def _extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        # Try og:title first
        og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
        if og_match:
            return og_match.group(1)

        # Try <title> tag
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()

        # Try <h1>
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()

        return None

    def _extract_text(self, html: str) -> str:
        """Extract main text content from HTML (basic fallback)."""
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Decode HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        return text

    def _extract_publication(self, url: str) -> Optional[str]:
        """Extract publication name from URL domain."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www prefix
        domain = re.sub(r'^www\.', '', domain)
        # Get the main domain name
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2].capitalize()
        return domain

    def verify_byline(self, article: ScrapedArticle, freelancer_name: str) -> bool:
        """Check if the freelancer's name appears in the article byline or text."""
        name_lower = freelancer_name.lower()
        name_parts = name_lower.split()

        # Check byline
        if article.byline:
            byline_lower = article.byline.lower()
            if name_lower in byline_lower:
                return True
            # Check if last name appears
            if len(name_parts) > 1 and name_parts[-1] in byline_lower:
                return True

        # Check first few hundred characters of text
        text_start = article.text[:1000].lower()
        if name_lower in text_start:
            return True

        return False
