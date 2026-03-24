"""REQ (Atomic Requirements) MCP tools.

Namespace: req_*
Layer: 7
Reference: UCX_v1_archive/ucx/validators/req.py
Implementation plan: docs/plans/PLAN-004_remaining_layers.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class REQTools:
    """MCP tools for REQ document lifecycle (Layer 7).

    Tools registered:
        req_validate   — Quality gate validation
        req_review     — AI-driven review
        req_remediate  — Apply remediations
        req_status     — Workflow completeness
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all req_* tools with the MCP server."""
        mcp.tool()(self.req_validate)
        mcp.tool()(self.req_review)
        mcp.tool()(self.req_remediate)
        mcp.tool()(self.req_status)

    async def req_validate(self, req_path: str) -> dict:
        """Validate a REQ document against UCX quality gates.

        Args:
            req_path: Absolute path to the REQ document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("REQ validation — implement via PLAN-004")

    async def req_review(self, req_path: str) -> dict:
        """Perform AI-driven review of a REQ document.

        Args:
            req_path: Absolute path to the REQ document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("REQ review — implement via PLAN-004")

    async def req_remediate(
        self,
        req_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediations to a REQ document.

        Args:
            req_path: Absolute path to the REQ document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("REQ remediation — implement via PLAN-004")

    async def req_status(self, req_dir: str) -> dict:
        """Report workflow completeness for REQ documents in a directory.

        Args:
            req_dir: Absolute path to a directory containing REQ documents.

        Returns:
            {status, req_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("REQ status — implement via PLAN-004")
