---
name: doc-bdd-validator
description: Validate Behavior-Driven Development (BDD) documents against Layer 4 schema standards
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
  upstream_artifacts: [BDD]
  downstream_artifacts: []
  version: "1.0"
  last_updated: "2026-02-10T15:00:00"
---

# doc-bdd-validator

Validate Behavior-Driven Development (BDD) documents against Layer 4 schema standards.

## Activation

Invoke when user requests validation of BDD documents or after creating/modifying BDD artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/BDD/BDD_SCHEMA.yaml`
Layer: 4
Artifact Type: BDD

## Validation Checklist

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

### 4. Traceability Validation

**Layer 4 Cumulative Tags:**
- @brd: BRD.NN.01.SS (required)
- @prd: PRD.NN.07.SS (required)
- @ears: EARS.NN.24.SS (required)

**Downstream Expected:**
- ADR documents
- SYS requirements
- Test implementations

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
| BDD-E013 | warning | File name does not match format |
| BDD-W001 | warning | Scenario missing Then step |
| BDD-W002 | warning | Missing upstream tags (@brd, @prd, @ears) |
| BDD-W003 | warning | ADR-Ready Score below 90% |
| BDD-W004 | warning | Scenario Outline missing Examples |
| BDD-W005 | warning | Test data incomplete |
| BDD-I001 | info | Consider adding Background steps |
| BDD-I002 | info | Consider adding negative scenarios |

## Validation Commands

```bash
# Validate single BDD document
python ai_dev_flow/scripts/validate_bdd.py docs/04_BDD/BDD-001_example.md

# Validate all BDD documents
python ai_dev_flow/scripts/validate_bdd.py docs/04_BDD/

# Validate .feature files
python ai_dev_flow/scripts/validate_bdd.py tests/bdd/features/

# Check with verbose output
python ai_dev_flow/scripts/validate_bdd.py docs/04_BDD/ --verbose
```

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
10. Calculate ADR-Ready Score
11. Verify file naming convention
12. Generate validation report

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
| 1.0 | 2026-02-08 | Initial validator skill definition with YAML frontmatter | System |
