import pytest
from app.pipeline.nlp import NLPPipeline
from app.pipeline.embeddings import EmbeddingService


class TestNLPPipeline:
    """Test NLP analysis pipeline."""

    def setup_method(self):
        self.nlp = NLPPipeline()

    def test_analyze_article(self):
        """Test full NLP analysis on sample text."""
        text = (
            "The investigation revealed that several major tech companies "
            "had been sharing user data with third-party brokers without "
            "explicit consent. According to documents obtained by our team, "
            "the practice affected millions of users. Senator Jane Smith "
            "said the findings were 'deeply concerning' and called for "
            "immediate congressional action. The study found that 78% "
            "of users were unaware their data was being shared."
        )

        analysis = self.nlp.analyze(text, "Big Tech's Secret Data Deals")

        assert analysis.avg_sentence_length > 0
        assert 0 <= analysis.passive_voice_ratio <= 1
        assert 0 <= analysis.citation_density <= 1
        assert analysis.headline_style == "declarative"
        assert len(analysis.topics) >= 0

    def test_headline_classification(self):
        """Test headline style classification."""
        assert self.nlp._classify_headline("How to Write Better") == "how_to"
        assert self.nlp._classify_headline("Is AI Taking Over?") == "question"
        assert self.nlp._classify_headline("10 Ways to Improve") == "list"
        assert self.nlp._classify_headline("Congress Passes New Law") == "declarative"

    def test_keyword_topic_classification(self):
        """Test keyword-based topic classification."""
        tech_text = (
            "The new software startup raised $50M in funding. "
            "The AI-powered technology aims to disrupt Silicon Valley."
        )
        topics, scores = self.nlp._keyword_classify(tech_text)
        assert "tech" in topics

        health_text = (
            "The hospital announced a new treatment for the disease. "
            "Doctors said the clinical trial showed promising results "
            "for patients with the condition."
        )
        topics, scores = self.nlp._keyword_classify(health_text)
        assert "health" in topics


class TestEmbeddingService:
    """Test embedding service."""

    def setup_method(self):
        self.embeddings = EmbeddingService()

    def test_fallback_encode(self):
        """Test fallback embedding generation."""
        embedding = self.embeddings._fallback_encode("test text")
        assert len(embedding) == 384
        # Check normalized
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01

    def test_deterministic_encoding(self):
        """Test that fallback embeddings are deterministic."""
        emb1 = self.embeddings._fallback_encode("same text")
        emb2 = self.embeddings._fallback_encode("same text")
        assert emb1 == emb2

    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        emb1 = self.embeddings._fallback_encode("text one")
        emb2 = self.embeddings._fallback_encode("text two")
        assert emb1 != emb2

    def test_cosine_similarity(self):
        """Test cosine similarity computation."""
        emb1 = self.embeddings._fallback_encode("artificial intelligence")
        emb2 = self.embeddings._fallback_encode("artificial intelligence")
        similarity = self.embeddings.cosine_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.01

        emb3 = self.embeddings._fallback_encode("underwater basket weaving")
        similarity2 = self.embeddings.cosine_similarity(emb1, emb3)
        assert similarity2 < similarity
