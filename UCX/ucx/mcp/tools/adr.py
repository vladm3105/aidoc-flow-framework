"""ADR (Architecture Decision Records) MCP tools.

Namespace: adr_*
Layer: 5
Reference: UCX_v1_archive/ucx/validators/adr.py
Implementation plan: docs/plans/PLAN-004_remaining_layers.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class ADRTools:
    """MCP tools for ADR document lifecycle (Layer 5).

    Tools registered:
        adr_validate   — Quality gate validation
        adr_review     — AI-driven review
        adr_remediate  — Apply remediations
        adr_status     — Workflow completeness
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all adr_* tools with the MCP server."""
        mcp.tool()(self.adr_validate)
        mcp.tool()(self.adr_review)
        mcp.tool()(self.adr_remediate)
        mcp.tool()(self.adr_status)

    async def adr_validate(self, adr_path: str) -> dict:
        """Validate an ADR document against UCX quality gates.

        Args:
            adr_path: Absolute path to the ADR document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("ADR validation — implement via PLAN-004")

    async def adr_review(self, adr_path: str) -> dict:
        """Perform AI-driven review of an ADR document.

        Args:
            adr_path: Absolute path to the ADR document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("ADR review — implement via PLAN-004")

    async def adr_remediate(
        self,
        adr_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediations to an ADR document.

        Args:
            adr_path: Absolute path to the ADR document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("ADR remediation — implement via PLAN-004")

    async def adr_status(self, adr_dir: str) -> dict:
        """Report workflow completeness for ADRs in a directory.

        Args:
            adr_dir: Absolute path to a directory containing ADR documents.

        Returns:
            {status, adr_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("ADR status — implement via PLAN-004")
