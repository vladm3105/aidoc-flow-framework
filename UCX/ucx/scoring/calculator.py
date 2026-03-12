"""
UCX Score Calculator.

Implements category-weighted scoring with per-category caps
to prevent runaway deductions.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from .categories import (
    Category,
    categorize_by_element_code,
    categorize_by_keyword,
    extract_element_code,
    get_persona_primary_category,
)
from .weights import (
    DocumentTypeWeights,
    load_weights,
)

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """A single finding from a review."""

    id: str
    priority: str  # P0, P1, P2
    text: str
    persona: str
    category: Optional[Category] = None
    raw_category_tag: Optional[str] = None  # [CAT:xxx] tag from prompt


@dataclass
class CategoryScore:
    """Score details for a single category."""

    category: Category
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    raw_deduction: float = 0.0
    capped_deduction: float = 0.0
    weighted_deduction: float = 0.0
    weight: float = 0.0
    max_deduction: int = 0

    @property
    def total_findings(self) -> int:
        """Total findings in this category."""
        return self.p0_count + self.p1_count + self.p2_count


@dataclass
class ScoringResult:
    """Complete scoring result."""

    doc_type: str
    weighted_score: float
    category_scores: dict[Category, CategoryScore] = field(default_factory=dict)
    uncategorized_count: int = 0
    total_findings: int = 0
    pass_status: str = "UNKNOWN"  # PASS, WARN, FAIL

    # Summary counts
    total_p0: int = 0
    total_p1: int = 0
    total_p2: int = 0

    def get_category_summary_table(self) -> str:
        """Generate markdown table for Chairperson manifest."""
        lines = [
            "| Category | P0 | P1 | P2 | Raw Deduction | Capped | Weighted |",
            "|----------|----|----|----|--------------:|-------:|---------:|",
        ]

        total_weighted = 0.0
        for cat in Category:
            if cat == Category.OTHER:
                continue

            score = self.category_scores.get(cat)
            if score:
                lines.append(
                    f"| {cat.value} | {score.p0_count} | {score.p1_count} | "
                    f"{score.p2_count} | -{score.raw_deduction:.1f} | "
                    f"-{score.capped_deduction:.1f} | -{score.weighted_deduction:.2f} |"
                )
                total_weighted += score.weighted_deduction
            else:
                lines.append(f"| {cat.value} | 0 | 0 | 0 | 0.0 | 0.0 | 0.00 |")

        lines.append(
            f"| **Total** | {self.total_p0} | {self.total_p1} | {self.total_p2} | "
            f"| | **-{total_weighted:.2f}** |"
        )

        return "\n".join(lines)


class ScoringCalculator:
    """
    Category-weighted score calculator.

    Implements the scoring formula from PLAN-002:
    1. Count findings per category and priority
    2. Calculate raw deduction: (P0 * 10) + (P1 * 3) + (P2 * 1)
    3. Cap at category maximum
    4. Apply category weight
    5. Sum weighted deductions
    6. Final score: 100 - sum(weighted deductions)
    """

    def __init__(self, doc_type: str, weights: Optional[DocumentTypeWeights] = None):
        """
        Initialize calculator for a document type.

        Args:
            doc_type: Document type (e.g., 'brd', 'prd').
            weights: Optional pre-loaded weights (loads default if None).
        """
        self.doc_type = doc_type.lower()
        self.weights = weights or load_weights(self.doc_type)
        self._conflict_count = 0
        self._uncategorized_count = 0

    def categorize_finding(self, finding: Finding) -> Category:
        """
        Assign a category to a finding.

        Resolution order (per PLAN-002):
        1. Explicit [CAT:xxx] tag from prompt
        2. Element code from finding ID
        3. Keyword match in finding text
        4. Persona's primary category
        5. Fallback to OTHER

        Args:
            finding: Finding to categorize.

        Returns:
            Assigned category.
        """
        # 1. Check for explicit category tag
        if finding.raw_category_tag:
            from .categories import get_category_by_name
            explicit_cat = get_category_by_name(finding.raw_category_tag)
            if explicit_cat:
                return explicit_cat

        # 2. Try element code
        element_code = extract_element_code(finding.id)
        if element_code is not None:
            cat_from_code = categorize_by_element_code(element_code)
            if cat_from_code:
                # Check for keyword conflict
                cat_from_keyword = categorize_by_keyword(finding.text)
                if cat_from_keyword and cat_from_keyword != cat_from_code:
                    self._conflict_count += 1
                    logger.info(
                        f"Category conflict resolved: {finding.id} "
                        f"code={cat_from_code.value} keyword={cat_from_keyword.value} "
                        f"-> using element code"
                    )
                return cat_from_code

        # 3. Try keyword match
        cat_from_keyword = categorize_by_keyword(finding.text)
        if cat_from_keyword:
            return cat_from_keyword

        # 4. Try persona primary category
        persona_cat = get_persona_primary_category(finding.persona)
        if persona_cat:
            logger.debug(
                f"Categorized {finding.id} by persona {finding.persona} "
                f"-> {persona_cat.value}"
            )
            return persona_cat

        # 5. Fallback to OTHER
        self._uncategorized_count += 1
        logger.warning(
            f"Could not categorize finding {finding.id} - assigning to OTHER"
        )
        return Category.OTHER

    def calculate_category_score(
        self,
        category: Category,
        p0_count: int,
        p1_count: int,
        p2_count: int,
    ) -> CategoryScore:
        """
        Calculate score for a single category.

        Args:
            category: Category to score.
            p0_count: Number of P0 findings.
            p1_count: Number of P1 findings.
            p2_count: Number of P2 findings.

        Returns:
            CategoryScore with all details.
        """
        # Get category weight config
        cat_name = category.value
        cat_config = self.weights.categories.get(cat_name)

        if not cat_config:
            # Category not in weights (e.g., OTHER)
            return CategoryScore(
                category=category,
                p0_count=p0_count,
                p1_count=p1_count,
                p2_count=p2_count,
                raw_deduction=0.0,
                capped_deduction=0.0,
                weighted_deduction=0.0,
                weight=0.0,
                max_deduction=0,
            )

        # Calculate raw deduction
        raw_deduction = (p0_count * 10) + (p1_count * 3) + (p2_count * 1)

        # Cap at category maximum
        max_deduction = cat_config.max_deduction
        capped_deduction = min(raw_deduction, max_deduction)

        # Apply weight
        weight = cat_config.weight
        weighted_deduction = capped_deduction * weight

        return CategoryScore(
            category=category,
            p0_count=p0_count,
            p1_count=p1_count,
            p2_count=p2_count,
            raw_deduction=raw_deduction,
            capped_deduction=capped_deduction,
            weighted_deduction=weighted_deduction,
            weight=weight,
            max_deduction=max_deduction,
        )

    def calculate(self, findings: list[Finding]) -> ScoringResult:
        """
        Calculate weighted score for all findings.

        Args:
            findings: List of findings to score.

        Returns:
            ScoringResult with full breakdown.
        """
        # Reset counters
        self._conflict_count = 0
        self._uncategorized_count = 0

        # Group findings by category
        category_findings: dict[Category, dict[str, int]] = {}
        for cat in Category:
            category_findings[cat] = {"P0": 0, "P1": 0, "P2": 0}

        for finding in findings:
            # Assign category if not already set
            if finding.category is None:
                finding.category = self.categorize_finding(finding)

            # Count by priority
            priority = finding.priority.upper()
            if priority in ("P0", "P1", "P2"):
                category_findings[finding.category][priority] += 1

        # Calculate per-category scores
        category_scores: dict[Category, CategoryScore] = {}
        total_weighted_deduction = 0.0
        total_p0 = total_p1 = total_p2 = 0

        for category, counts in category_findings.items():
            score = self.calculate_category_score(
                category,
                counts["P0"],
                counts["P1"],
                counts["P2"],
            )
            category_scores[category] = score
            total_weighted_deduction += score.weighted_deduction
            total_p0 += counts["P0"]
            total_p1 += counts["P1"]
            total_p2 += counts["P2"]

        # Calculate final score
        weighted_score = max(0, min(100, 100 - total_weighted_deduction))
        weighted_score = round(weighted_score, 1)

        # Determine pass status
        thresholds = self.weights.thresholds
        if weighted_score >= thresholds.pass_threshold:
            pass_status = "PASS"
        elif weighted_score >= thresholds.warn_threshold:
            pass_status = "WARN"
        else:
            pass_status = "FAIL"

        return ScoringResult(
            doc_type=self.doc_type,
            weighted_score=weighted_score,
            category_scores=category_scores,
            uncategorized_count=self._uncategorized_count,
            total_findings=len(findings),
            pass_status=pass_status,
            total_p0=total_p0,
            total_p1=total_p1,
            total_p2=total_p2,
        )

    @property
    def conflict_count(self) -> int:
        """Number of category conflicts resolved."""
        return self._conflict_count


def calculate_weighted_score(
    findings: list[Finding],
    doc_type: str,
) -> ScoringResult:
    """
    Calculate weighted score for findings.

    Convenience function wrapping ScoringCalculator.

    Args:
        findings: List of findings.
        doc_type: Document type.

    Returns:
        ScoringResult with full breakdown.
    """
    calculator = ScoringCalculator(doc_type)
    return calculator.calculate(findings)


def calculate_legacy_score(
    p0_count: int,
    p1_count: int,
    p2_count: int,
) -> int:
    """
    Calculate legacy (pre-v1.12.0) score.

    Formula: 100 - (P0 * 10) - (P1 * 3) - (P2 * 1)
    No category weighting or caps.

    Args:
        p0_count: Number of P0 findings.
        p1_count: Number of P1 findings.
        p2_count: Number of P2 findings.

    Returns:
        Score (can be negative).
    """
    return 100 - (p0_count * 10) - (p1_count * 3) - (p2_count * 1)
