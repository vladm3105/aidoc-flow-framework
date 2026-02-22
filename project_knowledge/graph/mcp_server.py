"""MCP server providing graph tools for Claude skills."""

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
server = Server("trading-graph")


# Tool definitions
TOOLS = [
    Tool(
        name="graph_extract",
        description="Extract entities and relationships from a YAML document",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to YAML file"},
                "extractor": {
                    "type": "string",
                    "default": "ollama",
                    "enum": ["ollama", "claude-api", "openrouter"],
                    "description": "LLM backend for extraction",
                },
                "commit": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to commit to Neo4j",
                },
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="graph_extract_text",
        description="Extract entities from raw text (for external content)",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to extract from"},
                "doc_type": {"type": "string", "description": "Document type"},
                "doc_id": {"type": "string", "description": "Document identifier"},
                "source_url": {"type": "string", "description": "Optional source URL"},
                "extractor": {"type": "string", "default": "ollama"},
            },
            "required": ["text", "doc_type", "doc_id"],
        },
    ),
    Tool(
        name="graph_search",
        description="Find all nodes connected to a ticker within N hops",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "depth": {"type": "integer", "default": 2, "description": "Max hops"},
            },
            "required": ["ticker"],
        },
    ),
    Tool(
        name="graph_peers",
        description="Get sector peers and competitors for a ticker",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
            },
            "required": ["ticker"],
        },
    ),
    Tool(
        name="graph_risks",
        description="Get known risks for a ticker",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
            },
            "required": ["ticker"],
        },
    ),
    Tool(
        name="graph_biases",
        description="Get bias history across trades",
        inputSchema={
            "type": "object",
            "properties": {
                "bias_name": {"type": "string", "description": "Optional filter by bias name"},
            },
            "required": [],
        },
    ),
    Tool(
        name="graph_context",
        description="Get comprehensive context for a ticker (peers, risks, strategies, biases)",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
            },
            "required": ["ticker"],
        },
    ),
    Tool(
        name="graph_query",
        description="Execute raw Cypher query",
        inputSchema={
            "type": "object",
            "properties": {
                "cypher": {"type": "string", "description": "Cypher query string"},
                "params": {"type": "object", "default": {}, "description": "Query parameters"},
            },
            "required": ["cypher"],
        },
    ),
    Tool(
        name="graph_status",
        description="Get graph statistics (node/edge counts)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
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
    from .extract import extract_document, extract_text
    from .layer import TradingGraph

    if name == "graph_extract":
        result = extract_document(
            file_path=args["file_path"],
            extractor=args.get("extractor", "ollama"),
            commit=args.get("commit", True),
        )
        return result.to_dict()

    elif name == "graph_extract_text":
        result = extract_text(
            text=args["text"],
            doc_type=args["doc_type"],
            doc_id=args["doc_id"],
            source_url=args.get("source_url"),
            extractor=args.get("extractor", "ollama"),
        )
        return result.to_dict()

    elif name == "graph_search":
        with TradingGraph() as graph:
            results = graph.find_related(args["ticker"].upper(), depth=args.get("depth", 2))
            return {"results": results}

    elif name == "graph_peers":
        with TradingGraph() as graph:
            peers = graph.get_sector_peers(args["ticker"].upper())
            competitors = graph.get_competitors(args["ticker"].upper())
            return {"peers": peers, "competitors": competitors}

    elif name == "graph_risks":
        with TradingGraph() as graph:
            return {"risks": graph.get_risks(args["ticker"].upper())}

    elif name == "graph_biases":
        with TradingGraph() as graph:
            return {"biases": graph.get_bias_history(args.get("bias_name"))}

    elif name == "graph_context":
        with TradingGraph() as graph:
            return graph.get_ticker_context(args["ticker"].upper())

    elif name == "graph_query":
        with TradingGraph() as graph:
            results = graph.run_cypher(args["cypher"], args.get("params", {}))
            return {"results": results}

    elif name == "graph_status":
        with TradingGraph() as graph:
            stats = graph.get_stats()
            return stats.to_dict()

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
