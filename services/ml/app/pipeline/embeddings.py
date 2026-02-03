import logging
from typing import Optional

import numpy as np

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers.

    Uses all-MiniLM-L6-v2 (384 dimensions) for fast, quality embeddings.
    Falls back to a simple TF-IDF-based approach if sentence-transformers
    is not available.
    """

    def __init__(self):
        self._model = None
        self._dimension = settings.embedding_dimension

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(settings.embedding_model)
            logger.info(f"Loaded embedding model: {settings.embedding_model}")
        except ImportError:
            logger.warning(
                "sentence-transformers not available. Using fallback embeddings."
            )
            self._model = "fallback"

    def encode(self, text: str) -> list[float]:
        """Encode text into a fixed-dimension embedding vector."""
        self._load_model()

        if self._model == "fallback":
            return self._fallback_encode(text)

        try:
            embedding = self._model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._fallback_encode(text)

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode multiple texts into embeddings."""
        self._load_model()

        if self._model == "fallback":
            return [self._fallback_encode(t) for t in texts]

        try:
            embeddings = self._model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return [self._fallback_encode(t) for t in texts]

    def cosine_similarity(
        self, embedding_a: list[float], embedding_b: list[float]
    ) -> float:
        """Compute cosine similarity between two embeddings."""
        a = np.array(embedding_a)
        b = np.array(embedding_b)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def _fallback_encode(self, text: str) -> list[float]:
        """Generate a simple hash-based embedding as fallback.

        This provides consistent, deterministic embeddings for development
        and testing when sentence-transformers is not installed.
        """
        import hashlib

        # Create a deterministic embedding from text hash
        text_bytes = text.lower().encode('utf-8')
        hash_bytes = hashlib.sha512(text_bytes).digest()

        # Extend hash to fill embedding dimension
        embedding = []
        idx = 0
        while len(embedding) < self._dimension:
            if idx >= len(hash_bytes):
                # Re-hash to get more bytes
                text_bytes = hash_bytes + str(idx).encode()
                hash_bytes = hashlib.sha512(text_bytes).digest()
                idx = 0
            # Convert byte to float in [-1, 1] range
            val = (hash_bytes[idx] / 255.0) * 2 - 1
            embedding.append(val)
            idx += 1

        # Normalize
        embedding = np.array(embedding[:self._dimension])
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()
