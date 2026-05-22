---
name: doc-bdd-validator
description: Validate Behavior-Driven Development (BDD) documents against Layer 4 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
    - quality-assurance
  custom_fields:
    layer: 4
    artifact_type: BDD
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "1.3"
    last_updated: "2026-05-22"
  versioning_policy: "tracks BDD-TEMPLATE schema_version"
---

# doc-bdd-validator

Validate Behavior-Driven Development (BDD) documents against Layer 4 schema standards.

## Activation

Invoke when user requests validation of BDD documents or after creating/modifying BDD artifacts.

## Validation Schema Reference

Template (single source of truth): `framework/layers/04_BDD/BDD-TEMPLATE.yaml`
Standards: `framework/governance/ID_NAMING_STANDARDS.md`, `framework/layers/04_BDD/README.md`
Layer: 4
Artifact Type: BDD

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL BDD documents MUST be in nested folders regardless of size.

**Required Structure**:

| BDD Type | Required Location |
|----------|-------------------|
| Markdown | `docs/04_BDD/BDD-NN_{slug}/BDD-NN_{slug}.md` |
| Feature | `docs/04_BDD/BDD-NN_{slug}/BDD-NN_{slug}.feature` |

**Validation**:

```
1. Check document is inside a nested folder: docs/04_BDD/BDD-NN_{slug}/
2. Verify folder name matches BDD ID pattern: BDD-NN_{slug}
3. Verify file name matches folder: BDD-NN_{slug}.md or .feature
4. Parent path must be: docs/04_BDD/
```

**Example Valid Structure**:

```
docs/04_BDD/
├── BDD-01_f1_iam/
│   ├── BDD-01_f1_iam.md           ✓ Valid
│   ├── BDD-01_f1_iam.feature      ✓ Valid (optional companion)
│   ├── BDD-01.A_audit_report_v001.md
│   ├── BDD-01.R_review_report_v001.md  (legacy)
│   └── .drift_cache.json
├── BDD-02_f2_session/
│   └── BDD-02_f2_session.md       ✓ Valid
```

**Invalid Structure**:

```
docs/04_BDD/
├── BDD-01_f1_iam.md               ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| BDD-E020 | ERROR | BDD not in nested folder (BLOCKING) |
| BDD-E021 | ERROR | Folder name doesn't match BDD ID |
| BDD-E022 | ERROR | File name doesn't match folder name |
| VAL-H001 | ERROR | Drift cache missing hash for upstream document |
| VAL-H002 | ERROR | Invalid hash format (must be sha256:<64 hex chars>) |

**This check is BLOCKING** - BDD must pass folder structure validation before other checks proceed.

---

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["bdd", "template"]
  - artifact_type: "BDD"
  - layer: 4
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - bdd (or bdd-template)
  - layer-4-artifact

Forbidden tag patterns:
  - "^behavior-driven$"
  - "^bdd-\\d{3}$"
```

### 2. Structure Validation

**Required Sections:**
- Title (H1): `# BDD-NNN: Title`
- Document Control (Section 1)
- Feature Overview (Section 2)
- Scenarios (Section 3)
- Scenario Outlines (Section 4)
- Background Steps (Section 5)
- Tags and Hooks (Section 6)
- Test Data (Section 7)
- Traceability (Section 8)
- Change History (Section 9)

**Document Control Required Fields:**
- BDD ID
- Document Name
- Version
- Date Created
- Last Updated
- Author
- Status
- Source EARS

**File Naming:**
Pattern: `BDD-NNN_descriptive_name.md`

### 3. Content Validation

**Gherkin Syntax:**
```gherkin
Feature: [Feature Name]
  As a [role]
  I want [feature]
  So that [benefit]

  Scenario: [Scenario Name]
    Given [context]
    When [action]
    Then [expected outcome]
    And [additional outcome]
```

**Scenario Format:**
- Pattern: `Scenario: Description`
- Required steps: Given, When, Then
- Optional steps: And, But

**Scenario Outline Format:**
```gherkin
Scenario Outline: [Description]
  Given [context with <variable>]
  When [action with <variable>]
  Then [outcome with <variable>]

  Examples:
    | variable | value |
    | data1    | val1  |
```

**ADR-Ready Score:**
- Minimum threshold: 90%
- Components: Scenario coverage, step clarity, data completeness, traceability

### 4. Element ID and Traceability Validation

**Element ID Format (MANDATORY):**
- 4-segment `BDD.NN.SS.xxxx` (`NN` = doc number, `SS` = section, `xxxx` = 4-char hex hash)
- REJECT legacy 3-segment `BDD.NN.xxxx` and legacy numeric type-code IDs (`BDD.NN.14.SS`, `BDD.NN.15.SS`) — scenario vs. step is conveyed by its section, not by an ID type code
- REJECT legacy patterns (SC-NNN, TC-NNN, TS-NNN)
- See `framework/governance/ID_NAMING_STANDARDS.md`

**Layer 4 Cumulative Tags:**
- @brd: BRD.NN.SS.xxxx (required)
- @prd: PRD.NN.SS.xxxx (required)
- @ears: EARS.NN.SS.xxxx (required)

**Downstream Expected:**
- ADR documents
- SPEC, TDD, IPLAN (added only once those artifacts exist)

**Same-Type References:**
- @related-bdd: BDD-NN
- @depends-bdd: BDD-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| BDD-E001 | error | Missing required tag 'bdd' |
| BDD-E002 | error | Missing required tag 'layer-4-artifact' |
| BDD-E003 | error | Invalid document_type |
| BDD-E004 | error | Invalid architecture_approaches format |
| BDD-E005 | error | Forbidden tag pattern detected |
| BDD-E006 | error | Missing required section |
| BDD-E007 | error | Multiple H1 headings detected |
| BDD-E008 | error | Section numbering not sequential |
| BDD-E009 | error | Document Control missing required fields |
| BDD-E010 | error | Invalid Gherkin syntax |
| BDD-E011 | error | Scenario missing Given-When-Then |
| BDD-E012 | error | Missing Traceability (Section 8) |
| BDD-E014 | error | Invalid element ID (not 4-segment `BDD.NN.SS.xxxx`) |
| BDD-E015 | error | Legacy element ID detected (3-segment or numeric type-code) |
| BDD-E013 | warning | File name does not match format |
| BDD-W001 | warning | Scenario missing Then step |
| BDD-W002 | warning | Missing upstream tags (@brd, @prd, @ears) |
| BDD-W003 | warning | ADR-Ready Score below 90% |
| BDD-W004 | warning | Scenario Outline missing Examples |
| BDD-W005 | warning | Test data incomplete |
| BDD-I001 | info | Consider adding Background steps |
| BDD-I002 | info | Consider adding negative scenarios |

## How Validation Runs

The framework ships no runtime scripts — **this skill is the validator**. There
is no external `validate_bdd.py` to call. Apply the Validation Checklist and
Validation Workflow below directly against the target document(s), checking each
against `framework/layers/04_BDD/BDD-TEMPLATE.yaml`,
`framework/governance/ID_NAMING_STANDARDS.md`, and
`framework/layers/04_BDD/README.md`:

- Single BDD suite: apply the checklist to `docs/04_BDD/BDD-NN_{slug}/`.
- All BDD documents: apply the checklist across every suite under `docs/04_BDD/`.
- `.feature` files: apply the Gherkin and element-ID checks to each feature file.
- Emit the Output Format report (below), listing errors/warnings/info by severity.

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-9)
5. Validate Document Control table
6. Check Gherkin syntax compliance
7. Verify Given-When-Then structure
8. Validate Scenario Outline Examples
9. Validate upstream references
10. Verify element IDs use the 4-segment `BDD.NN.SS.xxxx` form (reject legacy 3-segment / numeric type-code IDs)
11. Calculate ADR-Ready Score
12. Verify file naming convention
13. Generate validation report

## Gherkin Pattern Detection

```python
patterns = {
    'feature': r'^Feature:\s+.+',
    'scenario': r'^Scenario:\s+.+',
    'scenario_outline': r'^Scenario Outline:\s+.+',
    'given': r'^\s*Given\s+.+',
    'when': r'^\s*When\s+.+',
    'then': r'^\s*Then\s+.+',
    'and': r'^\s*And\s+.+',
    'but': r'^\s*But\s+.+',
    'background': r'^Background:',
    'examples': r'^\s*Examples:'
}
```

## Integration

- Invoked by: doc-flow, doc-bdd (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
BDD Validation Report
=====================
Document: BDD-001_example.md
Status: PASS/FAIL

Scenario Summary:
- Total Scenarios: N
- With Given-When-Then: N
- Scenario Outlines: N
- With Examples: N

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.3 | 2026-05-22 | Migrated to framework 8-layer model: enforces 4-segment element IDs `BDD.NN.SS.xxxx` and rejects legacy 3-segment / numeric type-code IDs (BDD-E014/E015); downstream SPEC/TDD/IPLAN (dropped SYS); `framework/layers/04_BDD/` template + governance references; removed runtime `validate_bdd.py` calls — the skill is the validator (declarative checklist) | System |
| 1.2 | 2026-02-27 | Migrated frontmatter to `metadata`; updated valid structure example for preferred `BDD-NN.A_audit_report_vNNN.md` with legacy reviewer compatibility; corrected validator command paths (later removed in 1.3) | System |
| 1.1 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING); BDD must be in `docs/04_BDD/BDD-NN_{slug}/` folders; Added error codes BDD-E020, BDD-E021, BDD-E022 |
| 1.0 | 2026-02-08 | Initial validator skill definition with YAML frontmatter | System |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

