"""Tool registration for UCX v2 MCP server.

Each SDD document layer has its own tool namespace class.
This module registers all namespaces with the FastMCP server.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


def register_all_tools(mcp: FastMCP, settings: UCXSettings) -> None:
    """Register all layer-specific tool namespaces with the MCP server.

    Import order defines tool registration order (cosmetic only).
    Each tool class registers its own tools via `register(mcp)`.
    """
    from ucx.mcp.tools.brd import BRDTools
    from ucx.mcp.tools.prd import PRDTools
    from ucx.mcp.tools.ears import EARSTools
    from ucx.mcp.tools.adr import ADRTools
    from ucx.mcp.tools.sys import SYSTools
    from ucx.mcp.tools.req import REQTools
    from ucx.mcp.tools.ctr import CTRTools

    for tool_class in [BRDTools, PRDTools, EARSTools, ADRTools, SYSTools, REQTools, CTRTools]:
        tool_class(settings).register(mcp)
