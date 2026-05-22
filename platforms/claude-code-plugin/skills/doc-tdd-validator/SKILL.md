---
name: doc-tdd-validator
description: Validate Test-Driven Development (TDD) documents against Layer 7 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - validation
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: [IPLAN]
    version: "1.4"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-tdd-validator

Validate Test-Driven Development (TDD) documents against Layer 7 schema standards.

## Purpose

Validates TDD documents for:

- YAML frontmatter metadata compliance
- Section structure (the 7 template sections)
- Document Control completeness
- Cumulative tagging (6 required: @brd, @prd, @ears, @bdd, @adr, @spec)
- IPLAN-Ready scoring
- File naming convention (`TDD-NN_{slug}.yaml`)
- Element ID format (`TDD.NN.04.xxxx` — test cases live in Section 4)
- Test type validation (`type` attribute: unit / integration / e2e / security)

## Activation

Invoke when:

- User requests validation of TDD documents
- After creating/modifying TDD artifacts
- Before generating downstream artifacts (IPLAN)
- As part of quality gate checks
- Validating test coverage matrices

## Schema Reference

| Item | Value |
|------|-------|
| TDD Index | `framework/layers/07_TDD/TDD-00_index.TEMPLATE.md` |
| TDD Template | `framework/layers/07_TDD/TDD-TEMPLATE.yaml` |
| TDD README | `framework/layers/07_TDD/README.md` |
| Layer | 7 |
| Artifact Type | TDD |

TDD is a **single unified template — no test subtypes**. Test categories
(unit, integration, e2e, security) are organized as content within one TDD
document via a `type` attribute on each test case, not as separate artifacts
or numeric ID codes.

## Validation Checklist

The framework is spec-only — there are no validation scripts to run. This
skill *is* the validator: apply the declarative checks below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL TDD documents MUST be in nested folders regardless of size.

**Required Structure**:

| Document | Required Location |
|----------|-------------------|
| TDD | `docs/07_TDD/TDD-NN_{slug}/TDD-NN_{slug}.yaml` |

**Validation**:

```
1. Check document is inside a nested folder: docs/07_TDD/TDD-NN_{slug}/
2. Verify folder name matches TDD ID pattern: TDD-NN_{slug}
3. Verify file name matches folder: TDD-NN_{slug}.yaml
4. Parent path must be: docs/07_TDD/
```

**Example Valid Structure**:

```
docs/07_TDD/
├── TDD-01_auth_service/
│   ├── TDD-01_auth_service.yaml      ✓ Valid
│   ├── TDD-01.A_audit_report_v001.md
│   ├── TDD-01.R_review_report_v001.md
│   └── .drift_cache.json
└── TDD-02_order_processing/
    └── TDD-02_order_processing.yaml  ✓ Valid
```

**Invalid Structure**:

```
docs/07_TDD/
├── TDD-01_auth_service.yaml          ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| TDD-E030 | ERROR | TDD not in nested folder (BLOCKING) |
| TDD-E031 | ERROR | Folder name doesn't match TDD ID |
| TDD-E032 | ERROR | File name doesn't match folder name |
| TDD-E033 | ERROR | TDD not in the `docs/07_TDD/` layer directory |

**This check is BLOCKING** - TDD must pass folder structure validation before other checks proceed.

---

### 1. Metadata Validation

```yaml
Required custom_fields:
  artifact_type: "TDD"
  layer: 7
  architecture_approaches: [array format]
  priority: ["primary", "shared", "fallback"]
  development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - sdd-workflow
  - layer-7-artifact

Forbidden tag patterns:
  - "^test-specification$"
  - "^tdd-\\d{3}$"
  - "^unit-test$"
  - "^integration-test$"
```

### 2. Structure Validation

**Required Sections (single unified TDD template)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Test Pyramid | MANDATORY |
| 3 | BDD Scenario to Test Mapping | MANDATORY |
| 4 | Test Case Definitions (includes edge/error cases) | MANDATORY |
| 5 | Test Thresholds | MANDATORY |
| 6 | TDD Execution Order | MANDATORY |
| 7 | Traceability | MANDATORY |

**Note**: Edge cases and error paths are embedded within Section 4 (Test Case
Definitions), not a separate section.

### 3. Document Control Required Fields

| Field | Description | Required |
|-------|-------------|----------|
| Status | Draft/Review/Approved/Implemented | MANDATORY |
| Version | Semantic versioning (X.Y.Z) | MANDATORY |
| Date Created | YYYY-MM-DDTHH:MM:SS format | MANDATORY |
| Last Updated | YYYY-MM-DDTHH:MM:SS format | MANDATORY |
| Author | Test author name | MANDATORY |
| Component | Component/module under test | MANDATORY |
| SPEC Reference | SPEC-NN | MANDATORY |
| IPLAN-Ready Score | `XX/100 (Target: >=90)` | MANDATORY |

### 4. Test Type Categories

Test cases are categorized by a `type` attribute on each case — NOT by
separate ID codes or separate documents.

| Test Type | Coverage Target | Primary Source |
|-----------|-----------------|----------------|
| unit | >=90% | SPEC (Sections 3-4) |
| integration | >=85% (contract validation passes) | SPEC (Section 5) |
| e2e | >=75% of happy paths (<=300s budget) | BDD (Layer 4) |
| security (optional) | all auth/authz paths; no OWASP Top 10 | SPEC, ADR |

### 5. Element ID Format

**Pattern**: `TDD.{doc_id}.{section_id}.{hash}` (4 segments, dot-separated)

- `TDD` — artifact prefix
- `doc_id` — two-digit document number (e.g. `01`)
- `section_id` — two-digit section number; test cases live in Section 4, so `04`
- `hash` — 4-character hex content hash (SHA256, first 4 chars)

**Examples**:

| Element ID | Valid | Notes |
|------------|-------|-------|
| `TDD.01.04.a3c1` | Yes | Test case (Section 4) |
| `TDD.02.04.5e2a` | Yes | Test case (Section 4) |
| `TDD.01.4001` | No | Legacy 3-segment / numeric type code |
| `TC-001` | No | Legacy pattern |
| `UT-001` | No | Legacy pattern |

**Deprecated Patterns (Do NOT use)**:

- `TC-XXX` → Use `TDD.NN.04.xxxx`
- `UT-XXX` / `IT-XXX` / `ST-XXX` / `FT-XXX` → Use `TDD.NN.04.xxxx` with a `type` attribute

### 6. Naming Compliance (doc-naming integration)

**File Naming Pattern**:

| Pattern | Example | Document Type |
|---------|---------|---------------|
| `TDD-NN_{slug}.yaml` | `TDD-01_auth_service.yaml` | TDD document |

**Directory Structure**:

```
docs/07_TDD/
  TDD-01_auth_service/
    TDD-01_auth_service.yaml
  TDD-02_order_processing/
    TDD-02_order_processing.yaml
  TDD-00_index.md
```

### 7. Cumulative Tagging Requirements

**Layer 7 Cumulative Tags (6 Required)**:

```yaml
@brd: BRD.NN.SS.xxxx
@prd: PRD.NN.SS.xxxx
@ears: EARS.NN.SS.xxxx
@bdd: BDD.NN.SS.xxxx
@adr: ADR.NN.SS.xxxx
@spec: SPEC-NN
```

Plus the self-tag `@tdd: TDD-NN` and the downstream IPLAN reference
(`@iplan: IPLAN-NN`) in Section 7.

**Tag Format Convention**:

| Notation | Format | Artifacts |
|----------|--------|-----------|
| Dash | TYPE-NN | ADR (document), SPEC, TDD (document), IPLAN |
| Dot | TYPE.NN.SS.xxxx | BRD, PRD, EARS, BDD, ADR, TDD (element) |

### 8. Test Case Format Requirements

Each test case MUST include:

```yaml
- id: "TDD.01.04.a3c1"
  name: "Reject empty username"
  type: unit              # unit | integration | e2e | security
  spec_ref: "@spec: SPEC-01"
  target: "AuthService.login"
  test_file: "tests/unit/test_auth.py"
  test_function: "test_reject_empty_username"
  inputs:
    - name: "username"
      type: "str"
      value: ""
  expected_output:
    type: "ValidationError"
    value: "username required"
  edge_cases:
    - condition: "whitespace-only username"
      expected: "ValidationError"
```

Integration cases add `contract`, `setup`, `action`, `expected_state`, and
`error_paths`. E2E cases add a `bdd_ref`, a numbered `workflow`,
`timeout_seconds`, and `cleanup`. Security cases (optional) add a `threat`
reference and an `expected_result`.

### 9. Coverage / Mapping Validation

Section 3 (BDD Scenario to Test Mapping) must trace each BDD scenario to one
or more test types and files.

**Required Format**:

```yaml
scenarios:
  - bdd_scenario: "@bdd: BDD.01.03.8f4c"
    description: "[Scenario name from BDD]"
    tests:
      - type: unit
        file: "tests/unit/test_auth.py"
        function: "test_valid_login"
        status: pending

coverage_summary:
  total_bdd_scenarios: N
  mapped: N
  coverage: XX%
```

### 10. Type-Specific Requirements

These are **content categories within the single TDD document**, distinguished
by the `type` attribute — not separate templates.

#### unit

| Requirement | Value |
|-------------|-------|
| Coverage Target | >=90% (function); >=80% (branch) |
| Required Tags | @spec |
| Categories | logic, state, validation, edge |

#### integration

| Requirement | Value |
|-------------|-------|
| Coverage Target | >=85% (contract validation passes) |
| Required Tags | @spec |
| Categories | interaction, contract, sequence |
| Mock Strategy | Must be documented |

#### e2e

| Requirement | Value |
|-------------|-------|
| Coverage Target | >=75% of happy paths (<=300s budget) |
| Required Tags | @bdd, @spec |
| Categories | workflow, end-to-end |
| Source | BDD acceptance scenarios (Layer 4) |

#### security (optional)

| Requirement | Value |
|-------------|-------|
| Coverage Target | all auth/authz paths; no OWASP Top 10 |
| Required Tags | @spec, @adr, @threshold |
| Categories | threat, vulnerability |
| Trigger | SPEC or ADR mandates security tests |

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| TDD-E001 | ERROR | Missing required tag 'sdd-workflow' |
| TDD-E002 | ERROR | Missing required tag 'layer-7-artifact' |
| TDD-E003 | ERROR | Invalid artifact_type value (must be TDD) |
| TDD-E004 | ERROR | Invalid architecture_approaches format (must be array) |
| TDD-E005 | ERROR | Forbidden tag pattern detected |
| TDD-E006 | ERROR | Missing required section |
| TDD-E007 | ERROR | Multiple H1 headings detected |
| TDD-E008 | ERROR | Section numbering not sequential |
| TDD-E009 | ERROR | Document Control missing required fields |
| TDD-E010 | ERROR | Missing Test Case Definitions (Section 4) |
| TDD-E011 | ERROR | Test case missing valid `type` (unit/integration/e2e/security) |
| TDD-E012 | ERROR | Missing cumulative tags (requires 6: @brd through @spec) |
| TDD-E013 | ERROR | Invalid element ID format (not `TDD.NN.04.xxxx`) |
| TDD-E014 | ERROR | Missing upstream @spec tag |
| TDD-E015 | ERROR | Missing BDD Scenario to Test Mapping (Section 3) |
| TDD-E016 | ERROR | Missing SPEC Reference in Document Control |
| TDD-E017 | ERROR | Deprecated ID pattern used (TC-XXX, UT-XXX, IT-XXX, etc.) |
| TDD-E018 | ERROR | Legacy numeric type code used (e.g. `TDD.NN.40xx`) |
| TDD-E019 | ERROR | Missing inputs/expected outputs for test case |
| TDD-E020 | ERROR | Missing traceability section (Section 7) |
| TDD-W001 | WARNING | File name does not match format `TDD-NN_{slug}.yaml` |
| TDD-W002 | WARNING | Missing edge cases for complex test case |
| TDD-W003 | WARNING | IPLAN-Ready Score below target (>=90) |
| TDD-W004 | WARNING | Coverage percentage below type target |
| TDD-W005 | WARNING | Missing error paths for integration tests |
| TDD-W006 | WARNING | Missing test fixtures documentation |
| TDD-W007 | WARNING | Missing mock strategy (integration tests) |
| TDD-W008 | WARNING | E2E budget exceeds 300s |
| TDD-W009 | WARNING | Missing @threshold tags (security tests) |
| TDD-W010 | WARNING | Missing TDD Execution Order (Section 6) |
| VAL-H001 | ERROR | Drift cache missing hash for upstream document |
| VAL-H002 | ERROR | Invalid hash format (must be sha256:<64 hex chars>) |
| TDD-I001 | INFO | Consider adding performance/timeout budgets for e2e |
| TDD-I002 | INFO | Consider adding test data setup documentation |
| TDD-I003 | INFO | Consider adding CI/CD integration notes |

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields (artifact_type, layer)
3. Validate tag taxonomy (sdd-workflow, layer-7-artifact)
4. Verify section structure (7 required sections)
5. Validate Document Control table completeness
6. Check SPEC Reference presence
7. Validate element ID format (`TDD.NN.04.xxxx`)
8. Verify each test case carries a valid `type` (unit/integration/e2e/security)
9. Validate cumulative tags (6 required: @brd through @spec)
10. Check BDD Scenario to Test Mapping completeness (Section 3)
11. Validate inputs/expected outputs present for all test cases
12. Check edge cases / error paths for complex tests
13. Verify Test Thresholds present (Section 5)
14. Verify TDD Execution Order present (Section 6)
15. Calculate IPLAN-Ready Score
16. Verify file naming convention
17. Detect deprecated patterns (TC-XXX, UT-XXX, numeric codes, etc.)
18. Run type-specific validations
19. Generate validation report

## Auto-Fix Actions

| Issue | Auto-Fix Action |
|-------|-----------------|
| Missing cumulative tags | Add with upstream document reference |
| Invalid element ID format | Convert to `TDD.NN.04.xxxx` format |
| Missing traceability section | Insert from template (Section 7) |
| Missing Document Control fields | Add placeholder fields |
| Deprecated ID patterns | Convert to `TDD.NN.04.xxxx` with `type` attribute |
| Legacy numeric type code | Replace code with `type` attribute on the case |
| Missing mapping section | Insert template structure (Section 3) |
| Missing IPLAN-Ready Score | Calculate and insert |

## Integration

- **Invoked by**: doc-flow, doc-tdd (post-creation), quality-advisor, doc-tdd-audit
- **Feeds into**: trace-check (cross-document validation)
- **Reports to**: quality-advisor
- **Validates output from**: doc-tdd skill

## Output Format

```
TDD Validation Report
=====================
Document: TDD-01_auth_service.yaml
Status: PASS/FAIL

IPLAN-Ready Score: 92/100 (Target: >=90) [PASS]

Cumulative Tags:
  @brd: BRD.01.07.a7f3 [PRESENT]
  @prd: PRD.01.09.1dbc [PRESENT]
  @ears: EARS.01.03.5e2a [PRESENT]
  @bdd: BDD.01.03.8f4c [PRESENT]
  @adr: ADR.01.03.e5b1 [PRESENT]
  @spec: SPEC-01 [PRESENT]
  Tags: 6/6 [COMPLETE]

Coverage Summary:
  unit: 88% (Target: >=90%) [BELOW TARGET]
  integration: 86% (Target: >=85%) [PASS]
  e2e: 80% happy paths (Target: >=75%) [PASS]

Test Cases: 12
  Element IDs Valid: 12/12
  Type attribute present: 12/12
  Inputs/Outputs present: 11/12

Errors: 0
Warnings: 3
Info: 1

[TDD-W002] WARNING: Missing edge cases for TDD.01.04.a3c1
[TDD-W004] WARNING: unit coverage (88%) below target (90%)
[TDD-E019] would-be ERROR: Missing inputs for TDD.01.04.b2d0
[TDD-I002] INFO: Consider adding test data setup documentation
```

## Related Resources

- **TDD Skill**: `../doc-tdd/SKILL.md`
- **Naming Standards**: `../doc-naming/SKILL.md` (element IDs)
- **Quality Advisor**: `../quality-advisor/SKILL.md`
- **TDD README**: `framework/layers/07_TDD/README.md`
- **TDD Index template**: `framework/layers/07_TDD/TDD-00_index.TEMPLATE.md`
- **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`

### Templates

- `framework/layers/07_TDD/TDD-TEMPLATE.yaml`

### Standards & Authority

- `framework/governance/ID_NAMING_STANDARDS.md`
- `framework/layers/07_TDD/README.md`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.4 | 2026-05-22 | Migrated to the 8-layer framework model: TDD (Layer 7), single unified template (no test subtypes); test categories (unit/integration/e2e/security) validated as a `type` attribute on test cases; element IDs use 4-segment `TDD.NN.04.xxxx`; cumulative tags reduced to 6 (@brd through @spec, no SYS/REQ/CTR); upstream is SPEC (Layer 6), downstream is IPLAN (Layer 8); removed numeric type-code tables and validation-script commands — this skill *is* the validator (framework is spec-only); template paths point at `framework/layers/07_TDD/`; cross-references use plugin-relative `../doc-X/` |
| 1.3 | 2026-02-27 | Normalized frontmatter to `metadata` schema with `versioning_policy`; type-specific validators; cross-document/tag validation references; added audit-report example path compatibility |
| 1.2 | 2026-02-26 | Added performance and security test categories; updated section count to 6 (error cases in Section 4) |
| 1.1 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING) |
| 1.0 | 2026-02-08 | Initial release: full test-document validation, cumulative tagging, type-specific requirements, doc-naming integration |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.
