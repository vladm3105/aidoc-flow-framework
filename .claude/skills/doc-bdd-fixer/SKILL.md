---
name: doc-bdd-fixer
description: Automated fix skill that reads review reports and applies fixes to BDD documents - handles broken links, element IDs, missing files, and iterative improvement
tags:
  - sdd-workflow
  - quality-assurance
  - bdd-fix
  - layer-4-artifact
  - shared-architecture
custom_fields:
  layer: 4
  artifact_type: BDD
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [BDD, Review Report, EARS]
  downstream_artifacts: [Fixed BDD, Fix Report]
  version: "1.0"
  last_updated: "2026-02-10T15:00:00"
---

# doc-bdd-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to BDD (Behavior-Driven Development) documents. This skill bridges the gap between `doc-bdd-reviewer` (which identifies issues) and the corrected BDD, enabling iterative improvement cycles.

**Layer**: 4 (BDD Quality Improvement)

**Upstream**: BDD document, Review Report (`BDD-NN.R_review_report_vNNN.md`), EARS (source requirements)

**Downstream**: Fixed BDD, Fix Report (`BDD-NN.F_fix_report_vNNN.md`)

---

## When to Use This Skill

Use `doc-bdd-fixer` when:

- **After Review**: Run after `doc-bdd-reviewer` identifies issues
- **Iterative Improvement**: Part of Review -> Fix -> Review cycle
- **Automated Pipeline**: CI/CD integration for quality gates
- **Batch Fixes**: Apply fixes to multiple BDD based on review reports

**Do NOT use when**:
- No review report exists (run `doc-bdd-reviewer` first)
- Creating new BDD (use `doc-bdd` or `doc-bdd-autopilot`)
- Only need validation (use `doc-bdd-validator`)

---

## Skill Dependencies

| Skill | Purpose | When Used |
|-------|---------|-----------|
| `doc-bdd-reviewer` | Source of issues to fix | Input (reads review report) |
| `doc-naming` | Element ID standards | Fix element IDs |
| `doc-bdd` | BDD creation rules | Create missing sections |
| `doc-ears-reviewer` | Upstream EARS validation | Check upstream alignment |

---

## Workflow Overview

```mermaid
flowchart TD
    A[Input: BDD Path] --> B[Find Latest Review Report]
    B --> C{Review Found?}
    C -->|No| D[Run doc-bdd-reviewer First]
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

    K2 --> L[Write Fixed BDD]
    L --> M[Generate Fix Report]
    M --> N{Re-run Review?}
    N -->|Yes| O[Invoke doc-bdd-reviewer]
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
| `BDD-00_GLOSSARY.md` | Create BDD glossary | Glossary template |
| `BDD-NN_STEP_DEFS.md` | Create step definitions placeholder | Step Defs template |
| Feature files (`*.feature`) | Create placeholder with TODO sections | Feature template |
| Shared context files | Create placeholder | Context template |

**BDD Glossary Template**:

```markdown
---
title: "BDD-00: Behavior Glossary"
tags:
  - bdd
  - glossary
  - reference
custom_fields:
  document_type: glossary
  artifact_type: BDD-REFERENCE
  layer: 4
---

# BDD-00: Behavior Glossary

Common terminology used across all BDD Feature Documents.

## Gherkin Keywords

| Term | Definition | Context |
|------|------------|---------|
| Feature | High-level behavior description | Feature header |
| Scenario | Specific test case | Test definition |
| Scenario Outline | Parameterized scenario | Data-driven tests |
| Given | Precondition setup | Context |
| When | Action trigger | Event |
| Then | Expected outcome | Assertion |
| And | Additional step | Continuation |
| But | Negative continuation | Exception |
| Background | Shared preconditions | Reusable setup |
| Examples | Data table for outlines | Test data |

## Step Definition Terms

| Term | Definition | Context |
|------|------------|---------|
| Step Definition | Code binding for Gherkin step | Implementation |
| World | Shared context object | State management |
| Hook | Before/After lifecycle method | Setup/teardown |
| Tag | Scenario/Feature annotation | Filtering |

## Domain Terms

<!-- Add project-specific terminology below -->

| Term | Definition | Context |
|------|------------|---------|
| [Term] | [Definition] | [Where used] |
```

**Feature Placeholder Template**:

```gherkin
# language: en
# encoding: UTF-8

@placeholder @needs-completion
Feature: [Feature Name]
  As a [role]
  I want [capability]
  So that [benefit]

  # TODO: Created by doc-bdd-fixer as placeholder
  # Complete this feature file to resolve broken link issues

  Background:
    Given [TODO: Define shared preconditions]

  @todo
  Scenario: [TODO: Define scenario name]
    Given [TODO: Define precondition]
    When [TODO: Define action]
    Then [TODO: Define expected outcome]
```

**Step Definitions Placeholder Template**:

```markdown
---
title: "BDD Step Definitions: [Module Name]"
tags:
  - bdd
  - step-definitions
  - reference
custom_fields:
  document_type: step-definitions
  status: placeholder
  created_by: doc-bdd-fixer
---

# BDD Step Definitions: [Module Name]

> **Status**: Placeholder - Requires completion

## 1. Overview

[TODO: Document step definitions overview]

## 2. Given Steps

| Step Pattern | Implementation | Status |
|--------------|----------------|--------|
| `Given [pattern]` | [TODO] | Placeholder |

## 3. When Steps

| Step Pattern | Implementation | Status |
|--------------|----------------|--------|
| `When [pattern]` | [TODO] | Placeholder |

## 4. Then Steps

| Step Pattern | Implementation | Status |
|--------------|----------------|--------|
| `Then [pattern]` | [TODO] | Placeholder |

## 5. Shared Helpers

[TODO: Document shared helper functions]

---

*Created by doc-bdd-fixer as placeholder. Complete this document to resolve broken link issues.*
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
| REV-L004 | Broken EARS reference | Update to correct EARS path |
| REV-L005 | Broken feature file reference | Update or create feature file |

**Path Resolution Logic**:

```python
def fix_link_path(bdd_location: str, target_path: str) -> str:
    """Calculate correct relative path based on BDD location."""

    # Monolithic BDD: docs/04_BDD/BDD-01.md
    # Sectioned BDD: docs/04_BDD/BDD-01_slug/BDD-01.3_section.md
    # Feature files: tests/bdd/features/*.feature

    if is_sectioned_bdd(bdd_location):
        # Need to go up one more level
        return "../" + calculate_relative_path(bdd_location, target_path)
    else:
        return calculate_relative_path(bdd_location, target_path)
```

**EARS Link Fix**:

| BDD Type | Original Link | Fixed Link |
|----------|---------------|------------|
| Monolithic | `../03_EARS/EARS-01.md` | `../03_EARS/EARS-01.md` |
| Sectioned | `../03_EARS/EARS-01.md` | `../../03_EARS/EARS-01.md` |

**Feature File Link Fix**:

| BDD Type | Original Link | Fixed Link |
|----------|---------------|------------|
| Monolithic | `../../tests/bdd/features/auth.feature` | `../../tests/bdd/features/auth.feature` |
| Sectioned | `../../tests/bdd/features/auth.feature` | `../../../tests/bdd/features/auth.feature` |

---

### Phase 3: Fix Element IDs

Converts invalid element IDs to correct format.

**Conversion Rules**:

| Pattern | Issue | Conversion |
|---------|-------|------------|
| `BDD.NN.01.SS` | Code 01 invalid for BDD | `BDD.NN.35.SS` (Feature Spec) |
| `BDD.NN.25.SS` | Code 25 invalid for BDD | `BDD.NN.36.SS` (Scenario Spec) |
| `BDD.NN.22.SS` | Code 22 invalid for BDD | `BDD.NN.37.SS` (Step Definition) |
| `FEAT-XXX` | Legacy pattern | `BDD.NN.35.SS` |
| `SCEN-XXX` | Legacy pattern | `BDD.NN.36.SS` |
| `STEP-XXX` | Legacy pattern | `BDD.NN.37.SS` |

**Type Code Mapping** (BDD-specific valid codes: 35, 36, 37):

| Invalid Code | Valid Code | Element Type |
|--------------|------------|--------------|
| 01 | 35 | Feature Specification |
| 02 | 36 | Scenario Specification |
| 03 | 37 | Step Definition |
| 05 | 36 | Scenario Specification |
| 06 | 37 | Step Definition |
| 22 | 35 | Feature Specification |
| 25 | 36 | Scenario Specification |
| 26 | 37 | Step Definition |

**Regex Patterns**:

```python
# Find element IDs with invalid type codes for BDD
invalid_bdd_type_01 = r'BDD\.(\d{2})\.01\.(\d{2})'
replacement_01 = r'BDD.\1.35.\2'

invalid_bdd_type_25 = r'BDD\.(\d{2})\.25\.(\d{2})'
replacement_25 = r'BDD.\1.36.\2'

invalid_bdd_type_22 = r'BDD\.(\d{2})\.22\.(\d{2})'
replacement_22 = r'BDD.\1.37.\2'

# Find legacy patterns
legacy_feat = r'###\s+FEAT-(\d+):'
legacy_scen = r'###\s+SCEN-(\d+):'
legacy_step = r'###\s+STEP-(\d+):'
```

---

### Phase 4: Fix Content Issues

Addresses placeholders, incomplete content, and BDD-specific syntax issues.

**Fix Actions**:

| Issue Code | Issue | Fix Action |
|------------|-------|------------|
| REV-P001 | `[TODO]` placeholder | Flag for manual completion (cannot auto-fix) |
| REV-P002 | `[TBD]` placeholder | Flag for manual completion (cannot auto-fix) |
| REV-P003 | Template date `YYYY-MM-DD` | Replace with current date |
| REV-P004 | Template name `[Name]` | Replace with metadata author or flag |
| REV-P005 | Empty section | Add minimum template content |
| REV-B001 | Missing Gherkin keyword | Flag for manual review |
| REV-B002 | Invalid scenario structure | Flag for manual review |
| REV-B003 | Missing Given/When/Then | Flag for manual review |
| REV-B004 | Orphan step definition | Flag for manual review |

**Auto-Replacements**:

```python
replacements = {
    'YYYY-MM-DDTHH:MM:SS': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    'YYYY-MM-DD': datetime.now().strftime('%Y-%m-%d'),
    'MM/DD/YYYY': datetime.now().strftime('%m/%d/%Y'),
    '[Current date]': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    '[Feature Name]': extract_feature_name_from_metadata(),
}
```

**Gherkin Structure Validation**:

| Pattern Type | Required Structure | Auto-Fix |
|--------------|-------------------|----------|
| Feature | Feature: [name] + user story format | No (flag) |
| Scenario | Scenario: [name] + Given/When/Then | No (flag) |
| Scenario Outline | Scenario Outline + Examples table | No (flag) |
| Background | Background: + Given steps only | No (flag) |
| Step | Given/When/Then/And/But + description | No (flag) |

---

### Phase 5: Update References

Ensures traceability and cross-references are correct.

**Fix Actions**:

| Issue | Fix Action |
|-------|------------|
| Missing `@ref:` for created files | Add reference tag |
| Incorrect cross-BDD path | Update to correct relative path |
| Missing EARS traceability | Add EARS reference with `@trace: EARS-NN` |
| Missing traceability entry | Add to traceability matrix |
| Missing feature tag | Add appropriate tag |

**Traceability Format**:

```markdown
<!-- Traceability to EARS -->
@trace: EARS-01.25.01 -> BDD-01.35.01

<!-- Reference to upstream -->
@ref: [EARS-01 Section 3](../03_EARS/EARS-01.md#3-functional-requirements)
```

**Tag Traceability in Feature Files**:

```gherkin
@trace:EARS-01.25.01 @feature:BDD-01.35.01
Feature: User Authentication
```

---

### Phase 6: Handle Upstream Drift

Addresses issues where upstream EARS documents have changed since BDD creation.

**Drift Issue Codes** (from `doc-bdd-reviewer` Check #9):

| Code | Severity | Description | Auto-Fix Possible |
|------|----------|-------------|-------------------|
| REV-D001 | Warning | EARS modified after BDD | No (flag for review) |
| REV-D002 | Warning | Referenced EARS statement content changed | No (flag for review) |
| REV-D003 | Info | EARS version incremented | Yes (update @ref version) |
| REV-D004 | Info | New requirements added to EARS | No (flag for review) |
| REV-D005 | Error | Critical EARS modification (>20% change) | No (flag for review) |

**Fix Actions**:

| Issue | Auto-Fix | Action |
|-------|----------|--------|
| REV-D001/D002/D004/D005 | No | Add `[DRIFT]` marker to affected references, generate drift summary |
| REV-D003 (version change) | Yes | Update `@ref:` tag to include current version |

**Drift Marker Format**:

```markdown
<!-- DRIFT: EARS-01.md modified 2026-02-08 (BDD created 2026-02-05) -->
@ref: [EARS-01 Section 3](../03_EARS/EARS-01.md#3-functional-requirements)
```

**Feature File Drift Marker**:

```gherkin
# DRIFT: EARS-01.25.01 modified 2026-02-08 (Scenario created 2026-02-05)
@trace:EARS-01.25.01 @needs-review
Scenario: User authenticates with valid credentials
```

**Drift Summary Block** (added to Fix Report):

```markdown
## Upstream Drift Summary

| Upstream Document | Reference | Modified | BDD Updated | Days Stale | Action Required |
|-------------------|-----------|----------|-------------|------------|-----------------|
| EARS-01.md | BDD-01.1:L57 | 2026-02-08 | 2026-02-05 | 3 | Review for changes |
| EARS-02.md | BDD-01.3:L319 | 2026-02-10 | 2026-02-05 | 5 | Review requirement updates |

**Recommendation**: Review upstream EARS documents and update BDD scenarios if requirements have changed.
Features potentially affected:
- BDD-01.1 auth.feature (Authentication scenarios)
- BDD-01.3 api.feature (API scenarios)
```

**Drift Cache Update**:

After processing drift issues, update `.drift_cache.json`:

```json
{
  "bdd_version": "1.0",
  "bdd_updated": "2026-02-10",
  "drift_reviewed": "2026-02-10",
  "upstream_hashes": {
    "../03_EARS/EARS-01.md#3": "a1b2c3d4...",
    "../03_EARS/EARS-02.md": "e5f6g7h8..."
  },
  "acknowledged_drift": [
    {
      "document": "EARS-01.md",
      "acknowledged_date": "2026-02-10",
      "reason": "Reviewed - no BDD impact"
    }
  ]
}
```

**Drift Acknowledgment Workflow**:

When drift is flagged but no BDD update is needed:

1. Run `/doc-bdd-fixer BDD-01 --acknowledge-drift`
2. Fixer prompts: "Review drift for EARS-01.md?"
3. User confirms no BDD changes needed
4. Fixer adds to `acknowledged_drift` array
5. Future reviews skip this drift until upstream changes again

---

## Command Usage

### Basic Usage

```bash
# Fix BDD based on latest review
/doc-bdd-fixer BDD-01

# Fix with explicit review report
/doc-bdd-fixer BDD-01 --review-report BDD-01.R_review_report_v001.md

# Fix and re-run review
/doc-bdd-fixer BDD-01 --revalidate

# Fix with iteration limit
/doc-bdd-fixer BDD-01 --revalidate --max-iterations 3
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--review-report` | latest | Specific review report to use |
| `--revalidate` | false | Run reviewer after fixes |
| `--max-iterations` | 3 | Max fix-review cycles |
| `--fix-types` | all | Specific fix types (comma-separated) |
| `--create-missing` | true | Create missing reference files |
| `--backup` | true | Backup BDD before fixing |
| `--dry-run` | false | Preview fixes without applying |
| `--acknowledge-drift` | false | Interactive drift acknowledgment mode |
| `--update-drift-cache` | true | Update .drift_cache.json after fixes |
| `--fix-features` | true | Also fix linked .feature files |

### Fix Types

| Type | Description |
|------|-------------|
| `missing_files` | Create missing glossary, step defs, feature files |
| `broken_links` | Fix link paths |
| `element_ids` | Convert invalid/legacy element IDs |
| `content` | Fix placeholders, dates, names |
| `references` | Update traceability and cross-references |
| `drift` | Handle upstream drift detection issues |
| `gherkin` | Fix Gherkin syntax issues (limited) |
| `all` | All fix types (default) |

---

## Output Artifacts

### Fix Report

**File Naming**: `BDD-NN.F_fix_report_vNNN.md`

**Location**: Same folder as the BDD document.

**Structure**:

```markdown
---
title: "BDD-NN.F: Fix Report v001"
tags:
  - bdd
  - fix-report
  - quality-assurance
custom_fields:
  document_type: fix-report
  artifact_type: BDD-FIX
  layer: 4
  parent_doc: BDD-NN
  source_review: BDD-NN.R_review_report_v001.md
  fix_date: "YYYY-MM-DDTHH:MM:SS"
  fix_tool: doc-bdd-fixer
  fix_version: "1.0"
---

# BDD-NN Fix Report v001

## Summary

| Metric | Value |
|--------|-------|
| Source Review | BDD-NN.R_review_report_v001.md |
| Issues in Review | 12 |
| Issues Fixed | 10 |
| Issues Remaining | 2 (manual review required) |
| Files Created | 3 |
| Files Modified | 5 |
| Feature Files Fixed | 2 |

## Files Created

| File | Type | Location |
|------|------|----------|
| BDD-00_GLOSSARY.md | Behavior Glossary | docs/04_BDD/ |
| BDD-01_STEP_DEFS.md | Step Definitions Placeholder | docs/04_BDD/ |
| auth_placeholder.feature | Feature Placeholder | tests/bdd/features/ |

## Fixes Applied

| # | Issue Code | Issue | Fix Applied | File |
|---|------------|-------|-------------|------|
| 1 | REV-L001 | Broken glossary link | Created BDD-00_GLOSSARY.md | BDD-01.3_scenarios.md |
| 2 | REV-L004 | Broken EARS reference | Updated path to ../03_EARS/EARS-01.md | BDD-01.1_core.md |
| 3 | REV-N004 | Element type 01 invalid | Converted to type 35 | BDD-01.1_core.md |
| 4 | REV-L005 | Broken feature file link | Created auth_placeholder.feature | BDD-01.2_features.md |

## Feature File Fixes

| File | Fixes Applied |
|------|---------------|
| auth.feature | Added @trace tag, fixed step reference |
| api.feature | Updated Examples table format |

## Issues Requiring Manual Review

| # | Issue Code | Issue | Location | Reason |
|---|------------|-------|----------|--------|
| 1 | REV-B001 | Missing Gherkin keyword | BDD-01.2:L45 | Scenario syntax needed |
| 2 | REV-B003 | Missing Given/When/Then | auth.feature:L32 | Step structure required |

## Validation After Fix

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Review Score | 92 | 97 | +5 |
| Errors | 2 | 0 | -2 |
| Warnings | 4 | 1 | -3 |

## Next Steps

1. Complete BDD-01_STEP_DEFS.md placeholder
2. Complete auth_placeholder.feature with proper scenarios
3. Address missing Gherkin keywords in flagged scenarios
4. Run `/doc-bdd-reviewer BDD-01` to verify fixes
```

---

## Integration with Autopilot

This skill is invoked by `doc-bdd-autopilot` in the Review -> Fix cycle:

```mermaid
flowchart LR
    subgraph Phase5["Phase 5: Review & Fix Cycle"]
        A[doc-bdd-reviewer] --> B{Score >= 85?}
        B -->|No| C[doc-bdd-fixer]
        C --> D{Iteration < Max?}
        D -->|Yes| A
        D -->|No| E[Flag for Manual Review]
        B -->|Yes| F[PASS]
    end
```

**Autopilot Integration Points**:

| Phase | Action | Skill |
|-------|--------|-------|
| Phase 5a | Run initial review | `doc-bdd-reviewer` |
| Phase 5b | Apply fixes if issues found | `doc-bdd-fixer` |
| Phase 5c | Re-run review | `doc-bdd-reviewer` |
| Phase 5d | Repeat until pass or max iterations | Loop |

---

## Error Handling

### Recovery Actions

| Error | Action |
|-------|--------|
| Review report not found | Prompt to run `doc-bdd-reviewer` first |
| Cannot create file (permissions) | Log error, continue with other fixes |
| Cannot parse review report | Abort with clear error message |
| Max iterations exceeded | Generate report, flag for manual review |
| EARS not found | Log warning, skip EARS-dependent fixes |
| Feature file parse error | Log error, skip Gherkin fixes for that file |

### Backup Strategy

Before applying any fixes:

1. Create backup in `tmp/backup/BDD-NN_YYYYMMDD_HHMMSS/`
2. Copy all BDD files and linked feature files to backup location
3. Apply fixes to original files
4. If error during fix, restore from backup

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-bdd-reviewer` | Provides review report (input) |
| `doc-bdd-autopilot` | Orchestrates Review -> Fix cycle |
| `doc-bdd-validator` | Structural validation |
| `doc-naming` | Element ID standards |
| `doc-bdd` | BDD creation rules |
| `doc-ears-reviewer` | Upstream EARS validation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial skill creation; 6-phase fix workflow; Glossary, step definitions, and feature file creation; Element ID conversion for BDD codes (35, 36, 37); Broken link fixes including feature files; EARS drift detection; Gherkin syntax validation; Integration with autopilot Review->Fix cycle |
