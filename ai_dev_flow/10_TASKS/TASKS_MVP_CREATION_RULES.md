---
title: "TASKS MVP Creation Rules"
tags:
  - creation-rules
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: TASKS
  layer: 11
  priority: shared
  development_status: active
  schema_version: "2.0"
  last_updated: "2026-01-15"
---

# =============================================================================
# Document Role: This is a DERIVATIVE of TASKS-TEMPLATE.md
# - Authority: TASKS-TEMPLATE.md is the single source of truth for TASKS structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to TASKS-TEMPLATE.md
# =============================================================================

> **Document Role**: This is a **CREATION HELPER** for TASKS-TEMPLATE.md v2.0.
> - **Authority**: `TASKS-TEMPLATE.md` is the single source of truth for TASKS structure
> - **Validation**: Use `TASKS_MVP_VALIDATION_RULES.md` after TASKS creation/changes

# TASKS Creation Rules (v2.0)

## Index-Only Generation Workflow

- Maintain `TASKS-00_index.md` as the authoritative source of planned and active TASKS files (mark planned items with Status: Planned).
- Generators use: `TASKS-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

Rules for creating AI Tasks (TASKS) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 2.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2026-01-15 |
| **Status** | Active |
| **Breaking Change** | v2.0: 13 sections, execution commands in Section 4 |

---

## Table of Contents

1. [When to Create a TASKS Document](#1-when-to-create-a-tasks-document)
2. [File Naming Convention](#2-file-naming-convention)
3. [Required Sections](#3-required-sections)
4. [Scope Section Rules](#4-scope-section-rules)
5. [Plan Section Rules](#5-plan-section-rules)
6. [Constraints Section Rules](#6-constraints-section-rules)
7. [Acceptance Section Rules](#7-acceptance-section-rules)
8. [Implementation Contracts Section](#8-implementation-contracts-section-mandatory)
9. [Traceability Tag Requirements](#9-traceability-tag-requirements)
10. [Unit Test Results Rules](#10-unit-test-results-rules)
11. [Implementation Summary Rules](#11-implementation-summary-rules)
12. [Quality Checklist](#12-quality-checklist)
13. [Common Anti-Patterns](#13-common-anti-patterns)
14. [Validation](#14-validation)
15. [Upstream Artifact Verification Process](#15-upstream-artifact-verification-process)
16. [Cross-Document Validation](#16-cross-document-validation-mandatory)

---

## 0. SPEC Dependency Analysis (MANDATORY FIRST STEP)

> **⚠️ CRITICAL**: Before creating ANY TASKS documents, you MUST complete SPEC dependency analysis to determine the correct code generation order.

### 0.1 Why This Matters

TASKS documents define code generation instructions. The order in which code is generated affects:
- Build success (dependencies must exist before dependents)
- Test execution (integration tests require dependent services)
- Contract verification (consumers need provider interfaces)

### 0.2 Dependency Analysis Process

**Before planning TASKS, execute these steps:**

1. **Inventory all SPEC files**: List all SPEC-NN files to be implemented
2. **Extract dependencies from each SPEC**:
   - `architecture.dependencies.internal` - other services/modules required
   - `interfaces.internal_apis` - contracts consumed from other services
   - `traceability.upstream_links` - upstream SPEC references
3. **Build dependency graph**: Map which SPECs depend on which
4. **Determine generation order**: Topological sort (dependencies first)
5. **Group into phases**: Parallelizable SPECs in same phase

### 0.3 Required Analysis Outputs

Before creating TASKS, document:

| Output | Purpose |
|--------|---------|
| **Dependency Matrix** | Which SPEC depends on which |
| **Generation Order** | Sequence for code generation |
| **Phase Groupings** | Parallelizable TASKS per phase |
| **Blocking Relationships** | What blocks what |

### 0.4 Dependency Extraction Checklist

For each SPEC file, extract:

```yaml
# From SPEC-NN.yaml, extract:
architecture:
  dependencies:
    internal:
      - name: "redis_client"      # → depends on Redis
      - name: "iam_service"       # → depends on SPEC-01
    external:
      - name: "vertex_ai"         # → external, no SPEC dependency

interfaces:
  internal_apis:
    - interface: "AuthService.validate()"  # → consumes from SPEC-01
```

### 0.5 Example Dependency Analysis

```
SPEC-01 (IAM) ────────────────→ No dependencies (Foundation)
SPEC-02 (Session) ────────────→ Depends on SPEC-01 (IAM)
SPEC-03 (Observability) ──────→ No dependencies (Foundation)
SPEC-08 (Trading Intelligence) → Depends on SPEC-01, SPEC-03, SPEC-07
```

**Resulting Order**:
1. Phase 1: SPEC-01, SPEC-03, SPEC-07 (parallel - no interdeps)
2. Phase 2: SPEC-02 (depends on 01)
3. Phase 3: SPEC-08 (depends on 01, 03, 07)

### 0.6 Anti-Pattern: Skipping Dependency Analysis

**DO NOT**:
- Create TASKS in arbitrary order
- Assume PRD numbering equals dependency order
- Generate code for dependents before dependencies
- Skip dependency extraction from SPEC files

**ALWAYS**:
- Review all SPEC files before planning TASKS
- Extract actual dependencies from SPEC YAML
- Build explicit dependency graph
- Document generation order in TASKS generation plan

---

## 1. When to Create a TASKS Document

### Create TASKS When

- [ ] **SPEC dependency analysis is complete** (Section 0)
- [ ] SPEC (YAML specification) is complete and approved
- [ ] Code generation plan needed for a single SPEC
- [ ] AI code generator requires structured implementation instructions
- [ ] Clear acceptance criteria needed before implementation
- [ ] Traceability from SPEC to code is required

### Do NOT Create TASKS When

- [ ] No SPEC exists yet (create SPEC first)
- [ ] **SPEC dependency analysis not done** (do Section 0 first)
- [ ] Need project management plan (use TASKS execution plan instead)
- [ ] Simple configuration changes only
- [ ] Documentation-only updates

---

## 2. File Naming Convention

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

### Format

```
TASKS-NN_{descriptive_component}.md
```

### Rules

1. **TASKS-NN**: Sequential ID based on creation order/dependency graph (e.g., `TASKS-01`, `TASKS-02`).
   - **Note**: TASKS IDs do **NOT** need to match SPEC IDs.
   - Example: `TASKS-02` might implement `SPEC-03`.
2. **descriptive_component**: Lowercase with underscores
3. **Extension**: Always `.md`

### Examples

- `TASKS-01_service_connector.md`
- `TASKS-02_data_integration.md`
- `TASKS-03_request_execution_service.md`

### 2.1 Element ID Format (MANDATORY)

**Pattern**: `TASKS.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Task | 18 | TASKS.02.18.01 |
| Task Item | 30 | TASKS.02.30.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `TASK-XXX` → Use `TASKS.NN.18.SS`
> - `T-XXX` → Use `TASKS.NN.18.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 3. Required Sections

### 3.1 Frontmatter

```yaml
---
title: "TASKS-NN: [Component Name] Implementation Tasks"
tags:
  - tasks-document
  - layer-11-artifact
  - code-generation
custom_fields:
  document_type: tasks
  artifact_type: TASKS
  layer: 11
  parent_spec: SPEC-NN
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| TASKS ID | Yes | TASKS-NN format |
| Title | Yes | Descriptive task name |
| Status | Yes | Draft/Ready/In Progress/Completed |
| Version | Yes | Semantic version (X.Y.Z) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Parent SPEC | Yes | SPEC-NN reference |
| Complexity | Yes | 1-5 scale |

### 3.3 Mandatory Sections (v2.0 - 13 sections)

| Section | Purpose |
|---------|---------|
| 1. Objective | Deliverables and business value |
| 2. Scope | Inclusions, exclusions, prerequisites |
| 3. Implementation Plan | Phased steps with durations |
| 4. Execution Commands | Setup, implementation, validation |
| 5. Constraints | Technical and quality constraints |
| 6. Acceptance Criteria | Functional, quality, operational criteria |
| 7. Implementation Contracts | Embedded contract definitions (mandatory) |
| 8. Traceability | Upstream refs, tags, code locations |
| 9. Risk & Mitigation | Risk table with mitigations |
| 10. Unit Test Results | Unit tests execution and results |
| 11. Implementation Summary | Summary, accomplishments, issues, remaining work |
| 12. Session Log | Progress tracking |
| 13. Change History | Version history |

> **Note**: v1.x had 8 mandatory sections. v2.0 has 13.

---

## 4. Scope Section Rules

### Requirements

- Clear statement of what component/functionality will be implemented
- Explicit boundaries (what IS included)
- Explicit exclusions (what is NOT included)
- Single SPEC focus (one TASKS per SPEC)

### Good Example

```markdown
## 1. Scope

Implement a minimal `service_connector` that:
- Establishes async TCP connections to External Service
- Manages connection state with 5-state machine
- Provides retry logic with exponential backoff
- Includes circuit breaker pattern

**Exclusions**:
- Data subscription (TASKS-02)
- Request execution (TASKS-03)
```

### Bad Example

```markdown
## 1. Scope

Build the whole gateway system.
```

---

## 5. Plan Section Rules

### Requirements

- Numbered sequential steps (1, 2, 3...)
- Each step is a specific coding task
- Steps reference SPEC line numbers where applicable
- Time estimates optional but recommended
- Verification step for each major component

### Good Example

```markdown
## 2. Plan

1. **Create module structure** (2 hours)
   - Create `src/services/__init__.py`
   - Create `src/services/models.py` (SPEC-01:15-45)
   - Create `src/services/errors.py` (SPEC-01:47-82)

2. **Implement connection protocol** (4 hours)
   - Create `src/services/connector.py`
   - Implement `ServiceConnector` protocol (SPEC-01:84-120)
   - Add type hints per SPEC-01:122-135

3. **Add retry handler** (3 hours)
   - Create `src/services/retry.py`
   - Implement exponential backoff (SPEC-01:137-165)
   - Verify: Unit tests pass with 85% coverage
```

### Bad Example

```markdown
## 2. Plan

1. Write the code.
2. Test it.
3. Deploy it.
```

---

## 6. Constraints Section Rules

### Required Constraint Categories

| Category | Description |
|----------|-------------|
| Technical | Language, framework, platform requirements |
| Coding Standards | Style guides, naming conventions |
| Interface | API compatibility, contract compliance |
| Performance | Latency, throughput targets |
| Quality | Test coverage, documentation requirements |

### Example

```markdown
## 3. Constraints

- **Technical**: Python 3.11+, asyncio, async_client library
- **Coding Standards**: PEP 8, snake_case naming
- **Interface**: Match SPEC-01 exactly, no additions
- **Performance**: p95 latency < 50ms for validations
- **Quality**: 85% unit test coverage minimum
- **Dependencies**: No new runtime dependencies without approval
```

---

## 7. Acceptance Section Rules

### Requirements

- Measurable, verifiable criteria
- Link to BDD scenarios
- Specific test requirements
- Performance validation
- Documentation requirements

### Example

```markdown
## 4. Acceptance

- [ ] All BDD scenarios in BDD-01 pass
- [ ] Unit test coverage ≥85%
- [ ] Integration test coverage ≥75%
- [ ] mypy type checking passes (--strict)
- [ ] p95 latency < 50ms (benchmark tests)
- [ ] All traceability links valid
- [ ] Code review approved
```

---

## 8. Implementation Contracts Section (MANDATORY) - v2.0: Section 7

### Section 7 Requirements (v2.0)

Every TASKS document MUST include "## 7. Implementation Contracts":

```markdown
## 7. Implementation Contracts

### 7.1 Contracts Provided (if provider)

| Contract Name | Type | Consumers | File |
|---------------|------|-----------|------|
| [InterfaceName] | Protocol | TASKS-XX, TASKS-YY | `src/contracts/[name].py` |

### 7.2 Contracts Consumed (if consumer)

| Source | Contract Name | Type | Usage |
|--------|---------------|------|-------|
| TASKS-NN | [ContractName] | Protocol | [How it's used] |

```

If no contracts: State "No implementation contracts for this TASKS."

> **Note**: In v1.x, this was Section 8. Updated to Section 7 in v2.0.

### Validation

```bash
# Section 7 must exist (v2.0)
grep -q "## 7. Implementation Contracts" TASKS-NN.md
# Or check for legacy v1.x
grep -q "## 8. Implementation Contracts" TASKS-NN.md
```

---

## 9. Traceability Tag Requirements

### Required Tags (Layer 10)

```markdown
## Traceability Tags

@brd: BRD.001.NN
@prd: PRD.001.NN
@ears: EARS.001.NN
@bdd: BDD.001.NN
@adr: ADR-NN
@sys: SYS.001.NN
@req: REQ.NN.EE.SS
@spec: SPEC-NN
```

### Optional Tags

```markdown
@ctr: CTR-NN (if external API contracts defined)
```

### 9.1 Cross-Linking Tags (AI-Friendly)

**Purpose**: Establish lightweight, machine-readable hints for AI discoverability and dependency tracing across TASKS documents without blocking validation.

**Tags Supported**:
- `@depends: TASKS-NN` — Hard prerequisite; this TASKS cannot proceed without the referenced TASKS
- `@discoverability: TASKS-NN (short rationale)` — Related document for AI search and ranking (informational)

**ID Format**: Document-level IDs follow `{DOC_TYPE}-NN` per `ID_NAMING_STANDARDS.md` (e.g., `TASKS-01`, `TASKS-02`).

**Placement**: Add tags to the Traceability section or inline with task descriptions.

**Example**:
```markdown
@depends: TASKS-01 (Infrastructure Setup)
@discoverability: TASKS-02 (Application Development - dependent implementation track)
```

**Validator Behavior**: Cross-linking tags are recognized and reported as **info-level** findings (non-blocking). They enable AI/LLM tools to infer relationships and improve search ranking without affecting document approval.

**Optional for MVP**: Cross-linking tags are optional in MVP templates and are not required for TASKS approval; they are purely informational.

---

## 10. Unit Test Results Rules

### Requirements

- Record of executed unit tests
- Summary of results (Pass/Fail)
- Coverage metrics per suite
- Must be updated after Verification phase

### Example
```markdown
## 10. Unit Test Results

| Test Suite | Function | Result | Coverage |
|------------|----------|--------|----------|
| `tests/unit/auth` | User Authentication | ✅ Passed | 98% |
| `tests/unit/api` | API Endpoints | ✅ Passed | 92% |
```

---

## 11. Implementation Summary Rules

### Requirements

- concise summary of the implementation
- bulleted list of accomplishments
- description of any issues encountered and their efficient/workaround
- list of remaining work (if incomplete)

### Example
```markdown
## 11. Implementation Summary

**Summary**:
Implemented the core Auth Service.

**Accomplishments**:
- Created User model
- Implemented JWT logic

**Issues Encountered**:
- None

**Remaining Work**:
- Integration tests
```

---

## 12. Quality Checklist

### Before Creating

- [ ] SPEC document exists and is approved
- [ ] REQ documents are complete
- [ ] BDD scenarios are defined
- [ ] Architecture decisions (ADR) documented

### During Creation (v2.0)

- [ ] Use TASKS-TEMPLATE.md v2.0 as starting point
- [ ] Follow all 13 section rules above
- [ ] Include specific SPEC line references
- [ ] Include execution commands in Section 4
- [ ] Define measurable acceptance criteria (Section 6)
- [ ] Include Section 7 (Implementation Contracts)

### After Creation

- [ ] All traceability tags valid (Section 8)
- [ ] Links resolve to existing documents
- [ ] Update TASKS-00_index.md
- [ ] Run validation script
- [ ] Update IMPLEMENTATION_PLAN.md with new TASKS entry

---

## 13. Common Anti-Patterns

### Avoid

1. **Vague scope** - Be specific about boundaries (Section 2)
2. **Generic steps** - Each step should be actionable (Section 3)
3. **Missing execution commands** - Section 4 required in v2.0
4. **Missing SPEC references** - Always link to SPEC lines
5. **No acceptance criteria** - Must be verifiable (Section 6)
6. **Missing Section 7** - ALWAYS include contracts section
7. **Missing contracts** - Section 7-8 must define contracts for parallel development
8. **Missing execution commands** - Use Section 4 for bash commands

---

## 14. Validation

### Automated Validation

```bash
./10_TASKS/scripts/validate_tasks.sh /path/to/TASKS-NN_name.md
```

### Manual Checklist (v2.0)

- [ ] Filename follows convention
- [ ] All 13 required sections present
- [ ] Execution commands in Section 4
- [ ] Traceability tags complete (Section 8)
- [ ] Section 7 Implementation Contracts included
- [ ] SPEC references valid
- [ ] BDD scenario links valid

---

## 15. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/01_BRD/    # Layer 1
ls -la docs/02_PRD/    # Layer 2
ls -la docs/03_EARS/   # Layer 3
ls -la docs/04_BDD/    # Layer 4
ls -la docs/05_ADR/    # Layer 5
ls -la docs/06_SYS/    # Layer 6
ls -la docs/07_REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

### Same-Type References (Conditional)

Include ONLY if relationships exist between TASKS documents sharing implementation context or execution dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | TASKS-NN | [Related TASKS title] | Shared implementation context |
| Depends | TASKS-NN | [Prerequisite TASKS title] | Must complete before this |

**Tags**:
```markdown
@related-tasks: TASKS-NN
@depends-tasks: TASKS-NN
```


## References

- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - Tasks template
- [TASKS-00_index.md](./TASKS-00_index.md) - Tasks registry
- [README.md](./README.md) - Directory overview
- Implementation contracts guide - reference only (link intentionally omitted)
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 2.0.0
**Last Updated**: 2026-01-15
**Schema Version**: TASKS v2.0 (13 sections)

---

## 16. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any TASKS document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/10_TASKS/TASKS-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all TASKS documents complete
python scripts/validate_cross_document.py --layer TASKS --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| TASKS (Layer 10) | @brd through @spec (+ optional @ctr) | 8-9 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd through @spec tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to implementation until Phase 1 validation passes with 0 errors.

**Workflow (v2.0)**: `SPEC (Layer 9) → TASKS (Layer 10) → Code → Tests`

