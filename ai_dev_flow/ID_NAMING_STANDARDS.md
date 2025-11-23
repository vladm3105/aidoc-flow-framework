---
title: "Document ID & Tagging Standards"
tags:
  - framework-guide
  - shared-architecture
  - required-both-approaches
  - active
custom_fields:
  document_type: naming-standards
  priority: shared
  development_status: active
  applies_to: [all-artifacts, documentation]
  version: "1.0"
  scope: documentation-only
---

# Document ID & Tagging Standards — ai_dev_flow

Status: Authoritative for this `ai_dev_flow` example set. These rules reflect the naming and linking already used here and supersede repo-wide norms within this directory (do not change existing files to match other guides).

Purpose
- Provide a single, practical guide for IDs, tags, links, file layout, and validation within this example.
- Eliminate duplication while preserving mandatory rules and quick-reference tips.

## Scope Clarification: Documentation Only

**IMPORTANT**: This naming standard applies ONLY to Specification-Driven Development (SDD) **documentation artifacts**. It does NOT apply to source code files.

### ✅ Apply ID_NAMING_STANDARDS To:
- Documentation files in `docs/` directories:
  - `BRD/` - Business Requirements Documents
  - `PRD/` - Product Requirements Documents
  - `REQ/` - Requirements
  - `ADR/` - Architecture Decision Records
  - `SPEC/` - Technical Specifications (YAML)
  - `CTR/` - API Contracts (CTR)
  - `IMPL/` - Implementation Plans
  - `TASKS/` - AI Task Lists
  - `BDD/` - Feature files (`.feature` format only)
  - `EARS/` - EARS Requirements
  - `SYS/` - System Requirements

### ❌ Do NOT Apply ID_NAMING_STANDARDS To:
- **Python source code**: Follow PEP 8 naming conventions
  - Modules: `snake_case.py`
  - Classes: `PascalCase`
  - Functions/methods: `snake_case()`
  - Constants: `UPPER_SNAKE_CASE`
- **Python test files**: Follow pytest conventions
  - Test modules: `test_*.py` or `*_test.py`
  - Test functions: `test_*()`
  - Fixtures: `snake_case()`
- **Other source files**: Follow language-specific conventions
  - JavaScript/TypeScript: Per ESLint/TSLint rules
  - Java: Per Java naming conventions
  - Go: Per Go style guide

### Exception: BDD Feature Files
BDD test scenarios in `.feature` files (Gherkin format) located in `tests/bdd/` or similar directories **SHOULD** follow ID_NAMING_STANDARDS:

```
tests/bdd/gateway/BDD-001_connection_management.feature
tests/bdd/gateway/BDD-002_error_handling.feature
```

Scope & Authority
- Applies to: PRD, SYS, REQ, ADR, BDD, SPEC, EARS, CTR, IMPL, AI-TASKS in this example.
- One document per file.
- Filenames use sequential numeric prefixes for ordering; the full document IDs live in the H1 headings and tags.
- Categories are expressed by folder paths (e.g., `REQ/api/av`, `REQ/risk/lim`).
- All cross-references use markdown link format: `[ID](relative/path.md#ANCHOR)`.
- **Exception**: CTR (API Contracts) uses dual-file format: both .md and .yaml files required per contract.

Universal Numbering Pattern (All Document Types)
- **Primary Number (NNN)**: 3-4 digit sequential number for atomic logical document (001-999, then 1000-9999 when needed)
  - **Notation**: "NNN" represents actual numeric digits (e.g., 001, 042, 099, 1000)
  - **NOT**: Three literal "N" characters or "XXX" placeholder text
- **Sub-Document Number (YY)**: 2-3 digit sequential number within atomic document [OPTIONAL] (01-99, then 100-999 when needed)
  - **Notation**: "YY" represents actual numeric digits (e.g., 01, 02, 99, 100)
  - **NOT**: Two literal "Y" characters
- **Format**: `TYPE-NNN` or `TYPE-NNN-YY` (e.g., `REQ-001`, `BRD-009-02`, `ADR-1000`)
- **Zero-Padding**: Always pad to minimum digit count (001, 01) until exceeding range
- **Sub-Numbering Use Cases**: Use -YY suffix ONLY when a single logical requirement/decision/feature has multiple related documents that:
  - Form a cohesive unit requiring sequential reading
  - Share common traceability and implementation scope
  - Follow logical reading order (e.g., 01=prerequisites, 02=main spec, 03=quick reference)
- **Default**: Most documents are single atomic units without -YY suffix
- **Uniqueness Rule**: Each NNN number is unique and can be used EITHER as:
  - Atomic document: `TYPE-NNN_{slug}.md` (e.g., `BRD-001_foundation.md`)
  - Multi-document group: `TYPE-NNN-01_{slug}.md`, `TYPE-NNN-02_{slug}.md`, etc.
  - ❌ INVALID: Cannot have both `BRD-009_{slug}.md` AND `BRD-009-01_{slug}.md` (NNN=009 collision)
  - ✅ VALID: Can have `BRD-009-01_{slug}.md` AND `BRD-009-02_{slug}.md` (same NNN, different YY)

Document ID Standards (ai_dev_flow)
- Requirements (REQ)
  - H1 ID: `REQ-NNN` or `REQ-NNN-YY` (e.g., `# REQ-001: [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] Integration`). Do not use category-coded IDs like `REQ-API-AV-001`.
  - Filename: `REQ-NNN_{slug}.md` or `REQ-NNN-YY_{slug}.md` under category folders: `REQ/{category}/{subcategory}/REQ-NNN_{slug}.md` (e.g., `REQ/api/av/REQ-001_alpha_vantage_integration.md`).
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Categories are encoded by folders. Use sub-numbering (-YY) when single logical requirement spans multiple related documents.
- ADRs
  - H1 ID: `ADR-NNN` or `ADR-NNN-YY` (e.g., `# ADR-033: Risk Limit Enforcement Architecture`).
  - Filename: `ADR/ADR-NNN_{slug}.md` or `ADR/ADR-NNN-YY_{slug}.md` (e.g., `ADR-033_risk_limit_enforcement_architecture.md`).
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Use sub-numbering (-YY) when single architectural decision requires multiple related documents.
- BDD Features and Tags
  - **File Format Clarification**:
    - **Test Scenarios**: `BDD-NNN_{slug}.feature` (Gherkin format - `.feature` extension)
    - **Index/Directory**: `BDD-000_index.md` (Markdown format - `.md` extension)
    - **Template**: `BDD-TEMPLATE.feature` (Gherkin format - `.feature` extension)
    - **Traceability Matrix**: `BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md` (Markdown format - `.md` extension)
  - Filename: `BDD/BDD-NNN_{slug}.feature` or `BDD/BDD-NNN-YY_{slug}.feature`.
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Tags (mandatory):
    - `@requirement:[REQ-NNN](../REQ/.../REQ-NNN_{slug}.md#REQ-NNN)` or `@requirement:[REQ-NNN-YY](...)`
    - `@adr:[ADR-NNN](../ADR/ADR-NNN_{slug}.md#ADR-NNN)` or `@adr:[ADR-NNN-YY](...)` (if applicable)
  - Tags appear before `Scenario:` using valid relative paths + anchors.
  - Index: maintain `BDD/BDD-000_index.md` (note: `.md` format, not `.feature`).
  - Notes: Use sub-numbering (-YY) when single feature requires multiple related test files.
- Technical Specifications (SPEC)
  - YAML `id:` uses lowercase snake_case; pattern: `^[a-z][a-z0-9_]*[a-z0-9]$`.
  - Filename: `SPEC/{type}/SPEC-NNN_{slug}.yaml` or `SPEC/{type}/SPEC-NNN-YY_{slug}.yaml` (e.g., `SPEC/services/SPEC-003_position_limit_service.yaml`).
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - The `id:` may differ from the filename; tags and prose should use the `id:` as the human-readable spec name.
  - Include traceability fields with markdown links: `requirements_source`, `architecture`, `verification`.
  - Notes: Use sub-numbering (-YY) when single component specification requires multiple related YAML files.
- API Contracts (CTR)
  - H1 ID: `CTR-NNN` or `CTR-NNN-YY` (e.g., `# CTR-001: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Validation Contract`).
  - Filename (Dual Format): `CTR-NNN_{slug}.md` + `CTR-NNN_{slug}.yaml` or `CTR-NNN-YY_{slug}.md` + `CTR-NNN-YY_{slug}.yaml` (both required)
  - Organization: Optional subdirectories by service type: `CTR/{agents,mcp,infra}/CTR-NNN_{slug}.{md,yaml}`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - YAML `contract_id:` uses lowercase_snake_case (e.g., `contract_id: position_risk_validation`)
  - Notes: Both .md and .yaml must exist for each CTR-NNN; slugs must match exactly. Use sub-numbering (-YY) when single contract spans multiple related interface definitions.
- Implementation Plans (IMPL)
  - H1 ID: `IMPL-NNN` or `IMPL-NNN-YY` (e.g., `# IMPL-001: [RESOURCE_MANAGEMENT - e.g., capacity planning, quota management] System Implementation`)
  - Filename: `IMPL/IMPL-NNN_{slug}.md` or `IMPL/IMPL-NNN-YY_{slug}.md` (e.g., `IMPL/IMPL-001_risk_management_system.md`)
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Project management documents (WHO/WHEN), not technical specifications (HOW). Lists deliverables: CTR, SPEC, TASKS to be created. Use sub-numbering (-YY) when single implementation plan requires multiple related planning documents.
- AI Tasks (TASKS)
  - H1 ID: `TASKS-NNN` or `TASKS-NNN-YY` (e.g., `# TASKS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Service Implementation`)
  - Filename: `TASKS/TASKS-NNN_{slug}.md` or `TASKS/TASKS-NNN-YY_{slug}.md` with a tasks index at `TASKS/TASKS-000_index.md`.
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: SPEC implementation plans with exact TODOs for code generation. Each TASKS corresponds to one SPEC. Use sub-numbering (-YY) when single SPEC implementation requires multiple related task files.
  - Allocation: reserve next number, do not reuse; keep slugs stable.
- Implementation Plans (IPLAN)
  - Filename Format: `IPLAN-NNN_{descriptive_slug}_YYYYMMDD_HHMMSS.md`
  - Components:
    - `IPLAN-NNN`: Sequential ID (001, 002, etc.)
    - `{descriptive_slug}`: Lowercase, hyphen-separated description
    - `YYYYMMDD_HHMMSS`: Timestamp (EST timezone)
  - Variable Length: NNN = 3-4 digits (001-999, 1000+)
  - Purpose: Session-based execution plans with bash commands
  - Layer: 12
  - Scope: Time-boxed implementation tasks for specific development sessions
  - Examples:
    - `IPLAN-001_database_migration_20251113_143022.md`
    - `IPLAN-002_api_refactoring_20251114_091500.md`
    - `IPLAN-003_test_coverage_improvement_20251115_140000.md`
  - Traceability Tag Format: `@iplan: IPLAN-001, IPLAN-002`
  - Tag Rules:
    - Tag format: `@iplan:` followed by comma-separated IPLAN IDs
    - Cumulative: Includes all upstream tags (@brd through @tasks)
    - Used in: Code files, test files, validation documents
  - Tag Count at Layer 12: 9-11 tags
    - Layer 1-11 tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @impl (optional), @ctr (optional), @spec, @tasks
    - Layer 12 tag: @iplan
  - Notes: Unlike other artifact types, IPLAN uses timestamp-based naming to track implementation sessions chronologically. H1 ID follows standard pattern (e.g., `# IPLAN-001: Database Migration Plan`).
- Business Requirements Documents (BRD)
  - H1 ID: `BRD-NNN` or `BRD-NNN-YY` (e.g., `# BRD-009-01: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Prerequisites`)
  - Filename: `BRD-NNN_{slug}.md` or `BRD-NNN-YY_{slug}.md`
  - Location: `docs/BRD/BRD-NNN_{slug}.md` or `docs/BRD/BRD-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Follows universal numbering pattern. Use sub-numbering (-YY) when single business requirement spans multiple related documents forming cohesive unit with logical reading order (e.g., 01=prerequisites, 02=main spec, 03=quick reference).
  - Examples:
    - Single atomic: `BRD-001_foundation_overview.md`
    - Multi-doc group: `BRD-009-01_prerequisites.md`, `BRD-009-02_broker_integration_pilot.md`, `BRD-009-03_phase_gates_quick_reference.md`
    - Extended atomic: `BRD-1000_advanced_feature.md` (when >999 BRDs)
    - Extended sub-doc: `BRD-009-100_detailed_appendix.md` (when >99 sub-docs)

PRD, SYS, and EARS Document Types
- Product Requirements Documents (PRD)
  - H1 ID: `PRD-NNN` or `PRD-NNN-YY` (e.g., `# PRD-003: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Limits`)
  - Filename: `PRD/PRD-NNN_{slug}.md` or `PRD/PRD-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Use sub-numbering (-YY) when single product requirement spans multiple related documents.
- System Architecture Documents (SYS)
  - H1 ID: `SYS-NNN` or `SYS-NNN-YY` (e.g., `# SYS-003: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Limits`)
  - Filename: `SYS/SYS-NNN_{slug}.md` or `SYS/SYS-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Use sub-numbering (-YY) when single system design spans multiple related documents.
- EARS Requirements (EARS)
  - H1 ID: `EARS-NNN` or `EARS-NNN-YY` (e.g., `# EARS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
  - Filename: `EARS/EARS-NNN_{slug}.md` or `EARS/EARS-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Use sub-numbering (-YY) when single EARS requirement spans multiple related documents.

File Organization Rules
- One document per file (PRD, SYS, REQ, ADR, SPEC, BDD, EARS, CTR, IMPL, AI-TASKS, IPLAN, BRD).
- **Exception**: CTR (API Contracts) requires dual files: .md + .yaml per contract.
- **Exception**: IPLAN uses timestamp-based naming: `IPLAN-NNN_{slug}_YYYYMMDD_HHMMSS.md`
- Filenames use variable-length `NNN` or `NNN-YY` numbering; H1 contains the full ID where applicable.
- Structure (this example):
  - `REQ/{category}/{subcategory}/REQ-NNN_{slug}.md` or `REQ-NNN-YY_{slug}.md`
  - `ADR/ADR-NNN_{slug}.md` or `ADR-NNN-YY_{slug}.md`
  - `BDD/BDD-NNN_{slug}.feature` or `BDD-NNN-YY_{slug}.feature`
  - `SPEC/{type}/SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml`
  - `CTR/CTR-NNN_{slug}.md` + `CTR-NNN_{slug}.yaml` (optional subdirs: `CTR/{agents,mcp,infra}/`)
  - `IMPL/IMPL-NNN_{slug}.md` or `IMPL-NNN-YY_{slug}.md`
  - `TASKS/TASKS-NNN_{slug}.md` or `TASKS-NNN-YY_{slug}.md`
  - `IPLAN/IPLAN-NNN_{slug}_YYYYMMDD_HHMMSS.md`
  - `PRD/PRD-NNN_{slug}.md` or `PRD-NNN-YY_{slug}.md`
  - `SYS/SYS-NNN_{slug}.md` or `SYS-NNN-YY_{slug}.md`
  - `EARS/EARS-NNN_{slug}.md` or `EARS-NNN-YY_{slug}.md`

Cross-Reference Link Format (MANDATORY)
- Universal rule: use markdown links for all references.
- Supports both atomic (NNN) and sub-document (NNN-YY) patterns for all types.
- Formats:
  - REQ in ADR: `[REQ-NNN](../REQ/.../REQ-NNN_{slug}.md#REQ-NNN)` or `[REQ-NNN-YY](...)`
  - ADR in BDD: `@adr:[ADR-NNN](../ADR/ADR-NNN_{slug}.md#ADR-NNN)` or `@adr:[ADR-NNN-YY](...)`
  - REQ in BDD: `@requirement:[REQ-NNN](../REQ/.../REQ-NNN_{slug}.md#REQ-NNN)` or `@requirement:[REQ-NNN-YY](...)`
  - REQ/ADR in CTR:
    - `[REQ-NNN](../REQ/.../REQ-NNN_{slug}.md#REQ-NNN)` or `[REQ-NNN-YY](...)` in Traceability section
    - `[ADR-NNN](../ADR/ADR-NNN_{slug}.md#ADR-NNN)` or `[ADR-NNN-YY](...)` in Traceability section
  - CTR in SPEC:
    - `contract_ref: CTR-NNN_{slug}` or `CTR-NNN-YY_{slug}` (YAML field)
    - `[CTR-NNN](../../CTR/CTR-NNN_{slug}.md#CTR-NNN)` or `[CTR-NNN-YY](...)` (markdown reference)
    - `[CTR-NNN Schema](../../CTR/CTR-NNN_{slug}.yaml)` or `[CTR-NNN-YY Schema](...)` (schema reference)
  - REQ/ADR in SPEC:
    - `requirements_source:
      - "[REQ-NNN](../../REQ/.../REQ-NNN_{slug}.md#REQ-NNN)"` or `"[REQ-NNN-YY](...)"`
    - `architecture:
      - "[ADR-NNN](../../ADR/ADR-NNN_{slug}.md#ADR-NNN)"` or `"[ADR-NNN-YY](...)"`
  - BDD in SPEC verification:
    - `verification:
      - BDD: "[feature_name.feature(:LNN)](../../BDD/feature_name.feature#LNN)"`
  - BRD in BRD:
    - `[BRD-NNN](BRD-NNN_{slug}.md)` (same directory)
    - `[BRD-NNN-YY](BRD-NNN-YY_{slug}.md)` (sub-document reference)
  - BRD in other docs:
    - `[BRD-NNN](../BRD/BRD-NNN_{slug}.md#BRD-NNN)` or `[BRD-NNN-YY](...)`

Traceability Requirements
- REQ: link ADR(s), BDD, CTR (if interface requirement), IMPL (if part of larger implementation), and SPEC via markdown links.
- IMPL: link upstream REQ/ADR (upstream sources), downstream CTR/SPEC/TASKS (deliverables).
- ADR: list addressed REQ(s) via markdown links.
- CTR: link upstream REQ/ADR (Traceability section), downstream SPEC/Code (Traceability section).
- BDD: include `@requirement` (mandatory) and `@adr` (when applicable).
- SPEC: include `requirements_source` (REQ/EARS), `architecture` (ADR), `contract_ref` (CTR if applicable), `impl_plan` (IMPL if part of phased implementation), `verification` (BDD); all as markdown links.
- TASKS: include `@spec` (mandatory - which SPEC being implemented), `@impl` (optional - parent implementation plan if applicable).
- IPLAN: include `@tasks` (mandatory - which TASKS being executed), cumulative tags from all upstream artifacts.
- BRD: link downstream REQ/IMPL/CTR (if applicable), related BRD sub-documents via markdown links.
- Code: reference SPEC, CTR (if contract implementation), and IPLAN (if session-based) in docstrings or header comments using relative paths.


Validation Rules & Aids
- Run before commit:
  - `python scripts/validate_requirement_ids.py`
  - Optional: `python scripts/check_broken_references.py`
  - Optional: `python scripts/complete_traceability_matrix.py`
- Quick regexes (conceptual) - supports variable-length XXX-YY pattern:
  - REQ H1 ID: `^#\sREQ-\d{3,4}(-\d{2,3})?:.+$`
  - REQ filename: `REQ-\d{3,4}(-\d{2,3})?_.+\.md$`
  - ADR H1 ID: `^#\sADR-\d{3,4}(-\d{2,3})?:.+$`
  - ADR filename: `ADR-\d{3,4}(-\d{2,3})?_.+\.md$`
  - BDD filename: `BDD-\d{3,4}(-\d{2,3})?_.+\.feature$`
  - BDD tag: `^@requirement:\[REQ-\d{3,4}(-\d{2,3})?\]\(.+\.md#REQ-\d{3,4}(-\d{2,3})?\)$`
  - SPEC id: `^[a-z][a-z0-9_]*[a-z0-9]$`
  - SPEC filename: `SPEC-\d{3,4}(-\d{2,3})?_.+\.ya?ml$`
  - CTR H1 ID: `^#\sCTR-\d{3,4}(-\d{2,3})?:.+$`
  - CTR filename: `CTR-\d{3,4}(-\d{2,3})?_.+\.(md|yaml)$`
  - IMPL H1 ID: `^#\sIMPL-\d{3,4}(-\d{2,3})?:.+$`
  - IMPL filename: `IMPL-\d{3,4}(-\d{2,3})?_.+\.md$`
  - TASKS H1 ID: `^#\sTASKS-\d{3,4}(-\d{2,3})?:.+$`
  - TASKS filename: `TASKS-\d{3,4}(-\d{2,3})?_.+\.md$`
  - IPLAN H1 ID: `^#\sIPLAN-\d{3,4}:.+$`
  - IPLAN filename: `IPLAN-\d{3,4}_.+_\d{8}_\d{6}\.md$`
  - BRD H1 ID: `^#\sBRD-\d{3,4}(-\d{2,3})?:.+$`
  - BRD filename: `BRD-\d{3,4}(-\d{2,3})?_.+\.md$`
  - PRD H1 ID: `^#\sPRD-\d{3,4}(-\d{2,3})?:.+$`
  - PRD filename: `PRD-\d{3,4}(-\d{2,3})?_.+\.md$`
  - SYS H1 ID: `^#\sSYS-\d{3,4}(-\d{2,3})?:.+$`
  - SYS filename: `SYS-\d{3,4}(-\d{2,3})?_.+\.md$`
  - EARS H1 ID: `^#\sEARS-\d{3,4}(-\d{2,3})?:.+$`
  - EARS filename: `EARS-\d{3,4}(-\d{2,3})?_.+\.md$`

Examples (ai_dev_flow) - Atomic Documents (XXX)
- PRD: `PRD/PRD-003_position_risk_limits.md` (H1: `# PRD-003: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Limits`)
- SYS: `SYS/SYS-003_position_risk_limits.md` (H1: `# SYS-003: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Limits`)
- EARS: `EARS/EARS-003_position_limit_enforcement.md` (H1: `# EARS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- REQ: `REQ/risk/lim/REQ-003_position_limit_enforcement.md` (H1: `# REQ-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- ADR: `ADR/ADR-033_risk_limit_enforcement_architecture.md` (H1: `# ADR-033: Risk Limit Enforcement Architecture`)
- CTR: `CTR/CTR-001_position_risk_validation.md` + `CTR-001_position_risk_validation.yaml` (H1: `# CTR-001: [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Validation Contract`, YAML: `contract_id: position_risk_validation`)
- BDD: `BDD/BDD-003_risk_limits_requirements.feature`
- SPEC: `SPEC/services/SPEC-003_position_limit_service.yaml` (id: `position_limit_service`)
- IMPL: `IMPL/IMPL-001_risk_management_system.md` (H1: `# IMPL-001: [RESOURCE_MANAGEMENT - e.g., capacity planning, quota management] System Implementation`)
- TASKS: `TASKS/TASKS-003_position_limit_service.md` (H1: `# TASKS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Service Implementation`)
- IPLAN: `IPLAN/IPLAN-001_database_migration_20251113_143022.md` (H1: `# IPLAN-001: Database Migration Plan`)
- BRD: `docs/BRD/BRD-001_foundation_overview.md` (H1: `# BRD-001: Foundation & Overview`)

Examples (ai_dev_flow) - Sub-Documents (XXX-YY)
- BRD-009 multi-document group ([EXTERNAL_INTEGRATION - e.g., third-party API, service provider] integration pilot):
  - Prerequisites: `docs/BRD/BRD-009-01_prerequisites.md` (H1: `# BRD-009-01: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Prerequisites`)
  - Main specification: `docs/BRD/BRD-009-02_broker_integration_pilot.md` (H1: `# BRD-009-02: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Pilot`)
  - Quick reference: `docs/BRD/BRD-009-03_phase_gates_quick_reference.md` (H1: `# BRD-009-03: Phase Gates Quick Reference`)
- Extended atomic (when >999 documents): `BRD-1000_advanced_feature.md`
- Extended sub-doc (when >99 sub-docs): `BRD-009-100_detailed_appendix.md`

Component Abbreviations (examples)
- SVC (Service), CL (Client), SRV (Server), GW (Gateway), AGG (Aggregator), MGR (Manager), CTRL (Controller), ADPT (Adapter), REPO (Repository), PROC (Processor), VAL (Validator), ORCH (Orchestrator), PROV (Provider)
- IB ([EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System]), AV ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API]), MKT (Market), ORD (Order), EXEC (Execution), POS ([RESOURCE_INSTANCE - e.g., database connection, workflow instance]), LIM (Limit), RISK (Risk), ACCT (Account), PFOL ([RESOURCE_COLLECTION - e.g., user accounts, active sessions]), CFG (Configuration), AUTH (Authentication), AUTHZ (Authorization), REDIS, PUBSUB, BQ (BigQuery), CSQL (Cloud SQL), GCR (Cloud Run), GSM (Secrets Manager)

BDD Tag Examples
```gherkin
# Atomic document references (XXX)
@requirement:[REQ-003](../REQ/risk/lim/REQ-003_position_limit_enforcement.md#REQ-003)
@adr:[ADR-033](../ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033)

# Sub-document references (XXX-YY)
@requirement:[REQ-009-01](../REQ/[EXTERNAL_INTEGRATION - e.g., third-party API, service provider]/ib/REQ-009-01_prerequisites.md#REQ-009-01)
@adr:[ADR-030-02](../ADR/ADR-030-02_connection_management.md#ADR-030-02)
```

Anchors & Linking
- Use ID anchors where applicable (e.g., `#REQ-001`, `#ADR-032`).
- Prefer stable ID anchors over line anchors. If a line anchor (e.g., `#L28`) is used, revalidate after edits.

Local Clarifications (ai_dev_flow)
- Variable-length numeric filename prefixes (NNN or NNN-YY) are required here for readability and ordering; do not rename to match other directories' styles.
- SPEC filenames keep `SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml`; the YAML `id:` is the stable spec identifier used by tags and prose.
- Keep tag headers at top of files (first non-empty lines) for machine-readability as shown in TRACEABILITY.md.
- Use sub-numbering (-YY) sparingly - only when single logical document truly requires multiple related files with sequential reading order.
- **ID Collision Prevention**: Each NNN number must be unique across atomic and multi-document patterns. Once allocated to a multi-document group (e.g., REQ-009-01, REQ-009-02), that NNN number (009) cannot be used for an atomic document (REQ-009).

Checklist
- H1 titles contain IDs for PRD/SYS/EARS/REQ/ADR/CTR/IMPL/TASKS/BRD where applicable (use `TYPE-NNN` or `TYPE-NNN-YY` format).
- BDD tags are markdown links with valid relative paths and anchors (supports both NNN and NNN-YY patterns).
- Spec files named `SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml`; inside, `id:` is snake_case and used by `@spec` tags; `requirements_source`/`architecture`/`verification` links resolve.
- All document types follow universal numbering pattern: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+).
- No ID collisions: each NNN number used only once (either atomic TYPE-NNN OR multi-doc TYPE-NNN-YY group, never both).
- Run `python scripts/validate_requirement_ids.py` and fix any violations before committing.
