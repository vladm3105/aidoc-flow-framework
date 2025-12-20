# doc-brd-validator

Validate Business Requirements Documents (BRD) against Layer 1 schema standards.

## Activation

Invoke when user requests validation of BRD documents or after creating/modifying BRD artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/BRD/BRD_SCHEMA.yaml`
Layer: 1
Artifact Type: BRD

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["brd", "template"]
  - artifact_type: "BRD"
  - layer: 1
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - brd (or brd-template)
  - layer-1-artifact

Forbidden tag patterns:
  - "^business-requirements$"
  - "^brd-\\d{3}$"
```

### 2. Structure Validation

**Required Sections:**
- Title (H1): `# BRD-NNN: Title`
- Document Control (Section 1)
- Executive Summary (Section 2)
- Business Objectives (Section 3)
- Business Requirements (Section 4)
- Success Metrics (Section 5)
- Constraints (Section 6)
- Assumptions (Section 7)
- Dependencies (Section 8)
- Stakeholder Analysis (Section 9)
- Risk Assessment (Section 10)
- Traceability (Section 11)
- Change History (Section 12)

**Document Control Required Fields:**
- BRD ID
- Document Name
- Version
- Date Created
- Last Updated
- Author
- Reviewer
- Status

**File Naming:**
Pattern: `BRD-NNN_descriptive_name.md`

### 3. Content Validation

**Business Objectives Format:**
- Pattern: `OBJ-NNN`
- Required fields: ID, Objective, Priority, Success Criteria, Measurement Method

**Business Requirements Format:**
- Pattern: `BR-NNN`
- Required fields: ID, Requirement, Type, Priority, Source, Rationale
- Priority values: Critical (P1), High (P2), Medium (P3), Low (P4)
- Type values: Functional, Non-Functional, Regulatory, Operational

**PRD-Ready Score:**
- Minimum threshold: 90%
- Components: Business objectives, requirements completeness, success metrics, constraints, stakeholder analysis, risk assessment, traceability

### 4. Traceability Validation

**Layer 1 Tags:**
- No upstream artifacts (BRD is the source)

**Downstream Expected:**
- PRD documents
- EARS statements
- ADR documents

**Same-Type References:**
- @related-brd: BRD-NN
- @supersedes-brd: BRD-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| BRD-E001 | error | Missing required tag 'brd' |
| BRD-E002 | error | Missing required tag 'layer-1-artifact' |
| BRD-E003 | error | Invalid document_type |
| BRD-E004 | error | Invalid architecture_approaches format |
| BRD-E005 | error | Forbidden tag pattern detected |
| BRD-E006 | error | Missing required section |
| BRD-E007 | error | Multiple H1 headings detected |
| BRD-E008 | error | Section numbering not sequential |
| BRD-E009 | error | Document Control missing required fields |
| BRD-E010 | error | Missing Business Objectives (Section 3) |
| BRD-E011 | error | Missing Business Requirements (Section 4) |
| BRD-E012 | error | Missing Traceability (Section 11) |
| BRD-E013 | warning | File name does not match format |
| BRD-W001 | warning | Objectives not using OBJ-NNN format |
| BRD-W002 | warning | Requirements not using BR-NNN format |
| BRD-W003 | warning | Missing Success Metrics (Section 5) |
| BRD-W004 | warning | PRD-Ready Score below 90% |
| BRD-W005 | warning | Missing Stakeholder Analysis |
| BRD-I001 | info | Consider adding regulatory compliance requirements |
| BRD-I002 | info | Consider adding market analysis context |

## Validation Commands

```bash
# Validate single BRD document
python ai_dev_flow/scripts/validate_brd.py docs/BRD/BRD-001_example.md

# Validate all BRD documents
python ai_dev_flow/scripts/validate_brd.py docs/BRD/

# Check with verbose output
python ai_dev_flow/scripts/validate_brd.py docs/BRD/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-12)
5. Validate Document Control table
6. Check business objectives format
7. Check business requirements format
8. Calculate PRD-Ready Score
9. Verify file naming convention
10. Generate validation report

## Integration

- Invoked by: doc-flow, doc-brd (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
BRD Validation Report
=====================
Document: BRD-001_example.md
Status: PASS/FAIL

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
