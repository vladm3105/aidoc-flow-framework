"""Cross-encoder reranking for improved relevance.

Implements two-stage retrieve-then-rerank search pattern:
1. Fast retrieval: Get top-K candidates using vector/hybrid search
2. Accurate reranking: Score candidates with cross-encoder model

Inspired by Haystack and industry best practices.
"""

import logging
from typing import Protocol

from .models import SearchResult

log = logging.getLogger(__name__)


class Reranker(Protocol):
    """Reranker protocol for dependency injection."""

    def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """Rerank candidates and return top_k results."""
        ...


class CrossEncoderReranker:
    """
    Cross-encoder reranker using sentence-transformers.

    Cross-encoders process query-document pairs jointly, providing
    more accurate relevance scores than bi-encoders (embeddings).
    Trade-off: slower but more accurate.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker with specified model.

        Args:
            model_name: HuggingFace model name. Options:
                - cross-encoder/ms-marco-MiniLM-L-6-v2 (fast, good quality)
                - cross-encoder/ms-marco-MiniLM-L-12-v2 (slower, better quality)
                - BAAI/bge-reranker-base (alternative)
        """
        self._model = None
        self._model_name = model_name

    @property
    def model(self):
        """Lazy-load model to avoid import overhead."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self._model_name)
                log.info(f"Loaded reranker: {self._model_name}")
            except ImportError:
                log.warning(
                    "sentence-transformers not installed, reranking disabled. "
                    "Install with: pip install sentence-transformers"
                )
                return None
            except Exception as e:
                log.warning(f"Failed to load reranker model: {e}")
                return None
        return self._model

    def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Rerank candidates using cross-encoder.

        Args:
            query: Original search query
            candidates: List of SearchResult from retrieval stage
            top_k: Number of top results to return

        Returns:
            Reranked list of SearchResult with rerank_score set
        """
        if not self.model or not candidates:
            return candidates[:top_k]

        # Create query-document pairs
        pairs = [(query, c.content) for c in candidates]

        try:
            # Get cross-encoder scores
            scores = self.model.predict(pairs)

            # Attach scores to candidates
            for candidate, score in zip(candidates, scores):
                candidate.rerank_score = float(score)

            # Sort by rerank score (descending)
            reranked = sorted(
                candidates,
                key=lambda c: getattr(c, "rerank_score", 0),
                reverse=True,
            )

            top_score = reranked[0].rerank_score if reranked else None
            if top_score is not None:
                log.debug(
                    f"Reranked {len(candidates)} candidates, "
                    f"top score: {top_score:.3f}"
                )

            return reranked[:top_k]

        except Exception as e:
            log.warning(f"Reranking failed: {e}, returning original order")
            return candidates[:top_k]


class NoOpReranker:
    """No-op reranker for when sentence-transformers unavailable."""

    def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Return candidates as-is (no reranking)."""
        return candidates[:top_k]


# =============================================================================
# Singleton Management
# =============================================================================

_reranker: Reranker | None = None


def get_reranker(model_name: str | None = None) -> Reranker:
    """
    Get singleton reranker with graceful fallback.

    Args:
        model_name: Optional model name override

    Returns:
        Reranker instance (CrossEncoderReranker or NoOpReranker)
    """
    global _reranker

    if _reranker is None:
        try:
            # Try to load config for model name
            if model_name is None:
                try:
                    import yaml
                    from pathlib import Path

                    config_path = Path(__file__).parent / "config.yaml"
                    if config_path.exists():
                        with open(config_path) as f:
                            config = yaml.safe_load(f) or {}
                        model_name = config.get("reranking", {}).get("model")
                except Exception:
                    pass

            _reranker = CrossEncoderReranker(
                model_name=model_name or "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )

            # Test that model loads
            if _reranker.model is None:
                log.info("Cross-encoder unavailable, using no-op reranker")
                _reranker = NoOpReranker()

        except Exception as e:
            log.warning(f"Reranker initialization failed: {e}")
            _reranker = NoOpReranker()

    return _reranker


def reset_reranker() -> None:
    """Reset singleton (for testing)."""
    global _reranker
    _reranker = None
