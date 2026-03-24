"""UCX v2 MCP Server — MCP-first agentic interface.

Entry point: `ucx-mcp` (defined in pyproject.toml [project.scripts])

Start the server:
    ucx-mcp

Or in agent configuration:
    {"mcpServers": {"ucx": {"command": "ucx-mcp"}}}
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings
from ucx.mcp.tools.registry import register_all_tools


def create_server(settings: UCXSettings | None = None) -> FastMCP:
    """Create and configure the UCX MCP server.

    Each call returns a new FastMCP instance with all layer tool namespaces
    registered. Suitable for use in tests and production entry points.

    Args:
        settings: Optional settings override. Loads from environment if None.

    Returns:
        Configured FastMCP instance with all layer tool namespaces registered.
    """
    if settings is None:
        settings = UCXSettings()
    mcp = FastMCP("UCX", version="2.0.0")
    register_all_tools(mcp, settings)
    return mcp


def main() -> None:
    """Entry point for `ucx-mcp` console script."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
