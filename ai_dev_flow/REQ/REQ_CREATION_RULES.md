# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of REQ-TEMPLATE.md
# - Authority: REQ-TEMPLATE.md is the single source of truth for REQ structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to REQ-TEMPLATE.md
# =============================================================================
---
title: "REQ Creation Rules"
tags:
  - creation-rules
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: REQ
  layer: 7
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for REQ-TEMPLATE.md.
> - **Authority**: `REQ-TEMPLATE.md` is the single source of truth for REQ structure
> - **Validation**: Use `REQ_VALIDATION_RULES.md` after REQ creation/changes

# REQ Creation Rules

## Index-Only Generation Workflow

- Maintain `REQ-00_index.md` as the authoritative source of planned and active REQ files (mark planned items with Status: Planned).
- Generators use: `REQ-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 3.2
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Extracted from REQ-TEMPLATE.md, REQ_VALIDATION_RULES.md, README.md, and REQ-00_index.md
**Purpose**: Complete reference for creating REQ files according to doc-flow SDD framework
**Changes**: Added Threshold Registry Integration section (v3.2). Previous: Status/Score mapping, common mistakes section (v3.1)

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (12 Required sections)](#2-document-structure-12-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Atomic Requirement Principles](#5-atomic-requirement-principles)
6. [Traceability Requirements](#6-traceability-requirements)
7. [Interface and Implementation Specifications](#7-interface-and-implementation-specifications)
8. [Acceptance Criteria Standards](#8-acceptance-criteria-standards)
9. [Quality Gates](#9-quality-gates)
10. [Business Rules and Validation](#10-business-rules-and-validation)
11. [Additional Requirements](#11-additional-requirements)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Threshold Registry Integration](#14-threshold-registry-integration)

---

## 1. File Organization and Directory Structure

- Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.
- **Location**: `REQ/{domain}/{subdomain}/` within project docs directory
- **Domains**: `api/` (external integrations), `risk/` (risk management), `data/` (data requirements), `ml/` (ML requirements), `auth/` (security), etc.
- **Naming**: `REQ-NN_descriptive_slug.md` (NN = 3-digit sequential number, lowercase snake_case slug)
- **Section Files**: For large requirements (>50KB), use Section Files format: `REQ-NN.S_section_title.md` (S = section number). See `ID_NAMING_STANDARDS.md` for metadata tags.

---

## 2. Document Structure (12 Required sections)

Every REQ must contain these exact sections in order:

1. **Document Control** - Metadata table with 11 required fields
2. **Description** - Atomic requirement + SHALL/SHOULD/MAY language + context + scenario
3. **Functional Requirements** - Core capabilities + business rules
4. **Interface Specifications** - Protocol/ABC definitions + DTOs + REST endpoints (if applicable)
5. **Data Schemas** - JSON Schema + Pydantic models + Database schema (if applicable)
6. **Error Handling Specifications** - Exception catalog + error response schema + state machine + circuit breaker config
7. **Configuration Specifications** - YAML schema + environment variables + validation
8. **Quality Attributes** - Performance targets (p50/p95/p99) + reliability/security/scalability/observability
9. **Implementation Guidance** - Algorithms/patterns + concurrency/async + dependency injection
10. **Acceptance Criteria** - ≥15 measurable criteria covering functional/error/quality/data/integration
11. **Verification Methods** - BDD scenarios + unit/integration/contract/performance tests
12. **Change History** - Version control table

---

## 3. Document Control Requirements (11 Mandatory Fields)

- Status, Version (semantic X.Y.Z), Date Created (ISO 8601), Last Updated
- Author, Priority (with P-level: P1/P2/P3/P4), Category (Functional/Security/Performance/etc.)
- Source Document (format: "DOC-ID section X.Y.Z"), Verification Method, Assigned Team
- SPEC-Ready Score (format: "✅ XX% (Target: ≥90%)"), IMPL-Ready Score (format: "✅ XX% (Target: ≥90%)"), Template Version (must be "3.0")

### Status and Ready Score Mapping

| Ready Score | Required Status |
|-------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

**Note**: For REQ documents with dual scores (SPEC-Ready + IMPL-Ready), use the lower score to determine status.

---

## 4. ID and Naming Standards

- **Filename**: `REQ-NN_slug.md` (e.g., `REQ-03_resource_limit_enforcement.md`)
- **H1 Header**: `# REQ-NN: [RESOURCE_INSTANCE] Title` (Template V2+) - includes resource classification tag
- **Template Version**: Must use 3.0 (current) - not legacy V1 or V2
- **Uniqueness**: Each NN number used once (either single REQ-NN or REQ-NN.S section group)

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `REQ.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | REQ.02.01.01 |
| Dependency | 05 | REQ.02.05.01 |
| **Acceptance Criteria** | **06** | **REQ.02.06.01** |
| Atomic Requirement | 27 | REQ.02.27.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `AC-XXX` → Use `REQ.NN.06.SS`
> - `FR-XXX` → Use `REQ.NN.01.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 5. Atomic Requirement Principles

- **Single Responsibility**: Each REQ defines exactly one requirement
- **Measurable**: Acceptance criteria provide true/false outcomes
- **Self-Contained**: Understandable without external context
- **SPEC-Ready**: Contains ALL information for automated SPEC generation (≥90% completeness)
- **Modal Language**: SHALL (absolute), SHOULD (preferred), MAY (optional)

---

## 6. Traceability Requirements (MANDATORY - Layer 7)

- **Upstream Chain**: Must reference ALL 6 artifact types: BRD, PRD, EARS, BDD, ADR, SYS
- **Cumulative Tagging**: All 6 tags required with format `@type: DOC-ID:NN` (numeric sub-IDs)
- **Downstream Links**: SPEC, TASKS, CTR (if applicable), BDD scenarios
- **Code Paths**: Actual file paths for implementation

---

## 7. Interface and Implementation Specifications

- **Protocol/ABC**: Complete class definitions with type annotations
- **DTOs**: Data transfer objects with validation
- **REST Endpoints**: Rate limits, schemas for request/response (if applicable)
- **Error Handling**: Catalog with retry strategies, state diagrams, circuit breaker
- **Schemas**: JSON Schema + Pydantic validators + Database constraints
- **Configuration**: YAML examples + environment variables + validation
- **Quality Attribute Metrics**: Performance (p50/p95/p99), reliability, security, scalability targets

---

## 8. Acceptance Criteria Standards

- **≥15 Criteria**: Covering functional, error, edge case, quality, data, integration scenarios
- **Measurable**: Specific thresholds, pass criteria, verification methods
- **Testable**: BDD scenarios, unit/integration tests, performance benchmarks
- **Comprehensive**: Success paths, failure modes, resource limits, error recovery

---

## 9. Quality Gates (Pre-Commit Validation)

- **18 Validation Checks**: Run `./scripts/validate_req_template.sh filename.md`
- **Blockers**: Missing sections, format errors, broken links, incomplete traceability
- **Warnings**: Missing resource tags, low SPEC-Ready score, incomplete upstream chain
- **SPEC-Ready Threshold**: ≥90% or reduce claimed score
- **Link Resolution**: All cross-references must resolve to existing files

---

## 10. Business Rules and Validation

- **Source Documents**: Link to specific strategy sections (BRD/PRD)
- **Original Context**: Describe why requirement exists and business justification
- **Verification Methods**: Unit/concept/integration/performance/contract tests
- **Error Recovery**: Dataclass configuration for circuit breakers and retry logic
- **Observability**: Metrics, logging, tracing, alerting requirements

---

## 11. Additional Requirements

- **Dependency Injection**: Container setup with providers for modular design
- **Database Integration**: SQLAlchemy models with constraints and migrations (if applicable)
- **Concurrent Patterns**: Async handling with semaphore and task management
- **security Requirements**: Authentication, data encryption, audit logging
- **Resource Tags**: Classify by component type (e.g., [EXTERNAL_SERVICE_GATEWAY])

---

## Quick Reference

**Pre-Commit Validation**:
```bash
# Validate single file
./scripts/validate_req_template.sh filename.md

# Validate all REQ files
find docs/REQ -name "REQ-*.md" -exec ./scripts/validate_req_template.sh {} \;
```

**Template Location**: [REQ-TEMPLATE.md](REQ-TEMPLATE.md)
**Validation Rules**: [REQ_VALIDATION_RULES.md](REQ_VALIDATION_RULES.md)
**Index**: [REQ-00_index.md](REQ-00_index.md)

---

**Framework Compliance**: 100% AI Dev Flow SDD framework aligned (Layer 7 - Requirements)
**Maintained By**: System Architect, Quality Assurance Team
**Review Frequency**: Updated with template and validation rule changes

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% SPEC-Ready score) | Match status to score threshold |
| Missing upstream tags (need all 6) | Include @brd, @prd, @ears, @bdd, @adr, @sys |
| <15 acceptance criteria | Minimum 15 covering functional/error/quality |
| Template Version != 3.0 | Update to current template version |
| Missing resource classification tag | Add [RESOURCE_INSTANCE] to H1 header |
| Incomplete traceability chain | All 6 upstream artifact types required |
| `response time < 200ms` (hardcoded) | `response time < @threshold: PRD.NN.perf.api.p95_latency` |
| `timeout: 5000` (magic number) | `timeout: @threshold: PRD.NN.timeout.default` |
| `retry_max: 3` (hardcoded config) | `retry_max: @threshold: PRD.NN.retry.max_attempts` |

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

Include ONLY if relationships exist between REQ documents sharing domain context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | REQ-NN | [Related REQ title] | Shared domain context |
| Depends | REQ-NN | [Prerequisite REQ title] | Must complete before this |

**Tags**:
```markdown
@related-req: REQ-NN
@depends-req: REQ-NN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values that are:
- Business-critical (compliance limits, SLAs)
- Configurable (timeout values, rate limits, retry policies)
- Shared across documents (performance targets)
- Quality attribute-related (p50/p95/p99 latencies, throughput limits)
- Error handling configurations (circuit breaker, retry counts)

### @threshold Tag Format

```markdown
@threshold: PRD.NN.category.subcategory.key
```

**Examples**:
- `@threshold: PRD.035.perf.api.p95_latency`
- `@threshold: PRD.035.timeout.circuit_breaker.threshold`
- `@threshold: PRD.035.retry.max_attempts`
- `@threshold: PRD.035.limit.api.requests_per_second`

### REQ-Specific Threshold Categories

| Category | REQ Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | Performance acceptance criteria | `perf.api.p95_latency` |
| `timeout.*` | Circuit breaker, connection configs | `timeout.circuit_breaker.reset` |
| `retry.*` | Retry policy configurations | `retry.max_attempts` |
| `limit.*` | Rate limits, resource limits | `limit.api.requests_per_second` |
| `resource.*` | Memory, CPU constraints | `resource.memory.max_heap` |

### Magic Number Detection

**Invalid (hardcoded values)**:
- `p95 response time: 200ms`
- `max_retries: 3`
- `rate_limit: 100 req/s`
- `circuit_breaker_threshold: 5`

**Valid (registry references)**:
- `p95 response time: @threshold: PRD.NN.perf.api.p95_latency`
- `max_retries: @threshold: PRD.NN.retry.max_attempts`
- `rate_limit: @threshold: PRD.NN.limit.api.requests_per_second`
- `circuit_breaker_threshold: @threshold: PRD.NN.timeout.circuit_breaker.threshold`

### Traceability Requirements Update

Add `@threshold` to Required Tags table in Traceability section:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NN:category.key | When referencing quality attributes, timing, limits, retry configs, or configurable values |

### Acceptance Criteria Integration

Acceptance criteria containing quantitative values MUST use threshold references:

**Invalid**:
```markdown
REQ.NN.06.01: Response time SHALL be < 200ms for 95th percentile
```

**Valid**:
```markdown
REQ.NN.06.01: Response time SHALL be < @threshold: PRD.NN.perf.api.p95_latency for 95th percentile
```

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in quality attribute sections
2. No hardcoded values in acceptance criteria
3. All `@threshold` references resolve to valid registry keys
4. All configuration values use threshold references

---

## 15. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any REQ document. Do NOT proceed to downstream artifacts until validation passes.

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
python scripts/validate_cross_document.py --document docs/REQ/REQ-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all REQ documents complete
python scripts/validate_cross_document.py --layer REQ --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| REQ (Layer 7) | @brd, @prd, @ears, @bdd, @adr, @sys | 6 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd/@adr/@sys tag | Add with upstream document reference |
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

**Blocking**: YES - Cannot proceed to IMPL/SPEC creation until Phase 1 validation passes with 0 errors.
