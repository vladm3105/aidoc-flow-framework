"""SYS (System Requirements) MCP tools.

Namespace: sys_*
Layer: 6
Reference: UCX_v1_archive/ucx/validators/sys.py
Implementation plan: docs/plans/PLAN-004_remaining_layers.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class SYSTools:
    """MCP tools for SYS document lifecycle (Layer 6).

    Tools registered:
        sys_validate   — Quality gate validation
        sys_review     — AI-driven review
        sys_remediate  — Apply remediations
        sys_status     — Workflow completeness
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all sys_* tools with the MCP server."""
        mcp.tool()(self.sys_validate)
        mcp.tool()(self.sys_review)
        mcp.tool()(self.sys_remediate)
        mcp.tool()(self.sys_status)

    async def sys_validate(self, sys_path: str) -> dict:
        """Validate a SYS document against UCX quality gates.

        Args:
            sys_path: Absolute path to the SYS document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("SYS validation — implement via PLAN-004")

    async def sys_review(self, sys_path: str) -> dict:
        """Perform AI-driven review of a SYS document.

        Args:
            sys_path: Absolute path to the SYS document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("SYS review — implement via PLAN-004")

    async def sys_remediate(
        self,
        sys_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediations to a SYS document.

        Args:
            sys_path: Absolute path to the SYS document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("SYS remediation — implement via PLAN-004")

    async def sys_status(self, sys_dir: str) -> dict:
        """Report workflow completeness for SYS documents in a directory.

        Args:
            sys_dir: Absolute path to a directory containing SYS documents.

        Returns:
            {status, sys_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("SYS status — implement via PLAN-004")
