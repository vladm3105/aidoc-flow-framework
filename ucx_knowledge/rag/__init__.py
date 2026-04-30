"""Trading RAG (Retrieval Augmented Generation) package."""

RAG_VERSION = "1.0.0"
EMBED_DIMS = 1536

from .exceptions import (
    ChunkingError,
    EmbeddingUnavailableError,
    EmbedError,
    RAGError,
    RAGUnavailableError,
)
from .models import (
    ChunkResult,
    EmbedResult,
    HybridContext,
    SearchResult,
)

__all__ = [
    "RAG_VERSION",
    "EMBED_DIMS",
    "ChunkResult",
    "EmbedResult",
    "SearchResult",
    "HybridContext",
    "RAGError",
    "RAGUnavailableError",
    "EmbeddingUnavailableError",
    "ChunkingError",
    "EmbedError",
]
