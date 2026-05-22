---
name: doc-tdd
description: Create Test-Driven Development guide (TDD) - Layer 7 artifact defining test cases for unit, integration, e2e, and security tests
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-tdd

## Purpose

Create a **Test-Driven Development guide (TDD)** - Layer 7 artifact in the SDD workflow that defines test cases for Test-Driven Development between SPEC (Layer 6) and IPLAN (Layer 8). Each TDD document maps BDD acceptance scenarios to concrete tests with inputs, expected outputs, edge cases, and quality thresholds.

**Layer**: 7

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SPEC (Layer 6)

**Downstream Artifacts**: IPLAN (Layer 8), Code

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/01_BRD/ docs/02_PRD/ docs/03_EARS/ docs/04_BDD/ docs/05_ADR/ docs/06_SPEC/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating TDD, read:

1. **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`
2. **Upstream SPEC**: Read technical specifications (PRIMARY SOURCE — defines the component contract)
3. **Upstream BDD**: Read acceptance scenarios (source of truth for behavior — TDD maps these to tests)
4. **Template**: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
5. **TDD README**: `framework/layers/07_TDD/README.md`

## When to Use This Skill

Use `doc-tdd` when:
- Have completed BRD through SPEC (Layers 1-6)
- Ready to define test cases before implementation
- Following Test-Driven Development workflow
- Need to specify unit, integration, e2e, or security tests
- You are at Layer 7 of the SDD workflow

## Reserved ID Exemption (TDD-00_*)

**Scope**: Documents with reserved ID `00` are FULLY EXEMPT from validation.

**Pattern**: `TDD-00_*` (e.g. `TDD-00_index.md`)

**Document Types**:
- Index documents (`TDD-00_index.md`)
- Traceability matrix templates
- Glossaries, registries, checklists

**Rationale**: Reserved ID 00 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `TDD-00_*` pattern.

## Element ID Format (MANDATORY)

**Pattern**: `TDD.{doc_id}.{section_id}.{hash}` (4 segments, dot-separated)

- `TDD` — artifact prefix
- `doc_id` — two-digit document number (e.g. `01`)
- `section_id` — two-digit section number; test cases live in Section 4, so `04`
- `hash` — 4-character hex content hash (SHA256, first 4 chars)

**Example**: `TDD.01.04.a3c1`

Test cases are categorized by **test type** (unit / integration / e2e / security) as a `type` attribute on each case — NOT by separate ID codes or separate documents.

> **REMOVED PATTERNS** - Do NOT use legacy formats:
> - `TC-XXX` → Use `TDD.NN.04.xxxx`
> - `UT-XXX` / `IT-XXX` / `ST-XXX` / `FT-XXX` → Use `TDD.NN.04.xxxx` with a `type` attribute

**Reference**: [ID_NAMING_STANDARDS.md](../../../../framework/governance/ID_NAMING_STANDARDS.md) for complete element-ID and tag formats.

## Document-Level Reference Format (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format | Artifacts | Purpose |
|----------|--------|-----------|---------|
| Dash | TYPE-NN | ADR, SPEC, IPLAN, TDD (document tag) | References to whole files/documents |
| Dot | TYPE.NN.SS.xxxx | BRD, PRD, EARS, BDD, ADR, TDD | References to elements inside documents |

**Key Distinction**:
- `@spec: SPEC-01` - Points to the document `SPEC-01.yaml`
- `@bdd: BDD.01.03.8f4c` - Points to element `03.8f4c` inside document `BDD-01`

## TDD Structure (single unified template — no subtypes)

The 8-layer TDD is a **single template** (`framework/layers/07_TDD/TDD-TEMPLATE.yaml`).
There are no test subtypes or separate test artifacts. Test categories
(unit, integration, e2e, security) are organized as content sections within a
single TDD document, one TDD per SPEC component.

**Test types (content categories, not separate artifacts)**:

| Test type | Purpose | Primary source |
|-----------|---------|----------------|
| unit | Validate individual functions, methods, and data-model constraints | SPEC (Sections 3-4) |
| integration | Validate component interactions, state transitions, error handling | SPEC (Section 5) |
| e2e | Validate full workflows mapped from acceptance scenarios | BDD (Layer 4) |
| security | Optional — vulnerability/threat tests when SPEC or ADR mandates them | SPEC, ADR |

**Note**: Acceptance scenarios remain in BDD (Layer 4); TDD maps them to tests, it does not duplicate them.

## TDD-Specific Guidance

### 1. Document Structure

One TDD document per SPEC component. Filename: `TDD-NN_{component_slug}.yaml`.

```
docs/07_TDD/
├── TDD-01_auth_service.yaml
├── TDD-02_order_processing.yaml
└── TDD-00_index.md
```

The template defines 7 sections:

1. **Document Control** — metadata, component, IPLAN-Ready score
2. **Test Pyramid** — distribution of effort across unit/integration/e2e
3. **BDD Scenario to Test Mapping** — each BDD scenario maps to test types and files
4. **Test Case Definitions** — concrete inputs, outputs, edge cases per test type
5. **Test Thresholds** — coverage targets and pass criteria per test type
6. **TDD Execution Order** — Red → Green → Refactor enforcement
7. **Traceability** — cumulative upstream tags + downstream IPLAN

### 2. Document Control (Section 1)

| Item | Details |
|------|---------|
| Status | Draft / Review / Approved / Implemented |
| Version | 1.0 |
| Date Created | YYYY-MM-DDTHH:MM:SS |
| Last Updated | YYYY-MM-DDTHH:MM:SS |
| Author | [Author name] |
| Component | [Component/module name] |
| SPEC Reference | SPEC-NN |
| IPLAN-Ready Score | [XX]/100 (Target: >=90) |

### 3. Test Pyramid (Section 2)

Define the distribution of test effort. Defaults are targets, not strict quotas:

- unit: 70%
- integration: 20%
- e2e: 10%

### 4. BDD Scenario to Test Mapping (Section 3)

Each BDD scenario maps to one or more test types. Test file paths declare where
tests will be written. **TDD order**: test files must exist before
implementation files.

```yaml
scenarios:
  - bdd_scenario: "@bdd: BDD.01.03.8f4c"
    description: "[Scenario name from BDD]"
    tests:
      - type: unit
        file: "tests/unit/test_auth.py"
        function: "test_valid_login"
        status: pending
      - type: e2e
        file: "tests/e2e/test_login_flow.py"
        function: "test_valid_login_e2e"
        status: pending
```

### 5. Test Case Definitions (Section 4)

Each test case carries a `type` attribute (unit / integration / e2e / security).

```yaml
unit_tests:
  cases:
    - id: "TDD.01.04.a3c1"
      name: "Reject empty username"
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

### 6. Test Thresholds (Section 5)

Quality gates per test type; CI must enforce these:

| Test type | Coverage target | Fail action |
|-----------|-----------------|-------------|
| unit | >=90% | Block merge |
| integration | >=85% (contract validation passes) | Block merge |
| e2e | >=75% of happy paths (<=300s budget) | Block deploy to staging |
| security (optional) | All auth/authz paths; no OWASP Top 10 | Block deploy |

### 7. TDD Execution Order (Section 6)

Declares the order the AI must follow when generating code:

1. **Write Tests** — generate all test files from Sections 3-4
2. **Run Tests (Red)** — confirm they fail (no implementation yet)
3. **Implement** — generate implementation files; make tests pass
4. **Verify (Green)** — run tests; confirm all pass
5. **Refactor** — clean up; tests remain green

## Cumulative Tagging Requirements

**Layer 7 (TDD)**: Must include tags from upstream Layers 1-6.

### Element Reference Format for Cumulative Tags

| Artifact | Reference style | Example |
|----------|-----------------|---------|
| BRD | element (dot) | BRD.01.07.a7f3 |
| PRD | element (dot) | PRD.01.09.1dbc |
| EARS | element (dot) | EARS.01.03.5e2a |
| BDD | element (dot) | BDD.01.03.8f4c |
| ADR | element (dot) | ADR.01.03.e5b1 |
| SPEC | document (dash) | SPEC-01 |
| TDD (self) | document (dash) | TDD-01 |

**Required tags (Section 7 — Traceability)**:
```yaml
traceability:
  tags:
    - "@tdd: TDD-01"
  upstream:
    - "@brd: BRD.01.07.a7f3"
    - "@prd: PRD.01.09.1dbc"
    - "@ears: EARS.01.03.5e2a"
    - "@bdd: BDD.01.03.8f4c"
    - "@adr: ADR.01.03.e5b1"
    - "@spec: SPEC-01"
  downstream:
    - type: IPLAN
      layer: 8
      description: "Implementation plan — test-first file generation order enforced"
```

## Validation Checks

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the declarative checks below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

### Tier 1: Errors (Blocking)

| Check | Description |
|-------|-------------|
| CHECK 1 | Filename format valid (`TDD-NN_{slug}.yaml`) |
| CHECK 2 | Document Control complete (Section 1) |
| CHECK 3 | All 7 template sections present |
| CHECK 4 | Element ID format compliance (`TDD.NN.04.xxxx`) |
| CHECK 5 | Each test case carries a valid `type` (unit/integration/e2e/security) |
| CHECK 6 | All required upstream traceability tags present (@brd…@spec) |
| CHECK 7 | Parent SPEC reference valid and file exists |

### Tier 2: Warnings

| Check | Description |
|-------|-------------|
| CHECK W1 | Inputs/expected outputs present for each test case |
| CHECK W2 | Edge cases documented for complex tests |
| CHECK W3 | BDD scenario → test mapping table complete |
| CHECK W4 | IPLAN-Ready Score meets target (>=90/100) |
| CHECK W5 | Error paths documented for integration tests |

### Tier 3: Info

| Check | Description |
|-------|-------------|
| CHECK I1 | Test fixtures documented |
| CHECK I2 | Mock/stub strategy specified |
| CHECK I3 | Performance/timeout budgets defined for e2e |

## Creation Process

### Step 1: Read Upstream Artifacts

Focus on SPEC (Layer 6) as the component contract and BDD (Layer 4) as the
source of behavior scenarios.

### Step 2: Reserve ID Number

Check `docs/07_TDD/` for the next available ID number.

**ID Numbering Convention**: Start with 2 digits and expand only as needed.
- Correct: TDD-01, TDD-02, TDD-99
- Incorrect: TDD-001 (extra leading zero not required)

### Step 3: Create TDD File

**File naming**: `docs/07_TDD/TDD-NN_{component_slug}.yaml`

**Examples**:
- `docs/07_TDD/TDD-01_auth_service.yaml`
- `docs/07_TDD/TDD-02_order_processing.yaml`

### Step 4: Fill Document Control (Section 1)

Complete metadata including SPEC Reference and IPLAN-Ready Score.

### Step 5: Define the Test Pyramid (Section 2)

Set the distribution of effort across unit/integration/e2e.

### Step 6: Map BDD Scenarios to Tests (Section 3)

For each BDD scenario, declare the test types, files, and functions.

### Step 7: Write Test Case Definitions (Section 4)

For each test case:
- Assign Element ID (`TDD.NN.04.xxxx`)
- Set `type` (unit / integration / e2e / security)
- Add `spec_ref` (and `bdd_ref` for e2e)
- Define inputs and expected outputs
- Document edge cases / error paths

### Step 8: Set Test Thresholds (Section 5)

Define coverage targets and pass/fail criteria per test type.

### Step 9: Declare TDD Execution Order (Section 6)

Confirm the Red → Green → Refactor phases are present.

### Step 10: Add Cumulative Tags (Section 7)

Include all upstream tags (@brd through @spec) plus the @tdd self-tag and the
downstream IPLAN reference.

### Step 11: Update the Index

**MANDATORY**: Update `docs/07_TDD/TDD-00_index.md` document registry.

### Step 12: Validate TDD

Run the declarative validation checklist (below). The framework is spec-only;
there are no scripts to invoke.

### Step 13: Commit Changes

Commit the TDD file and the index update.

## Validation

### Manual Checklist

- [ ] Document Control section complete (Section 1)
- [ ] Test Pyramid distribution set (Section 2)
- [ ] BDD scenario → test mapping complete (Section 3)
- [ ] Each test case has a `TDD.NN.04.xxxx` ID
- [ ] Each test case has a valid `type` (unit/integration/e2e/security)
- [ ] Inputs/expected outputs present for all test cases
- [ ] Edge cases / error paths documented
- [ ] Test thresholds set per type (Section 5)
- [ ] TDD execution order present (Section 6)
- [ ] Cumulative tags: @brd through @spec, plus @tdd self-tag
- [ ] IPLAN-Ready Score meets target (>=90/100)
- [ ] Index updated

### Diagram Standards

All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box
drawings) are prohibited. See the `mermaid-gen` skill.

## Common Pitfalls

1. **Inventing test subtypes or ID codes**: TDD is a single template; categorize tests with a `type` attribute, not separate artifacts or numeric codes.
2. **Missing inputs/outputs**: Every test case needs concrete input and expected-output specification.
3. **Skipping the BDD mapping**: Section 3 must trace each scenario to tests.
4. **Wrong reference format**: Use `TDD.NN.04.xxxx` for test-case elements, `SPEC-NN` (dash) for documents.
5. **Missing cumulative tags**: Layer 7 requires upstream tags @brd through @spec.
6. **Legacy test IDs**: Use `TDD.NN.04.xxxx`, NOT TC-XXX, UT-XXX, IT-XXX, etc.
7. **Implementation before tests**: TDD order requires test files first (Red), then code (Green).
8. **Incomplete error paths**: Document expected behavior for all error conditions.

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation.
Do NOT proceed to the next document until validation passes.

### Validation Loop

```
LOOP:
  1. Apply the Tier 1 / Tier 2 / Tier 3 checks above
  2. IF errors found and auto-fixable: fix → GOTO LOOP (re-validate)
  3. IF warnings auto-fixable: fix → GOTO LOOP (re-validate)
  4. IF unfixable issues: log for manual review, continue
  5. IF clean: mark VALIDATED, proceed
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| TDD (Layer 7) | @brd, @prd, @ears, @bdd, @adr, @spec | 6 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing upstream tag | Add with upstream document reference |
| Invalid tag format | Correct to `TYPE.NN.SS.xxxx` (element) or `TYPE-NN` (document) |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template (Section 7) |

### Quality Gate

**Blocking**: YES — cannot proceed to IPLAN until TDD validation passes with 0
errors and the IPLAN-Ready Score is >=90/100.

---

## Next Skill

After creating TDD, use:

**`doc-iplan`** - Create Implementation Plan (Layer 8)

The IPLAN will:
- Reference this TDD for test-first implementation order
- Include all upstream tags (…, @spec, @tdd)
- Orchestrate the build, enforcing test files before implementation files

## Reference Documents

TDD artifacts do not support REF documents. Reference documents are limited to
**BRD and ADR types only** per the SDD framework.

For supplementary documentation needs, create:
- **BRD-REF**: Business context documentation
- **ADR-REF**: Test strategy guides, coverage analysis reports

## Related Resources

- **Template**: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- **TDD README**: `framework/layers/07_TDD/README.md`
- **TDD Index template**: `framework/layers/07_TDD/TDD-00_index.TEMPLATE.md`
- **ID & Tag Standards**: `framework/governance/ID_NAMING_STANDARDS.md`
- **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`
- **doc-naming skill**: `../doc-naming/SKILL.md` (element ID formats)
- **doc-spec skill**: `../doc-spec/SKILL.md` (upstream SPEC creation)
- **doc-iplan skill**: `../doc-iplan/SKILL.md` (downstream implementation plan)
- **quality-advisor skill**: `../quality-advisor/SKILL.md` (quality guidance)

## Quick Reference

**TDD Purpose**: Test case definitions for the TDD workflow

**Layer**: 7

**Element ID Format**: `TDD.NN.04.xxxx` (4-segment; test cases live in Section 4)

**Test types (content categories, not subtypes)**: unit, integration, e2e, security

**Removed Patterns**: TC-XXX, UT-XXX, IT-XXX, ST-XXX, FT-XXX

**Tags Required**: @brd, @prd, @ears, @bdd, @adr, @spec (6 upstream) + @tdd self-tag

**Format**: YAML following `TDD-TEMPLATE.yaml` (7 sections)

**Key Sections**:
- Document Control
- Test Pyramid
- BDD Scenario to Test Mapping
- Test Case Definitions (inputs, outputs, edge cases)
- Test Thresholds
- TDD Execution Order
- Traceability (cumulative tags)

**Quality Gate**: IPLAN-Ready Score >=90/100

**Next**: doc-iplan

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Single unified template (no test subtypes or numeric codes); test types now a `type` attribute on test cases. 4-segment element IDs (`TDD.NN.04.xxxx`); upstream chain BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. Paths point at `framework/layers/07_TDD/`; validation is now this skill's declarative checklist (framework is spec-only). |
| 1.0 | 2026-02-08 | Initial release (pre-migration). |
