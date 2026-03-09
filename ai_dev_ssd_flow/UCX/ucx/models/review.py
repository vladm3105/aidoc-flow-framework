"""Review result models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

from ucx.models.enums import Status, ValidationStatus, Priority


@dataclass
class ValidationResult:
    """Result of document validation."""

    status: ValidationStatus
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passes: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASSED

    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return len(self.warnings)


@dataclass
class ReviewResult:
    """Result of UCR review."""

    doc_path: Path
    report_path: Path
    score: int
    status: Status
    validation_status: ValidationStatus
    findings: dict[str, int] = field(default_factory=lambda: {"P0": 0, "P1": 0, "P2": 0})
    raw_content: str = ""
    elapsed_time: float = 0.0

    @property
    def has_critical(self) -> bool:
        """Check if P0 findings exist."""
        return self.findings.get("P0", 0) > 0

    @property
    def has_high_priority(self) -> bool:
        """Check if P1 findings exist."""
        return self.findings.get("P1", 0) > 0

    @property
    def total_findings(self) -> int:
        """Get total number of findings."""
        return sum(self.findings.values())

    @classmethod
    def from_report(cls, report_path: Path, doc_path: Path) -> "ReviewResult":
        """
        Parse review result from report file.

        Args:
            report_path: Path to UCR review report
            doc_path: Path to original document

        Returns:
            ReviewResult with extracted metrics
        """
        content = report_path.read_text(encoding="utf-8")

        # Extract score
        score_match = re.search(r"(?:Score|PRD-Ready)[:\s]+(\d+)", content, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0

        # Count findings
        findings = {
            "P0": len(re.findall(r"P0-\d+", content)),
            "P1": len(re.findall(r"P1-\d+", content)),
            "P2": len(re.findall(r"P2-\d+", content)),
        }

        # Determine status
        if score >= 90 and findings["P0"] == 0:
            status = Status.PASS
        elif findings["P0"] > 0:
            status = Status.FAIL
        else:
            status = Status.NEEDS_MANUAL

        return cls(
            doc_path=doc_path,
            report_path=report_path,
            score=score,
            status=status,
            validation_status=ValidationStatus.PASSED,  # Default, updated by caller
            findings=findings,
            raw_content=content,
        )

    def get_findings_by_priority(self, priority: Priority) -> list[str]:
        """
        Extract finding IDs for a priority level.

        Args:
            priority: Priority level (P0, P1, P2)

        Returns:
            List of finding IDs
        """
        pattern = rf"{priority.value}-\d+"
        return re.findall(pattern, self.raw_content)
