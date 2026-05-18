#!/usr/bin/env python3
"""Query router for ucx_kb contracts.

Routes queries to ucx_kb contract types based on query intent:
- Factual/keyword queries -> RAG search contract
- Relational/thematic queries -> Graph context contract
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum

if "ucx_kb" not in sys.modules:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from ucx_kb.models.contracts import GraphContextRequest, SearchRequest


class QueryType(Enum):
    """Query type classification."""
    FACTUAL = "factual"      # Direct fact lookup
    RELATIONAL = "relational"  # Entity relationships
    THEMATIC = "thematic"     # Cross-document patterns
    UNKNOWN = "unknown"


@dataclass
class RoutingDecision:
    """Routing decision result."""
    service: str  # "rag" or "graph"
    query_type: QueryType
    confidence: float
    reasoning: str


# Keywords that indicate different query types
FACTUAL_KEYWORDS = [
    "what is", "what are", "define", "explain", "show me",
    "list", "describe", "specification", "requirement",
    "api", "endpoint", "function", "method", "class",
    "prd", "brd", "spec", "documentation",
]

RELATIONAL_KEYWORDS = [
    "connect", "relate", "relationship", "between",
    "affect", "impact", "influence", "depend",
    "how does", "why does", "what causes",
    "compare", "contrast", "difference",
]

THEMATIC_KEYWORDS = [
    "pattern", "theme", "across", "common",
    "trend", "insight", "analysis", "summary",
    "what patterns", "what themes", "overall",
]


def classify_query(query: str) -> RoutingDecision:
    """Classify query and determine routing.

    Args:
        query: User query string.

    Returns:
        RoutingDecision with service and reasoning.
    """
    query_lower = query.lower()

    # Score for each type
    factual_score = sum(1 for kw in FACTUAL_KEYWORDS if kw in query_lower)
    relational_score = sum(1 for kw in RELATIONAL_KEYWORDS if kw in query_lower)
    thematic_score = sum(1 for kw in THEMATIC_KEYWORDS if kw in query_lower)

    # Check for document type references (strong factual signal)
    doc_types = ["prd", "brd", "spec", "req", "adr", "tasks", "ears", "bdd"]
    if any(dt in query_lower for dt in doc_types):
        factual_score += 2

    # Check for entity relationship patterns
    if re.search(r"how .+ (relate|connect|affect)", query_lower):
        relational_score += 2

    # Check for cross-document patterns
    if re.search(r"(across|between) .+ (document|file|analysis)", query_lower):
        thematic_score += 2

    # Determine winner
    scores = {
        QueryType.FACTUAL: factual_score,
        QueryType.RELATIONAL: relational_score,
        QueryType.THEMATIC: thematic_score,
    }

    max_score = max(scores.values())
    total_score = sum(scores.values()) or 1

    if max_score == 0:
        # Default to ucx_kb RAG search for unknown queries
        return RoutingDecision(
            service="rag",
            query_type=QueryType.UNKNOWN,
            confidence=0.5,
            reasoning="No clear indicators, defaulting to ucx_kb RAG search"
        )

    query_type = max(scores, key=scores.get)
    confidence = max_score / total_score

    # Determine service
    if query_type == QueryType.FACTUAL:
        service = "rag"
        reasoning = "Factual/documentation query - using ucx_kb RAG search"
    else:
        service = "graph"
        reasoning = f"{query_type.value.title()} query - using ucx_kb graph context"

    return RoutingDecision(
        service=service,
        query_type=query_type,
        confidence=confidence,
        reasoning=reasoning,
    )


def execute_query(query: str, decision: RoutingDecision) -> dict:
    """Build ucx_kb contract payload for the selected route.

    Args:
        query: User query.
        decision: Routing decision.

    Returns:
        Dict payload compatible with ucx_kb contracts.
    """
    if decision.service == "rag":
        request = SearchRequest(query=query, top_k=5)
        return {
            "route": "kb_search",
            "request": asdict(request),
        }

    request = GraphContextRequest(entity_id="auto")
    return {
        "route": "kb_graph_context",
        "request": asdict(request),
        "note": "Set entity_id from caller context before execution.",
        "query": query,
        "query_type": decision.query_type.value,
    }


def main():
    parser = argparse.ArgumentParser(description="Route queries to ucx_kb contracts")
    parser.add_argument("query", nargs="?", help="Query to route")
    parser.add_argument("--analyze-only", action="store_true", help="Only show routing decision")
    parser.add_argument("--force-service", choices=["rag", "graph"])
    args = parser.parse_args()

    if not args.query:
        # Interactive mode
        print("Query Router - Interactive Mode")
        print("Type 'quit' to exit\n")

        while True:
            try:
                query = input("Query: ").strip()
                if query.lower() in ("quit", "exit", "q"):
                    break
                if not query:
                    continue

                decision = classify_query(query)
                print(f"\n  Service: {decision.service}")
                print(f"  Type: {decision.query_type.value}")
                print(f"  Confidence: {decision.confidence:.0%}")
                print(f"  Reasoning: {decision.reasoning}\n")

            except KeyboardInterrupt:
                break
    else:
        decision = classify_query(args.query)

        if args.force_service:
            decision = RoutingDecision(
                service=args.force_service,
                query_type=decision.query_type,
                confidence=1.0,
                reasoning=f"Forced to {args.force_service}"
            )

        print(f"Query: {args.query}")
        print(f"Service: {decision.service}")
        print(f"Type: {decision.query_type.value}")
        print(f"Confidence: {decision.confidence:.0%}")
        print(f"Reasoning: {decision.reasoning}")

        if not args.analyze_only:
            print("\nExecuting query...")
            result = execute_query(args.query, decision)
            print(f"Result: {result}")


if __name__ == "__main__":
    main()
