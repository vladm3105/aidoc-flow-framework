---
name: doc-req-validator
description: Validate Atomic Requirements (REQ) documents against Layer 7 schema standards
tags:
  - sdd-workflow
  - layer-7-artifact
  - quality-assurance
custom_fields:
  layer: 7
  artifact_type: REQ
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [REQ]
  downstream_artifacts: []
  version: "1.0"
  last_updated: "2026-02-08"
---

# doc-req-validator

Validate Atomic Requirements (REQ) documents against Layer 7 schema standards.

## Activation

Invoke when user requests validation of REQ documents or after creating/modifying REQ artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/REQ/REQ_SCHEMA.yaml`
Layer: 7
Artifact Type: REQ

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["req", "template"]
  - artifact_type: "REQ"
  - layer: 7
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - req (or req-template)
  - layer-7-artifact

Forbidden tag patterns:
  - "^req-document$"
  - "^requirements$"
  - "^atomic-requirements$"
  - "^req-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (12 sections):**
- Title (H1): `# REQ-NNN: Title`
- Section 1: Document Control
- Section 2: Functional Requirements
- Section 3: Interface Specifications (Protocol/ABC, DTOs, REST API)
- Section 4: Data Schemas (JSON Schema, Pydantic, Database)
- Section 5: Error Handling Specifications (Exception Catalog, Error Response, State Machine)
- Section 6: Configuration Specifications (YAML schema, Environment Variables)
- Section 7: Quality Attributes (Performance, Reliability, Security, Scalability)
- Section 8: Implementation Guidance (Architecture Patterns, Concurrency, DI)
- Section 9: Acceptance Criteria (≥15 criteria across 5 categories)
- Section 10: Verification Methods
- Section 11: Traceability
- Section 12: Change History

**Document Control Required Fields:**
- Status
- Version
- Date Created
- Last Updated
- Author
- Priority
- Category
- Source Document
- Verification Method
- Assigned Team
- SPEC-Ready Score

**File Naming:**
Pattern: `REQ-NNN_descriptive_name.md`

### 3. Content Validation

**Requirement Keywords:**
- SHALL: Mandatory requirement
- SHOULD: Recommended requirement
- MAY: Optional requirement

**Acceptance Criteria Format:**
- Pattern: `AC-NNN`
- Minimum count: 15 criteria
- Categories: Primary Functional (5), Error/Edge Case (5), Quality/Constraint (3), Data Validation (2), Integration (3)

**Interface Specifications:**
- Protocol/ABC definition with type hints
- DTO definitions (dataclass or Pydantic)
- REST endpoints (optional)

**Data Schema Patterns:**
- JSON Schema (draft-07)
- Pydantic BaseModel with validators
- Database schema (optional)

**SPEC-Ready Score:**
- Minimum threshold: 90%
- Components: Interface completeness, data schema, error handling, configuration, quality attributes, implementation guidance, acceptance criteria, traceability

### 4. Traceability Validation

**Layer 7 Cumulative Tags:**
- @brd: BRD.NN.EE.SS (required)
- @prd: PRD.NN.EE.SS (required)
- @ears: EARS.NN.EE.SS (required)
- @bdd: BDD.NN.EE.SS (required)
- @adr: ADR-NN (required)
- @sys: SYS.NN.EE.SS (required)

**Downstream Expected:**
- IMPL documents
- CTR documents
- SPEC documents
- TASKS documents

**Same-Type References:**
- @related-req: REQ-NN
- @depends-req: REQ-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| REQ-E001 | error | Missing required tag 'req' |
| REQ-E002 | error | Missing required tag 'layer-7-artifact' |
| REQ-E003 | error | Invalid document_type |
| REQ-E004 | error | Invalid architecture_approaches format |
| REQ-E005 | error | Forbidden tag pattern detected |
| REQ-E006 | error | Missing required section |
| REQ-E007 | error | Multiple H1 headings detected |
| REQ-E008 | error | Section numbering not sequential (1-12) |
| REQ-E009 | error | Document Control missing required fields |
| REQ-E010 | error | Missing Interface Specifications (Section 3) |
| REQ-E011 | error | Missing Data Schemas (Section 4) |
| REQ-E012 | error | Missing Error Handling (Section 5) |
| REQ-E013 | error | Missing Acceptance Criteria (Section 9) |
| REQ-E014 | warning | File name does not match format |
| REQ-E015 | error | Missing Protocol/ABC definition |
| REQ-E016 | error | Missing JSON Schema or Pydantic models |
| REQ-E017 | error | Missing Exception Catalog |
| REQ-W001 | warning | SPEC-Ready Score below 90% |
| REQ-W002 | warning | Acceptance Criteria count below 15 |
| REQ-W003 | warning | Missing upstream tags (require 6) |
| REQ-W004 | warning | Missing Description Context subsections |
| REQ-W005 | warning | Missing Performance targets (p50/p95/p99) |
| REQ-W006 | warning | Missing Implementation Guidance patterns |
| REQ-W007 | warning | Code paths appear to be placeholders |
| REQ-I001 | info | Consider adding database schema |
| REQ-I002 | info | Consider adding REST endpoints |
| REQ-I003 | info | Python code should include type hints |

## Validation Commands

```bash
# Validate single REQ document
python ai_dev_flow/scripts/validate_req.py docs/REQ/REQ-001_example.md

# Validate all REQ documents
python ai_dev_flow/scripts/validate_req.py docs/REQ/

# Check with verbose output
python ai_dev_flow/scripts/validate_req.py docs/REQ/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-12)
5. Validate Document Control table
6. Check Interface Specifications (Protocol/ABC)
7. Check Data Schemas (JSON/Pydantic)
8. Check Error Handling (Exception Catalog)
9. Verify Acceptance Criteria count (≥15)
10. Validate upstream references (6 required)
11. Calculate SPEC-Ready Score
12. Verify file naming convention
13. Generate validation report

## Integration

- Invoked by: doc-flow, doc-req (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
REQ Validation Report
=====================
Document: REQ-001_example.md
Status: PASS/FAIL

Interface Coverage:
- Protocol/ABC: Present/Missing
- DTOs: Present/Missing
- REST Endpoints: Present/Missing

Data Schema Coverage:
- JSON Schema: Present/Missing
- Pydantic Models: Present/Missing
- Database Schema: Present/Missing

Acceptance Criteria: N/15

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
