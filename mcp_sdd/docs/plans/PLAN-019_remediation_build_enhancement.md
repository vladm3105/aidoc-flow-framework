# PLAN-019: Remediation Build Enhancement — Review Report Parsing

## Context

During BRD-03 full pipeline testing, the deterministic `sdd_remediate` tool produced a near-empty report — a single tier2 finding "Review report linked for downstream manual remediation." All remediation intelligence came from the executor (Claude), not from mcp_sdd. The executor had to read the review report itself to figure out what to fix.

**Goal**: Make `sdd_remediate` parse the review report and produce structured, per-finding remediation entries so the `sdd_remediate_fix` prompt gives the executor an actionable task list.

**Status**: Planned (implement after PLAN-018)

**Scope**: `mcp_sdd/src/mcp_server/remediation/` (runner + new review_parser module)

---

## Current State (after PLAN-018)

```
run_remediation_build()
  ├── frontmatter check          # skipped for YAML (5fcd538)
  ├── placeholder check          # TBD/TODO tokens
  ├── YAML structure validation  # PLAN-018: required keys, empty sections, element IDs
  └── review_report link         # just adds pointer, doesn't parse content
```

**Output**: YAML documents get structure findings (PLAN-018), but the review report is still just a tier2 pointer. The executor prompt (~742 chars) says "apply_review_findings" with no specifics.

**Prompt already enhanced**: `_build_remediate_fix_prompt()` (improved in PLAN-016/017) automatically includes all findings in the prompt. Once the remediation report has parsed review findings, they flow into the prompt with no additional prompt code changes needed.

---

## Proposed Changes

### 1. Create `review_parser.py`

New module: `mcp_sdd/src/mcp_server/remediation/review_parser.py`

Parses UCR review reports (MD format) using two strategies:

**Strategy A — Frontmatter extraction** (fast, reliable):
Review reports have YAML frontmatter with structured metadata:
```yaml
custom_fields:
  prd_ready_score: "72/100"
  findings_p0: 3
  findings_p1: 18
  findings_p2: 11
  false_positives_identified: 4
```
Extract score, counts, and recommendation directly.

**Strategy B — Table row parsing** (detailed findings):
Two table formats to support:

1. **Section 4 "Required Remediations"** (preferred — has actionable detail):
   ```
   | R1 | P0 | `target_file.md` | Section ref | Remediation text | Source |
   ```
   Regex: `r'\|\s*(R\d+)\s*\|\s*(P[012])\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'`

2. **Sections 2-3 "Critical/High Findings"** (fallback — descriptive, not actionable):
   ```
   | REM-P0-001 | Finding text | Expert | Section | Impact |
   ```
   Regex: supports both `REM-P0-NNN` and `P0-N` ID patterns.

**Priority**: Parse Section 4 first. If found, use remediation text as `recommended_action`. If Section 4 absent, fall back to Sections 2-3 findings.

**Fallback**: If parsing extracts 0 findings, keep the existing "Review report linked" tier2 finding unchanged. Never replace a working fallback with an empty result.

**Function signatures**:

```python
@dataclass(frozen=True)
class ReviewSummary:
    score: str                    # e.g., "72/100"
    recommendation: str           # e.g., "REMEDIATION REQUIRED"
    p0_count: int
    p1_count: int
    p2_count: int
    false_positives: int

@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str               # "R1", "REM-P0-001", "P0-1"
    priority: str                 # "P0", "P1", "P2"
    severity: str                 # "tier1" (P0/P1), "tier2" (P2)
    message: str                  # Finding or remediation text
    section: str                  # Target section reference
    source_expert: str            # Which persona raised it
    recommended_action: str       # Remediation text (from Section 4) or inferred

def parse_review_report(report_path: Path) -> tuple[ReviewSummary | None, list[ReviewFinding]]:
    """Parse a UCR review report and extract structured findings.
    
    Returns (summary, findings). If parsing fails completely,
    returns (None, []) — caller should keep fallback finding.
    """
```

### 2. Wire into `run_remediation_build()`

In `remediation/runner.py`, replace the simple "review report linked" block:

```python
# Current:
if review_report is not None and review_report.exists():
    findings.append(_build_finding_entry(..., message="Review report linked..."))

# Proposed:
if review_report is not None and review_report.exists():
    from mcp_server.remediation.review_parser import parse_review_report
    review_summary, review_findings = parse_review_report(review_report)
    
    if review_findings:
        for rf in review_findings:
            findings.append(_build_finding_entry(
                file_path=str(review_report),
                doc_type=doc_type, layer=layer,
                category="review_finding",
                severity=rf.severity,
                message=rf.message,
                recommended_action=rf.recommended_action,
                finding_ids=finding_ids, action_ids=action_ids,
            ))
        # Add review summary to report
        report["review_summary"] = dataclasses.asdict(review_summary) if review_summary else None
    else:
        # Fallback: keep pointer if parsing returned nothing
        findings.append(_build_finding_entry(..., message="Review report linked..."))
```

### ~~3. Enhanced remediate_fix prompt~~ — Already done

`_build_remediate_fix_prompt()` was improved in PLAN-016/017 to automatically include all findings from the remediation report. Once parsed review findings are in the findings list, they flow into the executor prompt with no additional code changes.

---

## File Changes

| File | Action | Est. Lines |
|------|--------|-----------|
| `mcp_sdd/src/mcp_server/remediation/review_parser.py` | **Create** — frontmatter + table parsing | ~150 |
| `mcp_sdd/src/mcp_server/remediation/runner.py` | **Modify** — wire parsed findings, add review_summary | +30 |
| `mcp_sdd/tests/unit/test_review_parser.py` | **Create** — parser tests | ~180 |
| `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.9.0.md` | **Create** | ~40 |
| `mcp_sdd/docs/ROADMAP.md` | **Modify** — add v1.9.0 | +15 |
| `mcp_sdd/docs/README.md` | **Modify** — add changelog link | +1 |
| `changelog/CHANGELOG_v0.16.0.md` | **Create** | ~30 |
| `roadmap/ROADMAP.md` | **Modify** — add v0.16.0 | +15 |

**Total**: ~460 lines across 8 files

---

## Implementation Order

1. Create `review_parser.py` with `parse_review_report()`
2. Wire parsed findings into `run_remediation_build()`
3. Write `test_review_parser.py`
4. Run full test suite (187 existing + new)
5. Smoke test: `sdd_remediate` on BRD-03 with review report — verify structured findings
6. Smoke test: `sdd_remediate_fix` prompt — verify findings in executor prompt
7. Create mcp_sdd changelog v1.9.0 and roadmap entry
8. Create framework changelog v0.16.0 and roadmap entry
9. Update READMEs

---

## Expected Outcome

### Before (current)

```json
{
  "findings": [
    {"severity": "tier2", "message": "Review report linked for downstream manual remediation"}
  ],
  "summary": {"total_findings": 1}
}
```

### After (proposed)

```json
{
  "findings": [
    {"severity": "tier1", "category": "review_finding",
     "message": "Add Travel Rule FR BRD.03.01.13 — collect/transmit originator/beneficiary data for transactions >= $3,000 per 31 CFR 1010.410(f)",
     "recommended_action": "Add FR BRD.03.01.13 Travel Rule Compliance"},
    {"severity": "tier1", "category": "review_finding",
     "message": "Extend OFAC fail-closed to cover HTTP 200 with empty/null/malformed/schema-mismatch responses",
     "recommended_action": "Add schema validation to BRD.03.01.02 business rules"},
    {"severity": "tier1", "category": "review_finding",
     "message": "Revise budget constraint BRD.03.03.16 — include itemized cost breakdown",
     "recommended_action": "Revise BRD.03.03.16 with compliance cost breakdown table"}
  ],
  "review_summary": {
    "score": "72/100",
    "recommendation": "REMEDIATION REQUIRED",
    "p0_count": 3, "p1_count": 18, "p2_count": 11,
    "false_positives": 4
  },
  "summary": {"total_findings": 24, "tier1_findings": 21, "tier2_findings": 3}
}
```

---

## Test Plan

### `test_review_parser.py`

**Frontmatter parsing**:
- `test_parse_frontmatter_extracts_score` — score "72/100" from frontmatter
- `test_parse_frontmatter_extracts_counts` — p0=3, p1=18, p2=11
- `test_parse_frontmatter_missing_returns_none` — no frontmatter → summary is None

**Section 4 remediation table**:
- `test_parse_remediation_table_extracts_findings` — parse R1/R2/R3 rows
- `test_parse_remediation_priority_mapping` — P0 → tier1, P1 → tier1, P2 → tier2
- `test_parse_remediation_text_as_action` — remediation text becomes recommended_action

**Section 2-3 finding tables (fallback)**:
- `test_parse_finding_table_rem_id_pattern` — `REM-P0-001` ID format
- `test_parse_finding_table_short_id_pattern` — `P0-1` ID format
- `test_parse_fallback_when_no_section_4` — only Sections 2-3 present

**Integration**:
- `test_parse_returns_empty_on_unparseable` — garbage input → (None, [])
- `test_parse_full_brd03_report` — real BRD-03 review report (if available in test)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Review report format varies between executors | Parse frontmatter first (standardized); table parsing handles both ID patterns |
| Section 4 absent in some reviews | Fall back to Sections 2-3; if both fail, keep "review linked" finding |
| Large finding count inflates prompt | Cap at 50 findings; remainder as "N additional findings in report" |
| Breaking existing remediation flow | Additive — fallback preserved when parsing returns 0 results |
| Regex fragility on table formatting | Test against real BRD-03 report; handle pipe-alignment variations |

---

## Dependencies

- **PLAN-018** (YAML parity) — done; provides YAML structure validation and shared collector
- PLAN-020 (UCX relocation) — independent
- UCR output template format: `mcp_sdd/prompts/templates/review/UCR_OUTPUT_TEMPLATE.md`
