"""PRD validator for UCX v2.

Reference: UCX_v1_archive/ucx/validators/prd/quality_gate.py
Implementation plan: docs/plans/PLAN-002_prd_tools.md
"""

from __future__ import annotations

from ucx.validators.result import ValidationResult


class PRDValidator:
    """Validates PRD documents against UCX quality gates.

    Operates on source PRDs only. _validation copies use the same
    gates but also enforce immutable-source contract checks.

    Implementation via PLAN-002.
    """

    def validate(self, content: str, path: str) -> ValidationResult:
        """Validate a PRD document.

        Args:
            content: Full document text.
            path:    Absolute path (used in findings context).

        Returns:
            ValidationResult with all gate findings.
        """
        raise NotImplementedError("PRD validator — implement via PLAN-002")
