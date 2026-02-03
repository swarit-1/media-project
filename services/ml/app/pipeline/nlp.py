import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TextAnalysis:
    """Result of NLP analysis on text content."""

    # Style metrics
    avg_sentence_length: float = 0.0
    passive_voice_ratio: float = 0.0
    narrative_score: float = 0.0
    analytical_score: float = 0.0
    explanatory_score: float = 0.0
    citation_density: float = 0.0

    # Topics
    topics: list[str] = field(default_factory=list)
    topic_scores: dict[str, float] = field(default_factory=dict)

    # Headline style
    headline_style: str = "declarative"

    # Readability
    readability_score: float = 0.0

    # Tone profile
    tone_profile: dict[str, float] = field(default_factory=dict)


# Common journalism beats/topics for zero-shot classification
JOURNALISM_TOPICS = [
    "politics", "government", "tech", "science", "health",
    "business", "finance", "environment", "education", "sports",
    "entertainment", "culture", "legal", "crime", "international",
    "investigations", "opinion", "lifestyle", "real_estate", "food",
]


class NLPPipeline:
    """NLP pipeline for analyzing article content.

    Computes style metrics, classifies topics, and extracts
    tone signals from text.
    """

    def __init__(self):
        self._classifier = None

    def analyze(self, text: str, title: str = "") -> TextAnalysis:
        """Run full NLP analysis on text content."""
        analysis = TextAnalysis()

        # Compute style metrics
        sentences = self._split_sentences(text)
        if sentences:
            analysis.avg_sentence_length = sum(
                len(s.split()) for s in sentences
            ) / len(sentences)

            analysis.passive_voice_ratio = self._compute_passive_voice_ratio(sentences)
            analysis.citation_density = self._compute_citation_density(text, sentences)

        # Compute tone scores
        analysis.narrative_score = self._compute_narrative_score(text)
        analysis.analytical_score = self._compute_analytical_score(text)
        analysis.explanatory_score = self._compute_explanatory_score(text)

        # Classify headline
        if title:
            analysis.headline_style = self._classify_headline(title)

        # Topic classification
        topics, scores = self._classify_topics(text)
        analysis.topics = topics
        analysis.topic_scores = scores

        # Build tone profile
        analysis.tone_profile = {
            "narrative": analysis.narrative_score,
            "analytical": analysis.analytical_score,
            "explanatory": analysis.explanatory_score,
            "passive_voice": analysis.passive_voice_ratio,
            "citation_density": analysis.citation_density,
        }

        # Readability (Flesch-Kincaid approximation)
        analysis.readability_score = self._compute_readability(text, sentences)

        return analysis

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def _compute_passive_voice_ratio(self, sentences: list[str]) -> float:
        """Estimate passive voice ratio."""
        passive_patterns = [
            r'\b(?:was|were|is|are|been|being|be)\s+\w+ed\b',
            r'\b(?:was|were|is|are|been|being|be)\s+\w+en\b',
            r'\bhas been\b', r'\bhave been\b', r'\bhad been\b',
        ]

        passive_count = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break

        return passive_count / len(sentences) if sentences else 0.0

    def _compute_citation_density(self, text: str, sentences: list[str]) -> float:
        """Compute citation/attribution density."""
        citation_patterns = [
            r'\bsaid\b', r'\baccording to\b', r'\btold\b',
            r'\breported\b', r'\bstated\b', r'\bconfirmed\b',
            r'\bexplained\b', r'\bnoted\b', r'\bsuggested\b',
            r'"[^"]*"',  # Direct quotes
        ]

        citation_count = 0
        for pattern in citation_patterns:
            citation_count += len(re.findall(pattern, text, re.IGNORECASE))

        return min(citation_count / max(len(sentences), 1), 1.0)

    def _compute_narrative_score(self, text: str) -> float:
        """Estimate how narrative/storytelling the writing is."""
        narrative_markers = [
            r'\bonce\b', r'\bwhen\b', r'\bthen\b', r'\bafter\b',
            r'\bbefore\b', r'\bwhile\b', r'\bduring\b',
            r'\bremember\b', r'\bexperience\b', r'\bstory\b',
            r'\bjourney\b', r'\bmoment\b',
        ]

        count = 0
        for marker in narrative_markers:
            count += len(re.findall(marker, text, re.IGNORECASE))

        word_count = len(text.split())
        density = count / max(word_count, 1) * 100

        return min(density / 2.0, 1.0)

    def _compute_analytical_score(self, text: str) -> float:
        """Estimate how analytical the writing is."""
        analytical_markers = [
            r'\banalysis\b', r'\bdata\b', r'\bresearch\b',
            r'\bstudy\b', r'\bfindings\b', r'\bevidence\b',
            r'\bstatistics\b', r'\bpercent\b', r'\b\d+%',
            r'\bhowever\b', r'\btherefore\b', r'\bconsequently\b',
            r'\bfurthermore\b', r'\bmoreover\b', r'\bnevertheless\b',
        ]

        count = 0
        for marker in analytical_markers:
            count += len(re.findall(marker, text, re.IGNORECASE))

        word_count = len(text.split())
        density = count / max(word_count, 1) * 100

        return min(density / 2.0, 1.0)

    def _compute_explanatory_score(self, text: str) -> float:
        """Estimate how explanatory the writing is."""
        explanatory_markers = [
            r'\bmeans\b', r'\bexplain\b', r'\bbecause\b',
            r'\bin other words\b', r'\bfor example\b', r'\bsuch as\b',
            r'\bdefine\b', r'\bwork\b', r'\bhow\b',
            r'\bwhat\b', r'\bwhy\b', r'\bprocess\b',
        ]

        count = 0
        for marker in explanatory_markers:
            count += len(re.findall(marker, text, re.IGNORECASE))

        word_count = len(text.split())
        density = count / max(word_count, 1) * 100

        return min(density / 2.0, 1.0)

    def _classify_headline(self, title: str) -> str:
        """Classify the headline style."""
        title_lower = title.lower().strip()

        if title_lower.endswith('?'):
            return "question"
        if re.match(r'^how\s+', title_lower):
            return "how_to"
        if re.match(r'^\d+\s+', title_lower):
            return "list"
        return "declarative"

    def _classify_topics(
        self, text: str
    ) -> tuple[list[str], dict[str, float]]:
        """Classify text into journalism topics.

        Uses zero-shot classification if transformers are available,
        otherwise falls back to keyword matching.
        """
        # Try zero-shot classification
        try:
            return self._zero_shot_classify(text)
        except Exception:
            pass

        # Fallback: keyword-based classification
        return self._keyword_classify(text)

    def _zero_shot_classify(
        self, text: str
    ) -> tuple[list[str], dict[str, float]]:
        """Zero-shot classification using transformers."""
        if self._classifier is None:
            from transformers import pipeline
            self._classifier = pipeline(
                "zero-shot-classification",
                model=settings.topic_model,
            )

        # Use first 512 tokens for classification
        truncated = " ".join(text.split()[:512])
        result = self._classifier(
            truncated,
            candidate_labels=JOURNALISM_TOPICS,
            multi_label=True,
        )

        scores = dict(zip(result["labels"], result["scores"]))
        topics = [
            label for label, score in scores.items()
            if score > 0.3
        ][:5]

        return topics, scores

    def _keyword_classify(
        self, text: str
    ) -> tuple[list[str], dict[str, float]]:
        """Fallback keyword-based topic classification."""
        text_lower = text.lower()

        topic_keywords = {
            "politics": ["congress", "senator", "president", "election", "vote", "democrat", "republican", "legislation", "policy", "campaign"],
            "tech": ["technology", "software", "startup", "silicon valley", "ai", "artificial intelligence", "algorithm", "digital", "data", "app"],
            "health": ["health", "medical", "doctor", "patient", "hospital", "vaccine", "disease", "treatment", "healthcare", "clinical"],
            "business": ["business", "company", "market", "revenue", "profit", "ceo", "corporate", "industry", "economy", "trade"],
            "finance": ["wall street", "stock", "investor", "bank", "financial", "crypto", "bitcoin", "interest rate", "federal reserve", "gdp"],
            "science": ["research", "scientist", "study", "experiment", "discovery", "university", "lab", "nasa", "space", "climate"],
            "environment": ["environment", "climate change", "pollution", "renewable", "carbon", "emission", "conservation", "wildlife", "sustainability"],
            "education": ["school", "student", "teacher", "university", "education", "curriculum", "campus", "degree", "academic"],
            "legal": ["court", "judge", "lawyer", "lawsuit", "trial", "verdict", "attorney", "legal", "ruling", "justice"],
            "crime": ["police", "arrest", "crime", "murder", "investigation", "suspect", "victim", "prison", "fbi", "shooting"],
            "international": ["international", "foreign", "diplomat", "united nations", "treaty", "overseas", "global", "nato"],
            "investigations": ["investigation", "leaked", "documents", "whistleblower", "uncovered", "revealed", "expose", "scandal"],
        }

        scores = {}
        for topic, keywords in topic_keywords.items():
            count = sum(
                1 for kw in keywords if kw in text_lower
            )
            score = min(count / max(len(keywords) * 0.3, 1), 1.0)
            if score > 0:
                scores[topic] = round(score, 4)

        # Sort by score and take top topics
        sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        topics = [t for t, s in sorted_topics if s > 0.1][:5]

        return topics, scores

    def _compute_readability(self, text: str, sentences: list[str]) -> float:
        """Compute Flesch Reading Ease score (simplified)."""
        words = text.split()
        word_count = len(words)
        sentence_count = max(len(sentences), 1)

        # Approximate syllable count
        syllable_count = sum(self._count_syllables(w) for w in words)

        if word_count == 0:
            return 0.0

        # Flesch Reading Ease formula
        score = (
            206.835
            - 1.015 * (word_count / sentence_count)
            - 84.6 * (syllable_count / word_count)
        )

        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count for a word."""
        word = word.lower().strip(".,!?;:'\"")
        if not word:
            return 0
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(1, count)
