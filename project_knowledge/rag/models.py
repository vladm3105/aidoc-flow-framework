"""Data classes for RAG operations."""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class ChunkResult:
    """Single chunk from a document."""

    section_path: str  # YAML path: "phase2_fundamentals.competitive_context"
    section_label: str  # Human-readable: "Competitive Context"
    chunk_index: int  # 0 for first chunk of section
    content: str  # Flattened text
    content_tokens: int  # Token count
    prepared_text: str  # With context prefix for embedding

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "section_path": self.section_path,
            "section_label": self.section_label,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "content_tokens": self.content_tokens,
        }


@dataclass
class EmbedResult:
    """Result of embedding a document."""

    doc_id: str
    file_path: str
    doc_type: str
    ticker: str | None
    doc_date: date | None
    chunk_count: int
    embed_model: str
    embed_version: str
    duration_ms: int
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "doc_type": self.doc_type,
            "ticker": self.ticker,
            "doc_date": self.doc_date.isoformat() if self.doc_date else None,
            "chunk_count": self.chunk_count,
            "embed_model": self.embed_model,
            "embed_version": self.embed_version,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
        }


@dataclass
class SearchResult:
    """Single search result."""

    doc_id: str
    file_path: str
    doc_type: str
    ticker: str | None
    doc_date: date | None
    section_label: str
    content: str
    similarity: float  # 0.0 - 1.0 (cosine similarity or hybrid score)
    rerank_score: float | None = None  # Cross-encoder score (if reranked)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "doc_type": self.doc_type,
            "ticker": self.ticker,
            "doc_date": self.doc_date.isoformat() if self.doc_date else None,
            "section_label": self.section_label,
            "content": self.content,
            "similarity": round(self.similarity, 4),
        }
        if self.rerank_score is not None:
            result["rerank_score"] = round(self.rerank_score, 4)
        return result


@dataclass
class HybridContext:
    """Combined vector + graph context for Claude."""

    ticker: str
    vector_results: list[SearchResult]
    graph_context: dict  # From TradingGraph.get_ticker_context()
    formatted: str  # Ready-to-use context block

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "vector_results": [r.to_dict() for r in self.vector_results],
            "graph_context": self.graph_context,
            "formatted": self.formatted,
        }


@dataclass
class RAGStats:
    """RAG system statistics."""

    document_count: int
    chunk_count: int
    embed_model: str
    embed_version: str
    doc_types: dict[str, int]  # {"earnings-analysis": 10, ...}
    tickers: list[str]
    last_embed: datetime | None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_count": self.document_count,
            "chunk_count": self.chunk_count,
            "embed_model": self.embed_model,
            "embed_version": self.embed_version,
            "doc_types": self.doc_types,
            "tickers": self.tickers,
            "last_embed": self.last_embed.isoformat() if self.last_embed else None,
        }
