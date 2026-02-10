---
name: doc-req-fixer
description: Automated fix skill that reads review reports and applies fixes to REQ documents - handles broken links, element IDs, missing files, and iterative improvement
tags:
  - sdd-workflow
  - quality-assurance
  - req-fix
  - layer-7-artifact
  - shared-architecture
custom_fields:
  layer: 7
  artifact_type: REQ
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [REQ, Review Report, SYS]
  downstream_artifacts: [Fixed REQ, Fix Report]
  version: "1.0"
  last_updated: "2026-02-10T15:00:00"
---

# doc-req-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to REQ (Requirements Specification) documents. This skill bridges the gap between `doc-req-reviewer` (which identifies issues) and the corrected REQ, enabling iterative improvement cycles.

**Layer**: 7 (REQ Quality Improvement)

**Upstream**: REQ document, Review Report (`REQ-NN.R_fix_report_vNNN.md` or `REQ-NN-SSS.R_review_report_vNNN.md`), SYS (for system design alignment)

**Downstream**: Fixed REQ, Fix Report (`REQ-NN.F_fix_report_vNNN.md` or `REQ-NN-SSS.F_fix_report_vNNN.md`)

---

## When to Use This Skill

Use `doc-req-fixer` when:

- **After Review**: Run after `doc-req-reviewer` identifies issues
- **Iterative Improvement**: Part of Review -> Fix -> Review cycle
- **Automated Pipeline**: CI/CD integration for quality gates
- **Batch Fixes**: Apply fixes to multiple REQ documents based on review reports

**Do NOT use when**:
- No review report exists (run `doc-req-reviewer` first)
- Creating new REQ (use `doc-req` or `doc-req-autopilot`)
- Only need validation (use `doc-req-validator`)

---

## Skill Dependencies

| Skill | Purpose | When Used |
|-------|---------|-----------|
| `doc-req-reviewer` | Source of issues to fix | Input (reads review report) |
| `doc-naming` | Element ID standards | Fix element IDs |
| `doc-req` | REQ creation rules | Create missing sections |
| `doc-sys` | SYS alignment reference | Verify system traceability |

---

## Workflow Overview

```mermaid
flowchart TD
    A[Input: REQ Path] --> B[Find Latest Review Report]
    B --> C{Review Found?}
    C -->|No| D[Run doc-req-reviewer First]
    C -->|Yes| E[Parse Review Report]

    E --> F[Categorize Issues]

    subgraph FixPhases["Fix Phases"]
        F --> G[Phase 1: Create Missing Files]
        G --> H[Phase 2: Fix Broken Links]
        H --> I[Phase 3: Fix Element IDs]
        I --> J[Phase 4: Fix Content Issues]
        J --> K[Phase 5: Update References]
        K --> K2[Phase 6: Handle Upstream Drift]
    end

    K2 --> L[Write Fixed REQ]
    L --> M[Generate Fix Report]
    M --> N{Re-run Review?}
    N -->|Yes| O[Invoke doc-req-reviewer]
    O --> P{Score >= Threshold?}
    P -->|No, iterations < max| F
    P -->|Yes| Q[COMPLETE]
    N -->|No| Q
```

---

## Fix Phases

### Phase 1: Create Missing Files

Creates files that are referenced but don't exist.

**Scope**:

| Missing File | Action | Template Used |
|--------------|--------|---------------|
| `REQ-00_INDEX.md` | Create REQ index | Index template |
| `REQ-00_GLOSSARY.md` | Create requirements glossary | Glossary template |
| `UC_*.md` | Create placeholder use case doc | Use Case template |
| Reference docs (`*_REF_*.md`) | Create placeholder | REF template |

**REQ Index Template**:

```markdown
---
title: "REQ-00: Requirements Specifications Index"
tags:
  - req
  - index
  - reference
custom_fields:
  document_type: index
  artifact_type: REQ-REFERENCE
  layer: 7
---

# REQ-00: Requirements Specifications Index

Master index of all Requirements Specifications for this project.

## Functional Requirements

| REQ ID | Module | Status | Priority | SYS Refs |
|--------|--------|--------|----------|----------|
| REQ-01 | [Name] | Draft/Approved | P1/P2/P3 | SYS-01 |

## Non-Functional Requirements

| REQ ID | Category | Status | Priority |
|--------|----------|--------|----------|
| REQ-NFR-01 | Performance | Draft | P1 |
| REQ-NFR-02 | Security | Draft | P1 |

## Requirements by Priority

| Priority | REQ IDs | Count |
|----------|---------|-------|
| P1 (Critical) | | 0 |
| P2 (Important) | | 0 |
| P3 (Nice-to-have) | | 0 |

## Coverage Matrix

| SYS Component | REQ Coverage | Gaps |
|---------------|--------------|------|
| SYS-01 | REQ-01, REQ-02 | None |

---

*Maintained by doc-req-fixer. Update when adding new REQ documents.*
```

**REQ Glossary Template**:

```markdown
---
title: "REQ-00: Requirements Glossary"
tags:
  - req
  - glossary
  - reference
custom_fields:
  document_type: glossary
  artifact_type: REQ-REFERENCE
  layer: 7
---

# REQ-00: Requirements Glossary

Common terminology used across all Requirements Specification documents.

## Requirement Types

| Term | Definition | Example |
|------|------------|---------|
| FR | Functional Requirement | System shall authenticate users |
| NFR | Non-Functional Requirement | Response time < 200ms |
| UC | Use Case | User login flow |
| AC | Acceptance Criteria | Given/When/Then statement |

## Priority Levels

| Level | Definition | SLA |
|-------|------------|-----|
| P1 | Critical - Must have for MVP | Immediate |
| P2 | Important - Should have | Sprint N+1 |
| P3 | Nice-to-have - Could have | Backlog |

## Status Values

| Status | Definition | Next State |
|--------|------------|------------|
| Draft | Initial documentation | Review |
| Review | Under stakeholder review | Approved/Rejected |
| Approved | Accepted for implementation | Implemented |
| Implemented | Code complete | Verified |
| Verified | Testing complete | Closed |

## Domain Terms

<!-- Add project-specific terminology below -->

| Term | Definition | Context |
|------|------------|---------|
| [Term] | [Definition] | [Where used] |

---

*Maintained by doc-req-fixer. Update when terminology changes.*
```

**Use Case Placeholder Template**:

```markdown
---
title: "Use Case: [Use Case Name]"
tags:
  - use-case
  - requirements
  - reference
custom_fields:
  document_type: use-case
  status: placeholder
  created_by: doc-req-fixer
---

# Use Case: [Use Case Name]

> **Status**: Placeholder - Requires completion

## 1. Overview

| Attribute | Value |
|-----------|-------|
| UC ID | UC-NN |
| Actor | [Primary Actor] |
| Priority | P1/P2/P3 |
| Status | Placeholder |

## 2. Description

[TODO: Describe the use case purpose]

## 3. Preconditions

| # | Precondition |
|---|--------------|
| 1 | [Condition that must be true] |

## 4. Main Flow

| Step | Actor | System |
|------|-------|--------|
| 1 | [Actor action] | [System response] |

## 5. Alternative Flows

[TODO: Document alternative scenarios]

## 6. Postconditions

| # | Postcondition |
|---|---------------|
| 1 | [State after successful completion] |

## 7. Acceptance Criteria

| AC ID | Criteria | Type |
|-------|----------|------|
| AC-01 | [Given/When/Then] | Functional |

---

*Created by doc-req-fixer as placeholder. Complete this document to resolve broken link issues.*
```

---

### Phase 2: Fix Broken Links

Updates links to point to correct locations.

**Fix Actions**:

| Issue Code | Issue | Fix Action |
|------------|-------|------------|
| REV-L001 | Broken internal link | Update path or create target file |
| REV-L002 | External link unreachable | Add warning comment, keep link |
| REV-L003 | Absolute path used | Convert to relative path |
| REV-L004 | Missing SYS traceability link | Add link to corresponding SYS |

**Path Resolution Logic**:

```python
def fix_link_path(req_location: str, target_path: str) -> str:
    """Calculate correct relative path based on REQ location."""

    # Monolithic REQ: docs/07_REQ/REQ-01.md
    # Sectioned REQ: docs/07_REQ/REQ-01_slug/REQ-01-003_section.md

    if is_sectioned_req(req_location):
        # Need to go up one more level
        return "../" + calculate_relative_path(req_location, target_path)
    else:
        return calculate_relative_path(req_location, target_path)
```

**Cross-Layer Link Fix**:

| Source | Target | Link Pattern |
|--------|--------|--------------|
| REQ | SYS | `../06_SYS/SYS-NN.md` |
| REQ | CTR | `../08_CTR/CTR-NN.md` |
| REQ | SPEC | `../09_SPEC/SPEC-NN.md` |

---

### Phase 3: Fix Element IDs

Converts invalid element IDs to correct format.

**Conversion Rules**:

| Pattern | Issue | Conversion |
|---------|-------|------------|
| `REQ.NN.13.SS` | Code 13 invalid for REQ | `REQ.NN.01.SS` (Functional Req) |
| `FR-XXX` | Legacy pattern | `REQ.NN.01.SS` |
| `NFR-XXX` | Legacy pattern | `REQ.NN.27.SS` |
| `UC-XXX` | Legacy pattern | `REQ.NN.05.SS` |
| `AC-XXX` | Legacy pattern | `REQ.NN.06.SS` |

**Type Code Mapping** (REQ-specific valid codes: 01, 05, 06, 27):

| Code | Element Type | Description |
|------|--------------|-------------|
| 01 | Functional Requirement | System function specification |
| 05 | Use Case | User interaction scenario |
| 06 | Acceptance Criteria | Testable success criteria |
| 27 | Non-Functional Requirement | Quality attribute requirement |

**Invalid Code Conversions**:

| Invalid Code | Valid Code | Element Type |
|--------------|------------|--------------|
| 13 | 01 | Functional Requirement (was Decision Context) |
| 14 | 05 | Use Case (was Decision Statement) |
| 17 | 01 | Functional Requirement (was Component) |
| 18 | 06 | Acceptance Criteria (was Interface) |
| 22 | 01 | Functional Requirement (was Feature Item) |

**Regex Patterns**:

```python
# Find element IDs with invalid type codes for REQ
invalid_req_type_13 = r'REQ\.(\d{2})\.13\.(\d{2})'
replacement_13 = r'REQ.\1.01.\2'

invalid_req_type_14 = r'REQ\.(\d{2})\.14\.(\d{2})'
replacement_14 = r'REQ.\1.05.\2'

invalid_req_type_17 = r'REQ\.(\d{2})\.17\.(\d{2})'
replacement_17 = r'REQ.\1.01.\2'

# Find legacy patterns
legacy_fr = r'###\s+FR-(\d+):'
legacy_nfr = r'###\s+NFR-(\d+):'
legacy_uc = r'###\s+UC-(\d+):'
legacy_ac = r'###\s+AC-(\d+):'
```

---

### Phase 4: Fix Content Issues

Addresses placeholders and incomplete content.

**Fix Actions**:

| Issue Code | Issue | Fix Action |
|------------|-------|------------|
| REV-P001 | `[TODO]` placeholder | Flag for manual completion (cannot auto-fix) |
| REV-P002 | `[TBD]` placeholder | Flag for manual completion (cannot auto-fix) |
| REV-P003 | Template date `YYYY-MM-DD` | Replace with current date |
| REV-P004 | Template name `[Name]` | Replace with metadata author or flag |
| REV-P005 | Empty section | Add minimum template content |
| REV-P006 | Missing requirement status | Add "Draft" as default status |
| REV-P007 | Missing priority | Add "P2" as default priority |

**Auto-Replacements**:

```python
replacements = {
    'YYYY-MM-DDTHH:MM:SS': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    'YYYY-MM-DD': datetime.now().strftime('%Y-%m-%d'),
    'MM/DD/YYYY': datetime.now().strftime('%m/%d/%Y'),
    '[Current date]': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    '[Status]': 'Draft',
    '[Priority]': 'P2',
    '[Version]': '0.1',
}
```

**REQ-Specific Content Fixes**:

| Section | Missing Content | Auto-Fill |
|---------|-----------------|-----------|
| Status | Empty | "Draft" |
| Priority | Empty | "P2" |
| Version | Empty | "0.1" |
| Last Updated | Empty | Current date |
| Verification Method | Empty | "Test" |

---

### Phase 5: Update References

Ensures traceability and cross-references are correct.

**Fix Actions**:

| Issue | Fix Action |
|-------|------------|
| Missing `@ref:` for created files | Add reference tag |
| Incorrect cross-REQ path | Update to correct relative path |
| Missing SYS traceability | Add `@trace: SYS-NN.SS` tag |
| Missing CTR forward reference | Add `@trace: CTR-NN.SS` tag |
| Missing SPEC forward reference | Add `@trace: SPEC-NN.SS` tag |

**Traceability Matrix Update**:

```markdown
## Traceability

| REQ Element | Traces From | Traces To | Type |
|-------------|-------------|-----------|------|
| REQ.01.01.01 | SYS.01.17.01 | SPEC.01.01.01 | Requirement->Spec |
| REQ.01.05.01 | SYS.01.05.01 | BDD.01.09.01 | UseCase->Behavior |
| REQ.01.06.01 | REQ.01.01.01 | TSPEC.01.01.01 | Criteria->TestSpec |
```

---

### Phase 6: Handle Upstream Drift

Addresses issues where upstream source documents (SYS) have changed since REQ creation.

**Drift Issue Codes** (from `doc-req-reviewer` Check #9):

| Code | Severity | Description | Auto-Fix Possible |
|------|----------|-------------|-------------------|
| REV-D001 | Warning | SYS document modified after REQ | No (flag for review) |
| REV-D002 | Warning | System component changed | No (flag for review) |
| REV-D003 | Info | Upstream document version incremented | Yes (update @ref version) |
| REV-D004 | Info | New component added to SYS | No (flag for review) |
| REV-D005 | Error | Critical upstream modification (>20% change) | No (flag for review) |

**Fix Actions**:

| Issue | Auto-Fix | Action |
|-------|----------|--------|
| REV-D001/D002/D004/D005 | No | Add `[DRIFT]` marker to affected references, generate drift summary |
| REV-D003 (version change) | Yes | Update `@ref:` tag to include current version |

**Drift Marker Format**:

```markdown
<!-- DRIFT: SYS-01.md modified 2026-02-08 (REQ created 2026-02-05) -->
@ref: [SYS-01 Component 3](../../06_SYS/SYS-01.md#component-3)
```

**Drift Summary Block** (added to Fix Report):

```markdown
## Upstream Drift Summary

| Upstream Document | Reference | Modified | REQ Updated | Days Stale | Action Required |
|-------------------|-----------|----------|-------------|------------|-----------------|
| SYS-01.md | REQ-01:L57 | 2026-02-08 | 2026-02-05 | 3 | Review system changes |
| SYS-03.md | REQ-01:L89 | 2026-02-10 | 2026-02-05 | 5 | Review new component |

**Recommendation**: Review upstream SYS documents and update REQ sections if requirements are affected.
Sections potentially affected:
- REQ-01 Functional Requirements (Section 3)
- REQ-01 Use Cases (Section 5)
```

**Drift Cache Update**:

After processing drift issues, update `.drift_cache.json`:

```json
{
  "req_version": "1.0",
  "req_updated": "2026-02-10",
  "drift_reviewed": "2026-02-10",
  "upstream_hashes": {
    "../../06_SYS/SYS-01.md#component-3": "a1b2c3d4...",
    "../../06_SYS/SYS-03.md": "e5f6g7h8..."
  },
  "acknowledged_drift": [
    {
      "document": "SYS-01.md",
      "acknowledged_date": "2026-02-10",
      "reason": "Reviewed - no REQ impact"
    }
  ]
}
```

**Drift Acknowledgment Workflow**:

When drift is flagged but no REQ update is needed:

1. Run `/doc-req-fixer REQ-01 --acknowledge-drift`
2. Fixer prompts: "Review drift for SYS-01.md?"
3. User confirms no REQ changes needed
4. Fixer adds to `acknowledged_drift` array
5. Future reviews skip this drift until upstream changes again

---

## Command Usage

### Basic Usage

```bash
# Fix REQ based on latest review
/doc-req-fixer REQ-01

# Fix sectioned REQ
/doc-req-fixer REQ-01-003

# Fix with explicit review report
/doc-req-fixer REQ-01 --review-report REQ-01.R_review_report_v001.md

# Fix and re-run review
/doc-req-fixer REQ-01 --revalidate

# Fix with iteration limit
/doc-req-fixer REQ-01 --revalidate --max-iterations 3
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--review-report` | latest | Specific review report to use |
| `--revalidate` | false | Run reviewer after fixes |
| `--max-iterations` | 3 | Max fix-review cycles |
| `--fix-types` | all | Specific fix types (comma-separated) |
| `--create-missing` | true | Create missing reference files |
| `--backup` | true | Backup REQ before fixing |
| `--dry-run` | false | Preview fixes without applying |
| `--acknowledge-drift` | false | Interactive drift acknowledgment mode |
| `--update-drift-cache` | true | Update .drift_cache.json after fixes |

### Fix Types

| Type | Description |
|------|-------------|
| `missing_files` | Create missing index, glossary, use case docs |
| `broken_links` | Fix link paths |
| `element_ids` | Convert invalid/legacy element IDs |
| `content` | Fix placeholders, dates, status, priority |
| `references` | Update traceability and cross-references |
| `drift` | Handle upstream drift detection issues |
| `all` | All fix types (default) |

---

## Output Artifacts

### Fix Report

**File Naming**: `REQ-NN.F_fix_report_vNNN.md` or `REQ-NN-SSS.F_fix_report_vNNN.md`

**Location**: Same folder as the REQ document.

**Structure**:

```markdown
---
title: "REQ-NN.F: Fix Report v001"
tags:
  - req
  - fix-report
  - quality-assurance
custom_fields:
  document_type: fix-report
  artifact_type: REQ-FIX
  layer: 7
  parent_doc: REQ-NN
  source_review: REQ-NN.R_review_report_v001.md
  fix_date: "YYYY-MM-DDTHH:MM:SS"
  fix_tool: doc-req-fixer
  fix_version: "1.0"
---

# REQ-NN Fix Report v001

## Summary

| Metric | Value |
|--------|-------|
| Source Review | REQ-NN.R_review_report_v001.md |
| Issues in Review | 18 |
| Issues Fixed | 15 |
| Issues Remaining | 3 (manual review required) |
| Files Created | 3 |
| Files Modified | 5 |

## Files Created

| File | Type | Location |
|------|------|----------|
| REQ-00_INDEX.md | REQ Index | docs/07_REQ/ |
| REQ-00_GLOSSARY.md | REQ Glossary | docs/07_REQ/ |
| UC_UserLogin.md | Use Case Placeholder | docs/00_REF/use-cases/ |

## Fixes Applied

| # | Issue Code | Issue | Fix Applied | File |
|---|------------|-------|-------------|------|
| 1 | REV-L001 | Broken index link | Created REQ-00_INDEX.md | REQ-01.md |
| 2 | REV-L001 | Broken glossary link | Created REQ-00_GLOSSARY.md | REQ-01.md |
| 3 | REV-L001 | Broken use case link | Created placeholder UC file | REQ-01.md |
| 4 | REV-N004 | Element type 13 invalid | Converted to type 01 | REQ-01.md |
| 5 | REV-N004 | Legacy FR-XXX pattern | Converted to REQ.NN.01.SS | REQ-01.md |
| 6 | REV-P007 | Missing priority | Added P2 default | REQ-02.md |

## Issues Requiring Manual Review

| # | Issue Code | Issue | Location | Reason |
|---|------------|-------|----------|--------|
| 1 | REV-P001 | [TODO] placeholder | REQ-01:L67 | Domain expertise needed |
| 2 | REV-D001 | SYS drift detected | REQ-01:L145 | Review system changes |
| 3 | REV-R001 | Missing acceptance criteria | REQ-01:L200 | Define testable criteria |

## Validation After Fix

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Review Score | 82 | 93 | +11 |
| Errors | 5 | 0 | -5 |
| Warnings | 8 | 3 | -5 |

## Next Steps

1. Complete UC_UserLogin.md placeholder
2. Address remaining [TODO] placeholders
3. Add missing acceptance criteria for requirements
4. Review SYS drift and update requirements if needed
5. Run `/doc-req-reviewer REQ-01` to verify fixes
```

---

## Integration with Autopilot

This skill is invoked by `doc-req-autopilot` in the Review -> Fix cycle:

```mermaid
flowchart LR
    subgraph Phase5["Phase 5: Review & Fix Cycle"]
        A[doc-req-reviewer] --> B{Score >= 90?}
        B -->|No| C[doc-req-fixer]
        C --> D{Iteration < Max?}
        D -->|Yes| A
        D -->|No| E[Flag for Manual Review]
        B -->|Yes| F[PASS]
    end
```

**Autopilot Integration Points**:

| Phase | Action | Skill |
|-------|--------|-------|
| Phase 5a | Run initial review | `doc-req-reviewer` |
| Phase 5b | Apply fixes if issues found | `doc-req-fixer` |
| Phase 5c | Re-run review | `doc-req-reviewer` |
| Phase 5d | Repeat until pass or max iterations | Loop |

---

## Error Handling

### Recovery Actions

| Error | Action |
|-------|--------|
| Review report not found | Prompt to run `doc-req-reviewer` first |
| Cannot create file (permissions) | Log error, continue with other fixes |
| Cannot parse review report | Abort with clear error message |
| Max iterations exceeded | Generate report, flag for manual review |

### Backup Strategy

Before applying any fixes:

1. Create backup in `tmp/backup/REQ-NN_YYYYMMDD_HHMMSS/`
2. Copy all REQ files to backup location
3. Apply fixes to original files
4. If error during fix, restore from backup

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-req-reviewer` | Provides review report (input) |
| `doc-req-autopilot` | Orchestrates Review -> Fix cycle |
| `doc-req-validator` | Structural validation |
| `doc-naming` | Element ID standards |
| `doc-req` | REQ creation rules |
| `doc-sys` | Upstream system design |
| `doc-ctr` | Downstream contracts reference |
| `doc-spec` | Downstream specifications reference |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial skill creation; 6-phase fix workflow; REQ Index, Glossary, and Use Case file creation; Element ID conversion (types 01, 05, 06, 27); Broken link fixes; SYS upstream drift handling; Support for sectioned REQ naming (REQ-NN-SSS); Integration with autopilot Review->Fix cycle |
