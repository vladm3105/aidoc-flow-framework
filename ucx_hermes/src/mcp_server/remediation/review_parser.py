"""Parse UCR review reports (Markdown format) into structured findings.

Extracts ReviewSummary from YAML frontmatter and ReviewFinding items
from markdown tables (Section 4 preferred, Sections 2-3 + 5 fallback).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReviewSummary:
    """Structured summary extracted from report frontmatter."""

    score: str                    # e.g. "72/100"
    recommendation: str           # "REMEDIATION REQUIRED", "PROCEED", "FUNDAMENTAL REDESIGN"
    p0_count: int
    p1_count: int
    p2_count: int
    false_positives: int


@dataclass(frozen=True)
class ReviewFinding:
    """Single finding or remediation row from the review report."""

    finding_id: str               # "R1", "REM-P0-001", "P0-1"
    priority: str                 # "P0", "P1", "P2"
    severity: str                 # "tier1" (P0/P1), "tier2" (P2)
    message: str                  # Full finding / remediation text
    section: str                  # Target section reference
    source_expert: str            # Which persona raised the finding
    recommended_action: str       # Cleaned remediation text, truncated ~300 chars


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEVERITY_MAP: dict[str, str] = {
    "P0": "tier1",
    "P1": "tier1",
    "P2": "tier2",
}

# Section 4 — 6-column remediation table (preferred)
_RE_SEC4_ROW = re.compile(
    r"\|\s*(R\d+)\s*\|\s*(P[012])\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|"
)

# Sections 2-3 — 5-column P0/P1 findings table (fallback)
_RE_SEC23_ROW = re.compile(
    r"\|\s*((?:REM-)?P[012]-?\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|"
)

# Section 5 — 4-column P2 enhancements table
_RE_SEC5_ROW = re.compile(
    r"\|\s*((?:REM-)?P2-?\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|"
)


def _clean_text(text: str, max_len: int = 300) -> str:
    """Strip markdown formatting and truncate."""
    cleaned = text.strip()
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)   # strip bold
    cleaned = re.sub(r"`(.+?)`", r"\1", cleaned)          # strip backticks
    cleaned = cleaned.strip('" ')
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "..."
    return cleaned


def _priority_from_id(finding_id: str) -> str:
    """Derive priority string from a finding ID.

    Handles formats: R1 (needs external priority), REM-P0-001, P2-003.
    Returns "P0", "P1", or "P2".  Falls back to "P1" when ambiguous.
    """
    m = re.search(r"P([012])", finding_id)
    if m:
        return f"P{m.group(1)}"
    return "P1"


def _derive_recommendation(score_str: str) -> str:
    """Map numeric score to recommendation label.

    >=85 -> PROCEED, 60-84 -> REMEDIATION REQUIRED, <60 -> FUNDAMENTAL REDESIGN.
    """
    m = re.match(r"(\d+)", score_str)
    if not m:
        return "REMEDIATION REQUIRED"
    score = int(m.group(1))
    if score >= 85:
        return "PROCEED"
    if score >= 60:
        return "REMEDIATION REQUIRED"
    return "FUNDAMENTAL REDESIGN"


# ---------------------------------------------------------------------------
# Frontmatter parsing  (Strategy A)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> ReviewSummary | None:
    """Extract ReviewSummary from YAML frontmatter between ``---`` markers."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    if not isinstance(meta, dict):
        return None

    cf = meta.get("custom_fields", {})
    if not isinstance(cf, dict):
        return None

    score = str(cf.get("prd_ready_score", ""))
    if not score:
        return None

    return ReviewSummary(
        score=score,
        recommendation=_derive_recommendation(score),
        p0_count=int(cf.get("findings_p0", 0)),
        p1_count=int(cf.get("findings_p1", 0)),
        p2_count=int(cf.get("findings_p2", 0)),
        false_positives=int(cf.get("false_positives_identified", 0)),
    )


# ---------------------------------------------------------------------------
# Table parsing  (Strategy B)
# ---------------------------------------------------------------------------

def _parse_section4(text: str) -> list[ReviewFinding]:
    """Parse Section 4 'Required Remediations' 6-column table.

    Accepts both heading formats:
      ## 4. Required Remediations
      ## Section 4: Required Remediations [Table]
    """
    heading_match = re.search(
        r"^##\s+(?:Section\s+)?4[\.:]\s+Required\s+Remediations",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not heading_match:
        return []

    # Extract text from heading to next section heading or end
    section_start = heading_match.end()
    next_heading = re.search(r"^##\s+(?:Section\s+)?\d+[\.:]", text[section_start:], re.MULTILINE)
    section_text = (
        text[section_start : section_start + next_heading.start()]
        if next_heading
        else text[section_start:]
    )

    findings: list[ReviewFinding] = []
    for m in _RE_SEC4_ROW.finditer(section_text):
        fid = m.group(1).strip()
        priority = m.group(2).strip()
        # group(3) = target file, group(4) = section, group(5) = remediation, group(6) = source
        section = _clean_text(m.group(4))
        message = _clean_text(m.group(5), max_len=2000)
        source = _clean_text(m.group(6))

        findings.append(ReviewFinding(
            finding_id=fid,
            priority=priority,
            severity=_SEVERITY_MAP.get(priority, "tier2"),
            message=message,
            section=section,
            source_expert=source,
            recommended_action=_clean_text(m.group(5), max_len=2000),
        ))
    return findings


def _parse_sections_23(text: str) -> list[ReviewFinding]:
    """Parse Sections 2-3 (P0/P1 findings, 5-column tables)."""
    findings: list[ReviewFinding] = []

    for section_num in ("2", "3"):
        heading_pat = re.compile(
            rf"^##\s+(?:Section\s+)?{section_num}[\.:]\s+",
            re.MULTILINE,
        )
        heading_match = heading_pat.search(text)
        if not heading_match:
            continue

        section_start = heading_match.end()
        next_heading = re.search(r"^##\s+(?:Section\s+)?\d+[\.:]", text[section_start:], re.MULTILINE)
        section_text = (
            text[section_start : section_start + next_heading.start()]
            if next_heading
            else text[section_start:]
        )

        for m in _RE_SEC23_ROW.finditer(section_text):
            fid = m.group(1).strip()
            priority = _priority_from_id(fid)
            message = _clean_text(m.group(2), max_len=2000)
            source = _clean_text(m.group(3))
            section = _clean_text(m.group(4))

            findings.append(ReviewFinding(
                finding_id=fid,
                priority=priority,
                severity=_SEVERITY_MAP.get(priority, "tier2"),
                message=message,
                section=section,
                source_expert=source,
                recommended_action=_clean_text(m.group(2), max_len=2000),
            ))
    return findings


def _parse_section5(text: str) -> list[ReviewFinding]:
    """Parse Section 5 'Enhancement Recommendations' (P2, 4-column table)."""
    heading_match = re.search(
        r"^##\s+(?:Section\s+)?5[\.:]\s+(?:P2\s+)?Enhancement\s+Recommendations",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not heading_match:
        return []

    section_start = heading_match.end()
    next_heading = re.search(r"^##\s+(?:Section\s+)?\d+[\.:]", text[section_start:], re.MULTILINE)
    section_text = (
        text[section_start : section_start + next_heading.start()]
        if next_heading
        else text[section_start:]
    )

    findings: list[ReviewFinding] = []
    for m in _RE_SEC5_ROW.finditer(section_text):
        fid = m.group(1).strip()
        message = _clean_text(m.group(2), max_len=2000)
        source = _clean_text(m.group(3))
        value_add = _clean_text(m.group(4))

        findings.append(ReviewFinding(
            finding_id=fid,
            priority="P2",
            severity="tier2",
            message=message,
            section="",
            source_expert=source,
            recommended_action=value_add,
        ))
    return findings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_review_report(
    report_path: Path,
) -> tuple[ReviewSummary | None, list[ReviewFinding]]:
    """Parse a UCR review report.

    Returns ``(summary, findings)``.
    If parsing fails, returns ``(None, [])`` so the caller can keep its
    fallback behaviour.
    """
    try:
        text = report_path.read_text(encoding="utf-8")

        # Strategy A — frontmatter
        summary = _parse_frontmatter(text)

        # Strategy B — table parsing (Section 4 preferred, else 2-3 + 5)
        findings = _parse_section4(text)
        if not findings:
            findings = _parse_sections_23(text) + _parse_section5(text)

        return summary, findings
    except Exception:  # noqa: BLE001
        return None, []
