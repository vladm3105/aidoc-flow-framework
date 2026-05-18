"""MCP server entry point for SDD lifecycle tools.

Exposes 26 tools over stdio transport:
  - 2 session management (set/get project)
  - 18 deterministic (validation, scoring, consistency, link validation, etc.)
  - 2 orchestration (pipeline, next-action advisor)
  - 4 LLM-dependent (create/review/remediate with per-call executor selection)

Launch: python -m mcp_server.server
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.tool_registry import TOOLS, handle_tool
from mcp_server.executor.registry import load_config_file

logger = logging.getLogger(__name__)

server = Server("sdd-lifecycle")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return await handle_tool(name, arguments)


async def main() -> None:
    # Load optional executor config
    config_path = Path(__file__).parent.parent.parent / "executors.json"
    loaded = load_config_file(config_path)
    if loaded:
        logger.info("Loaded %d executor(s) from %s", loaded, config_path)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
