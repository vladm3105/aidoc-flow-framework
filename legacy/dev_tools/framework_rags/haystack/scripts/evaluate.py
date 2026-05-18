#!/usr/bin/env python3
"""Evaluate Haystack RAG quality using RAGAS metrics."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Sample evaluation queries with expected answers
EVAL_QUERIES = [
    {
        "query": "What are the validation rules for BRD documents?",
        "expected_context": ["BRD", "validation", "business requirements"],
        "category": "factual",
    },
    {
        "query": "How are PRD requirements structured?",
        "expected_context": ["PRD", "product requirements", "structure"],
        "category": "factual",
    },
    {
        "query": "What is the relationship between EARS and BDD?",
        "expected_context": ["EARS", "BDD", "requirements", "scenarios"],
        "category": "relational",
    },
    {
        "query": "What metadata fields are required in SPEC documents?",
        "expected_context": ["SPEC", "metadata", "frontmatter"],
        "category": "factual",
    },
    {
        "query": "How do ADR decisions flow into system requirements?",
        "expected_context": ["ADR", "SYS", "architecture", "decisions"],
        "category": "relational",
    },
]


def evaluate_retrieval(query: str, retrieved_docs: list, expected_context: list[str]) -> dict:
    """Evaluate retrieval quality for a single query.

    Args:
        query: The query string.
        retrieved_docs: List of retrieved documents.
        expected_context: Keywords expected in retrieved context.

    Returns:
        Evaluation metrics dictionary.
    """
    # Combine retrieved content
    retrieved_text = " ".join(doc.get("content", "") for doc in retrieved_docs).lower()

    # Calculate context precision (how many expected keywords found)
    found_keywords = sum(1 for kw in expected_context if kw.lower() in retrieved_text)
    context_precision = found_keywords / len(expected_context) if expected_context else 0

    # Calculate coverage (did we retrieve anything relevant)
    has_relevant = any(kw.lower() in retrieved_text for kw in expected_context)

    return {
        "query": query,
        "context_precision": context_precision,
        "has_relevant_context": has_relevant,
        "retrieved_count": len(retrieved_docs),
        "found_keywords": found_keywords,
        "total_keywords": len(expected_context),
    }


def run_evaluation(base_url: str = "http://localhost:1416", verbose: bool = False) -> dict:
    """Run full evaluation suite.

    Args:
        base_url: Haystack API URL.
        verbose: Print detailed results.

    Returns:
        Aggregated evaluation results.
    """
    import httpx

    results = []

    print("Running RAG Evaluation")
    print("=" * 50)

    for eval_item in EVAL_QUERIES:
        query = eval_item["query"]
        expected = eval_item["expected_context"]

        if verbose:
            print(f"\nQuery: {query}")

        try:
            response = httpx.post(
                f"{base_url}/query",
                json={"query": query},
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                retrieved_docs = data.get("documents", [])

                metrics = evaluate_retrieval(query, retrieved_docs, expected)
                metrics["category"] = eval_item["category"]
                results.append(metrics)

                if verbose:
                    print(f"  Context Precision: {metrics['context_precision']:.2%}")
                    print(f"  Retrieved: {metrics['retrieved_count']} docs")
            else:
                print(f"  Error: HTTP {response.status_code}")
                results.append({
                    "query": query,
                    "error": f"HTTP {response.status_code}",
                })

        except Exception as e:
            print(f"  Error: {e}")
            results.append({"query": query, "error": str(e)})

    # Aggregate results
    valid_results = [r for r in results if "error" not in r]

    if not valid_results:
        return {"error": "No successful queries", "results": results}

    avg_precision = sum(r["context_precision"] for r in valid_results) / len(valid_results)
    coverage_rate = sum(1 for r in valid_results if r["has_relevant_context"]) / len(valid_results)

    # By category
    by_category = {}
    for r in valid_results:
        cat = r.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r["context_precision"])

    category_scores = {
        cat: sum(scores) / len(scores)
        for cat, scores in by_category.items()
    }

    summary = {
        "total_queries": len(EVAL_QUERIES),
        "successful_queries": len(valid_results),
        "average_context_precision": avg_precision,
        "coverage_rate": coverage_rate,
        "by_category": category_scores,
        "results": results,
    }

    print("\n" + "=" * 50)
    print("Evaluation Summary")
    print("=" * 50)
    print(f"Queries: {summary['successful_queries']}/{summary['total_queries']}")
    print(f"Avg Context Precision: {avg_precision:.2%}")
    print(f"Coverage Rate: {coverage_rate:.2%}")
    print("\nBy Category:")
    for cat, score in category_scores.items():
        print(f"  {cat}: {score:.2%}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate Haystack RAG quality")
    parser.add_argument("--base-url", default="http://localhost:1416")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    args = parser.parse_args()

    results = run_evaluation(base_url=args.base_url, verbose=args.verbose)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    # Exit with error if precision is too low
    if results.get("average_context_precision", 0) < 0.5:
        print("\n⚠ Warning: Context precision below 50% threshold")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
