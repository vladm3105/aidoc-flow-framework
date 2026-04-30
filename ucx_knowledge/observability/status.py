"""Status and metrics summary for ucx_knowledge services."""

from __future__ import annotations

from ucx_knowledge.graph.adapter import kb_graph_status
from ucx_knowledge.rag.adapter import kb_status


def summary() -> dict:
    rag = kb_status().to_dict()
    graph = kb_graph_status()
    return {
        "rag": rag,
        "graph": graph,
        "healthy": bool(rag) and bool(graph),
    }
