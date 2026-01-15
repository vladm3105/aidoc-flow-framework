---
title: "SDD Validation Standards"
tags:
  - framework-guide
  - shared-architecture
  - required-both-approaches
  - active
custom_fields:
  document_type: validation-standards
  priority: shared
  development_status: active
  applies_to: [all-artifacts, documentation]
  version: "1.0"
---

# SDD Validation Standards

Note: Some examples in this guide show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

This document defines the complete error code registry, validation rules, and exit code conventions for the Specification-Driven Development (SDD) framework validation system.

## Validation Scope

**Artifact Layers (1-11)**: This validation system covers all 11 documentation artifact layers defined in `LAYER_REGISTRY.yaml`:

| Layer | Artifact | Description |
|-------|----------|-------------|
| 1-4 | BRD, PRD, EARS, BDD | Core requirements |
| 5-7 | ADR, SYS, REQ | Architecture and detailed requirements |
| 8-11 | IMPL, CTR, SPEC, TASKS | Implementation artifacts |

**Out of Scope**:
- Layer 0 (Strategy): Optional pre-artifact planning, not validated
- Layers 12-14 (Code, Tests, Validation): Source code traceability not implemented
- ICON: Non-layer artifact, optional validation
- IPLAN: **DEPRECATED** as of 2026-01-15 (merged into TASKS)

### MVP Validator Profile

- Validators support a relaxed MVP profile using frontmatter `custom_fields.template_profile: mvp` in MVP templates. Under the MVP profile, certain non-critical checks are downgraded to warnings to speed early drafting. Use the default (full) profile for enterprise/regulatory documents.

## Exit Code Conventions

| Exit Code | Meaning | CI/CD Action |
|-----------|---------|--------------|
| 0 | Pass - No errors or warnings | Continue pipeline |
| 1 | Warnings only | Continue with notification |
| 2 | Errors present | Fail pipeline |

## Error Code Format

All error codes follow the pattern: `{CATEGORY}-{SEVERITY}{NUMBER}`

| Component | Format | Description |
|-----------|--------|-------------|
| CATEGORY | 2-6 uppercase letters | Validation category (SEC, XREF, TERM, etc.) |
| SEVERITY | Single letter | E=Error, W=Warning, I=Info |
| NUMBER | 3 digits | Sequential within category (001-999) |

**Example**: `FWDREF-E001` = Forward Reference category, Error severity, code 001

---

## Error Code Registry

### Section File Validation (SEC)

Validates section file counts match metadata declarations.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| SEC-E001 | Error | Section count mismatch | Yes | Update `total_sections` to match actual section files |
| SEC-E002 | Error | Missing section file | No | Create missing section file or update `total_sections` |
| SEC-E003 | Error | Missing Section 0 file | No | Create Section 0 with document control and index |
| SEC-W001 | Warning | Section file gap detected | Yes | Renumber sections to be consecutive (1, 2, 3...) |

**Validation Script**: `validate_section_count.py`

---

### Cross-Reference Accuracy (XREF)

Validates cross-document references resolve correctly.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| XREF-E001 | Error | Section number mismatch | No | Update referenced section number to match target |
| XREF-E002 | Error | Section title mismatch | No | Update referenced section title to match target |
| XREF-E003 | Error | Anchor not found in target | No | Add missing anchor or correct reference |
| XREF-W001 | Warning | Fuzzy title match | Yes | Update link text to exactly match target heading |

**Validation Script**: `validate_cross_document.py`

---

### ID Pattern Consistency (IDPAT)

Ensures consistent ID formats across documents.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| IDPAT-E001 | Error | Inconsistent document ID format | No | Use consistent format: TYPE-NN+ (2+ digits) |
| IDPAT-E002 | Error | Inconsistent element ID format | No | Use TYPE.NN.TT.SS format for all element IDs |
| IDPAT-E003 | Error | Mixed ID notation | Yes | Normalize all IDs to dot notation (TYPE.NN.TT.SS) |
| IDPAT-W001 | Warning | Legacy ID format detected | No | Consider updating to unified 4-segment format |

**Validation Script**: `validate_requirement_ids.py`

**Valid Formats**:
- Document ID: `TYPE-NN` (e.g., `BRD-01`, `ADR-100`)
- Element ID: `TYPE.NN.TT.SS` (e.g., `BRD.01.01.05`)

**Invalid Formats**:
- Mixed: `TYPE-NN.TT` (hyphen then dot)
- Legacy: `FR-XXX`, `BC-XXX`, `AC-XXX`

---

### Diagram Consistency (DIAG)

Validates Mermaid diagrams match prose descriptions.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| DIAG-E001 | Error | Diagram-text component mismatch | No | Update diagram or prose to match |
| DIAG-E002 | Error | Missing diagram for architecture section | No | Add Mermaid diagram per DIAGRAM_STANDARDS.md |
| DIAG-W001 | Warning | Diagram count differs from text claim | No | Reconcile text count claim with diagram |
| DIAG-W002 | Warning | Node label not referenced in text | No | Reference diagram node in surrounding prose |

**Validation Script**: `validate_diagram_consistency.py`

---

### Terminology Consistency (TERM)

Validates terminology and acronym usage.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| TERM-E001 | Error | Conflicting term definition | No | Reconcile definitions in glossary and text |
| TERM-E002 | Error | Undefined acronym | No | Define acronym on first use: "Full Name (ACRONYM)" |
| TERM-W001 | Warning | Inconsistent term usage | Yes | Normalize term capitalization to glossary definition |
| TERM-W002 | Warning | Missing glossary entry | No | Add technical term to document glossary |

**Validation Script**: `validate_terminology.py`

**Well-Known Acronyms** (no definition required):
API, REST, HTTP, HTTPS, URL, JSON, XML, SQL, TCP, IP, AWS, GCP, CLI, SDK, UUID, JWT, OAuth, CI, CD, BRD, PRD, ADR, SYS, REQ, SPEC

---

### Timezone Validation (TZ)

Ensures consistent timezone formatting.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| TZ-E001 | Error | Non-standard timezone format | Yes | Replace EST/EDT with `ET (America/New_York)` |
| TZ-W001 | Warning | Ambiguous timezone abbreviation | Yes | Specify IANA timezone: `America/New_York` |

**Validation Script**: `validate_artifact.py`

**Correct Format**: `ET (America/New_York)`
**Incorrect Formats**: `EST`, `EDT`, bare `ET`

---

### Date Validation (DATE)

Validates date consistency and metadata.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| DATE-E001 | Error | Future document date | No | Correct date to present or past |
| DATE-E002 | Error | Timeline inconsistency | No | Align timeline dates with document creation date |
| DATE-W001 | Warning | Missing date metadata | Yes | Add `created`/`updated` fields from git history |

**Validation Script**: `validate_artifact.py`

---

### Element Code Validation (ELEM)

Validates element type codes in unified IDs.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| ELEM-E001 | Error | Undefined element type code | No | Use valid code from element type table (01-31) |
| ELEM-W001 | Warning | Undocumented custom code | No | Document custom element code (50-99 range) |

**Validation Script**: `validate_requirement_ids.py`

**Standard Element Type Codes**:

| Code | Element Type | Common In |
|------|--------------|-----------|
| 01 | Functional Requirement | BRD, PRD, SYS, REQ |
| 02 | Quality Attribute | BRD, PRD, SYS |
| 03 | Constraint | BRD, PRD |
| 04 | Assumption | BRD, PRD |
| 05 | Dependency | BRD, PRD, REQ |
| 06 | Acceptance Criteria | BRD, PRD, REQ |
| 07 | Risk | BRD, PRD |
| 08 | Metric | BRD, PRD |
| 09 | User Story | PRD, BRD |
| 10 | Decision | ADR, BRD |
| 11-20 | See ID_NAMING_STANDARDS.md | Various |
| 21-49 | Reserved | Future use |
| 50-99 | Custom | Requires documentation |

---

### Count Validation (COUNT)

Validates stated counts match itemized totals.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| COUNT-E001 | Error | Count mismatch | Yes | Update stated count to match itemized total |
| COUNT-W001 | Warning | Missing count verification | No | Add count statement for large lists (10+ items) |

**Validation Script**: `validate_counts.py`

**Example**:
- Text states: "18 requirements"
- Actual list: 21 bullet points
- Result: COUNT-E001 error, auto-fix updates to "21 requirements"

---

### Forward Reference Validation (FWDREF)

Prevents upstream documents from referencing specific downstream IDs.

| Code | Severity | Message | Auto-Fix | Resolution |
|------|----------|---------|----------|------------|
| FWDREF-E001 | Error | Specific downstream ID in upstream doc | No | Remove specific ID, use descriptive text instead |
| FWDREF-E002 | Error | Non-existent downstream reference | No | Remove reference or create referenced document |
| FWDREF-W001 | Warning | Downstream count claim | No | Avoid stating exact counts of future documents |

**Validation Script**: `validate_forward_references.py`

**SDD Layer Hierarchy**:

| Layer | Artifact | Can Reference |
|-------|----------|---------------|
| 1 | BRD | None (source document) |
| 2 | PRD | BRD only |
| 3 | EARS | BRD, PRD |
| 4 | BDD | BRD, PRD, EARS |
| 5 | ADR | BRD, PRD, EARS, BDD |
| 6 | SYS | Layers 1-5 |
| 7 | REQ | Layers 1-6 |
| 8 | IMPL | Layers 1-7 |
| 9 | CTR | Layers 1-8 |
| 10 | SPEC | Layers 1-9 |
| 11 | TASKS | Layers 1-10 |
| 12 | CODE | Layers 1-11 |

> **Note**: IPLAN (formerly Layer 12) has been deprecated as of 2026-01-15 and merged into TASKS.

**Correct** (PRD describing decision needs):
```markdown
Architecture decisions required for:
- Database selection (PostgreSQL vs MongoDB)
- Caching strategy (Redis vs in-memory)
- API versioning approach
```

**Incorrect** (PRD referencing non-existent ADRs):
```markdown
See ADR-01 through ADR-05 for implementation details.
@adr: ADR-01, ADR-02
```

---

## Validation Script Summary

### Layer-Specific Validators

| Script | Layer | Description |
|--------|-------|-------------|
| `validate_brd_template.sh` | 1 | BRD structure and content |
| `validate_prd.py` | 2 | PRD format and references |
| `validate_ears.py` | 3 | EARS syntax validation |
| `validate_bdd.py` | 4 | BDD feature file format |
| `validate_adr.py` | 5 | ADR structure and decisions |
| `validate_sys.py` | 6 | System requirements |
| `validate_req_template.sh` | 7 | Atomic requirements |
| `validate_impl.sh` | 8 | Implementation approach |
| `validate_ctr.sh` | 9 | Contract validation |
| `validate_spec.py` | 10 | SPEC YAML format |
| `validate_tasks.sh` | 11 | Task breakdown (now includes execution commands) |

### Cross-Document Validators

| Script | Category | Description |
|--------|----------|-------------|
| `validate_cross_document.py` | XDOC | Traceability validation |
| `validate_links.py` | LINKS | Link integrity |
| `validate_tags_against_docs.py` | TAGS | Tag compliance |
| `validate_section_count.py` | SECTION | Section file counts |
| `validate_diagram_consistency.py` | DIAGRAM | Mermaid diagram consistency |
| `validate_terminology.py` | TERM | Terminology consistency |
| `validate_counts.py` | COUNT | Count validation |
| `validate_forward_references.py` | FWDREF | Forward reference prevention |

### XDOC Error Codes Reference

The `validate_cross_document.py` script detects and reports the following issue codes:

| Code | Severity | Description | Auto-Fix Behavior |
|------|----------|-------------|-------------------|
| XDOC-001 | ERROR | Missing required traceability tag | Adds missing tag (prompts for ID) |
| XDOC-002 | ERROR | Missing cumulative tag from ancestor layer | Adds tag with null placeholder |
| XDOC-003 | ERROR | Reference to non-existent upstream document | **Removes tag** (requires confirmation) |
| XDOC-004 | WARNING | Bidirectional reference mismatch | No auto-fix |
| XDOC-005 | WARNING | Reference to deprecated document | Replaces with null + comment |
| XDOC-006 | WARNING | Tag format inconsistency | Corrects format |
| XDOC-007 | INFO | Optional tag missing | No auto-fix |
| XDOC-008 | ERROR | Broken internal link | Removes or fixes link |
| XDOC-009 | ERROR | Missing traceability section | Adds section template |
| XDOC-010 | WARNING | Duplicate tag reference | No auto-fix |

### Auto-Fix Command Options

```bash
# Preview changes without applying
python scripts/validate_cross_document.py --all --auto-fix --dry-run

# Apply fixes (XDOC-003 requires confirmation)
python scripts/validate_cross_document.py --all --auto-fix

# Apply all fixes including XDOC-003 without confirmation
python scripts/validate_cross_document.py --all --auto-fix --force-xdoc

# Disable backup creation
python scripts/validate_cross_document.py --all --auto-fix --no-backup
```

### Audit Log Format

All XDOC-003 tag removals are logged to `tmp/validation_audit.json`:

```json
{
  "timestamp": "2025-12-29T14:30:00.000000",
  "file": "/path/to/document.md",
  "issue_code": "XDOC_003",
  "action": "removed_tag",
  "removed_content": "@brd: BRD-01",
  "backup_path": "/path/to/document.md.bak"
}
```

---

## CI/CD Integration

### Basic Validation Pipeline

```yaml
validate:
  script:
    - python3 scripts/validate_all.py . --all
  allow_failure: false
```

### Validation with Auto-Fix

```yaml
validate-and-fix:
  script:
    - python3 scripts/validate_all.py . --all --auto-fix
    - git diff --exit-code || git commit -am "Auto-fix validation issues"
```

### Strict Mode (Warnings as Errors)

```yaml
validate-strict:
  script:
    - python3 scripts/validate_all.py . --all --strict
```

---

## Quick Reference

### Running All Validators

```bash
# All validators, text output
python3 scripts/validate_all.py . --all

# Specific layers
python3 scripts/validate_all.py . --layer BRD --layer PRD

# Markdown report
python3 scripts/validate_all.py . --all --report markdown

# JSON for CI/CD
python3 scripts/validate_all.py . --all --report json
```

### Running Individual Validators

```bash
# Section count validation
python3 scripts/validate_section_count.py .

# Forward reference validation
python3 scripts/validate_forward_references.py .

# Terminology with auto-fix
python3 scripts/validate_terminology.py . --auto-fix

# Count validation with auto-fix
python3 scripts/validate_counts.py . --auto-fix
```

### List Available Validators

```bash
python3 scripts/validate_all.py --list-validators
```

---

## Related Documents

- [ID_NAMING_STANDARDS.md](ID_NAMING_STANDARDS.md) - Document ID and element format standards
- [TRACEABILITY.md](TRACEABILITY.md) - Cross-reference tag standards
- [DIAGRAM_STANDARDS.md](DIAGRAM_STANDARDS.md) - Mermaid diagram requirements
