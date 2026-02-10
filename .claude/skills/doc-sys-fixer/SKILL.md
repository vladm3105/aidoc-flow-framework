---
name: doc-sys-fixer
description: Automated fix skill that reads review reports and applies fixes to SYS documents - handles broken links, element IDs, missing files, and iterative improvement
tags:
  - sdd-workflow
  - quality-assurance
  - sys-fix
  - layer-6-artifact
  - shared-architecture
custom_fields:
  layer: 6
  artifact_type: SYS
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [SYS, Review Report, ADR]
  downstream_artifacts: [Fixed SYS, Fix Report]
  version: "1.0"
  last_updated: "2026-02-10T15:00:00"
---

# doc-sys-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to SYS (System Design Specification) documents. This skill bridges the gap between `doc-sys-reviewer` (which identifies issues) and the corrected SYS, enabling iterative improvement cycles.

**Layer**: 6 (SYS Quality Improvement)

**Upstream**: SYS document, Review Report (`SYS-NN.F_fix_report_vNNN.md`), ADR (for architecture alignment)

**Downstream**: Fixed SYS, Fix Report (`SYS-NN.F_fix_report_vNNN.md`)

---

## When to Use This Skill

Use `doc-sys-fixer` when:

- **After Review**: Run after `doc-sys-reviewer` identifies issues
- **Iterative Improvement**: Part of Review -> Fix -> Review cycle
- **Automated Pipeline**: CI/CD integration for quality gates
- **Batch Fixes**: Apply fixes to multiple SYS documents based on review reports

**Do NOT use when**:
- No review report exists (run `doc-sys-reviewer` first)
- Creating new SYS (use `doc-sys` or `doc-sys-autopilot`)
- Only need validation (use `doc-sys-validator`)

---

## Skill Dependencies

| Skill | Purpose | When Used |
|-------|---------|-----------|
| `doc-sys-reviewer` | Source of issues to fix | Input (reads review report) |
| `doc-naming` | Element ID standards | Fix element IDs |
| `doc-sys` | SYS creation rules | Create missing sections |
| `doc-adr` | ADR alignment reference | Verify architecture traceability |

---

## Workflow Overview

```mermaid
flowchart TD
    A[Input: SYS Path] --> B[Find Latest Review Report]
    B --> C{Review Found?}
    C -->|No| D[Run doc-sys-reviewer First]
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

    K2 --> L[Write Fixed SYS]
    L --> M[Generate Fix Report]
    M --> N{Re-run Review?}
    N -->|Yes| O[Invoke doc-sys-reviewer]
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
| `SYS-00_INDEX.md` | Create SYS index | Index template |
| `COMP_*.md` | Create placeholder component doc | Component template |
| `INT_*.md` | Create placeholder interface doc | Interface template |
| Reference docs (`*_REF_*.md`) | Create placeholder | REF template |

**SYS Index Template**:

```markdown
---
title: "SYS-00: System Design Specifications Index"
tags:
  - sys
  - index
  - reference
custom_fields:
  document_type: index
  artifact_type: SYS-REFERENCE
  layer: 6
---

# SYS-00: System Design Specifications Index

Master index of all System Design Specifications for this project.

## System Components

| SYS ID | Component | Status | Last Updated | ADR Refs |
|--------|-----------|--------|--------------|----------|
| SYS-01 | [Name] | Draft/Final | YYYY-MM-DD | ADR-01, ADR-02 |

## Component Relationships

| Component | Depends On | Depended By |
|-----------|------------|-------------|
| SYS-01 | | |

## Interface Catalog

| Interface ID | Type | Provider | Consumer |
|--------------|------|----------|----------|
| INT-01 | API | SYS-01 | SYS-02 |

---

*Maintained by doc-sys-fixer. Update when adding new SYS documents.*
```

**Component Placeholder Template**:

```markdown
---
title: "Component Specification: [Component Name]"
tags:
  - component
  - system-design
  - reference
custom_fields:
  document_type: component
  status: placeholder
  created_by: doc-sys-fixer
---

# Component Specification: [Component Name]

> **Status**: Placeholder - Requires completion

## 1. Overview

[TODO: Document component overview]

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| [Name] | [What it handles] |

## 3. Interfaces

| Interface | Type | Direction | Connected To |
|-----------|------|-----------|--------------|
| [Name] | REST/gRPC/Event | In/Out | [Component] |

## 4. Data Structures

[TODO: Document key data structures]

## 5. Architecture Decisions

| ADR | Title | Impact |
|-----|-------|--------|
| ADR-NN | [Title] | [How it affects this component] |

---

*Created by doc-sys-fixer as placeholder. Complete this document to resolve broken link issues.*
```

**Interface Placeholder Template**:

```markdown
---
title: "Interface Specification: [Interface Name]"
tags:
  - interface
  - system-design
  - reference
custom_fields:
  document_type: interface
  status: placeholder
  created_by: doc-sys-fixer
---

# Interface Specification: [Interface Name]

> **Status**: Placeholder - Requires completion

## 1. Overview

[TODO: Document interface purpose]

## 2. Protocol

| Attribute | Value |
|-----------|-------|
| Type | REST / gRPC / Event / Message |
| Format | JSON / Protobuf / Avro |
| Authentication | JWT / API Key / mTLS |

## 3. Operations

| Operation | Method | Path/Topic | Description |
|-----------|--------|------------|-------------|
| [Name] | GET/POST | /path | [Description] |

## 4. Data Models

[TODO: Document request/response models]

---

*Created by doc-sys-fixer as placeholder. Complete this document to resolve broken link issues.*
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
| REV-L004 | Missing ADR traceability link | Add link to corresponding ADR |

**Path Resolution Logic**:

```python
def fix_link_path(sys_location: str, target_path: str) -> str:
    """Calculate correct relative path based on SYS location."""

    # Monolithic SYS: docs/06_SYS/SYS-01.md
    # Sectioned SYS: docs/06_SYS/SYS-01_slug/SYS-01.3_section.md

    if is_sectioned_sys(sys_location):
        # Need to go up one more level
        return "../" + calculate_relative_path(sys_location, target_path)
    else:
        return calculate_relative_path(sys_location, target_path)
```

**Cross-Layer Link Fix**:

| Source | Target | Link Pattern |
|--------|--------|--------------|
| SYS | ADR | `../05_ADR/ADR-NN.md` |
| SYS | REQ | `../07_REQ/REQ-NN.md` |
| SYS | CTR | `../08_CTR/CTR-NN.md` |

---

### Phase 3: Fix Element IDs

Converts invalid element IDs to correct format.

**Conversion Rules**:

| Pattern | Issue | Conversion |
|---------|-------|------------|
| `SYS.NN.06.SS` | Code 06 invalid for SYS | `SYS.NN.17.SS` (Component) |
| `COMP-XXX` | Legacy pattern | `SYS.NN.17.SS` |
| `INT-XXX` | Legacy pattern | `SYS.NN.18.SS` |
| `MOD-XXX` | Legacy pattern | `SYS.NN.19.SS` |
| `DEP-XXX` | Legacy pattern | `SYS.NN.20.SS` |
| `FLOW-XXX` | Legacy pattern | `SYS.NN.21.SS` |

**Type Code Mapping** (SYS-specific valid codes: 01, 05, 17, 18, 19, 20, 21):

| Code | Element Type | Description |
|------|--------------|-------------|
| 01 | Functional Requirement | System function specification |
| 05 | Use Case | System use case |
| 17 | Component | System component |
| 18 | Interface | System interface |
| 19 | Module | Software module |
| 20 | Dependency | External dependency |
| 21 | Data Flow | Data flow specification |

**Invalid Code Conversions**:

| Invalid Code | Valid Code | Element Type |
|--------------|------------|--------------|
| 06 | 01 | Functional Requirement (was Acceptance Criteria) |
| 13 | 17 | Component (was Decision Context) |
| 14 | 18 | Interface (was Decision Statement) |
| 22 | 19 | Module (was Feature Item) |

**Regex Patterns**:

```python
# Find element IDs with invalid type codes for SYS
invalid_sys_type_06 = r'SYS\.(\d{2})\.06\.(\d{2})'
replacement_06 = r'SYS.\1.01.\2'

invalid_sys_type_13 = r'SYS\.(\d{2})\.13\.(\d{2})'
replacement_13 = r'SYS.\1.17.\2'

# Find legacy patterns
legacy_comp = r'###\s+COMP-(\d+):'
legacy_int = r'###\s+INT-(\d+):'
legacy_mod = r'###\s+MOD-(\d+):'
legacy_dep = r'###\s+DEP-(\d+):'
legacy_flow = r'###\s+FLOW-(\d+):'
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
| REV-P006 | Missing component status | Add "Draft" as default status |

**Auto-Replacements**:

```python
replacements = {
    'YYYY-MM-DDTHH:MM:SS': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    'YYYY-MM-DD': datetime.now().strftime('%Y-%m-%d'),
    'MM/DD/YYYY': datetime.now().strftime('%m/%d/%Y'),
    '[Current date]': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    '[Status]': 'Draft',
    '[Version]': '0.1',
}
```

**SYS-Specific Content Fixes**:

| Section | Missing Content | Auto-Fill |
|---------|-----------------|-----------|
| Status | Empty | "Draft" |
| Version | Empty | "0.1" |
| Last Updated | Empty | Current date |
| Component Type | Empty | "[Specify type]" |

---

### Phase 5: Update References

Ensures traceability and cross-references are correct.

**Fix Actions**:

| Issue | Fix Action |
|-------|------------|
| Missing `@ref:` for created files | Add reference tag |
| Incorrect cross-SYS path | Update to correct relative path |
| Missing ADR traceability | Add `@trace: ADR-NN.SS` tag |
| Missing REQ forward reference | Add `@trace: REQ-NN.SS` tag |

**Traceability Matrix Update**:

```markdown
## Traceability

| SYS Element | Traces From | Traces To | Type |
|-------------|-------------|-----------|------|
| SYS.01.17.01 | ADR.01.14.01 | REQ.01.01.01 | Component->Requirement |
| SYS.01.18.01 | ADR.01.14.02 | CTR.01.09.01 | Interface->Contract |
```

---

### Phase 6: Handle Upstream Drift

Addresses issues where upstream source documents (ADR) have changed since SYS creation.

**Drift Issue Codes** (from `doc-sys-reviewer` Check #9):

| Code | Severity | Description | Auto-Fix Possible |
|------|----------|-------------|-------------------|
| REV-D001 | Warning | ADR document modified after SYS | No (flag for review) |
| REV-D002 | Warning | Architecture decision changed | No (flag for review) |
| REV-D003 | Info | Upstream document version incremented | Yes (update @ref version) |
| REV-D004 | Info | New ADR added to project | No (flag for review) |
| REV-D005 | Error | Critical upstream modification (>20% change) | No (flag for review) |

**Fix Actions**:

| Issue | Auto-Fix | Action |
|-------|----------|--------|
| REV-D001/D002/D004/D005 | No | Add `[DRIFT]` marker to affected references, generate drift summary |
| REV-D003 (version change) | Yes | Update `@ref:` tag to include current version |

**Drift Marker Format**:

```markdown
<!-- DRIFT: ADR-01.md modified 2026-02-08 (SYS created 2026-02-05) -->
@ref: [ADR-01 Decision 3](../../05_ADR/ADR-01.md#decision-3)
```

**Drift Summary Block** (added to Fix Report):

```markdown
## Upstream Drift Summary

| Upstream Document | Reference | Modified | SYS Updated | Days Stale | Action Required |
|-------------------|-----------|----------|-------------|------------|-----------------|
| ADR-01.md | SYS-01:L57 | 2026-02-08 | 2026-02-05 | 3 | Review architecture changes |
| ADR-03.md | SYS-01:L89 | 2026-02-10 | 2026-02-05 | 5 | Review new decision |

**Recommendation**: Review upstream ADRs and update SYS sections if system design is affected.
Sections potentially affected:
- SYS-01 Component Architecture (Section 3)
- SYS-01 Interface Definitions (Section 5)
```

**Drift Cache Update**:

After processing drift issues, update `.drift_cache.json`:

```json
{
  "sys_version": "1.0",
  "sys_updated": "2026-02-10",
  "drift_reviewed": "2026-02-10",
  "upstream_hashes": {
    "../../05_ADR/ADR-01.md#decision-3": "a1b2c3d4...",
    "../../05_ADR/ADR-03.md": "e5f6g7h8..."
  },
  "acknowledged_drift": [
    {
      "document": "ADR-01.md",
      "acknowledged_date": "2026-02-10",
      "reason": "Reviewed - no SYS impact"
    }
  ]
}
```

**Drift Acknowledgment Workflow**:

When drift is flagged but no SYS update is needed:

1. Run `/doc-sys-fixer SYS-01 --acknowledge-drift`
2. Fixer prompts: "Review drift for ADR-01.md?"
3. User confirms no SYS changes needed
4. Fixer adds to `acknowledged_drift` array
5. Future reviews skip this drift until upstream changes again

---

## Command Usage

### Basic Usage

```bash
# Fix SYS based on latest review
/doc-sys-fixer SYS-01

# Fix with explicit review report
/doc-sys-fixer SYS-01 --review-report SYS-01.R_review_report_v001.md

# Fix and re-run review
/doc-sys-fixer SYS-01 --revalidate

# Fix with iteration limit
/doc-sys-fixer SYS-01 --revalidate --max-iterations 3
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--review-report` | latest | Specific review report to use |
| `--revalidate` | false | Run reviewer after fixes |
| `--max-iterations` | 3 | Max fix-review cycles |
| `--fix-types` | all | Specific fix types (comma-separated) |
| `--create-missing` | true | Create missing reference files |
| `--backup` | true | Backup SYS before fixing |
| `--dry-run` | false | Preview fixes without applying |
| `--acknowledge-drift` | false | Interactive drift acknowledgment mode |
| `--update-drift-cache` | true | Update .drift_cache.json after fixes |

### Fix Types

| Type | Description |
|------|-------------|
| `missing_files` | Create missing index, component, interface docs |
| `broken_links` | Fix link paths |
| `element_ids` | Convert invalid/legacy element IDs |
| `content` | Fix placeholders, dates, status |
| `references` | Update traceability and cross-references |
| `drift` | Handle upstream drift detection issues |
| `all` | All fix types (default) |

---

## Output Artifacts

### Fix Report

**File Naming**: `SYS-NN.F_fix_report_vNNN.md`

**Location**: Same folder as the SYS document.

**Structure**:

```markdown
---
title: "SYS-NN.F: Fix Report v001"
tags:
  - sys
  - fix-report
  - quality-assurance
custom_fields:
  document_type: fix-report
  artifact_type: SYS-FIX
  layer: 6
  parent_doc: SYS-NN
  source_review: SYS-NN.R_review_report_v001.md
  fix_date: "YYYY-MM-DDTHH:MM:SS"
  fix_tool: doc-sys-fixer
  fix_version: "1.0"
---

# SYS-NN Fix Report v001

## Summary

| Metric | Value |
|--------|-------|
| Source Review | SYS-NN.R_review_report_v001.md |
| Issues in Review | 15 |
| Issues Fixed | 12 |
| Issues Remaining | 3 (manual review required) |
| Files Created | 3 |
| Files Modified | 4 |

## Files Created

| File | Type | Location |
|------|------|----------|
| SYS-00_INDEX.md | SYS Index | docs/06_SYS/ |
| COMP_AuthService.md | Component Placeholder | docs/00_REF/components/ |
| INT_UserAPI.md | Interface Placeholder | docs/00_REF/interfaces/ |

## Fixes Applied

| # | Issue Code | Issue | Fix Applied | File |
|---|------------|-------|-------------|------|
| 1 | REV-L001 | Broken index link | Created SYS-00_INDEX.md | SYS-01.md |
| 2 | REV-L001 | Broken component link | Created placeholder COMP file | SYS-01.md |
| 3 | REV-N004 | Element type 06 invalid | Converted to type 01 | SYS-01.md |
| 4 | REV-L003 | Absolute path used | Converted to relative | SYS-02.md |
| 5 | REV-N004 | Legacy COMP-XXX pattern | Converted to SYS.NN.17.SS | SYS-01.md |

## Issues Requiring Manual Review

| # | Issue Code | Issue | Location | Reason |
|---|------------|-------|----------|--------|
| 1 | REV-P001 | [TODO] placeholder | SYS-01:L67 | System expertise needed |
| 2 | REV-D001 | ADR drift detected | SYS-01:L145 | Review architecture changes |
| 3 | REV-R001 | Missing interface contract | SYS-01:L200 | Define API contract |

## Validation After Fix

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Review Score | 85 | 94 | +9 |
| Errors | 4 | 0 | -4 |
| Warnings | 6 | 3 | -3 |

## Next Steps

1. Complete COMP_AuthService.md placeholder
2. Complete INT_UserAPI.md placeholder
3. Address remaining [TODO] placeholders
4. Review ADR drift and update system design if needed
5. Run `/doc-sys-reviewer SYS-01` to verify fixes
```

---

## Integration with Autopilot

This skill is invoked by `doc-sys-autopilot` in the Review -> Fix cycle:

```mermaid
flowchart LR
    subgraph Phase5["Phase 5: Review & Fix Cycle"]
        A[doc-sys-reviewer] --> B{Score >= 90?}
        B -->|No| C[doc-sys-fixer]
        C --> D{Iteration < Max?}
        D -->|Yes| A
        D -->|No| E[Flag for Manual Review]
        B -->|Yes| F[PASS]
    end
```

**Autopilot Integration Points**:

| Phase | Action | Skill |
|-------|--------|-------|
| Phase 5a | Run initial review | `doc-sys-reviewer` |
| Phase 5b | Apply fixes if issues found | `doc-sys-fixer` |
| Phase 5c | Re-run review | `doc-sys-reviewer` |
| Phase 5d | Repeat until pass or max iterations | Loop |

---

## Error Handling

### Recovery Actions

| Error | Action |
|-------|--------|
| Review report not found | Prompt to run `doc-sys-reviewer` first |
| Cannot create file (permissions) | Log error, continue with other fixes |
| Cannot parse review report | Abort with clear error message |
| Max iterations exceeded | Generate report, flag for manual review |

### Backup Strategy

Before applying any fixes:

1. Create backup in `tmp/backup/SYS-NN_YYYYMMDD_HHMMSS/`
2. Copy all SYS files to backup location
3. Apply fixes to original files
4. If error during fix, restore from backup

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-sys-reviewer` | Provides review report (input) |
| `doc-sys-autopilot` | Orchestrates Review -> Fix cycle |
| `doc-sys-validator` | Structural validation |
| `doc-naming` | Element ID standards |
| `doc-sys` | SYS creation rules |
| `doc-adr` | Upstream architecture decisions |
| `doc-req` | Downstream requirements reference |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial skill creation; 6-phase fix workflow; SYS Index, Component, and Interface file creation; Element ID conversion (types 01, 05, 17, 18, 19, 20, 21); Broken link fixes; ADR upstream drift handling; Integration with autopilot Review->Fix cycle |
