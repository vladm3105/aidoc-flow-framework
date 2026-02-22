"""Status and metrics summary for project_knowledge services."""

from __future__ import annotations

from project_knowledge.graph.adapter import kb_graph_status
from project_knowledge.rag.adapter import kb_status


def summary() -> dict:
    rag = kb_status().to_dict()
    graph = kb_graph_status()
    return {
        "rag": rag,
        "graph": graph,
        "healthy": bool(rag) and bool(graph),
    }
