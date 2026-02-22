"""MCP server providing RAG tools for Claude skills."""

import asyncio
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to tradegent/.env
    trader_env = Path(__file__).parent.parent / ".env"
    if trader_env.exists():
        load_dotenv(trader_env)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

log = logging.getLogger(__name__)

# Create MCP server
server = Server("trading-rag")


# Tool definitions
TOOLS = [
    Tool(
        name="rag_embed",
        description="Embed a YAML document for semantic search",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to YAML file"},
                "force": {
                    "type": "boolean",
                    "default": False,
                    "description": "Re-embed even if unchanged",
                },
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="rag_embed_text",
        description="Embed raw text for semantic search",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to embed"},
                "doc_id": {"type": "string", "description": "Document identifier"},
                "doc_type": {"type": "string", "description": "Document type"},
                "ticker": {"type": "string", "description": "Optional ticker symbol"},
            },
            "required": ["text", "doc_id", "doc_type"],
        },
    ),
    Tool(
        name="rag_search",
        description="Semantic search across embedded documents",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "ticker": {"type": "string", "description": "Filter by ticker"},
                "doc_type": {"type": "string", "description": "Filter by document type"},
                "section": {"type": "string", "description": "Filter by section"},
                "top_k": {"type": "integer", "default": 5, "description": "Max results"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="rag_similar",
        description="Find similar past analyses for a ticker",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "analysis_type": {"type": "string", "description": "Optional analysis type"},
                "top_k": {"type": "integer", "default": 3, "description": "Max results"},
            },
            "required": ["ticker"],
        },
    ),
    Tool(
        name="rag_hybrid_context",
        description="Get combined vector + graph context for analysis",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "query": {"type": "string", "description": "Search query"},
                "analysis_type": {"type": "string", "description": "Optional analysis type"},
            },
            "required": ["ticker", "query"],
        },
    ),
    Tool(
        name="rag_status",
        description="Get RAG statistics (document/chunk counts)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # ==========================================================================
    # Phase 2+ Tools: Reranking, Query Expansion, Classification, Evaluation
    # ==========================================================================
    Tool(
        name="rag_search_rerank",
        description="Search with cross-encoder reranking for higher relevance",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "ticker": {"type": "string", "description": "Filter by ticker"},
                "doc_type": {"type": "string", "description": "Filter by document type"},
                "top_k": {"type": "integer", "default": 5, "description": "Results to return"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="rag_search_expanded",
        description="Search with query expansion for improved recall",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "ticker": {"type": "string", "description": "Filter by ticker"},
                "top_k": {"type": "integer", "default": 5, "description": "Results to return"},
                "n_expansions": {"type": "integer", "default": 3, "description": "Query variations"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="rag_classify_query",
        description="Classify query to determine optimal retrieval strategy",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query to classify"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="rag_expand_query",
        description="Generate semantic variations of a query",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query to expand"},
                "n": {"type": "integer", "default": 3, "description": "Number of variations"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="rag_evaluate",
        description="Evaluate RAG response quality using RAGAS metrics",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User's question"},
                "contexts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Retrieved context chunks",
                },
                "answer": {"type": "string", "description": "Generated answer"},
                "ground_truth": {"type": "string", "description": "Optional ground truth"},
            },
            "required": ["query", "contexts", "answer"],
        },
    ),
    Tool(
        name="rag_metrics_summary",
        description="Get RAG search metrics summary for recent operations",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 7, "description": "Days to summarize"},
            },
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return available tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        result = await _execute_tool(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def _execute_tool(name: str, args: dict) -> dict:
    """Execute a tool and return result."""
    from .embed import embed_document, embed_text
    from .hybrid import get_hybrid_context
    from .search import get_rag_stats, get_similar_analyses, semantic_search

    if name == "rag_embed":
        result = embed_document(
            file_path=args["file_path"],
            force=args.get("force", False),
        )
        return result.to_dict()

    elif name == "rag_embed_text":
        result = embed_text(
            text=args["text"],
            doc_id=args["doc_id"],
            doc_type=args["doc_type"],
            ticker=args.get("ticker"),
        )
        return result.to_dict()

    elif name == "rag_search":
        results = semantic_search(
            query=args["query"],
            ticker=args.get("ticker"),
            doc_type=args.get("doc_type"),
            section=args.get("section"),
            top_k=args.get("top_k", 5),
        )
        return {"results": [r.to_dict() for r in results]}

    elif name == "rag_similar":
        results = get_similar_analyses(
            ticker=args["ticker"],
            analysis_type=args.get("analysis_type"),
            top_k=args.get("top_k", 3),
        )
        return {"results": [r.to_dict() for r in results]}

    elif name == "rag_hybrid_context":
        # Use adaptive retrieval if enabled
        try:
            from .hybrid import ADAPTIVE_RETRIEVAL_ENABLED, get_hybrid_context_adaptive

            if ADAPTIVE_RETRIEVAL_ENABLED:
                result = get_hybrid_context_adaptive(
                    ticker=args["ticker"],
                    query=args["query"],
                    analysis_type=args.get("analysis_type"),
                )
            else:
                result = get_hybrid_context(
                    ticker=args["ticker"],
                    query=args["query"],
                    analysis_type=args.get("analysis_type"),
                )
        except ImportError:
            result = get_hybrid_context(
                ticker=args["ticker"],
                query=args["query"],
                analysis_type=args.get("analysis_type"),
            )
        return result.to_dict()

    elif name == "rag_status":
        stats = get_rag_stats()
        return stats.to_dict()

    # ==========================================================================
    # Phase 2+ Tools: Reranking, Query Expansion, Classification, Evaluation
    # ==========================================================================

    elif name == "rag_search_rerank":
        from .search import search_with_rerank

        results = search_with_rerank(
            query=args["query"],
            ticker=args.get("ticker"),
            doc_type=args.get("doc_type"),
            top_k=args.get("top_k", 5),
        )
        return {"results": [r.to_dict() for r in results]}

    elif name == "rag_search_expanded":
        from .search import search_with_expansion

        results = search_with_expansion(
            query=args["query"],
            ticker=args.get("ticker"),
            top_k=args.get("top_k", 5),
            n_expansions=args.get("n_expansions", 3),
        )
        return {"results": [r.to_dict() for r in results]}

    elif name == "rag_classify_query":
        from .query_classifier import classify_query

        analysis = classify_query(args["query"])
        return analysis.to_dict()

    elif name == "rag_expand_query":
        from .query_expander import expand_query

        expanded = expand_query(args["query"], n=args.get("n", 3))
        return expanded.to_dict()

    elif name == "rag_evaluate":
        from .evaluation import evaluate_rag

        result = evaluate_rag(
            query=args["query"],
            contexts=args["contexts"],
            answer=args["answer"],
            ground_truth=args.get("ground_truth"),
        )
        if result:
            return result.to_dict()
        return {"error": "RAGAS not available. Install with: pip install ragas datasets"}

    elif name == "rag_metrics_summary":
        from .metrics import get_metrics_collector

        summary = get_metrics_collector().get_summary(days=args.get("days", 7))
        return {
            "total_searches": summary.total_searches,
            "avg_latency_ms": round(summary.avg_latency_ms, 1),
            "avg_results": round(summary.avg_results, 1),
            "avg_top_similarity": round(summary.avg_top_similarity, 3),
            "strategy_distribution": summary.strategy_distribution,
            "query_type_distribution": summary.query_type_distribution,
            "rerank_rate": round(summary.rerank_rate, 2),
            "period_days": summary.period_days,
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
