"""BRD (Business Requirements Document) MCP tools.

Namespace: brd_*
Layer: 1
Reference: UCX_v1_archive/ucx/validators/brd/
Implementation plan: docs/plans/PLAN-001_brd_tools.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class BRDTools:
    """MCP tools for BRD document lifecycle (Layer 1).

    Tools registered:
        brd_validate        — Quality gate validation
        brd_review          — AI-driven document review
        brd_remediate       — Apply AI-generated remediations
        brd_status          — Workflow completeness report
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all brd_* tools with the MCP server."""
        mcp.tool()(self.brd_validate)
        mcp.tool()(self.brd_review)
        mcp.tool()(self.brd_remediate)
        mcp.tool()(self.brd_status)

    async def brd_validate(self, brd_path: str) -> dict:
        """Validate a BRD document against UCX quality gates.

        Args:
            brd_path: Absolute path to the BRD document (file or directory).

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("BRD validation — implement via PLAN-001")

    async def brd_review(self, brd_path: str) -> dict:
        """Perform AI-driven review of a BRD document.

        Args:
            brd_path: Absolute path to the BRD document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("BRD review — implement via PLAN-001")

    async def brd_remediate(
        self,
        brd_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply AI-generated remediations to a BRD document.

        Args:
            brd_path: Absolute path to the BRD document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing files.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("BRD remediation — implement via PLAN-001")

    async def brd_status(self, brd_dir: str) -> dict:
        """Report workflow completeness for BRD documents in a directory.

        Args:
            brd_dir: Absolute path to a directory containing BRD documents.

        Returns:
            {status, brd_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("BRD status — implement via PLAN-001")
