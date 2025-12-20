# doc-sys-validator

Validate System Requirements (SYS) documents against Layer 6 schema standards.

## Activation

Invoke when user requests validation of SYS documents or after creating/modifying SYS artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/SYS/SYS_SCHEMA.yaml`
Layer: 6
Artifact Type: SYS

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["sys", "template"]
  - artifact_type: "SYS"
  - layer: 6
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - sys (or sys-template)
  - layer-6-artifact

Forbidden tag patterns:
  - "^system-requirements$"
  - "^sys-doc$"
  - "^sys-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (15 sections):**
- Title (H1): `# SYS-NNN: Title`
- Section 1: Document Control
- Section 2: Executive Summary
- Section 3: Scope (Boundaries, Inclusions, Exclusions)
- Section 4: Functional Requirements (FR-NNN format)
- Section 5: Quality Attributes (Performance, Reliability, Security)
- Section 6: Interface Specifications
- Section 7: Data Management
- Section 8: Testing Requirements
- Section 9: Deployment Requirements
- Section 10: Compliance Requirements
- Section 11: Acceptance Criteria
- Section 12: Risk Assessment
- Section 13: Traceability
- Section 14: Implementation Notes
- Section 15: Change History

**Document Control Required Fields:**
- SYS ID
- Document Name
- Version
- Date Created
- Last Updated
- Author
- Reviewer
- Status

**File Naming:**
Pattern: `SYS-NNN_descriptive_name.md`

### 3. Content Validation

**Functional Requirement Format:**
- Pattern: `FR-NNN`
- Table columns: FR-ID, Requirement, Priority, Source, Verification Method
- Priority values: Must Have, Should Have, Could Have, Won't Have

**Quality Attribute Format (4-segment):**
- Pattern: `SYS.NN.25.SS`
- Example: `SYS.08.25.15`
- Categories: Performance, Reliability, Scalability, Security, Observability, Maintainability

**Quality Attribute Metrics:**

| Category | Keywords | Metrics |
|----------|----------|---------|
| Performance | latency, response time, throughput, p50/p95/p99 | Response Time, Throughput, Latency |
| Reliability | uptime, availability, MTBF, MTTR | Availability, Error Rate |
| Scalability | concurrent, horizontal, vertical | Concurrent Users, Data Volume |
| Security | auth, encrypt, RBAC, compliance | Authentication, Authorization |
| Observability | log, monitor, alert, trace | Logging, Monitoring, Alerting |
| Maintainability | coverage, deploy, CI/CD | Code Coverage, Deploy Frequency |

**REQ-Ready Score:**
- Minimum threshold: 90%
- Components: Functional completeness, quality attributes, interfaces, data management, testing, acceptance criteria, traceability

### 4. Traceability Validation

**Layer 6 Cumulative Tags:**
- @brd: BRD.NN.01.SS (required)
- @prd: PRD.NN.07.SS (required)
- @ears: EARS.NN.24.SS (required)
- @bdd: BDD.NN.13.SS (required)
- @adr: ADR-NN (required)

**Downstream Expected:**
- REQ documents
- SPEC documents
- TASKS documents

**Same-Type References:**
- @related-sys: SYS-NN
- @depends-sys: SYS-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| SYS-E001 | error | Missing required tag 'sys' |
| SYS-E002 | error | Missing required tag 'layer-6-artifact' |
| SYS-E003 | error | Invalid document_type |
| SYS-E004 | error | Invalid architecture_approaches format |
| SYS-E005 | error | Forbidden tag pattern detected |
| SYS-E006 | error | Missing required section |
| SYS-E007 | error | Multiple H1 headings detected |
| SYS-E008 | error | Section numbering not sequential (1-15) |
| SYS-E009 | error | Document Control missing required fields |
| SYS-E010 | error | Missing Functional Requirements (Section 4) |
| SYS-E011 | error | Missing Quality Attributes (Section 5) |
| SYS-E012 | error | Missing Traceability (Section 13) |
| SYS-E013 | warning | File name does not match format |
| SYS-W001 | warning | Functional requirements not using FR-NNN |
| SYS-W002 | warning | Quality attributes not using 4-segment format |
| SYS-W003 | warning | Missing Performance category |
| SYS-W004 | warning | Missing Security category |
| SYS-W005 | warning | Missing upstream tags (require 5) |
| SYS-W006 | warning | REQ-Ready Score below 90% |
| SYS-W007 | warning | Testing Requirements missing coverage |
| SYS-I001 | info | Consider adding p50/p95/p99 latency |
| SYS-I002 | info | Consider adding MTBF/MTTR metrics |

## Validation Commands

```bash
# Validate single SYS document
python ai_dev_flow/scripts/validate_sys.py docs/SYS/SYS-001_example.md

# Validate all SYS documents
python ai_dev_flow/scripts/validate_sys.py docs/SYS/

# Check with verbose output
python ai_dev_flow/scripts/validate_sys.py docs/SYS/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-15)
5. Validate Document Control table
6. Check functional requirement format
7. Check quality attribute format
8. Verify quality categories coverage
9. Validate upstream references (5 required)
10. Calculate REQ-Ready Score
11. Verify file naming convention
12. Generate validation report

## Integration

- Invoked by: doc-flow, doc-sys (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
SYS Validation Report
=====================
Document: SYS-001_example.md
Status: PASS/FAIL

Quality Attribute Coverage:
- Performance: Present/Missing
- Reliability: Present/Missing
- Security: Present/Missing
- Scalability: Present/Missing
- Observability: Present/Missing

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
