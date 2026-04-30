"""Domain-neutral adapter layer for ucx_knowledge Graph operations."""

from __future__ import annotations

from .extract import extract_document, extract_text
from .layer import TradingGraph


def kb_extract(file_path: str, extractor: str | None = None, commit: bool = True):
    return extract_document(file_path=file_path, extractor=extractor, commit=commit)


def kb_extract_text(
    text: str,
    doc_id: str,
    source_type: str,
    source_url: str | None = None,
    extractor: str | None = None,
):
    return extract_text(
        text=text,
        doc_type=source_type,
        doc_id=doc_id,
        source_url=source_url,
        extractor=extractor,
    )


def kb_graph_context(entity_id: str) -> dict:
    with TradingGraph() as graph:
        return graph.get_ticker_context(entity_id.upper())


def kb_graph_search(entity_id: str, depth: int = 2) -> list[dict]:
    with TradingGraph() as graph:
        return graph.find_related(entity_id.upper(), depth=depth)


def kb_graph_query(cypher: str, params: dict | None = None) -> list[dict]:
    with TradingGraph() as graph:
        return graph.run_cypher(cypher, params or {})


def kb_graph_status() -> dict:
    with TradingGraph() as graph:
        return graph.get_stats().to_dict()
