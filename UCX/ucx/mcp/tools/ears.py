"""EARS (Easy Approach to Requirements Syntax) MCP tools.

Namespace: ears_*
Layer: 3
Reference: UCX_v1_archive/ucx/validators/ears.py
Implementation plan: docs/plans/PLAN-003_ears_tools.md
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class EARSTools:
    """MCP tools for EARS requirements lifecycle (Layer 3).

    Tools registered:
        ears_validate   — Quality gate validation
        ears_review     — AI-driven review
        ears_remediate  — Apply remediations
        ears_status     — Workflow completeness
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all ears_* tools with the MCP server."""
        mcp.tool()(self.ears_validate)
        mcp.tool()(self.ears_review)
        mcp.tool()(self.ears_remediate)
        mcp.tool()(self.ears_status)

    async def ears_validate(self, ears_path: str) -> dict:
        """Validate an EARS requirements document.

        Args:
            ears_path: Absolute path to the EARS document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("EARS validation — implement via PLAN-003")

    async def ears_review(self, ears_path: str) -> dict:
        """Perform AI-driven review of an EARS document.

        Args:
            ears_path: Absolute path to the EARS document.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("EARS review — implement via PLAN-003")

    async def ears_remediate(
        self,
        ears_path: str,
        review_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediations to an EARS document.

        Args:
            ears_path: Absolute path to the EARS document.
            review_report_path: Absolute path to the UCX review report.
            dry_run: If True, return proposed changes without writing.

        Returns:
            {status, path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("EARS remediation — implement via PLAN-003")

    async def ears_status(self, ears_dir: str) -> dict:
        """Report workflow completeness for EARS documents in a directory.

        Args:
            ears_dir: Absolute path to a directory containing EARS documents.

        Returns:
            {status, ears_dir, documents: [{path, stage, complete}], next_step}
        """
        raise NotImplementedError("EARS status — implement via PLAN-003")
