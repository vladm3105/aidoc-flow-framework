"""Semantic chunking based on embedding similarity.

Splits documents based on semantic coherence rather than fixed token counts.
Inspired by Haystack's EmbeddingBasedDocumentSplitter.

Key concept: Keep semantically similar sentences together, split when
the topic/meaning changes significantly (low cosine similarity).
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from .tokens import estimate_tokens

log = logging.getLogger(__name__)

# Load config
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}
if _config_path.exists():
    with open(_config_path) as f:
        _config = yaml.safe_load(f) or {}

_semantic_config = _config.get("semantic_chunking", {})
DEFAULT_SIMILARITY_THRESHOLD = float(_semantic_config.get("similarity_threshold", 0.8))


@dataclass
class SemanticChunk:
    """A semantically coherent chunk."""

    content: str
    start_idx: int
    end_idx: int
    tokens: int
    sentence_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "start_idx": self.start_idx,
            "end_idx": self.end_idx,
            "tokens": self.tokens,
            "sentence_count": self.sentence_count,
        }


class SemanticChunker:
    """
    Split text based on semantic similarity between sentences.

    Algorithm:
    1. Split text into sentences
    2. Get embeddings for each sentence
    3. Calculate cosine similarity between adjacent sentences
    4. Split where similarity drops below threshold
    5. Respect max_tokens constraint

    Inspired by Haystack's EmbeddingBasedDocumentSplitter.
    """

    # Sentence splitting pattern (handles common abbreviations)
    SENTENCE_PATTERN = re.compile(
        r'(?<=[.!?])\s+(?=[A-Z])|'  # Standard sentence end
        r'(?<=[.!?])\s*\n+|'  # Sentence end before newline
        r'\n{2,}'  # Paragraph breaks
    )

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        max_tokens: int = 768,
        min_tokens: int = 50,
    ):
        """
        Initialize semantic chunker.

        Args:
            similarity_threshold: Min similarity to keep sentences together (0.0-1.0)
            max_tokens: Maximum tokens per chunk
            min_tokens: Minimum tokens per chunk (merge small chunks)
        """
        self.similarity_threshold = similarity_threshold
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self._embedder = None

    @property
    def embedder(self):
        """Lazy-load embedding client."""
        if self._embedder is None:
            try:
                from .embedding_client import EmbeddingClient

                self._embedder = EmbeddingClient()
            except Exception as e:
                log.warning(f"Failed to load embedding client: {e}")
                return None
        return self._embedder

    def chunk(self, text: str) -> list[SemanticChunk]:
        """
        Split text into semantically coherent chunks.

        Args:
            text: Input text to chunk

        Returns:
            List of SemanticChunk objects
        """
        # Handle short text
        total_tokens = estimate_tokens(text)
        if total_tokens <= self.max_tokens:
            return [
                SemanticChunk(
                    content=text,
                    start_idx=0,
                    end_idx=len(text),
                    tokens=total_tokens,
                    sentence_count=1,
                )
            ]

        # Split into sentences
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            # Can't split semantically, fall back to token-based
            return self._fallback_chunk(text)

        # Check if embedder is available
        if self.embedder is None:
            log.warning("Embedder not available, using fallback chunking")
            return self._fallback_chunk(text)

        # Get embeddings for all sentences
        try:
            sentence_texts = [s["text"] for s in sentences]
            embeddings = self.embedder.get_embeddings_batch(sentence_texts)
        except Exception as e:
            log.warning(f"Embedding failed: {e}, using fallback chunking")
            return self._fallback_chunk(text)

        # Find semantic breakpoints
        breakpoints = self._find_breakpoints(embeddings)

        # Create chunks respecting breakpoints and max_tokens
        chunks = self._create_chunks(sentences, breakpoints)

        return chunks

    def _split_sentences(self, text: str) -> list[dict]:
        """
        Split text into sentences with position tracking.

        Returns list of {"text": str, "start": int, "end": int}
        """
        sentences = []
        last_end = 0

        for match in self.SENTENCE_PATTERN.finditer(text):
            # Get sentence before this split point
            sentence_text = text[last_end : match.start()].strip()
            if sentence_text:
                sentences.append(
                    {
                        "text": sentence_text,
                        "start": last_end,
                        "end": match.start(),
                    }
                )
            last_end = match.end()

        # Don't forget the last sentence
        if last_end < len(text):
            sentence_text = text[last_end:].strip()
            if sentence_text:
                sentences.append(
                    {
                        "text": sentence_text,
                        "start": last_end,
                        "end": len(text),
                    }
                )

        return sentences

    def _find_breakpoints(self, embeddings: list[list[float]]) -> set[int]:
        """
        Find indices where semantic similarity drops below threshold.

        Returns set of indices where a new chunk should start.
        """
        breakpoints = set()

        for i in range(1, len(embeddings)):
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])
            if similarity < self.similarity_threshold:
                breakpoints.add(i)
                log.debug(f"Semantic breakpoint at sentence {i} (similarity: {similarity:.3f})")

        return breakpoints

    def _create_chunks(
        self,
        sentences: list[dict],
        breakpoints: set[int],
    ) -> list[SemanticChunk]:
        """
        Create chunks from sentences, respecting breakpoints and max_tokens.
        """
        chunks = []
        current_sentences = []
        current_tokens = 0
        current_start = sentences[0]["start"] if sentences else 0

        for i, sentence in enumerate(sentences):
            sentence_tokens = estimate_tokens(sentence["text"])

            # Check if we should break here
            should_break = (
                i in breakpoints  # Semantic breakpoint
                or current_tokens + sentence_tokens > self.max_tokens  # Token limit
            )

            if should_break and current_sentences:
                # Save current chunk
                chunk_text = " ".join(s["text"] for s in current_sentences)
                if current_tokens >= self.min_tokens:
                    chunks.append(
                        SemanticChunk(
                            content=chunk_text,
                            start_idx=current_start,
                            end_idx=current_sentences[-1]["end"],
                            tokens=current_tokens,
                            sentence_count=len(current_sentences),
                        )
                    )
                else:
                    # Chunk too small, will be merged with next
                    log.debug(f"Small chunk ({current_tokens} tokens), merging")

                # Start new chunk
                current_start = sentence["start"]
                current_sentences = []
                current_tokens = 0

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        # Save last chunk
        if current_sentences:
            chunk_text = " ".join(s["text"] for s in current_sentences)
            if current_tokens >= self.min_tokens or not chunks:
                chunks.append(
                    SemanticChunk(
                        content=chunk_text,
                        start_idx=current_start,
                        end_idx=current_sentences[-1]["end"],
                        tokens=current_tokens,
                        sentence_count=len(current_sentences),
                    )
                )
            elif chunks:
                # Merge with previous chunk if too small
                prev = chunks[-1]
                merged_content = prev.content + " " + chunk_text
                chunks[-1] = SemanticChunk(
                    content=merged_content,
                    start_idx=prev.start_idx,
                    end_idx=current_sentences[-1]["end"],
                    tokens=prev.tokens + current_tokens,
                    sentence_count=prev.sentence_count + len(current_sentences),
                )

        return chunks

    def _fallback_chunk(self, text: str) -> list[SemanticChunk]:
        """
        Fallback to simple token-based chunking when semantic chunking unavailable.
        """
        from .tokens import split_by_tokens

        chunks = []
        sub_texts = split_by_tokens(text, self.max_tokens, overlap=50)

        offset = 0
        for sub_text in sub_texts:
            tokens = estimate_tokens(sub_text)
            start_idx = text.find(sub_text, offset)
            if start_idx == -1:
                start_idx = offset
            end_idx = start_idx + len(sub_text)

            chunks.append(
                SemanticChunk(
                    content=sub_text,
                    start_idx=start_idx,
                    end_idx=end_idx,
                    tokens=tokens,
                    sentence_count=sub_text.count(". ") + 1,
                )
            )
            offset = end_idx

        return chunks

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a = np.array(a)
        b = np.array(b)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))


# =============================================================================
# Convenience Functions
# =============================================================================

_chunker: SemanticChunker | None = None


def get_semantic_chunker(
    similarity_threshold: float | None = None,
    max_tokens: int | None = None,
) -> SemanticChunker:
    """Get singleton semantic chunker."""
    global _chunker

    if _chunker is None:
        _chunker = SemanticChunker(
            similarity_threshold=similarity_threshold or DEFAULT_SIMILARITY_THRESHOLD,
            max_tokens=max_tokens or 768,
        )

    return _chunker


def semantic_chunk(text: str) -> list[SemanticChunk]:
    """
    Convenience function to chunk text semantically.

    Args:
        text: Input text

    Returns:
        List of SemanticChunk objects
    """
    return get_semantic_chunker().chunk(text)
