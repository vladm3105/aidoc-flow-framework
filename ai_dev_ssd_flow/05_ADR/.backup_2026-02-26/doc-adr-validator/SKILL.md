---
name: doc-adr-validator
description: Validate Architecture Decision Records (ADR) against Layer 5 schema standards
tags:
  - sdd-workflow
  - layer-5-artifact
  - quality-assurance
custom_fields:
  layer: 5
  artifact_type: ADR
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [ADR]
  downstream_artifacts: []
  version: "1.1"
  last_updated: "2026-02-11T18:00:00"
---

# doc-adr-validator

Validate Architecture Decision Records (ADR) against Layer 5 schema standards.

## Activation

Invoke when user requests validation of ADR documents or after creating/modifying ADR artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/ADR/ADR_SCHEMA.yaml`
Layer: 5
Artifact Type: ADR

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL ADR documents MUST be in nested folders regardless of size.

**Required Structure**:

| ADR Type | Required Location |
|----------|-------------------|
| Monolithic | `docs/05_ADR/ADR-NN_{slug}/ADR-NN_{slug}.md` |

**Validation**:

```
1. Check document is inside a nested folder: docs/05_ADR/ADR-NN_{slug}/
2. Verify folder name matches ADR ID pattern: ADR-NN_{slug}
3. Verify file name matches folder: ADR-NN_{slug}.md
4. Parent path must be: docs/05_ADR/
```

**Example Valid Structure**:

```
docs/05_ADR/
├── ADR-01_f1_iam/
│   ├── ADR-01_f1_iam.md           ✓ Valid
│   ├── ADR-01.R_review_report_v001.md
│   └── .drift_cache.json
├── ADR-02_f2_session/
│   └── ADR-02_f2_session.md       ✓ Valid
```

**Invalid Structure**:

```
docs/05_ADR/
├── ADR-01_f1_iam.md               ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| ADR-E020 | ERROR | ADR not in nested folder (BLOCKING) |
| ADR-E021 | ERROR | Folder name doesn't match ADR ID |
| ADR-E022 | ERROR | File name doesn't match folder name |

**This check is BLOCKING** - ADR must pass folder structure validation before other checks proceed.

---

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["adr", "template"]
  - artifact_type: "ADR"
  - layer: 5
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - adr (or adr-template)
  - layer-5-artifact

Forbidden tag patterns:
  - "^architecture-decision$"
  - "^decision-record$"
  - "^adr-\\d{3}$"
```

### 2. Structure Validation

**Document Parts:**
- PART 1: Decision Context and Requirements (Sections 1-6)
- PART 2: Impact Analysis and Architecture (Sections 7-10)
- PART 3: Implementation Strategy (Sections 11-13)
- PART 4: Traceability and Documentation (Sections 14-15)

**Required Sections:**
- Title (H1): `# ADR-NNN: Title`
- Section 1: Document Control
- Section 2: Position in Development Workflow
- Section 3: Status
- Section 4: Context (Problem Statement, Background, Driving Forces, Constraints)
- Section 5: Decision (Chosen Solution, Key Components, Implementation Approach)
- Section 6: Requirements Satisfied
- Section 7: Consequences (Positive, Negative Outcomes)
- Section 8: Architecture Flow (Mermaid diagram)
- Section 9: Implementation Assessment (Complexity, Dependencies)
- Section 10: Impact Analysis

**Optional Sections:**
- Section 11: Alternatives Considered
- Section 12: Security Considerations
- Section 13: Operational Considerations
- Section 14: Traceability
- Section 15: References

**Document Control Required Fields:**
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status

**File Naming:**
Pattern: `ADR-NNN_descriptive_name.md`

### 3. Content Validation

**Status Values:**
- Proposed
- Accepted
- Deprecated
- Superseded

**Context Subsections (Required):**
- 4.1 Problem Statement
- 4.2 Background
- 4.3 Driving Forces
- 4.4 Constraints

**Decision Subsections (Required):**
- 5.1 Chosen Solution
- 5.2 Key Components
- 5.3 Implementation Approach

**Consequences Subsections (Required):**
- 7.1 Positive Outcomes
- 7.2 Negative Outcomes

**Architecture Flow:**
- Must contain Mermaid diagram
- Allowed types: flowchart, sequenceDiagram, stateDiagram-v2

**ADR-Ready Score:**
- Minimum threshold: 90%
- Components: Problem statement, context, decision clarity, consequences, architecture diagram, implementation assessment, traceability

### 4. Traceability Validation

**Layer 5 Cumulative Tags:**
- @brd: BRD.NN.01.SS (required)
- @prd: PRD.NN.07.SS (required)
- @ears: EARS.NN.24.SS (required)
- @bdd: BDD.NN.13.SS (required)

**Downstream Expected:**
- SYS requirements
- REQ documents
- SPEC documents

**Same-Type References:**
- @related-adr: ADR-NN
- @supersedes: ADR-NN
- @depends-adr: ADR-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| ADR-E001 | error | Missing required tag 'adr' |
| ADR-E002 | error | Missing required tag 'layer-5-artifact' |
| ADR-E003 | error | Invalid document_type |
| ADR-E004 | error | Invalid architecture_approaches format |
| ADR-E005 | error | Forbidden tag pattern detected |
| ADR-E006 | error | Missing required section |
| ADR-E007 | error | Multiple H1 headings detected |
| ADR-E008 | error | Missing Context section (Section 4) |
| ADR-E009 | error | Missing Decision section (Section 5) |
| ADR-E010 | error | Missing Consequences section (Section 7) |
| ADR-E011 | error | Context missing Problem Statement subsection |
| ADR-E012 | error | Decision missing Chosen Solution subsection |
| ADR-E013 | error | Consequences missing outcomes |
| ADR-E014 | warning | File name does not match format |
| ADR-W001 | warning | Missing Architecture Flow Mermaid diagram |
| ADR-W002 | warning | Context missing Constraints subsection |
| ADR-W003 | warning | Missing upstream tags (@prd, @ears, @bdd) |
| ADR-W004 | warning | Implementation Assessment missing Complexity |
| ADR-W005 | warning | SYS-Ready Score below 90% |
| ADR-W006 | warning | Requirements Satisfied table missing |
| ADR-I001 | info | Consider adding Alternatives Considered |
| ADR-I002 | info | Consider adding Security Considerations |
| ADR-I003 | info | Consider adding Rollback Plan |

## Validation Commands

```bash
# Validate single ADR document
python ai_dev_flow/scripts/validate_adr.py docs/05_ADR/ADR-001_example.md

# Validate all ADR documents
python ai_dev_flow/scripts/validate_adr.py docs/05_ADR/

# Check with verbose output
python ai_dev_flow/scripts/validate_adr.py docs/05_ADR/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify 4-part structure
5. Validate required sections (1-10)
6. Check Context subsections
7. Check Decision subsections
8. Check Consequences subsections
9. Verify Mermaid diagram presence
10. Validate upstream references
11. Calculate SYS-Ready Score
12. Verify file naming convention
13. Generate validation report

## Integration

- Invoked by: doc-flow, doc-adr (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
ADR Validation Report
=====================
Document: ADR-001_example.md
Status: PASS/FAIL

Structure:
- Context: Complete/Incomplete
- Decision: Complete/Incomplete
- Consequences: Complete/Incomplete
- Architecture Flow: Present/Missing

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.1 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING); ADR must be in `docs/05_ADR/ADR-NN_{slug}/` folders; Added error codes ADR-E020, ADR-E021, ADR-E022 |
| 1.0 | 2026-02-08 | Initial validator skill definition with YAML frontmatter | System |
