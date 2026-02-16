---
title: "REQ MVP Creation Rules"
tags:
  - creation-rules
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: REQ
  layer: 7
  complexity: 1
  priority: shared
  development_status: active
---

# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of REQ-MVP-TEMPLATE.md
# - Authority: REQ-MVP-TEMPLATE.md is the single source of truth for REQ structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to REQ-MVP-TEMPLATE.md
# =============================================================================


**📋 Document Role**: This is a **CREATION HELPER** for REQ-MVP-TEMPLATE.md.
- **Authority**: `REQ-MVP-TEMPLATE.md` is the single source of truth for REQ structure
- **Validation**: Use `REQ_MVP_VALIDATION_RULES.md` after REQ creation/changes
- **Consistency Note**: All MVP artifacts (creation rules, validation rules, quality gates, schema) MUST stay consistent with `REQ-MVP-TEMPLATE.md` and `REQ-MVP-TEMPLATE.yaml`; keep changes synchronized.

# REQ MVP Creation Rules

## Template Selection (MVP Default)

**MVP templates are the framework default.**

| Template | File | When to Use |
|----------|------|-------------|
| **MVP (DEFAULT)** | `REQ-MVP-TEMPLATE.md` | All REQs |

## Index-Only Generation Workflow

- Maintain `REQ-00_index.md` as the authoritative source of planned and active REQ files (mark planned items with Status: Planned).
- Generators use: `REQ-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 3.2
**Date**: 2025-11-19T00:00:00
**Last Updated**: 2025-11-30T00:00:00
**Source**: Extracted from REQ-MVP-TEMPLATE.md, REQ_MVP_VALIDATION_RULES.md, README.md, and REQ-00_index.md
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
- **Location**: `07_REQ/REQ-{PRD_ID}_{Slug}/` (Vertical Slice Grouping)
- **Organization**: Group REQs by their parent PRD to maintain vertical alignment.
- **Naming**: `REQ-{DOC_NUM}_{slug}.md` (Sequential 01-401)
- **Example**: `07_REQ/REQ-01_iam/REQ-01_jwt_auth.md` (where REQ-01 maps to PRD-01)

### 1.1 Domain Classification (Metadata-Based - AI-Friendly Flat Structure)

REQ documents are classified by **functional domain** through metadata to support vertical slice organization while maintaining a flat, AI-friendly file structure.

**Recommended Pattern: Flat Structure with Metadata**
```
07_REQ/
├── REQ-01_jwt_authentication.md         # domain: auth (in metadata)
├── REQ-02_token_refresh_mechanism.md    # domain: auth (in metadata)
├── REQ-03_api_gateway_routing.md        # domain: api (in metadata)
├── REQ-04_order_execution_logic.md      # domain: trading (in metadata)
├── REQ-05_data_persistence_schema.md    # domain: data (in metadata)
└── ... [flat structure, no subfolders]
```

**Why Flat Structure**:
- ✅ **AI-Friendly**: Easier for language models to navigate and process
- ✅ **Scalable**: No folder hierarchy management overhead
- ✅ **Flexible**: Domain classification via metadata, not folder structure
- ✅ **Simple**: Clear, flat organization that's intuitive to all tools
- ✅ **Searchable**: Single directory for quick file discovery

**Domain Definition**: Domain should be **derived from the document's primary functional scope**. Examples:
- `auth` - Authentication, authorization, identity management
- `api` - API gateways, HTTP routing, REST contract
- `trading` - Trading logic, order execution, market data
- `data` - Data persistence, schemas, database operations
- `risk` - Risk management, compliance validation, monitoring
- `core` - Core business logic, computation, algorithms
- `collection` - Data collection, aggregation, ingestion
- `compliance` - Regulatory requirements, audit trails
- `ml` - Machine learning models, inference, training
- Other custom domains based on your project structure

**Validation**: GATE-13 validator checks domain classification by:
1. Reading `domain:` field from frontmatter YAML metadata (primary source)
2. Validating that domain is a valid identifier (lowercase alphanumeric + underscores)

**Usage in Frontmatter**:
```yaml
---
title: "REQ-01: JWT Authentication"
tags:
  - req-document
  - layer-7-artifact
custom_fields:
  document_type: req
  artifact_type: REQ
  domain: auth          # ← Define based on requirement's primary domain
  layer: 7
  # ... other fields
---
```

---

## 2. Document Structure (11 Required sections — MVP)

Every REQ must contain these exact sections in order (MVP profile):

1. **Document Control** - Metadata table with required fields
2. **Requirement Description** - Atomic requirement + SHALL/SHOULD/MAY language + context + scenario
3. **Functional Specification** - Core capabilities + business rules + I/O
4. **Interface Definition** - API contract + schemas/DTOs
5. **Error Handling** - Exception catalog + recovery strategies
6. **Quality Attributes** - Performance/security/reliability targets using @threshold
7. **Configuration** - Parameters, feature flags, validation
8. **Testing Requirements** - **Logical TDD (Pre-Code)**, Unit, Integration, and BDD scenarios
  - **8.1 Logical Unit test **: Define WHAT to test before HOW (drives SPEC interface design)
  - Format: `| Test Case | Input | Expected Output | Coverage |`
  - Min 3 entries with prefixes: `[Logic]`, `[State]`, `[Validation]`, `[Edge]`
9. **Acceptance Criteria** - ≥3 measurable criteria (MVP) with IDs `REQ.NN.06.SS`
10. **Traceability** - Upstream chain, downstream artifacts, cumulative tags
11. **Implementation Notes** - Technical approach, code locations, dependencies

> **Note**: Deployment requirements and Change History are omitted in the MVP structure to keep a lean 11-section flow. Deployment concerns live in SYS-NN documents.

---

## 3. Document Control Requirements (12 Mandatory Fields)

- Status, Version (semantic X.Y.Z), Date Created (ISO 8601), Last Updated
- Author, Priority (with P-level: P1/P2/P3/P4), Category (Functional/Security/Performance/Reliability/Scalability/Compliance)
- Infrastructure Type (Compute/Database/Storage/Network/Deployment/None)
- Source Document (format: "DOC-ID section X.Y.Z"), Verification Method, Assigned Team
- SPEC-Ready Score (format: "✅ XX% (Target: ≥90%)")

**Optional (not validated):** CTR-Ready Score, Template Version

> **Note**: Template Version is informational only (not validated). Each template may use its own version numbering.

### Status and Ready Score Mapping (MVP)

| Ready Score | Required Status |
|-------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

**Note**: If CTR-Ready Score is present, use the lower score of SPEC/CTR when assigning status.

---

## 4. ID and Naming Standards

- **Filename**: `REQ-NN_slug.md` (e.g., `REQ-03_resource_limit_enforcement.md`)
- **H1 Header**: `# REQ-NN: [RESOURCE_INSTANCE] Title` (Template V2+) - includes resource classification tag
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
- **Downstream Links**: SPEC, TASKS, CTR, BDD scenarios, and generated artifacts
- **Generated Artifact Tags**: `@deployment`, `@ansible`, `@iac`, `@config_file_type`, `@source_code`
- **Code Paths**: Actual file paths for implementation

---

## 7. Interface and Implementation Specifications

- **Protocol/ABC (REQUIRED)**: Complete class definitions with type annotations (Section 3.4)
- **DTOs**: Data transfer objects with validation
- **REST Endpoints**: Rate limits, schemas for request/response (if applicable)
- **Error Handling**: Catalog with retry strategies, state diagrams, circuit breaker
- **Exceptions (REQUIRED)**: Custom Python Exception classes (Section 5.3)
- **Schemas**: JSON Schema + Pydantic validators + Database constraints
- **Configuration (REQUIRED)**: YAML schema + environment variables + validation (Section 7.3)
- **Quality Attribute Metrics**: Performance (p50/p95/p99), reliability, security, scalability targets

---

## 8. Acceptance Criteria Standards

- **≥15 Criteria**: Covering functional, error, edge case, quality, data, integration scenarios
- **Measurable**: Specific thresholds, pass criteria, verification methods
- **Testable**: BDD scenarios, unit/integration tests, performance benchmarks
- **Comprehensive**: Success paths, failure modes, resource limits, error recovery

---

## 9. Quality Gates (Pre-Commit Validation)

- **20 Validation Checks**: Run `./07_REQ/scripts/validate_req_template.sh filename.md`
- **Blockers**: Missing sections, format errors, broken links, incomplete traceability
- **Warnings**: Missing resource tags, low SPEC-Ready score, incomplete upstream chain
- **SPEC-Ready Threshold**: ≥90% for MVP profile (adjust claimed score if lower)
- **Link Resolution**: All cross-references must resolve to existing files

---

## 9.1 Cross-Linking Tags (AI-Friendly)

**Purpose**: Establish lightweight, machine-readable hints for AI discoverability and dependency tracing across REQ documents without blocking validation.

**Tags Supported**:
- `@depends: REQ-NN` — Hard prerequisite; this REQ cannot proceed without the referenced REQ
- `@discoverability: REQ-NN (short rationale)` — Related document for AI search and ranking (informational)

**ID Format**: Document-level IDs follow `{DOC_TYPE}-NN` per `ID_NAMING_STANDARDS.md` (e.g., `REQ-01`, `REQ-02`).

**Placement**: Add tags to the Traceability section or inline with requirement descriptions.

**Example**:
```markdown
@depends: REQ-01 (Core Requirements)
@discoverability: REQ-02 (Extended Requirements - shared specification domain)
```

**Validator Behavior**: Cross-linking tags are recognized and reported as **info-level** findings (non-blocking). They enable AI/LLM tools to infer relationships and improve search ranking without affecting document approval.

**Optional for MVP**: Cross-linking tags are optional in MVP templates and are not required for REQ approval; they are purely informational.

---


## 10. Business Rules and Validation

- **Source Documents**: Link to specific strategy sections (01_BRD/PRD)
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
./07_REQ/scripts/validate_req_template.sh filename.md

# Validate all REQ files
find docs/REQ -name "REQ-*.md" -exec ./07_REQ/scripts/validate_req_template.sh {} \;
```

**Template Location**: [REQ-MVP-TEMPLATE.md](REQ-MVP-TEMPLATE.md)
**Validation Rules**: [REQ_MVP_VALIDATION_RULES.md](REQ_MVP_VALIDATION_RULES.md)
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

Include ONLY if relationships exist between REQ documents sharing domain context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | REQ-NN | [Related REQ title] | Shared domain context |
| Depends | REQ-NN | [Prerequisite REQ title] | Must complete before this |

**Tags**:
```markdown
@depends: REQ-NN   # Hard prerequisite requirements
@discoverability: REQ-NN (short rationale); REQ-NN (short rationale)
```

- Use `@depends` for sequencing/blocking dependencies.
- Use `@discoverability` for related REQs with a one-phrase rationale (AI/search-friendly).
- Avoid legacy "See also" strings; prefer the structured tags above.

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
python scripts/validate_cross_document.py --document docs/07_REQ/REQ-NN_slug.md --auto-fix

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

**Blocking**: YES - Cannot proceed to 08_CTR/SPEC creation until Phase 1 validation passes with 0 errors.

## 15. REQ Generation Planning

When creating a **REQ Generation Plan** (e.g., `REQ_GENERATION_PLAN.md`), ensure the document includes the following to prevent common issues:

### 15.1 Required Frontmatter
Must include standard fields plus `complexity`:
```yaml
---
type: plan
project: [Project Name]
status: planning
date: YYYY-MM-DDTHH:MM:SS
complexity: [1-5]
---
```

### 15.2 Mandatory Sections
1. **Executive Summary**: Scope assessment and key findings.
2. **Prerequisites & Dependencies**: Upstream requirements (SYS/ADR), and templates.
3. **Risk Assessment**: Identify risks (e.g., schema deviation) and failure modes with mitigations.
4. **Phases**: Break down work into P0/P1/P2 phases.
   - **MUST Include**: Tasks with complexity ratings, Acceptance Criteria, Validation Steps, and Deliverables.
5. **Validation Commands**: Explicit commands to run for verification.

### 15.3 Common Pitfalls to Avoid
- **Count Mismatch**: Ensure summary counts match the task list items.
- **Missing Complexity**: Rate every task (1-5) and the overall document.
- **Vague Archives**: Clearly state how legacy/archive files are handled.
