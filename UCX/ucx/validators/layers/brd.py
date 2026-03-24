"""BRD validator for UCX v2.

Reference: UCX_v1_archive/ucx/validators/brd/quality_gate.py
Implementation plan: docs/plans/PLAN-001_brd_tools.md
"""

from __future__ import annotations

from ucx.validators.result import Finding, Severity, ValidationResult


class BRDValidator:
    """Validates BRD documents against UCX quality gates.

    Quality gates (to be implemented via PLAN-001):
        GATE-01  Placeholder detection
        GATE-02  Downstream references
        GATE-06  Diagram contracts
        GATE-08  Element uniqueness
        GATE-10  File size limit
    """

    def validate(self, content: str, path: str) -> ValidationResult:
        """Validate a BRD document.

        Args:
            content: Full document text.
            path:    Absolute path (used in findings context).

        Returns:
            ValidationResult with all gate findings.
        """
        raise NotImplementedError("BRD validator — implement via PLAN-001")
