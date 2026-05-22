---
name: doc-spec-validator
description: Validate Technical Specifications (SPEC) documents against Layer 6 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "1.5"
    last_updated: "2026-05-22"
  versioning_policy: "tracks SPEC-TEMPLATE schema_version"
---

# doc-spec-validator

Validate Technical Specifications (SPEC) documents against Layer 6 schema standards.

## Activation

Invoke when user requests validation of SPEC documents or after creating/modifying SPEC artifacts.

## Validation Schema Reference

Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
Standards: `framework/governance/ID_NAMING_STANDARDS.md`, `framework/layers/06_SPEC/README.md`
Layer: 6
Artifact Type: SPEC

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL SPEC documents MUST be in nested folders regardless of size.

**Required Structure**:

| SPEC Type | Required Location |
|-----------|-------------------|
| YAML | `docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml` |

**Validation**:

```
1. Check document is inside a nested folder: docs/06_SPEC/SPEC-NN_{slug}/
2. Verify folder name matches SPEC ID pattern: SPEC-NN_{slug}
3. Verify file name matches folder: SPEC-NN_{slug}.yaml
4. Parent path must be: docs/06_SPEC/
```

**Example Valid Structure**:

```
docs/06_SPEC/
├── SPEC-01_f1_iam/
│   ├── SPEC-01_f1_iam.yaml        ✓ Valid
│   ├── SPEC-01.A_audit_report_v001.md (preferred)
│   ├── SPEC-01.R_review_report_v001.md (legacy-compatible)
│   └── .drift_cache.json
├── SPEC-02_f2_session/
│   └── SPEC-02_f2_session.yaml    ✓ Valid
```

**Invalid Structure**:

```
docs/06_SPEC/
├── SPEC-01_f1_iam.yaml            ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| SPEC-E020 | ERROR | SPEC not in nested folder (BLOCKING) |
| SPEC-E021 | ERROR | Folder name doesn't match SPEC ID |
| SPEC-E022 | ERROR | File name doesn't match folder name |
| VAL-H001 | ERROR | Drift cache missing hash for upstream document |
| VAL-H002 | ERROR | Invalid hash format (must be sha256:<64 hex chars>) |

**This check is BLOCKING** - SPEC must pass folder structure validation before other checks proceed.

---

### 1. File Format Validation

```yaml
File Format:
  - Extension: .yaml (NOT .md)
  - Naming pattern: SPEC-NN_descriptive_name.yaml
  - Encoding: UTF-8
  - YAML version: 1.2
```

### 2. Required Top-Level Fields

```yaml
Required fields:
  - id: Component identifier (snake_case)
  - summary: Single-sentence description (10-200 chars)
  - metadata: Document control and versioning
  - traceability: Upstream and downstream references
  - architecture: Component architecture and dependencies
  - interfaces: Interface definitions (classes, methods)
  - behavior: Behavioral specifications
  - performance: Performance targets
  - security: Security specifications
  - observability: Metrics, logging, health checks
  - verification: Test scenarios
  - implementation: Implementation specifics

Optional fields:
  - caching
  - rate_limiting
  - circuit_breaker
  - operations
  - changelog
  - maintenance
  - notes
```

### 3. Metadata Section Validation

**Required Fields:**
- version: Semantic version (MAJOR.MINOR.PATCH)
- status: draft | review | approved | implemented | deprecated
- created_date: YYYY-MM-DD format
- last_updated: YYYY-MM-DD format
- authors: Array with at least one author (name required)

**Optional Fields:**
- task_ready_score
- reviewers
- owners

### 4. Interfaces Section Validation

**Class Requirements:**
- name: PascalCase format
- description: Required
- methods: At least one method required per class

**Method Requirements:**
- name: snake_case format
- description: Required
- input: Optional parameters object
- output: Optional return object
- errors: Optional error definitions

### 5. Performance Section Validation

**Required Fields:**
- latency_targets:
  - p50_milliseconds
  - p95_milliseconds
  - p99_milliseconds
- throughput_targets:
  - sustained_requests_per_second
- resource_limits:
  - cpu_cores_allocated
  - memory_mb_allocated

**Validation Rules:**
- p95 must be greater than p50
- p99 must be greater than p95

### 6. Security Section Validation

**Required Fields:**
- authentication.required: boolean
- authentication.methods: array
- authorization.enabled: boolean
- input_validation.strategy: string

### 7. Observability Section Validation

**Required Fields:**
- metrics.standard_metrics: array (min 1 item)
- logging.level: DEBUG | INFO | WARN | ERROR
- logging.format: json | text | structured
- health_checks.enabled: boolean
- health_checks.endpoints: array

### 8. Traceability Validation

**Layer 6 Cumulative Tags** (4-segment element IDs `TYPE.NN.SS.xxxx`; ADR uses document-level `ADR-NN`):
- @brd: BRD.NN.SS.xxxx (required)
- @prd: PRD.NN.SS.xxxx (required)
- @ears: EARS.NN.SS.xxxx (required)
- @bdd: BDD.NN.SS.xxxx (required)
- @adr: ADR-NN (required)

No `@sys`, `@req`, or `@ctr` tags — the 8-layer model has no SYS/REQ/CTR layers. SPEC carries its own document-level reference `@spec: SPEC-NN`.

**Downstream Expected:**
- TDD documents (Layer 7)
- IPLAN documents (Layer 8)
- Code (src/...)
- Tests (tests/...)

**Same-Type References:**
- related_spec: [SPEC-NN]
- depends_spec: [SPEC-NN]

**Legacy forms REJECTED** (validation must flag these):
- 3-segment element IDs `TYPE.NN.xxxx` (e.g. `SPEC.02.2801`) or any numeric type-code element ID from the retired scheme
- Document IDs with extra leading zero `SPEC-NNN`
- Upstream tags or layer references for the retired system/requirement/contract layers

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| SPEC-E001 | error | File is not valid YAML |
| SPEC-E002 | error | Missing required top-level field |
| SPEC-E003 | error | Missing required metadata field |
| SPEC-E004 | error | Invalid version format |
| SPEC-E005 | error | Invalid status value |
| SPEC-E006 | error | Invalid date format |
| SPEC-E007 | error | No authors specified |
| SPEC-E008 | error | No classes defined in interfaces |
| SPEC-E009 | error | Class has no methods |
| SPEC-E010 | error | Missing latency_targets in performance |
| SPEC-E011 | error | Missing authentication in security |
| SPEC-E012 | error | Missing metrics in observability |
| SPEC-E013 | warning | File name does not match format |
| SPEC-E014 | error | Missing traceability section |
| SPEC-E015 | error | Missing cumulative_tags in traceability |
| SPEC-W001 | warning | Missing business_requirements in upstream |
| SPEC-W002 | warning | Missing cumulative tags for traceability |
| SPEC-W003 | warning | No BDD scenarios in verification |
| SPEC-W004 | warning | p95 latency not greater than p50 |
| SPEC-W005 | warning | p99 latency not greater than p95 |
| SPEC-W006 | warning | Method name not in snake_case |
| SPEC-W007 | warning | Class name not in PascalCase |
| SPEC-W008 | warning | id field does not match file name |
| SPEC-W009 | warning | task_ready_score below target |
| SPEC-I001 | info | Consider adding caching section |
| SPEC-I002 | info | Consider adding rate_limiting section |
| SPEC-I003 | info | Consider adding circuit_breaker section |
| SPEC-I004 | info | Consider adding operations runbook |

## Validation Procedure

The framework ships no runtime validation scripts — **this skill is the validator**. Apply the checklist above declaratively against each SPEC document:

```
1. Locate SPEC documents: docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
2. For each document, walk Checklist sections 0-8 in order.
3. Section 0 (folder structure) is BLOCKING — stop if it fails.
4. Record every finding with its Error Code and severity.
5. Emit the Output Format report.
```

Authoritative references:
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
- Layer contract: `framework/layers/06_SPEC/README.md`

## Validation Workflow

1. Verify file is valid YAML
2. Check all required top-level fields present
3. Validate metadata section (version, status, dates, authors)
4. Check interfaces section (classes with methods)
5. Validate performance section (latency targets, p50 < p95 < p99)
6. Check security section (authentication, authorization)
7. Validate observability section (metrics, logging, health)
8. Check traceability cumulative tags (5 required: @brd, @prd, @ears, @bdd, @adr)
9. Verify verification section (BDD scenarios)
10. Validate implementation section
11. Check file naming convention
12. Generate validation report

## Integration

- Invoked by: doc-flow, doc-spec (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
SPEC Validation Report
======================
Document: SPEC-01_example.yaml
Status: PASS/FAIL

YAML Validity: Valid/Invalid

Required Sections:
- metadata: Present/Missing
- traceability: Present/Missing
- architecture: Present/Missing
- interfaces: Present/Missing
- behavior: Present/Missing
- performance: Present/Missing
- security: Present/Missing
- observability: Present/Missing
- verification: Present/Missing
- implementation: Present/Missing

Interface Summary:
- Classes defined: N
- Methods defined: N

Performance Targets:
- p50: Nms
- p95: Nms (> p50: Yes/No)
- p99: Nms (> p95: Yes/No)

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```

## Related Resources

- **SPEC Skill**: `../doc-spec/SKILL.md`
- **Naming Standards**: `../doc-naming/SKILL.md` (ID and naming conventions)
- **SPEC Template** (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- **ID Naming Standards**: `framework/governance/ID_NAMING_STANDARDS.md`
- **SPEC Layer Contract**: `framework/layers/06_SPEC/README.md`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.5 | 2026-05-22 | Migrated to the framework 8-layer model: SPEC renumbered to **Layer 6**; dropped the retired system/requirement/contract upstream layers (now @brd,@prd,@ears,@bdd,@adr); 4-segment element IDs `TYPE.NN.SS.xxxx` with `SPEC-NN`/`ADR-NN` document refs (rejects legacy 3-segment, numeric type-code, and `SPEC-NNN` forms); downstream TDD (L7) + IPLAN (L8); paths repointed to `framework/layers/06_SPEC/` + `framework/governance/`; removed dead validation-script references (skill is the validator) | System |
| 1.4 | 2026-02-27 | Normalized metadata schema and command references | System |
| 1.3 | 2026-02-26 | Updated cumulative tag formats to unified dot notation; Fixed validation rules paths | System |
| 1.2 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING); Added error codes SPEC-E020, SPEC-E021, SPEC-E022 | System |
| 1.1.0 | 2026-02-08 | Updated layer assignment per LAYER_REGISTRY v1.6; removed @impl from cumulative tags | System |
| 1.0.0 | 2025-01-15 | Initial validator skill definition | System |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

