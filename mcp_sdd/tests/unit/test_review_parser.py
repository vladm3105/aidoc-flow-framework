"""Tests for mcp_server.remediation.review_parser module."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.remediation.review_parser import (  # noqa: E402
    ReviewFinding,
    ReviewSummary,
    parse_review_report,
)


# ---------------------------------------------------------------------------
# Helpers — minimal review report fragments
# ---------------------------------------------------------------------------

_FRONTMATTER = """\
---
custom_fields:
  prd_ready_score: "72/100"
  findings_p0: 3
  findings_p1: 18
  findings_p2: 11
  false_positives_identified: 2
---
# Review Report
"""

_SECTION4_TABLE = """\
## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation | Source |
|----|----------|-------------|---------|-------------|--------|
| R1 | P0 | file.md | Section A | Add new FR | Auditor |
| R2 | P1 | file.md | Section B | Fix typo | Reviewer |
| R3 | P2 | file.md | Section C | Improve wording | Editor |
"""

_SECTION23_TABLE = """\
## 2. Critical Findings (P0)

| ID | Finding | Expert | Section | Impact |
|----|---------|--------|---------|--------|
| REM-P0-001 | Missing requirement | Auditor | Section A | High |
| REM-P0-002 | Broken link | Reviewer | Section B | Medium |

## 3. High-Priority Findings (P1)

| ID | Finding | Expert | Section | Impact |
|----|---------|--------|---------|--------|
| P1-1 | Unclear scope | Analyst | Section C | Medium |
"""

_SECTION23_SHORT_ID = """\
## 2. Critical Findings (P0)

| ID | Finding | Expert | Section | Impact |
|----|---------|--------|---------|--------|
| P0-1 | Missing requirement | Auditor | Section A | High |
"""

_SECTION5_TABLE = """\
## 5. Enhancement Recommendations

| ID | Finding | Expert | Value |
|----|---------|--------|-------|
| REM-P2-001 | Add logging | DevOps | Observability |
| REM-P2-002 | Add caching | Architect | Performance |
"""


# ---------------------------------------------------------------------------
# Frontmatter tests
# ---------------------------------------------------------------------------

def test_parse_frontmatter_extracts_score(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_FRONTMATTER, encoding="utf-8")
    summary, _ = parse_review_report(report)
    assert summary is not None
    assert summary.score == "72/100"


def test_parse_frontmatter_extracts_counts(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_FRONTMATTER, encoding="utf-8")
    summary, _ = parse_review_report(report)
    assert summary is not None
    assert summary.p0_count == 3
    assert summary.p1_count == 18
    assert summary.p2_count == 11


def test_parse_frontmatter_missing_returns_none(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text("# Review Report\nNo frontmatter here.\n", encoding="utf-8")
    summary, _ = parse_review_report(report)
    assert summary is None


# ---------------------------------------------------------------------------
# Section 4 remediation table tests
# ---------------------------------------------------------------------------

def test_parse_remediation_table(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION4_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) == 3
    assert findings[0].finding_id == "R1"
    assert findings[1].finding_id == "R2"


def test_parse_remediation_priority_mapping(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION4_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert findings[0].severity == "tier1"  # P0
    assert findings[1].severity == "tier1"  # P1
    assert findings[2].severity == "tier2"  # P2


def test_parse_remediation_text_as_action(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION4_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert "Add new FR" in findings[0].recommended_action


# ---------------------------------------------------------------------------
# Sections 2-3 fallback tests
# ---------------------------------------------------------------------------

def test_parse_finding_table_rem_id(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION23_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) >= 2
    ids = [f.finding_id for f in findings]
    assert "REM-P0-001" in ids
    assert "REM-P0-002" in ids


def test_parse_finding_table_short_id(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION23_SHORT_ID, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) >= 1
    assert findings[0].finding_id == "P0-1"


def test_parse_fallback_when_no_section_4(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    content = _SECTION23_TABLE + _SECTION5_TABLE
    report.write_text(content, encoding="utf-8")
    _, findings = parse_review_report(report)
    # Should have findings from sections 2-3 and 5 combined
    assert len(findings) >= 3


# ---------------------------------------------------------------------------
# Section 5 P2 tests
# ---------------------------------------------------------------------------

def test_parse_p2_table_4_columns(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION5_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) == 2
    ids = [f.finding_id for f in findings]
    assert "REM-P2-001" in ids
    assert "REM-P2-002" in ids


def test_parse_p2_severity_tier2(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text(_SECTION5_TABLE, encoding="utf-8")
    _, findings = parse_review_report(report)
    for f in findings:
        assert f.severity == "tier2"


# ---------------------------------------------------------------------------
# Text cleanup tests
# ---------------------------------------------------------------------------

def test_strip_markdown_bold(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    content = """\
## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation | Source |
|----|----------|-------------|---------|-------------|--------|
| R1 | P0 | file.md | Section A | **Add bold FR** | Auditor |
"""
    report.write_text(content, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) == 1
    assert "**" not in findings[0].recommended_action
    assert "Add bold FR" in findings[0].recommended_action


def test_strip_backticks(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    content = """\
## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation | Source |
|----|----------|-------------|---------|-------------|--------|
| R1 | P0 | file.md | Section A | Add `code` ref | Auditor |
"""
    report.write_text(content, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) == 1
    assert "`" not in findings[0].recommended_action
    assert "code" in findings[0].recommended_action


def test_truncate_long_action(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    long_text = "A" * 500
    content = f"""\
## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation | Source |
|----|----------|-------------|---------|-------------|--------|
| R1 | P0 | file.md | Section A | {long_text} | Auditor |
"""
    report.write_text(content, encoding="utf-8")
    _, findings = parse_review_report(report)
    assert len(findings) == 1
    # recommended_action uses default max_len=300
    assert len(findings[0].recommended_action) <= 305  # 300 + "..."
    assert findings[0].recommended_action.endswith("...")


# ---------------------------------------------------------------------------
# Wiring tests (via run_remediation_build)
# ---------------------------------------------------------------------------

def test_findings_capped_at_50(tmp_path: Path) -> None:
    from mcp_server.remediation.runner import run_remediation_build

    # Create a source document
    doc = tmp_path / "BRD-01_test.md"
    doc.write_text("---\ntitle: test\n---\n# BRD\n", encoding="utf-8")

    # Create a review report with 60 findings in Section 4
    rows = []
    for i in range(1, 61):
        rows.append(f"| R{i} | P0 | file.md | Section {i} | Fix issue {i} | Auditor |")
    table = "\n".join(rows)
    review = tmp_path / "review_report.md"
    review.write_text(
        f"""\
## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation | Source |
|----|----------|-------------|---------|-------------|--------|
{table}
""",
        encoding="utf-8",
    )

    result = run_remediation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="1",
        document_path=doc,
        review_report=review,
    )

    review_findings = [
        f for f in result.report["findings"]
        if f["category"] == "review_finding"
    ]
    overflow = [
        f for f in result.report["findings"]
        if f["category"] == "review_finding_overflow"
    ]
    assert len(review_findings) == 50
    assert len(overflow) == 1
    assert "10 additional" in overflow[0]["message"]


def test_review_summary_in_report(tmp_path: Path) -> None:
    from mcp_server.remediation.runner import run_remediation_build

    doc = tmp_path / "BRD-01_test.md"
    doc.write_text("---\ntitle: test\n---\n# BRD\n", encoding="utf-8")

    review = tmp_path / "review_report.md"
    review.write_text(
        _FRONTMATTER + _SECTION4_TABLE,
        encoding="utf-8",
    )

    result = run_remediation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="1",
        document_path=doc,
        review_report=review,
    )

    assert "review_summary" in result.report
    summary = result.report["review_summary"]
    assert summary is not None
    assert summary["score"] == "72/100"


# ---------------------------------------------------------------------------
# Integration / edge-case tests
# ---------------------------------------------------------------------------

def test_parse_returns_empty_on_unparseable(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text("@@@ garbage content $$$\x00\x01\x02", encoding="utf-8")
    summary, findings = parse_review_report(report)
    assert summary is None
    assert findings == []


def test_parse_nonexistent_file(tmp_path: Path) -> None:
    report = tmp_path / "does_not_exist.md"
    summary, findings = parse_review_report(report)
    assert summary is None
    assert findings == []
