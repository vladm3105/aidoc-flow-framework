# doc-ctr-validator

Validate Data Contracts (CTR) documents against Layer 9 schema standards.

## Activation

Invoke when user requests validation of CTR documents or after creating/modifying CTR artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/CTR/CTR_SCHEMA.yaml`
Layer: 9
Artifact Type: CTR

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["ctr", "template"]
  - artifact_type: "CTR"
  - layer: 9
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - ctr (or ctr-template)
  - layer-9-artifact

Forbidden tag patterns:
  - "^ctr-document$"
  - "^contract$"
  - "^api-contract$"
  - "^ctr-\\d{3}$"
```

### 2. Structure Validation (Dual-File Format)

**File Format:**
- Documentation: `.md` file
- Schema: `.yaml` file
- Pattern: `CTR-NNN_descriptive_name.md` + `CTR-NNN_descriptive_name.yaml`

**Required Sections (20 sections in 5 Parts):**

Part 1: Contract Context and Requirements
- Title (H1): `# CTR-NNN: Title`
- Section 1: Document Control
- Section 2: Status
- Section 3: Context (Problem Statement, Background, Driving Forces, Constraints)
- Section 4: Contract Definition (Interface Overview, Parties, Communication Pattern)
- Section 5: Requirements Satisfied

Part 2: Interface Specification and Schema
- Section 6: Schema Reference (YAML file link)
- Section 7: Interface Definition (Endpoints/Functions/Messages)
- Section 8: Error Handling (Error Codes, Failure Modes)
- Section 9: Consequences (Positive/Negative Outcomes)

Part 3: Quality Attributes and Operations
- Section 10: Quality Attributes (Performance, Reliability, Security)
- Section 11: Versioning Strategy (Version Policy, Compatibility, Deprecation)
- Section 12: Examples (Request/Response)
- Section 13: Monitoring & Observability
- Section 14: Alternatives Considered

Part 4: Testing and Implementation
- Section 15: Verification (Contract Testing, BDD Scenarios)
- Section 16: Impact Analysis (Affected Components, Migration, Security)
- Section 17: Related Contracts
- Section 18: Implementation Notes

Part 5: Traceability and Documentation
- Section 19: Traceability
- Section 20: References

**Document Control Required Fields:**
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status

### 3. Content Validation

**Status Values:**
- Draft
- In Review
- Approved
- Active
- Deprecated

**Communication Patterns:**
- Synchronous: REST, gRPC, GraphQL
- Asynchronous: Event-driven, Message Queue, Pub/Sub

**Error Code Format:**
- Pattern: `^[A-Z_]+$`
- Examples: INVALID_INPUT, INSUFFICIENT_DATA, RATE_LIMITED, SERVICE_UNAVAILABLE, INTERNAL_ERROR

**Versioning:**
- Format: MAJOR.MINOR.PATCH (Semantic versioning)

**YAML Schema Requirements:**
- OpenAPI 3.x or JSON Schema format
- Required: info (title, version, description), paths, components/schemas
- All endpoints must have request and response schemas

### 4. Traceability Validation

**Layer 9 Cumulative Tags:**
- @brd: BRD.NN.EE.SS (required)
- @prd: PRD.NN.EE.SS (required)
- @ears: EARS.NN.EE.SS (required)
- @bdd: BDD.NN.EE.SS (required)
- @adr: ADR-NN (required)
- @sys: SYS.NN.EE.SS (required)
- @req: REQ.NN.EE.SS (required)
- @impl: IMPL.NN.EE.SS (optional)

**Downstream Expected:**
- SPEC documents
- TASKS documents
- Code (src/...)

**Same-Type References:**
- @related-ctr: CTR-NN
- @depends-ctr: CTR-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| CTR-E001 | error | Missing required tag 'ctr' |
| CTR-E002 | error | Missing required tag 'layer-9-artifact' |
| CTR-E003 | error | Invalid document_type |
| CTR-E004 | error | Invalid architecture_approaches format |
| CTR-E005 | error | Forbidden tag pattern detected |
| CTR-E006 | error | Missing required section |
| CTR-E007 | error | Multiple H1 headings detected |
| CTR-E008 | error | Section numbering not sequential (1-20) |
| CTR-E009 | error | Document Control missing required fields |
| CTR-E010 | error | Missing companion YAML schema file |
| CTR-E011 | error | YAML schema is not valid OpenAPI 3.x or JSON Schema |
| CTR-E012 | error | Missing request/response schemas for endpoints |
| CTR-E013 | error | Missing Error Handling section |
| CTR-E014 | warning | File name does not match format |
| CTR-E015 | error | Contract Definition missing Provider/Consumer |
| CTR-E016 | error | Error Codes table missing |
| CTR-W001 | warning | Missing Context Problem Statement |
| CTR-W002 | warning | Missing success/failure examples |
| CTR-W003 | warning | Missing upstream tags (require 7) |
| CTR-W004 | warning | Missing Versioning Strategy Version Policy |
| CTR-W005 | warning | Error responses not defined in YAML schema |
| CTR-W006 | warning | Missing contract testing requirements |
| CTR-I001 | info | Consider adding performance metrics |
| CTR-I002 | info | Consider documenting migration strategy |
| CTR-I003 | info | Consider adding alternative approaches |

## Validation Commands

```bash
# Validate single CTR document (validates both .md and .yaml)
python ai_dev_flow/scripts/validate_ctr.py docs/CTR/CTR-001_example.md

# Validate all CTR documents
python ai_dev_flow/scripts/validate_ctr.py docs/CTR/

# Check with verbose output
python ai_dev_flow/scripts/validate_ctr.py docs/CTR/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-20)
5. Validate Document Control table
6. Check companion YAML schema file exists
7. Validate YAML schema (OpenAPI 3.x or JSON Schema)
8. Check Error Handling section (Error Codes table)
9. Verify Provider/Consumer in Contract Definition
10. Check Examples section (success and failure)
11. Validate upstream references (7 required)
12. Verify file naming convention
13. Generate validation report

## Integration

- Invoked by: doc-flow, doc-ctr (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
CTR Validation Report
=====================
Document: CTR-001_example.md
Status: PASS/FAIL

Dual-File Check:
- Markdown file: Present
- YAML schema file: Present/Missing
- Schema valid: Yes/No

Contract Structure:
- Provider defined: Yes/No
- Consumer defined: Yes/No
- Error codes table: Present/Missing

Schema Coverage:
- OpenAPI/JSON Schema: Valid/Invalid
- Request schemas: Complete/Incomplete
- Response schemas: Complete/Incomplete
- Error responses: Defined/Missing

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
