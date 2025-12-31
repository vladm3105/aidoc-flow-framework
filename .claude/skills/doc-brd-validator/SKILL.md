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
- Pattern: `BRD.NN.23.SS` (unified 4-segment format)
- Required fields: ID, Objective, Priority, Success Criteria, Measurement Method

**Business Requirements Format:**
- Pattern: `BRD.NN.01.SS` (unified 4-segment format)
- Required fields: ID, Requirement, Type, Priority, Source, Rationale
- Priority values: Critical (P1), High (P2), Medium (P3), Low (P4)
- Type values: Functional, Non-Functional, Regulatory, Operational

**PRD-Ready Score:**
- Minimum threshold: 90%
- Components: Business objectives, requirements completeness, success metrics, constraints, stakeholder analysis, risk assessment, traceability, **ADR topics completeness**

### 3.5 Architecture Decision Requirements (Section 7.2) - MANDATORY

**7 Mandatory ADR Topic Categories:**

| # | Category | Element ID | Status Values |
|---|----------|------------|---------------|
| 1 | Infrastructure | BRD.NN.32.01 | Selected/Pending/N/A |
| 2 | Data Architecture | BRD.NN.32.02 | Selected/Pending/N/A |
| 3 | Integration | BRD.NN.32.03 | Selected/Pending/N/A |
| 4 | Security | BRD.NN.32.04 | Selected/Pending/N/A |
| 5 | Observability | BRD.NN.32.05 | Selected/Pending/N/A |
| 6 | AI/ML | BRD.NN.32.06 | Selected/Pending/N/A |
| 7 | Technology Selection | BRD.NN.32.07 | Selected/Pending/N/A |

**Required Fields Per Topic (Status=Selected):**
- Status (Selected/Pending/N/A)
- Business Driver
- Business Constraints
- Alternatives Overview table (Option | Function | Est. Monthly Cost | Selection Rationale)
- Cloud Provider Comparison table (Criterion | GCP | Azure | AWS)
- Recommended Selection
- PRD Requirements

**Required Fields Per Topic (Status=Pending):**
- Status with reason
- Business Driver
- Business Constraints
- PRD Requirements

**Required Fields Per Topic (Status=N/A):**
- Status with explicit reason
- PRD Requirements (can be "None for current scope")

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
| BRD-E013 | error | Missing Section 7.2 (Architecture Decision Requirements) |
| BRD-E014 | error | Missing mandatory ADR topic category |
| BRD-E015 | error | ADR topic missing required Status field |
| BRD-E016 | error | Selected ADR topic missing Alternatives Overview table |
| BRD-E017 | error | Selected ADR topic missing Cloud Provider Comparison table |
| BRD-E018 | error | N/A ADR topic missing explicit reason |
| BRD-W001 | warning | Objectives not using BRD.NN.23.SS format |
| BRD-W002 | warning | Requirements not using BRD.NN.01.SS format |
| BRD-W003 | warning | Missing Success Metrics (Section 5) |
| BRD-W004 | warning | PRD-Ready Score below 90% |
| BRD-W005 | warning | Missing Stakeholder Analysis |
| BRD-W006 | warning | File name does not match format |
| BRD-W007 | warning | ADR topic missing cost estimates in Alternatives Overview |
| BRD-W008 | warning | ADR topic missing PRD Requirements field |
| BRD-I001 | info | Consider adding regulatory compliance requirements |
| BRD-I002 | info | Consider adding market analysis context |
| BRD-I003 | info | Consider completing Pending ADR topics before PRD creation |

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
6. Check business objectives format (BRD.NN.23.SS)
7. Check business requirements format (BRD.NN.01.SS)
8. **Validate Section 7.2 ADR Topics** (NEW):
   - Verify all 7 mandatory categories present
   - Check Status field (Selected/Pending/N/A)
   - For Selected: Verify Alternatives Overview table, Cloud Provider Comparison table
   - For N/A: Verify explicit reason provided
   - Validate element ID format (BRD.NN.32.SS)
9. Calculate PRD-Ready Score (includes ADR completeness)
10. Verify file naming convention
11. Generate validation report

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
