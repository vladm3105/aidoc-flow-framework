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
    weighted_score: float = 0.0  # Category-weighted score (v1.12.0+)
    category_scores: dict[str, any] = field(default_factory=dict)  # Per-category breakdown

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

        # Extract weighted score from frontmatter (v1.12.0+ format)
        weighted_match = re.search(r"weighted_score:\s*([\d.]+)", content)
        weighted_score = float(weighted_match.group(1)) if weighted_match else 0.0

        # Fallback: Extract legacy score from content
        score_match = re.search(r"(?:Score|PRD-Ready)[:\s]+(\d+)", content, re.IGNORECASE)
        legacy_score = int(score_match.group(1)) if score_match else 0

        # Use weighted score if available, else legacy
        score = int(weighted_score) if weighted_score > 0 else legacy_score

        # Extract finding counts from frontmatter (v1.12.0+ format)
        p0_match = re.search(r"p0_findings:\s*(\d+)", content)
        p1_match = re.search(r"p1_findings:\s*(\d+)", content)
        p2_match = re.search(r"p2_findings:\s*(\d+)", content)

        if p0_match and p1_match and p2_match:
            findings = {
                "P0": int(p0_match.group(1)),
                "P1": int(p1_match.group(1)),
                "P2": int(p2_match.group(1)),
            }
        else:
            # Fallback: Count findings in content
            findings = {
                "P0": len(re.findall(r"P0-\d+", content)),
                "P1": len(re.findall(r"P1-\d+", content)),
                "P2": len(re.findall(r"P2-\d+", content)),
            }

        # Determine status based on weighted score (v1.12.0 thresholds)
        if weighted_score >= 85 and findings["P0"] == 0:
            status = Status.PASS
        elif weighted_score >= 70:
            status = Status.NEEDS_MANUAL  # Warning range
        elif findings["P0"] > 0:
            status = Status.FAIL
        else:
            status = Status.FAIL

        return cls(
            doc_path=doc_path,
            report_path=report_path,
            score=score,
            status=status,
            validation_status=ValidationStatus.PASSED,  # Default, updated by caller
            findings=findings,
            raw_content=content,
            weighted_score=weighted_score,
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
