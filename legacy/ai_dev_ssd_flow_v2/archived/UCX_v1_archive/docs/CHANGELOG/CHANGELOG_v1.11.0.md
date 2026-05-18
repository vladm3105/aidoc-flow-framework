# UCX v1.11.0 - Unified UCX Scanner with Chairperson Manifest

**Release Date**: 2026-03-12
**Validation Date**: 2026-03-12

## Summary

UCX v1.11.0 introduces the **Unified UCX Scanner** with **Chairperson Remediation Findings Manifest** - a structured output format that provides authoritative finding counts, eliminating the discrepancy between raw CLI extraction and Chairperson synthesis.

**Status**: VALIDATED (BRD-02 review confirmed manifest generation)

## Validation Results

| Source | P0 | P1 | P2 | Score |
|--------|----|----|-----|-------|
| Raw CLI | 115 | 58 | 9 | 0 |
| UCX Scan (Manifest) | **10** | **14** | 9 | **62/100** |
| **Reduction** | **91%** | **76%** | 0% | - |

## New Features

### `ucx scan` Command

Unified report scanner that extracts authoritative counts from Chairperson manifest:

```bash
ucx scan BRD-02.UCR_review_report_v001.md

# Output:
# ✓ Chairperson Manifest detected (authoritative)
#
# UCX Scan Results (Manifest)
# ┌─────────────────┬────────┐
# │ Metric          │ Value  │
# ├─────────────────┼────────┤
# │ Total findings  │ 33     │
# │   P0 (Critical) │ 10     │
# │   P1 (High)     │ 14     │
# │   P2 (Medium)   │ 9      │
# │ PRD-Ready Score │ 62/100 │
# └─────────────────┴────────┘
# → Remediation will load 6 fixers
```

### Chairperson Manifest Format

Reports now include structured manifest between markers:

```markdown
<!-- UCX-MANIFEST-START -->
### Manifest Summary
| Metric | Count |
|--------|-------|
| Total Unique Findings | 33 |
| P0 (Critical) | 10 |
| P1 (High) | 14 |

### Fixer Assignment
| Fixer | Finding Count | Finding IDs |
|-------|---------------|-------------|
| architect | 3 | REM-P0-002, REM-P0-009, REM-P1-006 |

### Findings Table
| ID | Priority | Status | Fixer | Target File | Target Section | Description |
|----|----------|--------|-------|-------------|----------------|-------------|
| REM-P0-001 | P0 | OPEN | auditor | BRD-02.6.md | Add BRD.02.01.09 | SAR filing human review mandate missing |
<!-- UCX-MANIFEST-END -->
```

### Two-Layer Extraction

| Layer | Source | Purpose |
|-------|--------|---------|
| **Manifest** (authoritative) | Chairperson's `<!-- UCX-MANIFEST-START -->` section | Unique counts, PRD-Ready score, fixer assignments |
| **Persona** (fallback) | Individual persona sections | Backward compat for pre-manifest reports |

## New Module Components

| Component | Purpose |
|-----------|---------|
| `ManifestFinding` | Single finding from Chairperson manifest |
| `ManifestResult` | Extracted manifest data (counts, score, fixer routing) |
| `ScanResult` | Unified result with both manifest and persona extraction |
| `parse_chairperson_manifest()` | Parse manifest section from report |
| `scan_ucr_report()` | Unified scanner function |

## Files Changed

| File | Change |
|------|--------|
| `ucx/prescreening/ucr_analyzer.py` | Added ManifestFinding, ManifestResult, ScanResult, scan_ucr_report() |
| `ucx/prescreening/__init__.py` | Export new classes and functions |
| `ucx/cli/main.py` | New `ucx scan` command |
| `ucx/version.py` | v1.11.0 changelog with validation notes |
| `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | Chairperson manifest output format |
| `docs/UCX/skills/chairperson.md` | Manifest generation requirements |

## Benefits

1. **Eliminates discrepancy**: CLI counts now match Chairperson synthesis
2. **Authoritative source**: PRD-Ready score from Chairperson
3. **Skip pre-screening**: Remediation reads manifest directly
4. **Full traceability**: Target file + section for each finding
5. **Backward compatible**: Falls back to persona extraction for older reports

## Migration

No migration required. Existing reports without manifest will use persona extraction (fallback). New reviews automatically generate manifest.

## Related Documentation

- [UCX README](../README.md)
- [IPLAN-001 Roadmap](../../../../b-local/b-local-docs/work_plans/IPLAN-001_ucx_brd_roadmap_v1.6.md)
- [Chairperson Skill](../../skills/chairperson.md)
