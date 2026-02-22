"""Exceptions for RAG operations."""


class RAGError(Exception):
    """Base exception for RAG operations."""

    pass


class RAGUnavailableError(RAGError):
    """pgvector/PostgreSQL is not reachable."""

    pass


class EmbeddingUnavailableError(RAGError):
    """All embedding providers failed."""

    pass


class ChunkingError(RAGError):
    """Document chunking failed."""

    pass


class EmbedError(RAGError):
    """Embedding pipeline failed."""

    pass
