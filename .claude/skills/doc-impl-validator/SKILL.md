# doc-impl-validator

Validate Implementation Approach (IMPL) documents against Layer 8 schema standards.

## Activation

Invoke when user requests validation of IMPL documents or after creating/modifying IMPL artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/IMPL/IMPL_SCHEMA.yaml`
Layer: 8
Artifact Type: IMPL

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["impl", "template"]
  - artifact_type: "IMPL"
  - layer: 8
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - impl (or impl-template)
  - layer-8-artifact

Forbidden tag patterns:
  - "^implementation-plan$"
  - "^implementation_plan$"
  - "^project-plan$"
  - "^impl-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (4-Part Structure):**
- Title (H1): `# IMPL-NNN: Title`
- Section 1: Document Control
- Section 2: PART 1 - Project Context and Strategy (Overview, Objectives, Scope, Dependencies)
- Section 3: PART 2 - Phased Implementation and Work Breakdown
- Section 4: PART 3 - Project Management and Risk (Resources, Risk Register, Communication)
- Section 5: PART 4 - Tracking and Completion (Deliverables, Validation, Criteria)
- Section 6: Traceability
- Section 7: References

**Document Control Required Fields:**
- IMPL ID
- Title
- Status
- Created
- Author
- Owner
- Last Updated
- Version
- Related REQs
- Deliverables

**File Naming:**
Pattern: `IMPL-NNN_descriptive_name.md`

### 3. Content Validation

**Status Values:**
- Draft
- Planned
- In Progress
- On Hold
- Completed
- Cancelled

**Phase Table Required Fields:**
- Purpose
- Owner
- Timeline
- Deliverables
- Dependencies

**Risk Register Format:**
- Pattern: `R-NNN`
- Required columns: Risk ID, Risk Description, Probability, Impact, Mitigation Strategy, Owner, Status
- Probability values: Low, Medium, High
- Impact values: Low, Medium, High
- Status values: Open, Mitigated, Accepted, Closed

**Scope Boundaries:**
- IMPL must NOT contain technical HOW details (belongs in SPEC)
- IMPL must NOT contain test details (belongs in BDD/TASKS)
- IMPL focuses on WHO, WHAT, WHEN, WHY

### 4. Traceability Validation

**Layer 8 Cumulative Tags:**
- @brd: BRD.NN.EE.SS (required)
- @prd: PRD.NN.EE.SS (required)
- @ears: EARS.NN.EE.SS (required)
- @bdd: BDD.NN.EE.SS (required)
- @adr: ADR-NN (required)
- @sys: SYS.NN.EE.SS (required)
- @req: REQ.NN.EE.SS (required)

**Downstream Expected:**
- CTR documents
- SPEC documents
- TASKS documents

**Same-Type References:**
- @related-impl: IMPL-NN
- @depends-impl: IMPL-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| IMPL-E001 | error | Missing required tag 'impl' |
| IMPL-E002 | error | Missing required tag 'layer-8-artifact' |
| IMPL-E003 | error | Invalid document_type |
| IMPL-E004 | error | Invalid architecture_approaches format |
| IMPL-E005 | error | Forbidden tag pattern detected |
| IMPL-E006 | error | Missing required Document Control field |
| IMPL-E007 | error | Invalid IMPL ID format |
| IMPL-E008 | error | Multiple H1 headings detected |
| IMPL-E009 | error | Missing required PART section |
| IMPL-E010 | error | No Related REQs specified |
| IMPL-E011 | error | No Deliverables specified |
| IMPL-W001 | warning | Risk ID not using R-NNN format |
| IMPL-W002 | warning | Phase missing required fields |
| IMPL-W003 | warning | Section numbering not sequential |
| IMPL-W004 | warning | Technical implementation details found (belongs in SPEC) |
| IMPL-W005 | warning | Missing cumulative traceability tags |

## Validation Commands

```bash
# Validate single IMPL document
python ai_dev_flow/scripts/validate_impl.py docs/IMPL/IMPL-001_example.md

# Validate all IMPL documents
python ai_dev_flow/scripts/validate_impl.py docs/IMPL/

# Check with verbose output
python ai_dev_flow/scripts/validate_impl.py docs/IMPL/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify 4-PART structure
5. Validate Document Control table
6. Check Phase definitions (Purpose, Owner, Timeline, Deliverables)
7. Validate Risk Register format (R-NNN)
8. Verify no technical implementation details (scope check)
9. Validate upstream references (7 required)
10. Verify file naming convention
11. Generate validation report

## Integration

- Invoked by: doc-flow, doc-impl (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
IMPL Validation Report
======================
Document: IMPL-001_example.md
Status: PASS/FAIL

Structure:
- PART 1 (Context): Present/Missing
- PART 2 (Implementation): Present/Missing
- PART 3 (Management): Present/Missing
- PART 4 (Tracking): Present/Missing

Risk Register:
- Total Risks: N
- Using R-NNN format: N

Scope Check:
- No technical details: PASS/FAIL

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
