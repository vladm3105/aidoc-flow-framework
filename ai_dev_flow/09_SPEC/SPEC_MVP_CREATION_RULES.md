---
title: "SPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: SPEC
  layer: 9
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for SPEC-MVP-TEMPLATE.yaml (MVP profile).
> - **Authority**: `SPEC-MVP-TEMPLATE.yaml` (MVP profile) is the primary source of truth for SPEC structure; use the full profile only when explicitly requested
> - **Validation**: Use `SPEC_VALIDATION_RULES.md` after SPEC creation/changes

# SPEC Creation Rules

## Index-Only Generation Workflow

- Maintain `SPEC-00_index.md` as the authoritative source of planned and active SPEC files (mark planned items with Status: Planned).
- Generators use: `SPEC-00_index.md` + selected template profile (`SPEC-MVP-TEMPLATE.yaml` as MVP default; full profile only when explicitly requested).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.3
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Derived from SPEC-MVP-TEMPLATE.yaml and technical specification patterns
**Purpose**: Complete reference for creating SPEC YAML files according to AI Dev Flow SDD framework
**Changes**: v1.3: Added file size limits as warning, removed document splitting requirement. v1.2: Added Threshold Registry Integration section. v1.1: Status/Score mapping, common mistakes section

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (YAML Specification)](#2-document-structure-yaml-specification)
3. [Document Control and Metadata](#3-document-control-and-metadata)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Technical Specification Categories](#5-technical-specification-categories)
6. [TASKS Relationship Guidelines](#6-tasks-relationship-guidelines)
7. [TASKS-Ready Scoring System](#7-tasks-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Threshold Registry Integration](#14-threshold-registry-integration)

---

## 1. File Organization and Directory Structure

- Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → "Using This Repo" for path mapping.
- **Location**: `docs/09_SPEC/` within project docs directory
- **Naming**: `SPEC-{DOC_NUM}_{descriptive_component_name}.yaml` (DOC_NUM = variable-length, starts at 2 digits)
- **Structure**: One monolithic YAML file per architectural component (codegen source)
- **File Size Limits** (Warning):
  - Markdown: Target 300-500 lines, warning at 600 lines
  - YAML: Warning at 1000 lines

---

## 2. Document Structure (YAML Specification)

**Complete YAML structure with 7 major sections (kept in a single YAML file):**

```yaml
# Header section with required metadata
id: component_name
summary: Single-sentence description

# Metadata with TASKS-ready scoring
metadata:
  version: "1.0.0"
  status: "draft"
  task_ready_score: ✅ 95% (Target: ≥90%)  # Added for quality gates

# Complete traceability chain
traceability:
  upstream_sources: [...]
  downstream_artifacts: [...]
  cumulative_tags: [...]  # Include @threshold registry tag and use null only when an upstream type truly does not exist

# Threshold registry references (required when using @threshold)
threshold_references:
  registry_document: "PRD-NN"
  keys_used:
    - perf.api.p95_latency
    - timeout.request.sync

# Architecture definition
architecture: [...]

# Interface definitions (CTR references)
interfaces: [...]

# Behavioral specifications
behavior: [...]

# Quality attributes (caching, rate limiting, circuit breaker)
# Performance specifications
performance: [...]

# security specifications
security: [...]

# Observability specifications
observability: [...]

# Verification and validation
verification: [...]

# Implementation specifics
implementation: [...]

# Operational runbook
operations: [...]
```

---

## 3. Document Control and Metadata

**Required Metadata Fields**:
- version, status, created_date, authors, reviewers
- TASKS-ready score (⭐ NEW) format: `✅ NN% (Target: ≥90%)`

### Status and TASKS-Ready Score Mapping

| TASKS-Ready Score | Required Status |
|-------------------|-----------------|
| >= 90% | approved |
| 70-89% | in_review |
| < 70% | draft |

**Authors and Reviewers**:
- authors: Technical implementers
- reviewers: Architecture leads, senior engineers

---

## 4. ID and Naming Standards

- **Filename**: `SPEC-NN_descriptive_component_name.yaml`
- **id field**: `component_name` (snake_case, unique)
- **Versioning**: Semantic versioning (1.0.0)

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `SPEC.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Step | 15 | SPEC.02.15.01 |
| Interface | 16 | SPEC.02.16.01 |
| Data Model | 17 | SPEC.02.17.01 |
| Validation Rule | 21 | SPEC.02.21.01 |
| Specification Element | 28 | SPEC.02.28.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use legacy formats like `STEP-XXX`, `INT-XXX`.
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 5. Technical Specification Categories

**Component Types**:
- **API Services**: REST, GraphQL interfaces
- **Data Processors**: ETL, stream processing
- **Integration Adapters**: Third-party service connectors
- **Supporting Services**: Caching, messaging, configuration

**Specification Categories**:
- **Functional Specs**: Request/response workflows
- **Performance Specs**: Latency, throughput targets
- **security Specs**: Authentication, authorization
- **Operational Specs**: Monitoring, deployment, scaling

---

## 6. TASKS Relationship Guidelines

**SPEC → TASKS Workflow**:
- SPECs define technical HOW (implementation blueprints)
- TASKS provide AI-assisted coding instructions using SPEC definitions
- Code generation tools consume SPEC YAML directly

**TASKS Implementation Requirements**:
- All SPEC sections must be translatable to TASKS tasks
- Interface definitions must enable API contract generation
- Behavior sections must enable method implementation planning

---

## 7. TASKS-Ready Scoring System ⭐ NEW

### Overview
TASKS-ready scoring measures SPEC maturity and readiness for progression to TASKS implementation planning.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: metadata.task_ready_score field
**Validation**: Enforced before TASKS creation

### Scoring Criteria

**YAML Completeness (25%)**:
- All required metadata fields present: 10%
- Complete traceability chain defined: 10%
- All specification sections populated: 5%

**Interface Definitions (25%)**:
- External APIs fully specified with contracts: 15%
- Internal interfaces documented: 5%
- Data schemas and types defined: 5%

**Implementation Specifications (25%)**:
- Behavior sections enable code generation: 15%
- Performance/security targets quantifiable: 5%
- Dependencies and configuration specified: 5%

**Code Generation Readiness (25%)**:
- All fields machine-readable and parseable: 15%
- TASKS-ready tags and metadata included: 5%
- Validation schemas complete: 5%

### Quality Gate Enforcement
- Score <90% prevents TASKS artifact creation
- Format validation requires ✅ emoji and percentage
- YAML syntax must be valid for TASKS parsing

---

## 8. Traceability Requirements (MANDATORY - Layer 9)

**Complete Upstream Tag Chain**:
```yaml
cumulative_tags:
  brd: "BRD.NN.EE.SS"         # Unified dot notation for sub-ID references (use null only if the artifact type does not exist)
  prd: "PRD.NN.EE.SS"         # Unified dot notation for sub-ID references (use null only if the artifact type does not exist)
  ears: "EARS.NN.EE.SS"       # Unified dot notation (use null only if the artifact type does not exist)
  bdd: "BDD.NN.EE.SS"         # Unified dot notation for sub-ID references (use null only if the artifact type does not exist)
  adr: "ADR-NN"             # Document-level reference (no sub-ID, use null only if the artifact type does not exist)
  sys: "SYS.NN.EE.SS"         # Unified dot notation for sub-ID references (use null only if the artifact type does not exist)
  req: "REQ.NN.EE.SS"         # Unified dot notation for sub-ID references (use null only if the artifact type does not exist)
  threshold: "PRD-NN"         # Threshold registry document reference (use null only if thresholds are not applicable)
```

**Layer 9 Requirements**: SPEC must reference ALL previous artifacts or explicitly mark `null` when genuinely absent

---

## 9. Quality Attributes

**Machine-Readable**: All specifications parseable by code generation tools

**Implementation-Complete**: Sufficient detail for autonomous development

**Interface-First**: API contracts separated but referenced

**Test-Driving**: Specifications enable comprehensive testing strategies

---

## 10. Quality Gates (Pre-Commit Validation)

- YAML syntax validation
- TASKS-ready score verification ≥90%
- Traceability completeness
- Interface contract references validation

---

## 11. Additional Requirements

- Contract separation: CTR files for interface specifications
- Implementation-path metadata for code generation
- Configuration schemas for deployment automation
- Performance benchmarks for operational monitoring

---

**Framework Compliance**: 100% AI Dev Flow SDD framework (Layer 9)
**Integration**: Enforces SPEC → TASKS progression quality gates

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `status: approved` (with <90% TASKS-Ready score) | Match status to score threshold |
| Invalid YAML syntax | Validate with YAML linter before commit |
| Missing traceability.cumulative_tags | Include all upstream artifact tags |
| Hardcoded values in behavior | Use configuration references |
| Missing interface CTR references | Create CTR for external API specifications |
| Incomplete performance specifications | Include latency/throughput/error rate targets |
| `latency_ms: 200` (hardcoded) | `latency_ms: "@threshold: PRD.NN.perf.api.p95_latency"` |
| **Split List Syntax** (e.g., `tests:` under `- path:`) | **Use nested structure**: `tests:` as a child key of the list item |
| Missing `security` or `observability` | **Mandatory**: Include `authentication` (method specified) and `health_checks` (endpoints specified) |

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
| @brd | Yes/No | BRD-NN or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-NN or null | Reference/Create/Skip |
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

Include ONLY if relationships exist between SPEC documents sharing implementation context or technical dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | SPEC-NN | [Related SPEC title] | Shared implementation context |
| Depends | SPEC-NN | [Prerequisite SPEC title] | Must complete before this |

**Tags**:
```markdown
@related-spec: SPEC-NN
@depends-spec: SPEC-NN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values in SPEC YAML that are:
- Performance configurations (latencies, throughput, IOPS)
- Timeout configurations (connection, read, write timeouts)
- Rate limiting values (requests per second, burst limits)
- Resource limits (memory, CPU, storage)
- Circuit breaker configurations

### @threshold Tag Format in YAML

```yaml
# String value format
performance:
  p95_latency_ms: "@threshold: PRD.NN.perf.api.p95_latency"

# Comment format for documentation
timeout:
  request_ms: 5000  # @threshold: PRD.NN.timeout.request.sync
```

**Examples**:
- `"@threshold: PRD.035.perf.api.p95_latency"`
- `"@threshold: PRD.035.timeout.circuit_breaker.threshold"`
- `"@threshold: PRD.035.limit.api.requests_per_second"`

### SPEC-Specific Threshold Categories

| Category | SPEC Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | Performance specifications | `perf.api.p95_latency` |
| `timeout.*` | Connection, request timeouts | `timeout.request.sync` |
| `limit.*` | Rate limits, connection pools | `limit.api.requests_per_second` |
| `resource.*` | Memory, CPU, storage limits | `resource.memory.max_heap` |
| `retry.*` | Retry configurations | `retry.max_attempts` |

### Magic Number Detection

**Invalid (hardcoded values)**:
```yaml
performance:
  p95_latency_ms: 200
timeout:
  request_ms: 5000
rate_limit:
  requests_per_second: 100
```

**Valid (registry references)**:
```yaml
performance:
  p95_latency_ms: "@threshold: PRD.NN.perf.api.p95_latency"
timeout:
  request_ms: "@threshold: PRD.NN.timeout.request.sync"
rate_limit:
  requests_per_second: "@threshold: PRD.NN.limit.api.requests_per_second"
```

### Traceability Integration

Add `threshold` to cumulative_tags section:

```yaml
traceability:
  cumulative_tags:
    brd: "BRD.NN.EE.SS"
    prd: "PRD.NN.EE.SS"
    threshold: "PRD-NN"  # Registry document reference
```

### threshold_references Section

Add dedicated section for threshold dependencies:

```yaml
threshold_references:
  registry_document: "PRD-NN"
  keys_used:
    - perf.api.p95_latency
    - timeout.request.sync
    - limit.api.requests_per_second
    - retry.max_attempts
```

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in performance sections
2. No hardcoded values in timeout configurations
3. All `@threshold` references resolve to valid registry keys
4. All rate limits and resource constraints use threshold references

---

## 15. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any SPEC document. Do NOT proceed to downstream artifacts until validation passes.

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
python scripts/validate_cross_document.py --document docs/09_SPEC/SPEC-NN_slug/SPEC-NN_slug.yaml --auto-fix

# Layer validation (Phase 2) - run when all SPEC documents complete
python scripts/validate_cross_document.py --layer SPEC --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| SPEC (Layer 9) | @brd through @req (+ optional @ctr) | 7-8 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd through @req tag | Add with upstream document reference |
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

**Blocking**: YES - Cannot proceed to TASKS creation until Phase 1 validation passes with 0 errors.
