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
> - **Validation**: Use `TASKS_VALIDATION_RULES.md` after TASKS creation/changes

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
| **Breaking Change** | v2.0: 11 sections, execution commands in Section 4 |

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
10. [Quality Checklist](#10-quality-checklist)
11. [Common Anti-Patterns](#11-common-anti-patterns)
12. [Validation](#12-validation)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Cross-Document Validation](#14-cross-document-validation-mandatory)

---

## 1. When to Create a TASKS Document

### Create TASKS When

- [ ] SPEC (YAML specification) is complete and approved
- [ ] Code generation plan needed for a single SPEC
- [ ] AI code generator requires structured implementation instructions
- [ ] Clear acceptance criteria needed before implementation
- [ ] Traceability from SPEC to code is required

### Do NOT Create TASKS When

- [ ] No SPEC exists yet (create SPEC first)
- [ ] Need project management plan (use IMPL instead)
- [ ] Simple configuration changes only
- [ ] Documentation-only updates

---

## 2. File Naming Convention

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

### Format

```
TASKS-NN_{descriptive_component}_tasks.md
```

### Rules

1. **TASKS-NN**: Sequential numbering starting from 001
2. **descriptive_component**: Lowercase with underscores
3. **_tasks**: Required suffix
4. **Extension**: Always `.md`

### Examples

- `TASKS-01_service_connector_tasks.md`
- `TASKS-02_data_integration_tasks.md`
- `TASKS-03_request_execution_service_tasks.md`

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

### 3.3 Mandatory Sections (v2.0 - 11 sections)

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
| 10. Session Log | Progress tracking |
| 11. Change History | Version history |

> **Note**: v1.x had 8 mandatory sections. v2.0 has 11.

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

### Required Tags (Layer 11)

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
@impl: IMPL.NN.EE.SS (if project uses IMPL)
@ctr: CTR-NN (if external API contracts defined)
```

---

## 10. Quality Checklist

### Before Creating

- [ ] SPEC document exists and is approved
- [ ] REQ documents are complete
- [ ] BDD scenarios are defined
- [ ] Architecture decisions (ADR) documented

### During Creation (v2.0)

- [ ] Use TASKS-TEMPLATE.md v2.0 as starting point
- [ ] Follow all 11 section rules above
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

## 11. Common Anti-Patterns

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

## 12. Validation

### Automated Validation

```bash
./scripts/validate_tasks.sh /path/to/TASKS-NN_name.md
```

### Manual Checklist (v2.0)

- [ ] Filename follows convention
- [ ] All 11 required sections present
- [ ] Execution commands in Section 4
- [ ] Traceability tags complete (Section 8)
- [ ] Section 7 Implementation Contracts included
- [ ] SPEC references valid
- [ ] BDD scenario links valid

---

## 13. Upstream Artifact Verification Process

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
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](./IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contracts guide
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 2.0.0
**Last Updated**: 2026-01-15
**Schema Version**: TASKS v2.0 (11 sections)

---

## 14. Cross-Document Validation (MANDATORY)

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
python scripts/validate_cross_document.py --document docs/11_TASKS/TASKS-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all TASKS documents complete
python scripts/validate_cross_document.py --layer TASKS --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| TASKS (Layer 11) | @brd through @spec (+ optional @impl, @ctr) | 8-10 |

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

**Workflow (v2.0)**: `SPEC (Layer 10) → TASKS (Layer 11) → Code → Tests`

