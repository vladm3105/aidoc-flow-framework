"""UCX MCP Server Module.

Provides Model Context Protocol (MCP) server for AI tool integration.

The MCP server exposes UCX functionality as tools that can be invoked
by AI models like Claude.

Usage:
    from ucx.mcp import UCXMCPServer

    # Create and run server
    server = UCXMCPServer(config)
    server.run(transport="stdio")
"""

from ucx.mcp.server import UCXMCPServer
from ucx.mcp.tools import UCXTools
from ucx.mcp.resources import UCXResources

__all__ = [
    "UCXMCPServer",
    "UCXTools",
    "UCXResources",
]
