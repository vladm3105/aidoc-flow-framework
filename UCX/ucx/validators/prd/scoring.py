"""PRD Dual Readiness Scoring Module.

Calculates SYS-Ready and EARS-Ready scores for PRD documents.

SYS-Ready Score (System Development Readiness):
- 40% Product Completeness (sections, elements, acceptance criteria)
- 30% Technical Readiness (constraints, dependencies, risks)
- 20% Business Alignment (goals, metrics, stakeholders)
- 10% Traceability (upstream BRD, element coverage)

EARS-Ready Score (EARS Conversion Readiness):
- 25% Timing Profiles (sequence, priority, phases)
- 25% Boundary Values (limits, thresholds, constraints)
- 25% State Machine (states, transitions, conditions)
- 15% Fallback Paths (error handling, edge cases)
- 10% Threshold Registry (metrics, KPIs, targets)

Thresholds:
- MVP Profile: ≥85%
- Standard Profile: ≥90%
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from ucx.validators.prd.schema import (
    REQUIRED_SECTIONS,
    BLOCKING_SECTIONS,
    VALID_TYPE_CODES,
    TEMPLATE_PROFILES,
)


@dataclass
class ScoringResult:
    """Result of PRD scoring calculation."""

    sys_ready: float
    ears_ready: float
    profile: str
    threshold: int

    # SYS-Ready components
    product_completeness: float
    technical_readiness: float
    business_alignment: float
    traceability: float

    # EARS-Ready components
    timing_profiles: float
    boundary_values: float
    state_machine: float
    fallback_paths: float
    threshold_registry: float

    @property
    def sys_passed(self) -> bool:
        """Check if SYS-Ready score meets threshold."""
        return self.sys_ready >= self.threshold

    @property
    def ears_passed(self) -> bool:
        """Check if EARS-Ready score meets threshold."""
        return self.ears_ready >= self.threshold

    @property
    def both_passed(self) -> bool:
        """Check if both scores pass threshold."""
        return self.sys_passed and self.ears_passed

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "sys_ready": self.sys_ready,
            "ears_ready": self.ears_ready,
            "profile": self.profile,
            "threshold": self.threshold,
            "sys_passed": self.sys_passed,
            "ears_passed": self.ears_passed,
            "components": {
                "sys": {
                    "product_completeness": self.product_completeness,
                    "technical_readiness": self.technical_readiness,
                    "business_alignment": self.business_alignment,
                    "traceability": self.traceability,
                },
                "ears": {
                    "timing_profiles": self.timing_profiles,
                    "boundary_values": self.boundary_values,
                    "state_machine": self.state_machine,
                    "fallback_paths": self.fallback_paths,
                    "threshold_registry": self.threshold_registry,
                },
            },
        }


class PRDScorer:
    """Calculator for PRD dual readiness scores."""

    def __init__(self, profile: str = "mvp"):
        """Initialize scorer with profile.

        Args:
            profile: Template profile ('mvp' or 'standard')
        """
        self.profile = profile
        self.threshold = TEMPLATE_PROFILES.get(profile, TEMPLATE_PROFILES["mvp"])["sys_ready_threshold"]

    def calculate(self, content: str) -> ScoringResult:
        """Calculate both readiness scores.

        Args:
            content: Combined PRD content

        Returns:
            ScoringResult with both scores and components
        """
        # Calculate SYS-Ready components
        product_completeness = self._calc_product_completeness(content)
        technical_readiness = self._calc_technical_readiness(content)
        business_alignment = self._calc_business_alignment(content)
        traceability = self._calc_traceability(content)

        # SYS-Ready weighted average
        sys_ready = (
            product_completeness * 0.40 +
            technical_readiness * 0.30 +
            business_alignment * 0.20 +
            traceability * 0.10
        )

        # Calculate EARS-Ready components
        timing_profiles = self._calc_timing_profiles(content)
        boundary_values = self._calc_boundary_values(content)
        state_machine = self._calc_state_machine(content)
        fallback_paths = self._calc_fallback_paths(content)
        threshold_registry = self._calc_threshold_registry(content)

        # EARS-Ready weighted average
        ears_ready = (
            timing_profiles * 0.25 +
            boundary_values * 0.25 +
            state_machine * 0.25 +
            fallback_paths * 0.15 +
            threshold_registry * 0.10
        )

        return ScoringResult(
            sys_ready=round(sys_ready, 1),
            ears_ready=round(ears_ready, 1),
            profile=self.profile,
            threshold=self.threshold,
            product_completeness=round(product_completeness, 1),
            technical_readiness=round(technical_readiness, 1),
            business_alignment=round(business_alignment, 1),
            traceability=round(traceability, 1),
            timing_profiles=round(timing_profiles, 1),
            boundary_values=round(boundary_values, 1),
            state_machine=round(state_machine, 1),
            fallback_paths=round(fallback_paths, 1),
            threshold_registry=round(threshold_registry, 1),
        )

    # =========================================================================
    # SYS-READY COMPONENTS (40% + 30% + 20% + 10% = 100%)
    # =========================================================================

    def _calc_product_completeness(self, content: str) -> float:
        """Calculate product completeness score (40% of SYS-Ready).

        Measures:
        - Section coverage (21 sections)
        - Element density (element IDs per section)
        - Acceptance criteria coverage
        - Section 10 content (BLOCKING)
        """
        score = 0.0

        # Section coverage (40%)
        section_pattern = re.compile(r"^## (\d+)\.", re.MULTILINE)
        found_sections = set(int(m.group(1)) for m in section_pattern.finditer(content))
        section_coverage = len(found_sections) / 21.0
        score += section_coverage * 40.0

        # Element density (25%)
        element_pattern = re.compile(r"\bPRD\.\d{2}\.\d{2}\.\d{2}\b")
        element_count = len(element_pattern.findall(content))
        # Expect roughly 3-5 elements per section = 63-105 total
        element_density = min(element_count / 50.0, 1.0)  # Cap at 50+ elements
        score += element_density * 25.0

        # Acceptance criteria (20%)
        ac_pattern = re.compile(r"PRD\.\d{2}\.06\.\d{2}")
        ac_count = len(ac_pattern.findall(content))
        ac_coverage = min(ac_count / 10.0, 1.0)  # Expect at least 10 ACs
        score += ac_coverage * 20.0

        # Section 10 content (15%) - BLOCKING
        section_10 = self._get_section_content(content, 10)
        if section_10:
            # Check for substantive content
            content_only = re.sub(r"^#+.*$", "", section_10, flags=re.MULTILINE).strip()
            if len(content_only) >= 200:
                score += 15.0
            elif len(content_only) >= 100:
                score += 7.5

        return score

    def _calc_technical_readiness(self, content: str) -> float:
        """Calculate technical readiness score (30% of SYS-Ready).

        Measures:
        - Constraints defined (PRD.NN.03.SS)
        - Dependencies mapped (PRD.NN.05.SS)
        - Risks identified (PRD.NN.07.SS)
        - Functional requirements (PRD.NN.01.SS)
        """
        score = 0.0

        # Constraints (25%)
        constraint_pattern = re.compile(r"PRD\.\d{2}\.03\.\d{2}")
        constraint_count = len(constraint_pattern.findall(content))
        score += min(constraint_count / 5.0, 1.0) * 25.0

        # Dependencies (25%)
        dep_pattern = re.compile(r"PRD\.\d{2}\.05\.\d{2}")
        dep_count = len(dep_pattern.findall(content))
        score += min(dep_count / 5.0, 1.0) * 25.0

        # Risks (25%)
        risk_pattern = re.compile(r"PRD\.\d{2}\.07\.\d{2}")
        risk_count = len(risk_pattern.findall(content))
        score += min(risk_count / 5.0, 1.0) * 25.0

        # Functional requirements (25%)
        fr_pattern = re.compile(r"PRD\.\d{2}\.01\.\d{2}")
        fr_count = len(fr_pattern.findall(content))
        score += min(fr_count / 10.0, 1.0) * 25.0

        return score

    def _calc_business_alignment(self, content: str) -> float:
        """Calculate business alignment score (20% of SYS-Ready).

        Measures:
        - Goals defined (PRD.NN.23.SS)
        - Success metrics (PRD.NN.08.SS)
        - Stakeholder needs (PRD.NN.24.SS)
        - User stories (PRD.NN.09.SS)
        """
        score = 0.0

        # Goals (25%)
        goal_pattern = re.compile(r"PRD\.\d{2}\.23\.\d{2}")
        goal_count = len(goal_pattern.findall(content))
        score += min(goal_count / 3.0, 1.0) * 25.0

        # Success metrics (25%)
        metric_pattern = re.compile(r"PRD\.\d{2}\.08\.\d{2}")
        metric_count = len(metric_pattern.findall(content))
        score += min(metric_count / 5.0, 1.0) * 25.0

        # Stakeholder needs (25%)
        stakeholder_pattern = re.compile(r"PRD\.\d{2}\.24\.\d{2}")
        stakeholder_count = len(stakeholder_pattern.findall(content))
        score += min(stakeholder_count / 3.0, 1.0) * 25.0

        # User stories (25%)
        us_pattern = re.compile(r"PRD\.\d{2}\.09\.\d{2}")
        us_count = len(us_pattern.findall(content))
        score += min(us_count / 10.0, 1.0) * 25.0

        return score

    def _calc_traceability(self, content: str) -> float:
        """Calculate traceability score (10% of SYS-Ready).

        Measures:
        - BRD upstream references (@brd: tags)
        - Element cross-references
        - Document Control completeness
        """
        score = 0.0

        # BRD traceability (40%)
        brd_pattern = re.compile(r"@brd:\s*BRD\.\d{2}\.\d{2}\.\d{2}")
        brd_refs = len(brd_pattern.findall(content))
        if brd_refs > 0:
            score += min(brd_refs / 10.0, 1.0) * 40.0

        # Cross-references (30%)
        xref_pattern = re.compile(r"(?:see|ref|→)\s*PRD\.\d{2}\.\d{2}\.\d{2}", re.IGNORECASE)
        xref_count = len(xref_pattern.findall(content))
        score += min(xref_count / 10.0, 1.0) * 30.0

        # Document Control (30%)
        doc_control = self._get_section_content(content, 1)
        if doc_control:
            required_fields = ["status", "version", "author", "brd"]
            found = sum(1 for f in required_fields if f.lower() in doc_control.lower())
            score += (found / len(required_fields)) * 30.0

        return score

    # =========================================================================
    # EARS-READY COMPONENTS (25% + 25% + 25% + 15% + 10% = 100%)
    # =========================================================================

    def _calc_timing_profiles(self, content: str) -> float:
        """Calculate timing profiles score (25% of EARS-Ready).

        Measures:
        - Sequence/order indicators
        - Priority definitions
        - Phase/milestone references
        - Timeline mentions
        """
        score = 0.0

        # Sequence indicators (30%)
        sequence_keywords = ["first", "then", "after", "before", "next", "finally", "step"]
        sequence_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in sequence_keywords
        )
        score += min(sequence_count / 20.0, 1.0) * 30.0

        # Priority indicators (30%)
        priority_pattern = re.compile(r"\bP[0-4]\b|\bMust\b|\bShould\b|\bCould\b", re.IGNORECASE)
        priority_count = len(priority_pattern.findall(content))
        score += min(priority_count / 10.0, 1.0) * 30.0

        # Phase/milestone (20%)
        phase_keywords = ["phase", "milestone", "sprint", "release", "iteration"]
        phase_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in phase_keywords
        )
        score += min(phase_count / 5.0, 1.0) * 20.0

        # Timeline (20%)
        timeline_pattern = re.compile(r"\b(?:day|week|month|quarter|year)\b", re.IGNORECASE)
        timeline_count = len(timeline_pattern.findall(content))
        score += min(timeline_count / 5.0, 1.0) * 20.0

        return score

    def _calc_boundary_values(self, content: str) -> float:
        """Calculate boundary values score (25% of EARS-Ready).

        Measures:
        - Numeric limits and ranges
        - Min/max specifications
        - Threshold values
        - Capacity constraints
        """
        score = 0.0

        # Numeric ranges (40%)
        range_pattern = re.compile(r"\d+\s*[-–]\s*\d+|\d+\s*to\s*\d+", re.IGNORECASE)
        range_count = len(range_pattern.findall(content))
        score += min(range_count / 10.0, 1.0) * 40.0

        # Min/max (30%)
        minmax_pattern = re.compile(r"\b(?:min(?:imum)?|max(?:imum)?|at\s+(?:least|most))\b", re.IGNORECASE)
        minmax_count = len(minmax_pattern.findall(content))
        score += min(minmax_count / 10.0, 1.0) * 30.0

        # Units/measures (30%)
        unit_pattern = re.compile(r"\d+\s*(?:ms|seconds?|minutes?|hours?|MB|GB|KB|%|users?|requests?)", re.IGNORECASE)
        unit_count = len(unit_pattern.findall(content))
        score += min(unit_count / 10.0, 1.0) * 30.0

        return score

    def _calc_state_machine(self, content: str) -> float:
        """Calculate state machine score (25% of EARS-Ready).

        Measures:
        - State definitions
        - Transition language
        - Condition indicators
        - Status/workflow mentions
        """
        score = 0.0

        # State keywords (35%)
        state_keywords = ["state", "status", "mode", "phase", "pending", "active", "completed"]
        state_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in state_keywords
        )
        score += min(state_count / 15.0, 1.0) * 35.0

        # Transition language (35%)
        transition_keywords = ["transition", "change", "become", "switch", "move to", "enters"]
        transition_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in transition_keywords
        )
        score += min(transition_count / 10.0, 1.0) * 35.0

        # Conditions (30%)
        condition_pattern = re.compile(r"\b(?:if|when|while|unless|until|given)\b", re.IGNORECASE)
        condition_count = len(condition_pattern.findall(content))
        score += min(condition_count / 20.0, 1.0) * 30.0

        return score

    def _calc_fallback_paths(self, content: str) -> float:
        """Calculate fallback paths score (15% of EARS-Ready).

        Measures:
        - Error handling mentions
        - Edge case coverage
        - Fallback/alternative flows
        - Exception handling
        """
        score = 0.0

        # Error handling (40%)
        error_keywords = ["error", "fail", "exception", "invalid", "timeout", "retry"]
        error_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in error_keywords
        )
        score += min(error_count / 15.0, 1.0) * 40.0

        # Edge cases (30%)
        edge_keywords = ["edge case", "corner case", "boundary", "limit", "overflow", "empty"]
        edge_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in edge_keywords
        )
        score += min(edge_count / 5.0, 1.0) * 30.0

        # Alternatives (30%)
        alt_keywords = ["fallback", "alternative", "otherwise", "default", "else", "backup"]
        alt_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in alt_keywords
        )
        score += min(alt_count / 5.0, 1.0) * 30.0

        return score

    def _calc_threshold_registry(self, content: str) -> float:
        """Calculate threshold registry score (10% of EARS-Ready).

        Measures:
        - KPI definitions
        - Metric thresholds
        - Target values
        - SLA/SLO mentions
        """
        score = 0.0

        # KPI/metric mentions (40%)
        kpi_keywords = ["kpi", "metric", "measure", "indicator", "benchmark"]
        kpi_count = sum(
            len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
            for kw in kpi_keywords
        )
        score += min(kpi_count / 10.0, 1.0) * 40.0

        # Target values (30%)
        target_pattern = re.compile(r"\btarget\s*[:=]?\s*\d+", re.IGNORECASE)
        target_count = len(target_pattern.findall(content))
        score += min(target_count / 5.0, 1.0) * 30.0

        # SLA/SLO (30%)
        sla_pattern = re.compile(r"\b(?:SLA|SLO|uptime|availability|latency)\b", re.IGNORECASE)
        sla_count = len(sla_pattern.findall(content))
        score += min(sla_count / 5.0, 1.0) * 30.0

        return score

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_section_content(self, content: str, section_num: int) -> Optional[str]:
        """Extract content for a specific section."""
        pattern = re.compile(
            rf"^## {section_num}\..*?(?=^## \d+\.|\Z)",
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(content)
        return match.group(0) if match else None


def calculate_scores(content: str, profile: str = "mvp") -> ScoringResult:
    """Convenience function to calculate scores.

    Args:
        content: PRD content
        profile: Template profile

    Returns:
        ScoringResult with both scores
    """
    scorer = PRDScorer(profile=profile)
    return scorer.calculate(content)
