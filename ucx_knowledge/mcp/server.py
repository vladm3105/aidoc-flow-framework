"""Unified MCP server for ucx_knowledge tools."""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from ucx_knowledge.graph.adapter import (
    kb_extract,
    kb_extract_text,
    kb_graph_context,
    kb_graph_query,
    kb_graph_search,
    kb_graph_status,
)
from ucx_knowledge.rag.adapter import (
    kb_embed,
    kb_embed_text,
    kb_hybrid_context,
    kb_search,
    kb_status,
)

server = Server("project-knowledge")

TOOLS = [
    Tool(
        name="kb_embed",
        description="Embed a document into ucx_knowledge RAG",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="kb_embed_text",
        description="Embed raw text into ucx_knowledge RAG",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "doc_id": {"type": "string"},
                "source_type": {"type": "string"},
                "entity_id": {"type": "string"},
            },
            "required": ["text", "doc_id", "source_type"],
        },
    ),
    Tool(
        name="kb_search",
        description="Search ucx_knowledge RAG",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "entity_id": {"type": "string"},
                "source_type": {"type": "string"},
                "section": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="kb_hybrid_context",
        description="Get combined vector + graph context for entity",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "entity_id": {"type": "string"},
                "analysis_type": {"type": "string"},
                "adaptive": {"type": "boolean", "default": True},
            },
            "required": ["query", "entity_id"],
        },
    ),
    Tool(
        name="kb_status",
        description="Get ucx_knowledge RAG status",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="kb_extract",
        description="Extract entities/relations from document",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "extractor": {"type": "string"},
                "commit": {"type": "boolean", "default": True},
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="kb_extract_text",
        description="Extract entities/relations from text",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "doc_id": {"type": "string"},
                "source_type": {"type": "string"},
                "source_url": {"type": "string"},
                "extractor": {"type": "string"},
            },
            "required": ["text", "doc_id", "source_type"],
        },
    ),
    Tool(
        name="kb_graph_context",
        description="Get graph context for entity",
        inputSchema={
            "type": "object",
            "properties": {"entity_id": {"type": "string"}},
            "required": ["entity_id"],
        },
    ),
    Tool(
        name="kb_graph_search",
        description="Graph N-hop search around entity",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "depth": {"type": "integer", "default": 2},
            },
            "required": ["entity_id"],
        },
    ),
    Tool(
        name="kb_graph_query",
        description="Run raw graph query",
        inputSchema={
            "type": "object",
            "properties": {
                "cypher": {"type": "string"},
                "params": {"type": "object", "default": {}},
            },
            "required": ["cypher"],
        },
    ),
    Tool(
        name="kb_graph_status",
        description="Get graph status",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "kb_embed":
            result = kb_embed(arguments["file_path"], arguments.get("force", False)).to_dict()
        elif name == "kb_embed_text":
            result = kb_embed_text(
                text=arguments["text"],
                doc_id=arguments["doc_id"],
                source_type=arguments["source_type"],
                entity_id=arguments.get("entity_id"),
            ).to_dict()
        elif name == "kb_search":
            result = {
                "results": [
                    r.to_dict()
                    for r in kb_search(
                        query=arguments["query"],
                        entity_id=arguments.get("entity_id"),
                        source_type=arguments.get("source_type"),
                        section=arguments.get("section"),
                        top_k=arguments.get("top_k", 5),
                    )
                ]
            }
        elif name == "kb_hybrid_context":
            result = kb_hybrid_context(
                query=arguments["query"],
                entity_id=arguments["entity_id"],
                analysis_type=arguments.get("analysis_type"),
                adaptive=arguments.get("adaptive", True),
            ).to_dict()
        elif name == "kb_status":
            result = kb_status().to_dict()
        elif name == "kb_extract":
            result = kb_extract(
                file_path=arguments["file_path"],
                extractor=arguments.get("extractor"),
                commit=arguments.get("commit", True),
            ).to_dict()
        elif name == "kb_extract_text":
            result = kb_extract_text(
                text=arguments["text"],
                doc_id=arguments["doc_id"],
                source_type=arguments["source_type"],
                source_url=arguments.get("source_url"),
                extractor=arguments.get("extractor"),
            ).to_dict()
        elif name == "kb_graph_context":
            result = kb_graph_context(arguments["entity_id"])
        elif name == "kb_graph_search":
            result = {
                "results": kb_graph_search(arguments["entity_id"], arguments.get("depth", 2))
            }
        elif name == "kb_graph_query":
            result = {"results": kb_graph_query(arguments["cypher"], arguments.get("params", {}))}
        elif name == "kb_graph_status":
            result = kb_graph_status()
        else:
            raise ValueError(f"Unknown tool: {name}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
