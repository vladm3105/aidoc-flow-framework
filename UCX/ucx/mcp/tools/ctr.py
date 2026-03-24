"""CTR (Data Contracts) MCP tools.

Namespace: ctr_*
Layer: 8
Reference: UCX_v1_archive/ucx/validators/ctr.py
Implementation plan: docs/plans/PLAN-004_remaining_layers.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class CTRTools:
    """MCP tools for CTR document lifecycle (Layer 8).

    Tools registered:
        ctr_validate   — Quality gate validation
        ctr_review     — AI-driven review
        ctr_remediate  — Apply remediations
        ctr_status     — Workflow completeness
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all ctr_* tools with the MCP server."""
        mcp.tool()(self.ctr_validate)
        mcp.tool()(self.ctr_review)
        mcp.tool()(self.ctr_remediate)
        mcp.tool()(self.ctr_status)

    async def ctr_validate(self, ctr_path: str) -> dict:
        """Validate a CTR data contract document against UCX quality gates.

        Args:
            ctr_path: Absolute path to the CTR document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("CTR validation — implement via PLAN-004")

    async def ctr_review(self, ctr_path: str) -> dict:
        """Perform AI-driven review of a CTR document.

        Args:
            ctr_path: Absolute path to the CTR document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("CTR review — implement via PLAN-004")

    async def ctr_remediate(
        self,
        ctr_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediations to a CTR document.

        Args:
            ctr_path: Absolute path to the CTR document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("CTR remediation — implement via PLAN-004")

    async def ctr_status(self, ctr_dir: str) -> dict:
        """Report workflow completeness for CTR documents in a directory.

        Args:
            ctr_dir: Absolute path to a directory containing CTR documents.

        Returns:
            {status, ctr_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("CTR status — implement via PLAN-004")
