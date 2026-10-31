"""Semantic Memory Vector Engine for Module 3.

Provides dense vector encoding via sentence-transformers (all-MiniLM-L6-v2)
and cosine similarity matching for agent critiques, code diffs, and query retrieval.
"""

from __future__ import annotations

import logging
from typing import List, Sequence
import numpy as np

logger = logging.getLogger(__name__)


class MemoryEngine:
    """Vector encoder and cosine similarity search engine."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the sentence transformer model.

        Args:
            model_name: HuggingFace model identifier. Defaults to 'all-MiniLM-L6-v2'.
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy loader for SentenceTransformer model to optimize startup time."""
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            from sentence_transformers import SentenceTransformer
            try:
                # Load from local HuggingFace cache first for instant startup
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                # Fallback to downloading if not yet cached
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def generate_embedding(
        self,
        failure_signature: str,
        root_cause: str,
        fix_strategy: str,
    ) -> List[float]:
        """Encode agent critique into a 384-dimensional dense float vector.

        Format: 'Failure: {failure_signature}. Cause: {root_cause}. Strategy: {fix_strategy}'

        Args:
            failure_signature: Short error/failure identifier.
            root_cause: Detailed diagnosis of why the code failed.
            fix_strategy: Actionable remedy or architectural fix.

        Returns:
            List of 384 floating-point values representing the normalized semantic embedding.
        """
        text = f"Failure: {failure_signature}. Cause: {root_cause}. Strategy: {fix_strategy}"
        return self.encode_text(text)

    def encode_text(self, text: str) -> List[float]:
        """Encode arbitrary text into a normalized dense vector.

        Args:
            text: Query or code diff description.

        Returns:
            Normalized 384-dimensional vector as list of floats.
        """
        if not text or not text.strip():
            return [0.0] * 384

        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return list(embedding)

    def compute_similarity(
        self,
        query_embedding: Sequence[float],
        target_embeddings: Sequence[Sequence[float]],
    ) -> List[float]:
        """Compute cosine similarity between a query embedding and target embeddings.

        Uses normalized dot product via NumPy.

        Args:
            query_embedding: 1D vector of length D (e.g. 384).
            target_embeddings: 2D array-like of shape (N, D).

        Returns:
            List of float cosine similarity scores of length N (range -1.0 to 1.0).
        """
        if not target_embeddings:
            return []

        q = np.asarray(query_embedding, dtype=np.float32)
        targets = np.asarray(target_embeddings, dtype=np.float32)

        if targets.ndim == 1:
            targets = targets.reshape(1, -1)

        q_norm = np.linalg.norm(q)
        if q_norm < 1e-9:
            return [0.0] * len(targets)

        t_norms = np.linalg.norm(targets, axis=1)
        t_norms = np.where(t_norms < 1e-9, 1e-9, t_norms)

        similarities = np.dot(targets, q) / (t_norms * q_norm)
        similarities = np.clip(similarities, -1.0, 1.0)
        return similarities.tolist()
