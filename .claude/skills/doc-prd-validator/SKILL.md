# doc-prd-validator

Validate Product Requirements Documents (PRD) against Layer 2 schema standards.

## Activation

Invoke when user requests validation of PRD documents or after creating/modifying PRD artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
Layer: 2
Artifact Type: PRD

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["prd", "template"]
  - artifact_type: "PRD"
  - layer: 2
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - prd (or prd-template)
  - layer-2-artifact

Forbidden tag patterns:
  - "^product-requirements$"
  - "^prd-\\d{3}$"
```

### 2. Structure Validation

**Required Sections:**
- Title (H1): `# PRD-NNN: Title`
- Document Control (Section 1)
- Executive Summary (Section 2)
- Product Vision (Section 3)
- User Personas (Section 4)
- User Stories (Section 5)
- Feature Requirements (Section 6)
- Acceptance Criteria (Section 7)
- Non-Functional Requirements (Section 8)
- UI/UX Requirements (Section 9)
- Technical Constraints (Section 10)
- Dependencies (Section 11)
- Traceability (Section 12)
- Change History (Section 13)

**Document Control Required Fields:**
- PRD ID
- Document Name
- Version
- Date Created
- Last Updated
- Author
- Reviewer
- Status
- Source BRD

**File Naming:**
Pattern: `PRD-NNN_descriptive_name.md`

### 3. Content Validation

**User Story Format:**
- Pattern: `US-NNN`
- Format: "As a [role], I want [feature], so that [benefit]"
- Required fields: ID, User Story, Priority, Acceptance Criteria

**Feature Requirement Format:**
- Pattern: `FR-NNN`
- Required fields: ID, Feature, Priority, Source User Story, Acceptance Criteria
- Priority values: Must Have, Should Have, Could Have, Won't Have

**EARS-Ready Score:**
- Minimum threshold: 90%
- Components: User stories, feature requirements, acceptance criteria, NFRs, UI/UX, traceability

### 4. Traceability Validation

**Layer 2 Cumulative Tags:**
- @brd: BRD.NN.01.SS (required)

**Downstream Expected:**
- EARS statements
- BDD scenarios
- ADR documents

**Same-Type References:**
- @related-prd: PRD-NN
- @depends-prd: PRD-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| PRD-E001 | error | Missing required tag 'prd' |
| PRD-E002 | error | Missing required tag 'layer-2-artifact' |
| PRD-E003 | error | Invalid document_type |
| PRD-E004 | error | Invalid architecture_approaches format |
| PRD-E005 | error | Forbidden tag pattern detected |
| PRD-E006 | error | Missing required section |
| PRD-E007 | error | Multiple H1 headings detected |
| PRD-E008 | error | Section numbering not sequential |
| PRD-E009 | error | Document Control missing required fields |
| PRD-E010 | error | Missing User Stories (Section 5) |
| PRD-E011 | error | Missing Feature Requirements (Section 6) |
| PRD-E012 | error | Missing Traceability (Section 12) |
| PRD-E013 | warning | File name does not match format |
| PRD-W001 | warning | User stories not using US-NNN format |
| PRD-W002 | warning | Features not using FR-NNN format |
| PRD-W003 | warning | Missing upstream @brd tag |
| PRD-W004 | warning | EARS-Ready Score below 90% |
| PRD-W005 | warning | Missing User Personas (Section 4) |
| PRD-I001 | info | Consider adding competitive analysis |
| PRD-I002 | info | Consider adding success metrics |

## Validation Commands

```bash
# Validate single PRD document
python ai_dev_flow/scripts/validate_prd.py docs/PRD/PRD-001_example.md

# Validate all PRD documents
python ai_dev_flow/scripts/validate_prd.py docs/PRD/

# Check with verbose output
python ai_dev_flow/scripts/validate_prd.py docs/PRD/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-13)
5. Validate Document Control table
6. Check user story format
7. Check feature requirement format
8. Validate upstream BRD reference
9. Calculate EARS-Ready Score
10. Verify file naming convention
11. Generate validation report

## Integration

- Invoked by: doc-flow, doc-prd (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
PRD Validation Report
=====================
Document: PRD-001_example.md
Status: PASS/FAIL

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
