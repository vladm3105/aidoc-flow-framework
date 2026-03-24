"""UCX MCP Server implementation.

Provides FastMCP-based server exposing UCX tools and resources.
"""

import signal
import sys
from pathlib import Path
from typing import Any, Optional

from ucx.config.settings import UCXConfig
from ucx.observability.logging import get_logger
from ucx.version import __version__

logger = get_logger(__name__)


class UCXMCPServer:
    """
    MCP Server for UCX Framework.

    Exposes UCX functionality as MCP tools:
    - ucx_autopilot: Full UCC→UCR→UCRem cycle
    - ucx_create: Create document (UCC)
    - ucx_review: Review document (UCR)
    - ucx_remediate: Generate fixes (UCRem)
    - ucx_check_drift: Check for upstream drift
    - ucx_validate: Validate document structure
    - ucx_batch: Batch processing
    - ucx_status: Document status

    Resources:
    - ucx://config: Current configuration
    - ucx://doc-types: Supported document types
    - ucx://health: Server health status
    - ucx://version: UCX version
    - ucx://skills: Available skills/personas
    - ucx://templates: Available prompt templates
    - ucx://validators: Available validators
    """

    def __init__(self, config: Optional[UCXConfig] = None) -> None:
        """
        Initialize the UCX MCP server.

        Args:
            config: UCX configuration
        """
        self._config = config or UCXConfig()
        self._mcp = None
        self._running = False

        logger.info("UCXMCPServer initialized", version=__version__)

    def _get_mcp(self) -> Any:
        """Get or create FastMCP instance."""
        if self._mcp is None:
            try:
                from fastmcp import FastMCP

                self._mcp = FastMCP("UCX Framework")
                self._register_tools()
                self._register_resources()
            except ImportError:
                logger.error("FastMCP not installed. Run: pip install fastmcp")
                raise ImportError(
                    "FastMCP is required for MCP server. Install with: pip install fastmcp"
                )

        return self._mcp

    def _register_tools(self) -> None:
        """Register MCP tools using tools module."""
        from ucx.mcp.tools import UCXTools
        from ucx.mcp.tools_prd import PRDTools

        tools = UCXTools(self._config)
        tools.register(self._mcp)

        prd_tools = PRDTools(self._config)
        prd_tools.register(self._mcp)

        logger.debug("MCP tools registered")

    def _register_resources(self) -> None:
        """Register MCP resources using resources module."""
        from ucx.mcp.resources import UCXResources

        resources = UCXResources(self._config)
        resources.register(self._mcp)

        logger.debug("MCP resources registered")

    def health_check(self) -> dict:
        """
        Return server health status.

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "version": __version__,
            "config_loaded": self._config is not None,
            "mcp_initialized": self._mcp is not None,
        }

    def run(
        self,
        host: str = "localhost",
        port: int = 8765,
        transport: str = "stdio",
    ) -> None:
        """
        Run the MCP server.

        Args:
            host: Server host (for HTTP transport)
            port: Server port (for HTTP transport)
            transport: Transport type (stdio, streamable-http)
        """
        mcp = self._get_mcp()

        # Set up graceful shutdown
        def graceful_shutdown(signum: int, frame: Any) -> None:
            logger.info("Received shutdown signal", signal=signum)
            self._running = False
            sys.exit(0)

        signal.signal(signal.SIGTERM, graceful_shutdown)
        signal.signal(signal.SIGINT, graceful_shutdown)

        self._running = True
        logger.info("Starting UCX MCP server", transport=transport)

        if transport == "stdio":
            mcp.run()
        else:
            mcp.run(transport="streamable-http", host=host, port=port)

    def stop(self) -> None:
        """Stop the server."""
        self._running = False
        logger.info("UCX MCP server stopped")

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    @property
    def config(self) -> UCXConfig:
        """Get current configuration."""
        return self._config
