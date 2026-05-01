"""Domain-neutral adapter layer for ucx_kb RAG operations."""

from __future__ import annotations

from .embed import embed_document, embed_text
from .hybrid import get_hybrid_context, get_hybrid_context_adaptive
from .search import get_rag_stats, semantic_search


def kb_embed(file_path: str, force: bool = False):
    return embed_document(file_path=file_path, force=force)


def kb_embed_text(text: str, doc_id: str, source_type: str, entity_id: str | None = None):
    return embed_text(text=text, doc_id=doc_id, doc_type=source_type, ticker=entity_id)


def kb_search(
    query: str,
    entity_id: str | None = None,
    source_type: str | None = None,
    section: str | None = None,
    top_k: int = 5,
):
    return semantic_search(
        query=query,
        ticker=entity_id,
        doc_type=source_type,
        section=section,
        top_k=top_k,
    )


def kb_hybrid_context(
    query: str,
    entity_id: str,
    analysis_type: str | None = None,
    adaptive: bool = True,
):
    if adaptive:
        return get_hybrid_context_adaptive(
            ticker=entity_id,
            query=query,
            analysis_type=analysis_type,
        )
    return get_hybrid_context(
        ticker=entity_id,
        query=query,
        analysis_type=analysis_type,
    )


def kb_status():
    return get_rag_stats()
