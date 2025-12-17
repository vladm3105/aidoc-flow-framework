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
  - `REF/` - Reference Documents (supplementary, non-workflow documentation)

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
  - H1 ID: `REQ-NNN` or `REQ-NNN-YY` (e.g., `# REQ-001: [EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API] Integration`). Do not use category-coded IDs like `REQ-API-AV-001`.
  - Filename: `REQ-NNN_{slug}.md` or `REQ-NNN-YY_{slug}.md` under category folders: `REQ/{category}/{subcategory}/REQ-NNN_{slug}.md` (e.g., `REQ/api/av/REQ-001_external_api_integration.md`).
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
  - Filename: `SPEC/{type}/SPEC-NNN_{slug}.yaml` or `SPEC/{type}/SPEC-NNN-YY_{slug}.yaml` (e.g., `SPEC/services/SPEC-003_resource_limit_service.yaml`).
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - The `id:` may differ from the filename; tags and prose should use the `id:` as the human-readable spec name.
  - Include traceability fields with markdown links: `requirements_source`, `architecture`, `verification`.
  - Notes: Use sub-numbering (-YY) when single component specification requires multiple related YAML files.
- API Contracts (CTR)
  - H1 ID: `CTR-NNN` or `CTR-NNN-YY` (e.g., `# CTR-001: resource Risk Validation Contract`).
  - Filename (Dual Format): `CTR-NNN_{slug}.md` + `CTR-NNN_{slug}.yaml` or `CTR-NNN-YY_{slug}.md` + `CTR-NNN-YY_{slug}.yaml` (both required)
  - Organization: Optional subdirectories by service type: `CTR/{agents,mcp,infra}/CTR-NNN_{slug}.{md,yaml}`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - YAML `contract_id:` uses lowercase_snake_case (e.g., `contract_id: position_risk_validation`)
  - Notes: Both .md and .yaml must exist for each CTR-NNN; slugs must match exactly. Use sub-numbering (-YY) when single contract spans multiple related interface definitions.
- Implementation Plans (IMPL)
  - H1 ID: `IMPL-NNN` or `IMPL-NNN-YY` (e.g., `# IMPL-001: resource management System Implementation`)
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
  - Filename Format: `IPLAN-NNN_{descriptive_slug}.md`
  - Components:
    - `IPLAN-NNN`: Sequential ID (001, 002, etc.)
    - `{descriptive_slug}`: Lowercase, underscore-separated description
  - Variable Length: NNN = 3-4 digits (001-999, 1000+)
  - Purpose: Session-based execution plans with bash commands
  - Layer: 12
  - Scope: Implementation tasks organized into executable sessions
  - Examples:
    - `IPLAN-001_database_migration.md`
    - `IPLAN-002_api_refactoring.md`
    - `IPLAN-003_test_coverage_improvement.md`
  - Traceability Tag Format: `@iplan: IPLAN-001, IPLAN-002`
  - Tag Rules:
    - Tag format: `@iplan:` followed by comma-separated IPLAN IDs
    - Cumulative: Includes all upstream tags (@brd through @tasks)
    - Used in: Code files, test files, validation documents
  - Tag Count at Layer 12: 9-11 tags
    - Layer 1-11 tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @impl (optional), @ctr (optional), @spec, @tasks
    - Layer 12 tag: @iplan
  - Notes: H1 ID follows standard pattern (e.g., `# IPLAN-001: Database Migration Plan`). Version history tracked via Git.
- Implementation Contracts (ICON) - Optional
  - **Default**: Embed contracts in TASKS files (section 8: Implementation Contracts)
  - **Standalone ICON Files** (when 5+ consumers, >500 lines, platform-level):
    - H1 ID: `ICON-NNN` (e.g., `# ICON-001: Gateway Connector Protocol`)
    - Filename Format: `ICON-NNN_descriptive_name.md`
    - Components:
      - `ICON-NNN`: Sequential ID (001, 002, etc.)
      - `descriptive_name`: Lowercase with underscores
    - Variable Length: NNN = 3-4 digits (001-999, 1000+)
    - Location: `ai_dev_flow/ICON/` or `docs/ICON/`
    - Layer: 11 (same as TASKS)
    - Purpose: Standalone implementation contracts for parallel development coordination
    - Examples:
      - `ICON-001_gateway_connector_protocol.md`
      - `ICON-002_external_data_event_bus.md`
      - `ICON-003_order_execution_exceptions.md`
    - Traceability Tag Format: `@icon: TASKS-NNN:ContractName` or `@icon: ICON-NNN:ContractName`
    - Tag Rules:
      - Tag format: `@icon:` with contract reference and optional `@icon-role: provider|consumer`
      - Used in: TASKS files (provider/consumer), Code files (implementation)
      - Distinguishes from `@ctr:` (Layer 9 external API contracts)
    - Decision Criteria (ALL must be met):
      - 5+ consumer TASKS files
      - Contract definition >500 lines
      - Platform-level shared interface
      - Cross-project usage
    - Registry: `ICON-000_index.md` tracks all standalone contracts
    - Notes: Most implementation contracts should be embedded in TASKS files. Use standalone ICON only when criteria met. See [ICON_CREATION_RULES.md](ICON/ICON_CREATION_RULES.md).
- Reference Documents (REF)
  - H1 ID: `{TYPE}-REF-NNN` (e.g., `# BRD-REF-001: Project Overview`)
  - Filename: `{TYPE}-REF-NNN_{slug}.md` (e.g., `BRD-REF-001_project_overview.md`)
  - Location: Within parent TYPE directory (e.g., `docs/BRD/BRD-REF-001_project_overview.md`)
  - Variable Length: NNN = 3-4 digits (001-999, 1000+)
  - Numbering: Independent sequence per parent TYPE (BRD-REF-001, ADR-REF-001 are separate sequences)
  - Traceability: Optional (encouraged but not required)
  - Validation: Minimal (non-blocking)
  - Required Sections: Document Control, Revision History, Introduction
  - Use Cases:
    - General project descriptions from business perspective
    - Infrastructure requirements documentation
    - Strategic vision descriptions
    - Dictionaries and glossaries
    - Reference material and guides
  - Notes: REF documents are supplementary and do not participate in formal traceability chain. Similar exemption treatment as `{TYPE}-000` index documents.
- Business Requirements Documents (BRD)
  - H1 ID: `BRD-NNN` or `BRD-NNN-YY` (e.g., `# BRD-009-01: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Prerequisites`)
  - Filename: `BRD-NNN_{slug}.md` or `BRD-NNN-YY_{slug}.md`
  - Location: `docs/BRD/BRD-NNN_{slug}.md` or `docs/BRD/BRD-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Follows universal numbering pattern. Use sub-numbering (-YY) when single business requirement spans multiple related documents forming cohesive unit with logical reading order (e.g., 01=prerequisites, 02=main spec, 03=quick reference).
  - Examples:
    - Single atomic: `BRD-001_foundation_overview.md`
    - Multi-doc group: `BRD-009-01_prerequisites.md`, `BRD-009-02_provider_integration_pilot.md`, `BRD-009-03_phase_gates_quick_reference.md`
    - Extended atomic: `BRD-1000_advanced_feature.md` (when >999 BRDs)
    - Extended sub-doc: `BRD-009-100_detailed_appendix.md` (when >99 sub-docs)

PRD, SYS, and EARS Document Types
- Product Requirements Documents (PRD)
  - H1 ID: `PRD-NNN` or `PRD-NNN-YY` (e.g., `# PRD-003: resource Risk Limits`)
  - Filename: `PRD/PRD-NNN_{slug}.md` or `PRD/PRD-NNN-YY_{slug}.md`
  - Variable Length: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+)
  - Notes: Use sub-numbering (-YY) when single product requirement spans multiple related documents.
- System Architecture Documents (SYS)
  - H1 ID: `SYS-NNN` or `SYS-NNN-YY` (e.g., `# SYS-003: resource Risk Limits`)
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
- Filenames use variable-length `NNN` or `NNN-YY` numbering; H1 contains the full ID where applicable.
- Structure (this example):
  - `REQ/{category}/{subcategory}/REQ-NNN_{slug}.md` or `REQ-NNN-YY_{slug}.md`
  - `ADR/ADR-NNN_{slug}.md` or `ADR-NNN-YY_{slug}.md`
  - `BDD/BDD-NNN_{slug}.feature` or `BDD-NNN-YY_{slug}.feature`
  - `SPEC/{type}/SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml`
  - `CTR/CTR-NNN_{slug}.md` + `CTR-NNN_{slug}.yaml` (optional subdirs: `CTR/{agents,mcp,infra}/`)
  - `IMPL/IMPL-NNN_{slug}.md` or `IMPL-NNN-YY_{slug}.md`
  - `TASKS/TASKS-NNN_{slug}.md` or `TASKS-NNN-YY_{slug}.md`
  - `IPLAN/IPLAN-NNN_{slug}.md`
  - `PRD/PRD-NNN_{slug}.md` or `PRD-NNN-YY_{slug}.md`
  - `SYS/SYS-NNN_{slug}.md` or `SYS-NNN-YY_{slug}.md`
  - `EARS/EARS-NNN_{slug}.md` or `EARS-NNN-YY_{slug}.md`

## Section-Based File Splitting (Document Chunking)

**Purpose**: When documents exceed 50KB standard limit (or 100KB maximum), split into section-based files using dot notation. This maintains document cohesion while enabling AI tool processing.

### Three Coexisting ID Patterns

The framework uses three distinct ID patterns for different purposes:

| Pattern | Format | Example | Purpose |
|---------|--------|---------|---------|
| **Document ID** | `TYPE-NNN` | `BRD-03` | Complete document reference |
| **Section File** | `TYPE-NNN.S` | `BRD-03.1` | Section S of document TYPE-NNN |
| **Element ID** | `TYPE.NN.TT.SS` | `BRD.03.01.05` | Internal element (all dots, 4-segment) |

**Key Distinction**:
- `BRD-03.1` → Section file (dash before doc number, single dot for section)
- `BRD.03.01.05` → Element ID (all dots, 4-segment format for internal references)
- `@ref: BRD-03.1` → References a **document/section file**, not an element

### Section File Naming Pattern

**Pattern**: `{TYPE}-{NNN}.{SECTION}[.{SUBSECTION}]_{slug}.md`

| Component | Format | Description |
|-----------|--------|-------------|
| `TYPE` | 2-5 uppercase letters | Document type (BRD, PRD, REQ, etc.) |
| `-` | Dash separator | Separates type from document number |
| `NNN` | 2-4 digits | Document number (01, 001, 0001) |
| `.` | Dot separator | Separates document number from section |
| `SECTION` | 1-2 digits | Section number (0-99) |
| `.SUBSECTION` | Optional 1-2 digits | Subsection (e.g., 1.1, 2.3) |
| `_` | Underscore separator | Separates ID from descriptive slug |
| `slug` | lowercase_snake_case | Human-readable description |

**Validation Regex**: `^[A-Z]{2,5}(-REF)?-[0-9]{2,4}\.[0-9]+(\.[0-9]+)?_[a-z0-9_]+\.md$`

### When to Split Documents

| File Size | Action | Rationale |
|-----------|--------|-----------|
| <50KB | Keep as single file | Optimal for all AI tools |
| 50-100KB | Consider splitting | May cause issues with some tools |
| >100KB | **MUST split** | Exceeds Claude Code practical limit |

**Split Triggers**:
1. File exceeds 50KB standard limit
2. Document has clear logical sections (chapters, modules)
3. Sections can stand alone with minimal cross-references
4. Team needs independent section maintenance

### Section Numbering Rules

| Section | Purpose | Content |
|---------|---------|---------|
| **Section 0** | Index/Overview | Document control, section map, navigation |
| **Section 1+** | Content sections | Actual document content, numbered sequentially |

**Section 0 Requirements** (MANDATORY for all split documents):
- Document control metadata
- Complete section map with links
- Version history
- Cross-reference summary
- Reading order guidance

### Mandatory Metadata Header (YAML Frontmatter)

**ALL section files MUST include YAML frontmatter**:

```yaml
---
doc_id: TYPE-NNN
section: S
title: "Section Title"
parent_doc: TYPE-NNN.0_index.md      # null for section 0
prev_section: TYPE-NNN.{S-1}_slug.md  # null for section 0 or 1
next_section: TYPE-NNN.{S+1}_slug.md  # null for last section
tags:
  - section-file
  - document-type-tag
custom_fields:
  total_sections: N
  section_type: content  # or "index" for section 0
  architecture_approach: approach-name
  priority: primary|fallback|shared
  split_date: YYYY-MM-DD
---
```

**Required Metadata Fields**:

| Field | Required In | Description |
|-------|-------------|-------------|
| `doc_id` | All sections | Parent document ID (TYPE-NNN) |
| `section` | All sections | Section number (0 = index, 1+ = content) |
| `title` | All sections | Section-specific title |
| `total_sections` | Section 0 | Total number of sections in split document |
| `parent_doc` | Content sections | Link to Section 0 index file |
| `prev_section` | Content sections | Link to previous section (if exists) |
| `next_section` | Content sections | Link to next section (if exists) |
| `tags` | All sections | Must include `section-file` or `section-index` |

### Section File Examples

**Source Document**: `BRD-003_trading_platform_requirements.md` (150KB)

**Split into Section Files**:

```
docs/BRD/
├── BRD-003.0_index.md              # Section 0: Index/Overview
├── BRD-003.1_executive_summary.md   # Section 1: Executive Summary
├── BRD-003.2_business_context.md    # Section 2: Business Context
├── BRD-003.3_functional_requirements.md  # Section 3: Functional Requirements
├── BRD-003.4_non_functional_requirements.md  # Section 4: Non-Functional Requirements
├── BRD-003.5_architecture_decisions.md  # Section 5: Architecture Decisions
└── BRD-003.6_appendices.md          # Section 6: Appendices
```

**Section 0 Header Example** (`BRD-003.0_index.md`):
```markdown
---
doc_id: BRD-003
section: 0
title: "Trading Platform Requirements - Index"
total_sections: 7
original_size_kb: 146
split_date: 2025-12-17
tags:
  - section-index
  - platform-brd
custom_fields:
  section_type: index
  architecture_approach: ai-agent-primary
  priority: primary
  development_status: active
---

# BRD-003.0: Trading Platform Requirements - Index

## Document Control

| Field | Value |
|-------|-------|
| **Document ID** | BRD-003 |
| **Status** | Active |
| **Total Sections** | 7 |

## Section Map

| Section | Title | Size | Link |
|---------|-------|------|------|
| 0 | Index (this file) | 3KB | [BRD-003.0](BRD-003.0_index.md) |
| 1 | Executive Summary | 8KB | [BRD-003.1](BRD-003.1_executive_summary.md) |
| 2 | Business Context | 25KB | [BRD-003.2](BRD-003.2_business_context.md) |
| 3 | Functional Requirements | 45KB | [BRD-003.3](BRD-003.3_functional_requirements.md) |
| 4 | Non-Functional Requirements | 30KB | [BRD-003.4](BRD-003.4_non_functional_requirements.md) |
| 5 | Architecture Decisions | 20KB | [BRD-003.5](BRD-003.5_architecture_decisions.md) |
| 6 | Appendices | 15KB | [BRD-003.6](BRD-003.6_appendices.md) |

## Reading Order

1. Start with Section 0 (this index) for overview
2. Proceed through sections 1-6 sequentially
3. Reference Section 6 for detailed appendices
```

**Content Section Example** (`BRD-003.1_executive_summary.md`):
```markdown
---
doc_id: BRD-003
section: 1
title: "Executive Summary"
parent_doc: "BRD-003.0_index.md"
prev_section: null
next_section: "BRD-003.2_business_context.md"
tags:
  - section-file
  - platform-brd
custom_fields:
  total_sections: 7
  section_type: content
  architecture_approach: ai-agent-primary
  priority: primary
---

# BRD-003.1: Executive Summary

> **Navigation**: [Index](BRD-003.0_index.md) | Previous: None | [Next](BRD-003.2_business_context.md)
>
> **Parent Document**: BRD-003
> **Section**: 1 of 7

---

## Section Content

[Section content here...]
```

### Cross-Reference Format for Section Files

**Tagging Section References**:
- `@ref: BRD-003.1` → References section 1 of BRD-003
- `@ref: BRD-003.2.3` → References subsection 2.3 of BRD-003

**Markdown Links to Sections**:
- Same directory: `[BRD-003.1](BRD-003.1_executive_summary.md)`
- Cross-directory: `[BRD-003.1](../BRD/BRD-003.1_executive_summary.md)`

### Section File vs Sub-Document Comparison

| Aspect | Section Files | Sub-Documents |
|--------|---------------|---------------|
| **Use Case** | Split large documents | Related but distinct documents |
| **Pattern** | `TYPE-NNN.S_{slug}.md` | `TYPE-NNN-YY_{slug}.md` |
| **Example** | `BRD-003.1_summary.md` | `BRD-009-01_prerequisites.md` |
| **Separator** | Single dot (.) | Dash (-) |
| **Metadata** | Requires parent_document | Independent document |
| **Navigation** | Must have prev/next links | Optional relationships |
| **Section 0** | Required index | No index required |
| **Traceability** | Inherits parent's tags | Has own traceability |

### Type-Specific Section Templates

Each document type has dedicated section templates providing type-specific metadata, tags, and traceability fields. Use these instead of generic templates for better compliance.

**Template Locations**:

| Type | Layer | Index Template | Content Template |
|------|-------|----------------|------------------|
| BRD | 1 | `BRD/BRD-SECTION-0-TEMPLATE.md` | `BRD/BRD-SECTION-TEMPLATE.md` |
| PRD | 2 | `PRD/PRD-SECTION-0-TEMPLATE.md` | `PRD/PRD-SECTION-TEMPLATE.md` |
| EARS | 3 | `EARS/EARS-SECTION-0-TEMPLATE.md` | `EARS/EARS-SECTION-TEMPLATE.md` |
| BDD | 4 | `BDD/BDD-SECTION-0-TEMPLATE.md` | `BDD/BDD-SECTION-TEMPLATE.md` |
| ADR | 5 | `ADR/ADR-SECTION-0-TEMPLATE.md` | `ADR/ADR-SECTION-TEMPLATE.md` |
| SYS | 6 | `SYS/SYS-SECTION-0-TEMPLATE.md` | `SYS/SYS-SECTION-TEMPLATE.md` |
| REQ | 7 | `REQ/REQ-SECTION-0-TEMPLATE.md` | `REQ/REQ-SECTION-TEMPLATE.md` |
| IMPL | 8 | `IMPL/IMPL-SECTION-0-TEMPLATE.md` | `IMPL/IMPL-SECTION-TEMPLATE.md` |
| CTR | 9 | `CTR/CTR-SECTION-0-TEMPLATE.md` | `CTR/CTR-SECTION-TEMPLATE.md` |
| SPEC | 10 | `SPEC/SPEC-SECTION-0-TEMPLATE.md` | `SPEC/SPEC-SECTION-TEMPLATE.md` |

**Types NOT requiring section templates**: TASKS, IPLAN, ICON (typically remain under 25KB)

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
- Quick regexes (conceptual):
  - **Unified Element ID** (all document types): `^[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
  - **Internal Heading**: `^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$`
  - **Cross-Reference Tag**: `^@[a-z]+:\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
- Document filename regexes (unchanged - dash format for files):
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
  - IPLAN filename: `IPLAN-\d{3,4}_.+\.md$`
  - BRD H1 ID: `^#\sBRD-\d{3,4}(-\d{2,3})?:.+$`
  - BRD filename: `BRD-\d{3,4}(-\d{2,3})?_.+\.md$`
  - PRD H1 ID: `^#\sPRD-\d{3,4}(-\d{2,3})?:.+$`
  - PRD filename: `PRD-\d{3,4}(-\d{2,3})?_.+\.md$`
  - SYS H1 ID: `^#\sSYS-\d{3,4}(-\d{2,3})?:.+$`
  - SYS filename: `SYS-\d{3,4}(-\d{2,3})?_.+\.md$`
  - EARS H1 ID: `^#\sEARS-\d{3,4}(-\d{2,3})?:.+$`
  - EARS filename: `EARS-\d{3,4}(-\d{2,3})?_.+\.md$`
  - REF H1 ID: `^#\s[A-Z]{2,5}-REF-\d{3,4}:.+$`
  - REF filename: `[A-Z]{2,5}-REF-\d{3,4}_.+\.md$`
- Section file regexes (dot notation for document chunks):
  - Section filename: `[A-Z]{2,5}(-REF)?-[0-9]{2,4}\.[0-9]+(\.[0-9]+)?_.+\.md$`
  - Section H1 ID: `^#\s[A-Z]{2,5}(-REF)?-[0-9]{2,4}\.[0-9]+(\.[0-9]+)?:.+$`
  - Section reference tag: `@ref:\s+[A-Z]{2,5}(-REF)?-[0-9]{2,4}\.[0-9]+(\.[0-9]+)?`
  - Section 0 (index) filename: `[A-Z]{2,5}(-REF)?-[0-9]{2,4}\.0_[a-z_]+\.md$`

Examples (ai_dev_flow) - Atomic Documents (XXX)
- PRD: `PRD/PRD-003_position_risk_limits.md` (H1: `# PRD-003: resource Risk Limits`)
- SYS: `SYS/SYS-003_position_risk_limits.md` (H1: `# SYS-003: resource Risk Limits`)
- EARS: `EARS/EARS-003_resource_limit_enforcement.md` (H1: `# EARS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- REQ: `REQ/risk/lim/REQ-003_resource_limit_enforcement.md` (H1: `# REQ-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- ADR: `ADR/ADR-033_risk_limit_enforcement_architecture.md` (H1: `# ADR-033: Risk Limit Enforcement Architecture`)
- CTR: `CTR/CTR-001_position_risk_validation.md` + `CTR-001_position_risk_validation.yaml` (H1: `# CTR-001: resource Risk Validation Contract`, YAML: `contract_id: position_risk_validation`)
- BDD: `BDD/BDD-003_risk_limits_requirements.feature`
- SPEC: `SPEC/services/SPEC-003_resource_limit_service.yaml` (id: `resource_limit_service`)
- IMPL: `IMPL/IMPL-001_risk_management_system.md` (H1: `# IMPL-001: resource management System Implementation`)
- TASKS: `TASKS/TASKS-003_resource_limit_service.md` (H1: `# TASKS-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Service Implementation`)
- IPLAN: `IPLAN/IPLAN-001_database_migration_20251113_143022.md` (H1: `# IPLAN-001: Database Migration Plan`)
- BRD: `docs/BRD/BRD-001_foundation_overview.md` (H1: `# BRD-001: Foundation & Overview`)

Examples (ai_dev_flow) - Sub-Documents (XXX-YY)
- BRD-009 multi-document group ([EXTERNAL_INTEGRATION - e.g., third-party API, service provider] integration pilot):
  - Prerequisites: `docs/BRD/BRD-009-01_prerequisites.md` (H1: `# BRD-009-01: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Prerequisites`)
  - Main specification: `docs/BRD/BRD-009-02_provider_integration_pilot.md` (H1: `# BRD-009-02: [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Pilot`)
  - Quick reference: `docs/BRD/BRD-009-03_phase_gates_quick_reference.md` (H1: `# BRD-009-03: Phase Gates Quick Reference`)
- Extended atomic (when >999 documents): `BRD-1000_advanced_feature.md`
- Extended sub-doc (when >99 sub-docs): `BRD-009-100_detailed_appendix.md`

Examples (ai_dev_flow) - Section Files (XXX.S)
- Split BRD document (150KB original → 7 sections):
  - Index: `docs/BRD/BRD-003.0_index.md` (H1: `# BRD-003.0: Trading Platform - Index`)
  - Section 1: `docs/BRD/BRD-003.1_executive_summary.md` (H1: `# BRD-003.1: Executive Summary`)
  - Section 2: `docs/BRD/BRD-003.2_business_context.md` (H1: `# BRD-003.2: Business Context`)
  - Section 3: `docs/BRD/BRD-003.3_functional_requirements.md` (H1: `# BRD-003.3: Functional Requirements`)
- Split PRD document with subsections:
  - Index: `docs/PRD/PRD-015.0_index.md`
  - Section 2.1: `docs/PRD/PRD-015.2.1_api_features.md` (H1: `# PRD-015.2.1: API Features`)
  - Section 2.2: `docs/PRD/PRD-015.2.2_ui_features.md` (H1: `# PRD-015.2.2: UI Features`)

Component Abbreviations (examples)
- SVC (Service), CL (Client), SRV (Server), GW (Gateway), AGG (Aggregator), MGR (Manager), CTRL (Controller), ADPT (Adapter), REPO (Repository), PROC (Processor), VAL (Validator), ORCH (Orchestrator), PROV (Provider)
- IB ([EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System]), AV ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API]), MKT (Market), ORD (Order), EXEC (Execution), POS (resource), LIM (Limit), RISK (Risk), ACCT (Account), PFOL (resource collection), CFG (Configuration), AUTH (Authentication), AUTHZ (Authorization), REDIS, PUBSUB, BQ (BigQuery), CSQL (Cloud SQL), GCR (Cloud Run), GSM (Secrets Manager)

BDD Tag Examples
```gherkin
# Document-level references (dash format for file links)
@requirement:[REQ-003](../REQ/risk/lim/REQ-003_resource_limit_enforcement.md#REQ-003)
@adr:[ADR-033](../ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033)

# Internal element references (dot format for element IDs)
# Format: TYPE.DOC_NUM.ELEM_TYPE.SEQ
@brd: BRD.01.01.05    # BRD doc 1, Functional Requirement #5
@brd: BRD.01.03.02    # BRD doc 1, Constraint #2
@prd: PRD.02.07.15    # PRD doc 2, User Story #15
@adr: ADR.03.10.01    # ADR doc 3, Decision #1
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

---

## Unified Element ID Format (MANDATORY)

The SDD framework uses a **single unified format** for all internal element references across all document types. This format is optimized for AI-first workflows where AI assistants write documentation and humans query AI about specific elements.

### Format Specification

```
{DOC_TYPE}.{DOC_NUM}.{ELEM_TYPE}.{SEQ}
```

**Validation Regex**: `^[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`

| Segment | Min Digits | Max Digits | Start Value | Purpose |
|---------|------------|------------|-------------|---------|
| DOC_TYPE | 2 chars | 5 chars | - | Document type (BRD, PRD, REQ, SPEC, etc.) |
| DOC_NUM | 2 | 9 | 01 | Document instance number |
| ELEM_TYPE | 2 | 9 | 01 | Element category code (see table below) |
| SEQ | 2 | 9 | 01 | Sequential within element type |

### Standardized Element Type Codes

Consistent across ALL document types:

| Code | Element Type | Common In |
|------|--------------|-----------|
| 01 | Functional Requirement | BRD, PRD, SYS, REQ |
| 02 | Quality Attribute | BRD, PRD, SYS |
| 03 | Constraint | BRD, PRD |
| 04 | Assumption | BRD, PRD |
| 05 | Dependency | BRD, PRD, REQ |
| 06 | Acceptance Criteria | BRD, PRD, REQ |
| 07 | User Story | PRD |
| 08 | Use Case | PRD, SYS |
| 09 | Risk | BRD, PRD |
| 10 | Decision | ADR |
| 11 | Alternative | ADR |
| 12 | Consequence | ADR |
| 13 | Test Scenario | BDD |
| 14 | Step | BDD, SPEC |
| 15 | Interface | SPEC, CTR |
| 16 | Data Model | SPEC, CTR |
| 17 | Task | TASKS |
| 18 | Command | IPLAN |
| 19 | Contract Clause | CTR |
| 20 | Validation Rule | SPEC |
| 21 | Feature Item | BRD, PRD |
| 22 | Business Objective | BRD |
| 23 | Stakeholder Need | BRD, PRD |
| 24 | EARS Statement | EARS |
| 25 | System Requirement | SYS |
| 26 | Atomic Requirement | REQ |
| 27 | Specification Element | SPEC |
| 28 | Implementation Phase | IMPL |
| 29 | Task Item | TASKS |
| 30 | Plan Step | IPLAN |
| 31-99 | Reserved for future use | - |

### Examples

| ID | Length | Meaning |
|----|--------|---------|
| `BRD.01.01.01` | 12 | BRD #1, Functional Requirement #1 |
| `BRD.01.03.05` | 12 | BRD #1, Constraint #5 |
| `PRD.02.07.42` | 12 | PRD #2, User Story #42 |
| `ADR.01.10.01` | 12 | ADR #1, Decision #1 |
| `TASKS.01.17.128` | 15 | TASKS #1, Task #128 |
| `BRD.99.01.9999` | 15 | BRD #99, Functional Requirement #9999 |
| `SPEC.01.15.03` | 13 | SPEC #1, Interface #3 |

### Growth Pattern

IDs automatically expand as needed without schema changes:

```text
BRD.01.01.01      → Start (minimum)
BRD.01.01.99      → Approaching 2-digit limit
BRD.01.01.100     → Auto-expand to 3 digits
BRD.01.01.9999    → Still valid (4 digits)
BRD.99.99.999999  → Maximum practical scale
```

### Cross-Reference Tag Format

| Tag Format | Example | Meaning |
|------------|---------|---------|
| `@brd: BRD.01.01.01` | BRD doc 1, FR #1 | Functional requirement reference |
| `@prd: PRD.02.07.05` | PRD doc 2, User Story #5 | User story reference |
| `@adr: ADR.03.10.01` | ADR doc 3, Decision #1 | Architecture decision reference |
| `@spec: SPEC.01.15.02` | SPEC doc 1, Interface #2 | Interface specification reference |

### AI-First Design Rationale

This format is optimized for AI-assisted documentation workflows:

1. **Token efficiency**: 12 chars minimum vs 15+ for human-readable formats
2. **AI translation**: Human asks "what is BRD.01.03.05?", AI responds "Constraint #5: Budget limit $50K"
3. **Single regex pattern**: `[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}` validates all types
4. **Zero capacity planning**: Grows automatically without range management
5. **Consistent parsing**: Same pattern across all 12+ document types

### DEPRECATED Formats (do NOT use)

| Deprecated | Replacement | Notes |
|------------|-------------|-------|
| `BRD-017:001` | `BRD.17.01.01` | Colon separator removed |
| `FR-001` | `BRD.01.01.01` | Type-specific prefixes removed |
| `BC-001` | `BRD.01.03.01` | Use element type code 03 |
| `BA-001` | `BRD.01.04.01` | Use element type code 04 |
| `AC-001` | `BRD.01.06.01` | Use element type code 06 |
| `DEP-001` | `BRD.01.05.01` | Use element type code 05 |
| `QA-001` | `BRD.01.02.01` | Use element type code 02 |

---

## Internal Feature Heading Format (MANDATORY)

**Purpose**: All internal feature/requirement headings within documents MUST use the unified 4-segment format for:

1. Direct searchability across all documents
2. Consistency between internal headings and external cross-references
3. Element type identification without lookup

**Internal Heading Pattern**:

| Document Type | Heading Format | Example |
|---------------|----------------|---------|
| BRD | `### BRD.NN.TT.SS: Name` | `### BRD.01.01.01: Market Data Feed` |
| PRD | `### PRD.NN.TT.SS: Name` | `### PRD.02.07.01: User Dashboard` |
| EARS | `### EARS.NN.TT.SS: Name` | `### EARS.01.01.01: Data Validation` |
| BDD | `### BDD.NN.TT.SS: Name` | `### BDD.01.13.01: Login Scenario` |
| SYS | `### SYS.NN.TT.SS: Name` | `### SYS.01.01.01: API Gateway` |
| ADR | `### ADR.NN.TT.SS: Name` | `### ADR.01.10.01: Database Selection` |

**Format Breakdown**:

| Component | Description | Example |
|-----------|-------------|---------|
| `TYPE` | Document type in SDD framework | `BRD`, `PRD`, `ADR`, `SPEC` |
| `.NN` | Document number (2+ digits) | `.01` = document 1 |
| `.TT` | Element type code (see table above) | `.01` = Functional Requirement |
| `.SS` | Sequential within element type | `.01` = first item of this type |

**Example**: `BRD.01.03.05` = BRD document 01, Constraint (type 03), item #5

**Validation Regex**:

```python
INTERNAL_HEADING_PATTERN = r'^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$'
# Matches: ### BRD.01.01.01: Feature Name
```

**REMOVED Patterns (v3.0 - No Backward Compatibility)**:

The following patterns are **REMOVED** and MUST NOT be used:

| Removed Pattern | Previous Usage | Migration Path |
|-----------------|----------------|----------------|
| `FR-XXX` | BRD feature headings | Use `### BRD.NN.01.SS: Feature` |
| `BC-XXX` | Business Constraints | Use `### BRD.NN.03.SS: Constraint` |
| `BA-XXX` | Business Assumptions | Use `### BRD.NN.04.SS: Assumption` |
| `QA-XXX` | Quality Attributes | Use `### BRD.NN.02.SS: Quality` |
| `TYPE.NN.EE.SS` | 3-segment format | Use `TYPE.NN.TT.SS` (4-segment) |
| `Feature F-XXX` | PRD feature headings | Use `### PRD.NN.07.SS: User Story` |

**Migration Examples**:

| Before (REMOVED) | After (MANDATORY) |
|------------------|-------------------|
| `#### FR-001: Recipient Selection` | `### BRD.01.01.01: Recipient Selection` |
| `#### BC-003: Budget Limit` | `### BRD.01.03.03: Budget Limit` |
| `### BRD.017.001: Feature` | `### BRD.17.01.01: Feature` |
| `### Feature F-001: User Dashboard` | `### PRD.01.07.01: User Dashboard` |

---

## Architecture Decision Topic Subsection Format

**Purpose**: Document Section 7.2 "Architecture Decision Requirements" contains numbered subsections identifying architectural topics requiring formal ADR decisions. These use the standard 4-segment format with element type code `10` (Decision).

**Subsection ID Pattern**: `{DOC_TYPE}.NN.10.SS` (using Decision element type)

| Component | Description | Example |
|-----------|-------------|---------|
| `{DOC_TYPE}` | Document type (BRD, PRD, etc.) | `BRD` |
| `.NN` | Document number (2+ digits) | `.01` = BRD-01 |
| `.10` | Element type code for Decision | `.10` = Decision type |
| `.SS` | Sequential topic number | `.03` = third topic |

**Heading Format**:

```markdown
#### BRD.01.10.03: [Topic Name]

**Business Driver**: [Why this decision matters to business - reference upstream requirements]
**Business Constraints**:
- [Non-negotiable business rule 1]
- [Non-negotiable business rule 2]
**PRD Requirements**: [What PRD must elaborate for THIS topic - technical options, evaluation criteria, performance benchmarks]
```

**Note**: Heading level varies by context (H3-H5) depending on document structure. The pattern uses H4 (`####`) in BRD Section 7.2 as subsections.

**Examples**:

| Document | Topic # | Full ID | Meaning |
|----------|---------|---------|---------|
| BRD-01 | 3 | `BRD.01.10.03` | Third architecture decision topic in BRD-01 |
| BRD-17 | 1 | `BRD.17.10.01` | First architecture decision topic in BRD-17 |
| BRD-03 | 12 | `BRD.03.10.12` | Twelfth architecture decision topic in BRD-03 |

**Content Rules (Business-Only)**:

| Include in Section 7.2 | Exclude from Section 7.2 |
|------------------------|--------------------------|
| Business objectives | Technology options |
| Regulatory constraints | Performance specifications |
| Non-negotiable business rules | Evaluation criteria |
| Business impact statements | Implementation patterns |

**Cross-Reference Flow**:

```text
BRD Section 7.2 (BRD.NN.10.SS)  →  PRD Section 18           →  ADR
Business drivers/constraints        Technical options/criteria    Final decision
```

**PRD Reference**: PRD Section 18 elaborates each BRD Section 7.2 topic with:

- `**Upstream**: BRD.NN.10.SS` - Reference to originating BRD topic
- Technical options and evaluation criteria
- `**ADR Requirements**: [guidance]` - What ADR must decide for this topic

**ADR Reference**: ADR Section 4.1 includes:

- `**Originating Topic**: BRD.NN.10.SS - [Topic Name]`
- Business driver and constraints from BRD
- Technical options evaluated from PRD

**Validation Regex**:

```python
ARCHITECTURE_TOPIC_PATTERN = r'^#{3,5}\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$'
# Matches: ### BRD.01.10.03: ... OR #### PRD.17.10.01: ...
# Heading level (H3-H5) varies by document section context
```

---

## Complete Tag Reference

For the complete list of valid traceability tags, see [TRACEABILITY.md - Complete Tag Reference](./TRACEABILITY.md#complete-tag-reference).

**Quick Reference:**

- **Document Type Tags**: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@impl`, `@ctr`, `@spec`, `@tasks`, `@iplan`
- **Non-Document Tags**: `@test`, `@code`, `@impl-status`, `@icon`, `@icon-role`, `@threshold`, `@entity`, `@priority`, `@component`, `@supersedes`
- **Same-Type Tags**: `@related-{type}`, `@depends-{type}`
- **Invalid Tags**: `@nfr:`, `@fr:`, `@contract:`, `@tests:` (deprecated, do NOT use)

---

## Checklist

- H1 titles contain IDs for PRD/SYS/EARS/REQ/ADR/CTR/IMPL/TASKS/BRD where applicable (use `TYPE-NNN` or `TYPE-NNN-YY` format).
- BDD tags are markdown links with valid relative paths and anchors (supports both NNN and NNN-YY patterns).
- Spec files named `SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml`; inside, `id:` is snake_case and used by `@spec` tags; `requirements_source`/`architecture`/`verification` links resolve.
- All document types follow universal numbering pattern: NNN = 3-4 digits (001-999, 1000+), YY = 2-3 digits [OPTIONAL] (01-99, 100+).
- No ID collisions: each NNN number used only once (either atomic TYPE-NNN OR multi-doc TYPE-NNN-YY group, never both).
- Internal feature IDs use simple sequential numbering (001, 002, 003) within each document.
- Run `python scripts/validate_requirement_ids.py` and fix any violations before committing.
