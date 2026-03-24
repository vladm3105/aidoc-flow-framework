"""PRD (Product Requirements Document) MCP tools.

Namespace: prd_*
Layer: 2
Reference: UCX_v1_archive/ucx/validators/prd/  (PLAN-012, PLAN-014)
Implementation plan: docs/plans/PLAN-002_prd_tools.md

PRD Workflow Stages (immutable-source model):
  source PRD  →  [validate_fix]  →  _validation copy  →  [review]
  →  review report  →  [remediate]  →  remediation report
  →  [remediate_apply]  →  _validation_fixed copy
"""

from __future__ import annotations

from fastmcp import FastMCP

from ucx.config.settings import UCXSettings


class PRDTools:
    """MCP tools for PRD document lifecycle (Layer 2).

    Tools registered:
        prd_validate          — Quality gate validation (source PRD)
        prd_validate_fix      — Fix validation issues, produce _validation copy
        prd_review            — AI review of _validation copy
        prd_remediate         — Generate remediation report from review
        prd_remediate_apply   — Apply patches, produce _validation_fixed copy
        prd_artifacts         — Classify PRD artifacts in a directory
        prd_status            — Workflow completeness + next_step
    """

    def __init__(self, settings: UCXSettings) -> None:
        self._settings = settings

    def register(self, mcp: FastMCP) -> None:
        """Register all prd_* tools with the MCP server."""
        mcp.tool()(self.prd_validate)
        mcp.tool()(self.prd_validate_fix)
        mcp.tool()(self.prd_review)
        mcp.tool()(self.prd_remediate)
        mcp.tool()(self.prd_remediate_apply)
        mcp.tool()(self.prd_artifacts)
        mcp.tool()(self.prd_status)

    async def prd_validate(self, prd_path: str) -> dict:
        """Validate a PRD source document against UCX quality gates.

        Only accepts source PRDs (not _validation copies).

        Args:
            prd_path: Absolute path to the source PRD document.

        Returns:
            {status, path, findings, score, next_step}
        """
        raise NotImplementedError("PRD validation — implement via PLAN-002")

    async def prd_validate_fix(
        self,
        prd_path: str,
        dry_run: bool = False,
        max_iterations: int = 3,
    ) -> dict:
        """Fix validation issues in a source PRD, producing a _validation copy.

        Source PRD is never modified. Output written to {stem}_validation.md.

        Args:
            prd_path: Absolute path to the source PRD (must not be _validation).
            dry_run: If True, return proposed fixes without writing files.
            max_iterations: Maximum fix-validate cycles.

        Returns:
            {status, source_path, validation_path, iterations, findings_remaining, next_step}
        """
        raise NotImplementedError("PRD validate-fix — implement via PLAN-002")

    async def prd_review(self, validation_prd_path: str) -> dict:
        """Perform AI-driven review of a PRD _validation copy.

        Args:
            validation_prd_path: Absolute path to the _validation PRD copy.

        Returns:
            {status, path, review_report_path, findings_summary, next_step}
        """
        raise NotImplementedError("PRD review — implement via PLAN-002")

    async def prd_remediate(
        self,
        validation_prd_path: str,
        review_report_path: str,
    ) -> dict:
        """Generate a remediation report from a PRD review report.

        Args:
            validation_prd_path: Absolute path to the _validation PRD.
            review_report_path: Absolute path to the UCX review report.

        Returns:
            {status, path, remediation_report_path, action_count, next_step}
        """
        raise NotImplementedError("PRD remediate — implement via PLAN-002")

    async def prd_remediate_apply(
        self,
        validation_prd_path: str,
        remediation_report_path: str,
        dry_run: bool = False,
    ) -> dict:
        """Apply remediation patches, producing a _validation_fixed copy.

        Args:
            validation_prd_path: Absolute path to the _validation PRD.
            remediation_report_path: Absolute path to the remediation report.
            dry_run: If True, return proposed changes without writing files.

        Returns:
            {status, path, fixed_path, changes_applied, dry_run, next_step}
        """
        raise NotImplementedError("PRD remediate-apply — implement via PLAN-002")

    async def prd_artifacts(self, prd_dir: str) -> dict:
        """Discover and classify all PRD artifacts in a directory.

        Classifies each file as: source | validation | validation_fixed |
        review_report | remediation_report | unknown

        Args:
            prd_dir: Absolute path to a directory containing PRD artifacts.

        Returns:
            {status, prd_dir, artifacts: [{path, artifact_class, stage}]}
        """
        raise NotImplementedError("PRD artifacts — implement via PLAN-002")

    async def prd_status(self, prd_dir: str) -> dict:
        """Report PRD workflow completeness for all source PRDs in a directory.

        Args:
            prd_dir: Absolute path to a directory containing PRD documents.

        Returns:
            {status, prd_dir, documents: [{path, current_stage, complete, next_step}], next_step}
        """
        raise NotImplementedError("PRD status — implement via PLAN-002")
