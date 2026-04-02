# PLAN-019: Remediation Build Enhancement for YAML Documents

## Context

During BRD-03 full pipeline testing (`sdd_validate → sdd_validate_fix → sdd_review → sdd_remediate → sdd_remediate_fix`), the deterministic `sdd_remediate` tool produced a near-empty report — a single tier2 finding "Review report linked for downstream manual remediation." All remediation intelligence came from the executor (Claude), not from mcp_sdd.

The `run_remediation_build()` function currently performs only two checks (frontmatter presence, placeholder tokens) — both irrelevant for YAML documents. It does not parse the review report to extract actionable findings, nor does it validate YAML document structure.

**Goal**: Make `sdd_remediate` produce a structured, actionable remediation report by parsing the review report findings into per-finding remediation entries.

**Status**: Planned (implement after PLAN-020)

**Scope**: `mcp_sdd/src/mcp_server/remediation/` (runner + new review_parser module)

**Note**: YAML structure validation originally in this plan (Section 2) has been moved to PLAN-020 (YAML Parity), which is implemented first. This plan retains only review report parsing (Section 1) and enhanced prompt generation (Section 3).

---

## Current State

```
run_remediation_build()
  ├── _collect_markdown_files()     # also picks up YAML
  ├── frontmatter check             # skipped for YAML (fixed in 5fcd538)
  ├── placeholder check (TBD/TODO)  # rarely fires on structured YAML
  └── review_report link            # just adds pointer, doesn't parse content
```

**Output**: 1 finding ("review report linked") — no P0/P1/P2 detail, no structured actions.

**Executor prompt**: 742 chars — just says "apply_review_findings" with no specifics. The executor has to read the review report itself to figure out what to fix.

---

## Proposed Changes

### 1. Parse review report findings

When `review_report` parameter is provided and file exists:

- Read the review report (MD format)
- Extract P0/P1/P2 findings using regex patterns:
  - `| REM-P0-NNN |` table rows
  - `### Errors`, `### Warnings` sections
  - Score line (`PRD-Ready Score: NN/100`)
- Create one remediation finding per review finding with:
  - `severity`: P0 → tier1, P1 → tier1, P2 → tier2
  - `message`: finding text from review
  - `recommended_action`: specific action (add_fr, fix_business_rule, update_traceability, fix_budget, etc.)
  - `section`: which BRD section to fix (extracted from review finding)
  - `source_finding_id`: the review finding ID (REM-P0-001, etc.)

### ~~2. YAML document structure validation~~ → Moved to PLAN-020

YAML structure validation (required keys, element ID format, empty sections) is now part of PLAN-020 (YAML Parity and API Consistency), which implements YAML support across all tools including remediation.

### 2. Enhanced remediate_fix prompt

The `_build_remediate_fix_prompt()` already includes findings. With parsed review findings, the prompt will contain:

- Each P0/P1/P2 finding with specific section references
- Recommended action per finding
- Review score and threshold
- Structural validation findings

This gives the executor a structured task list instead of "go read the review report."

---

## File Changes

| File | Action | Est. Lines |
|------|--------|-----------|
| `mcp_sdd/src/mcp_server/remediation/review_parser.py` | Create — extract findings from review report MD | ~120 |
| `mcp_sdd/src/mcp_server/remediation/runner.py` | Modify `run_remediation_build()` — wire parsed findings | +30 |
| `mcp_sdd/tests/unit/test_review_parser.py` | Create — test review parsing | ~150 |

**Total**: ~300 new lines across 3 files

---

## Implementation Order

1. Create `review_parser.py` with regex-based review report parser
2. Wire parsed findings into `run_remediation_build()` remediation report
3. Write tests
4. Run full test suite
5. Smoke test against BRD-03 review report
6. Verify remediate_fix prompt includes structured findings

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
    {"severity": "tier1", "message": "Travel Rule FR absent (31 CFR 1010.410(f))",
     "source_finding_id": "REM-P0-001", "section": "functional_requirements",
     "recommended_action": "add_functional_requirement"},
    {"severity": "tier1", "message": "OFAC silent failure (HTTP 200 + malformed response)",
     "source_finding_id": "REM-P0-002", "section": "functional_requirements",
     "recommended_action": "fix_business_rule"},
    {"severity": "tier1", "message": "Budget inconsistency ($500K vs stated components)",
     "source_finding_id": "REM-P0-003", "section": "constraints_and_assumptions",
     "recommended_action": "fix_budget"}
  ],
  "review_summary": {
    "score": "72/100",
    "recommendation": "REMEDIATION REQUIRED",
    "p0_count": 3, "p1_count": 18, "p2_count": 11
  },
  "summary": {"total_findings": 32, "tier1_findings": 21, "tier2_findings": 11}
}
```

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Review report format varies | Regex patterns cover UCR output template; fallback to raw link if parsing fails |
| Large finding count inflates prompt | Cap at 50 findings in prompt; remainder as "N additional findings in report" |
| Breaking existing remediation flow | Additive — new findings supplement existing checks; no existing behavior removed |

---

## Dependencies

- **PLAN-020** (YAML parity) — must implement first; provides YAML structure validation and shared source file collector
- PLAN-018 (UCX relocation) — independent, no blocking dependency
- Review report format stability — UCR output template in `mcp_sdd/prompts/templates/review/UCR_OUTPUT_TEMPLATE.md`
