"""FastAPI HTTP endpoints for RAG operations."""

import logging
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .embed import delete_document, embed_document, embed_text
from .exceptions import EmbedError, RAGUnavailableError
from .hybrid import get_hybrid_context
from .schema import health_check
from .search import get_document_chunks, get_rag_stats, list_documents, semantic_search

log = logging.getLogger(__name__)

app = FastAPI(title="Trading RAG API", version="1.0.0")


# --- Request Models ---


class EmbedRequest(BaseModel):
    file_path: str
    force: bool = False


class EmbedTextRequest(BaseModel):
    text: str
    doc_id: str
    doc_type: str
    ticker: str | None = None


class SearchRequest(BaseModel):
    query: str
    ticker: str | None = None
    doc_type: str | None = None
    section: str | None = None
    date_from: str | None = None  # YYYY-MM-DD
    date_to: str | None = None
    top_k: int = 5
    min_similarity: float = 0.3


class HybridContextRequest(BaseModel):
    ticker: str
    query: str
    analysis_type: str | None = None


# --- Endpoints ---


@app.post("/api/rag/embed")
async def api_embed_document(req: EmbedRequest) -> dict:
    """Embed a YAML file."""
    try:
        result = embed_document(
            file_path=req.file_path,
            force=req.force,
        )
        return result.to_dict()
    except EmbedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/rag/embed-text")
async def api_embed_text(req: EmbedTextRequest) -> dict:
    """Embed raw text."""
    try:
        result = embed_text(
            text=req.text,
            doc_id=req.doc_id,
            doc_type=req.doc_type,
            ticker=req.ticker,
        )
        return result.to_dict()
    except EmbedError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/rag/search")
async def api_search(req: SearchRequest) -> dict:
    """Semantic search with filters."""
    try:
        # Parse dates
        date_from = None
        date_to = None
        if req.date_from:
            date_from = date.fromisoformat(req.date_from)
        if req.date_to:
            date_to = date.fromisoformat(req.date_to)

        results = semantic_search(
            query=req.query,
            ticker=req.ticker,
            doc_type=req.doc_type,
            section=req.section,
            date_from=date_from,
            date_to=date_to,
            top_k=req.top_k,
            min_similarity=req.min_similarity,
        )
        return {"results": [r.to_dict() for r in results]}
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/rag/hybrid-context")
async def api_get_hybrid_context(req: HybridContextRequest) -> dict:
    """Get combined vector + graph context."""
    try:
        result = get_hybrid_context(
            ticker=req.ticker,
            query=req.query,
            analysis_type=req.analysis_type,
        )
        return result.to_dict()
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/rag/status")
async def api_get_status() -> dict:
    """Get RAG statistics."""
    try:
        stats = get_rag_stats()
        return stats.to_dict()
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/rag/documents")
async def api_list_documents(
    ticker: str | None = None,
    doc_type: str | None = None,
    limit: int = 50,
) -> dict:
    """List embedded documents."""
    try:
        documents = list_documents(ticker=ticker, doc_type=doc_type, limit=limit)
        return {"documents": documents}
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/rag/document/{doc_id}")
async def api_get_document(doc_id: str) -> dict:
    """Get document and its chunks."""
    try:
        chunks = get_document_chunks(doc_id)
        if not chunks:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        return {"doc_id": doc_id, "chunks": chunks}
    except RAGUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.delete("/api/rag/document/{doc_id}")
async def api_delete_document(doc_id: str) -> dict:
    """Delete document and chunks."""
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return {"status": "deleted", "doc_id": doc_id}


@app.get("/api/rag/health")
async def api_health_check() -> dict:
    """Health check endpoint."""
    try:
        if health_check():
            return {"status": "healthy", "pgvector": "connected"}
        return {"status": "unhealthy", "pgvector": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/rag/ready")
async def api_readiness_check() -> dict:
    """Readiness check - can accept traffic."""
    try:
        stats = get_rag_stats()
        return {
            "status": "ready",
            "document_count": stats.document_count,
            "chunk_count": stats.chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "error": str(e)})
