#!/usr/bin/env python3
"""Query router for RAG services.

Routes queries to the appropriate RAG service based on query type:
- Factual/keyword queries -> Haystack
- Relational/thematic queries -> LightRAG
"""

import argparse
import re
from dataclasses import dataclass
from enum import Enum

import httpx


class QueryType(Enum):
    """Query type classification."""
    FACTUAL = "factual"      # Direct fact lookup
    RELATIONAL = "relational"  # Entity relationships
    THEMATIC = "thematic"     # Cross-document patterns
    UNKNOWN = "unknown"


@dataclass
class RoutingDecision:
    """Routing decision result."""
    service: str  # "haystack" or "lightrag"
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
        # Default to Haystack for unknown queries
        return RoutingDecision(
            service="haystack",
            query_type=QueryType.UNKNOWN,
            confidence=0.5,
            reasoning="No clear indicators, defaulting to Haystack"
        )

    query_type = max(scores, key=scores.get)
    confidence = max_score / total_score

    # Determine service
    if query_type == QueryType.FACTUAL:
        service = "haystack"
        reasoning = "Factual/documentation query - using Haystack hybrid search"
    else:
        service = "lightrag"
        reasoning = f"{query_type.value.title()} query - using LightRAG graph retrieval"

    return RoutingDecision(
        service=service,
        query_type=query_type,
        confidence=confidence,
        reasoning=reasoning,
    )


def execute_query(query: str, decision: RoutingDecision) -> dict:
    """Execute query against the selected service.

    Args:
        query: User query.
        decision: Routing decision.

    Returns:
        Query result from the service.
    """
    if decision.service == "haystack":
        return execute_haystack_query(query)
    else:
        return execute_lightrag_query(query, decision.query_type)


def execute_haystack_query(query: str, base_url: str = "http://localhost:1416") -> dict:
    """Execute query against Haystack."""
    try:
        response = httpx.post(
            f"{base_url}/query",
            json={"query": query},
            timeout=60,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def execute_lightrag_query(
    query: str,
    query_type: QueryType,
    base_url: str = "http://localhost:9621",
    api_key: str = "lightragsecretkey",
) -> dict:
    """Execute query against LightRAG."""
    # Map query type to LightRAG mode
    mode_mapping = {
        QueryType.FACTUAL: "local",
        QueryType.RELATIONAL: "local",
        QueryType.THEMATIC: "global",
        QueryType.UNKNOWN: "hybrid",
    }
    mode = mode_mapping.get(query_type, "hybrid")

    try:
        response = httpx.post(
            f"{base_url}/query",
            headers={"X-API-Key": api_key},
            json={"query": query, "mode": mode},
            timeout=60,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Route queries to RAG services")
    parser.add_argument("query", nargs="?", help="Query to route")
    parser.add_argument("--analyze-only", action="store_true", help="Only show routing decision")
    parser.add_argument("--force-service", choices=["haystack", "lightrag"])
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
