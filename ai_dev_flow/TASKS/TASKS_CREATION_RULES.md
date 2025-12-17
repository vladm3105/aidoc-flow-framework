# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of TASKS-TEMPLATE.md
# - Authority: TASKS-TEMPLATE.md is the single source of truth for TASKS structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to TASKS-TEMPLATE.md
# =============================================================================
---
title: "TASKS Creation Rules"
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
---

> **📋 Document Role**: This is a **CREATION HELPER** for TASKS-TEMPLATE.md.
> - **Authority**: `TASKS-TEMPLATE.md` is the single source of truth for TASKS structure
> - **Validation**: Use `TASKS_VALIDATION_RULES.md` after TASKS creation/changes

# TASKS Creation Rules

Rules for creating AI Tasks (TASKS) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

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

### Format

```
TASKS-NNN_{descriptive_component}_tasks.md
```

### Rules

1. **TASKS-NNN**: Sequential numbering starting from 001
2. **descriptive_component**: Lowercase with underscores
3. **_tasks**: Required suffix
4. **Extension**: Always `.md`

### Examples

- `TASKS-001_service_connector_tasks.md`
- `TASKS-002_data_integration_tasks.md`
- `TASKS-003_request_execution_service_tasks.md`

---

## 3. Required Sections

### 3.1 Frontmatter

```yaml
---
title: "TASKS-NNN: [Component Name] Implementation Tasks"
tags:
  - tasks-document
  - layer-11-artifact
  - code-generation
custom_fields:
  document_type: tasks
  artifact_type: TASKS
  layer: 11
  parent_spec: SPEC-NNN
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| TASKS ID | Yes | TASKS-NNN format |
| Title | Yes | Descriptive task name |
| Status | Yes | Draft/Ready/In Progress/Completed |
| Version | Yes | Semantic version (X.Y.Z) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Parent SPEC | Yes | SPEC-NNN reference |
| Complexity | Yes | 1-5 scale |

### 3.3 Mandatory Sections

| Section | Purpose |
|---------|---------|
| 1. Scope | Define implementation boundaries |
| 2. Plan | Numbered implementation steps |
| 3. Constraints | Technical and development limitations |
| 4. Acceptance | Verification requirements |
| 5. Dependencies | Upstream/downstream artifacts |
| 6. Traceability Tags | Links to all upstream artifacts |
| 7. File Structure | Output file organization |
| 8. Implementation Contracts | ICON integration (mandatory) |

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
- Data subscription (TASKS-002)
- Request execution (TASKS-003)
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
   - Create `src/services/models.py` (SPEC-001:15-45)
   - Create `src/services/errors.py` (SPEC-001:47-82)

2. **Implement connection protocol** (4 hours)
   - Create `src/services/connector.py`
   - Implement `ServiceConnector` protocol (SPEC-001:84-120)
   - Add type hints per SPEC-001:122-135

3. **Add retry handler** (3 hours)
   - Create `src/services/retry.py`
   - Implement exponential backoff (SPEC-001:137-165)
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
- **Interface**: Match SPEC-001 exactly, no additions
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

- [ ] All BDD scenarios in BDD-001 pass
- [ ] Unit test coverage ≥85%
- [ ] Integration test coverage ≥75%
- [ ] mypy type checking passes (--strict)
- [ ] p95 latency < 50ms (benchmark tests)
- [ ] All traceability links valid
- [ ] Code review approved
```

---

## 8. Implementation Contracts Section (MANDATORY)

### Section 8 Requirements

Every TASKS document MUST include "## 8. Implementation Contracts":

```markdown
## 8. Implementation Contracts

### 8.1 Contracts Provided (if provider)

@icon: ICON-001:ContractName
@icon-role: provider

This TASKS implements the following contract:
- [ICON-001](../ICON/ICON-001.md): [Contract description]

### 8.2 Contracts Consumed (if consumer)

@icon: ICON-001:ContractName
@icon-role: consumer

This TASKS depends on:
- [ICON-001](../ICON/ICON-001.md): [Usage description]

### 8.3 No Contracts (if neither)

No implementation contracts for this TASKS.
```

### Validation

```bash
# Section 8 must exist
grep -q "## 8. Implementation Contracts" TASKS-NNN.md
```

---

## 9. Traceability Tag Requirements

### Required Tags (Layer 11)

```markdown
## Traceability Tags

@brd: BRD.001.NNN
@prd: PRD.001.NNN
@ears: EARS.001.NNN
@bdd: BDD.001.NNN
@adr: ADR-NNN
@sys: SYS.001.NNN
@req: REQ.NN.EE.SS
@spec: SPEC-NNN
```

### Optional Tags

```markdown
@impl: IMPL.NN.EE.SS (if project uses IMPL)
@ctr: CTR-NNN (if contracts defined)
@icon: ICON-NNN:ContractName (if implementation contracts)
```

---

## 10. Quality Checklist

### Before Creating

- [ ] SPEC document exists and is approved
- [ ] REQ documents are complete
- [ ] BDD scenarios are defined
- [ ] Architecture decisions (ADR) documented

### During Creation

- [ ] Use TASKS-TEMPLATE.md as starting point
- [ ] Follow all section rules above
- [ ] Include specific SPEC line references
- [ ] Define measurable acceptance criteria
- [ ] Include Section 8 (Implementation Contracts)

### After Creation

- [ ] All traceability tags valid
- [ ] Links resolve to existing documents
- [ ] Update TASKS-000_index.md
- [ ] Run validation script
- [ ] Notify downstream IPLAN creators

---

## 11. Common Anti-Patterns

### Avoid

1. **Vague scope** - Be specific about boundaries
2. **Generic steps** - Each step should be actionable
3. **Missing SPEC references** - Always link to SPEC lines
4. **No acceptance criteria** - Must be verifiable
5. **Missing Section 8** - ALWAYS include contracts section
6. **Orphaned contracts** - ICON references must exist

---

## 12. Validation

### Automated Validation

```bash
./scripts/validate_tasks.sh /path/to/TASKS-NNN_name.md
```

### Manual Checklist

- [ ] Filename follows convention
- [ ] All 8 required sections present
- [ ] Traceability tags complete
- [ ] Section 8 Implementation Contracts included
- [ ] SPEC references valid
- [ ] BDD scenario links valid

---

## 13. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
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
| Related | TASKS-NNN | [Related TASKS title] | Shared implementation context |
| Depends | TASKS-NNN | [Prerequisite TASKS title] | Must complete before this |

**Tags**:
```markdown
@related-tasks: TASKS-NNN
@depends-tasks: TASKS-NNN
```


## References

- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - Tasks template
- [TASKS-000_index.md](./TASKS-000_index.md) - Tasks registry
- [README.md](./README.md) - Directory overview
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](./IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contracts guide
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27

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
python scripts/validate_cross_document.py --document docs/TASKS/TASKS-NNN_slug.md --auto-fix

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
| Invalid tag format | Correct to TYPE.NN.EE.SS or TYPE-NNN format |
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

**Blocking**: YES - Cannot proceed to IPLAN creation until Phase 1 validation passes with 0 errors.
