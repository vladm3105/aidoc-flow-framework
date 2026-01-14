---
title: "AI Dev Flow - Universal Specification-Driven Development Framework"
tags:
  - index-document
  - shared-architecture
custom_fields:
  document_type: readme
  priority: shared
---

# AI Dev Flow - Universal Specification-Driven Development Framework

**Purpose**: Enable AI-assisted software development across any project domain through structured, traceable requirements and specifications.

**Status**: Production-ready framework with generic templates, domain adaptation guidance, cumulative tagging hierarchy, and automated validation tooling.

**Version**: 2.2 | **Last Updated**: 2025-11-30

## Overview

This directory provides a **universal, reusable framework** for Specification-Driven Development (SDD), transforming business needs into production-ready code through a systematic, traceable workflow.

### Framework Purpose

This framework is a sophisticated and well-conceived system for a new paradigm of software development where human architects design systems and AI assistants build them.

- The Architect's Blueprint: The initial layers (BRD, PRD, ADR, SYS) serve as the formal blueprint created by the software architect. This is where human expertise in system design, architectural trade-offs, and business strategy is captured.

- The AI's Instruction Set: The subsequent layers (REQ, SPEC, TASKS) act as a detailed, unambiguous instruction set automatically derived from the architect's blueprint. This breakdown translates high-level architectural decisions into granular tasks that are ideal for consumption by an AI code generator.

- The Governance and Audit Layer: The framework's most critical function is providing a robust governance and audit mechanism. The full traceability chain, from BRD to TASKS and IPLAN, creates an unimpeachable record of the AI's intended actions. This allows the architect to:
  1. Verify Compliance: Ensure the AI's generated code adheres strictly to the established architectural and business rules.
  2. Mitigate AI Risk: Audit the AI's plans to prevent hallucinations or unintended features before code is even written.
  3. Validate at a High Level: Confirm the success of the project by reviewing BDD test results and traceability matrices, rather than performing a line-by-line code review.

### Why AI Dev Flow?

**Traditional Development Challenges**:
- Requirements drift from implementation over time
- Manual traceability is incomplete and outdated
- Inconsistent documentation across teams
- AI code generation requires unstructured guidance

**AI Dev Flow Solutions**:
- ✅ **Domain-Agnostic**: Adaptable to any software project (e-commerce, SaaS, IoT, healthcare, finance)
- ✅ **Complete Traceability**: Bidirectional links from business requirements to production code
- ✅ **Cumulative Tagging Hierarchy**: Each artifact includes tags from ALL upstream layers for complete audit trails
- ✅ **AI-Optimized**: YAML specifications designed for deterministic code generation
- ✅ **16-Layer Architecture**: Structured progression from strategy through validation
 - ✅ **Dual-File Contracts (CTR only)**: Human-readable `.md` + machine-readable `.yaml` for API Contracts
- ✅ **Strict ID Standards**: Consistent naming and organization across all documents
- ✅ **Example-Driven**: Generic examples with `[PLACEHOLDER]` format for easy customization
- ✅ **Automated Validation**: Scripts for tag validation, traceability matrix generation, cumulative hierarchy enforcement

**📚 New to this framework?** Start with [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) for domain-specific guidance (financial, healthcare, e-commerce, SaaS, IoT, or generic software).

## Using This Repo

- Docs root: In this repository, artifact folders (`01_BRD/`, `02_PRD/`, `03_EARS/`, `04_BDD/`, `05_ADR/`, `06_SYS/`, `07_REQ/`, `08_IMPL/`, `09_CTR/`, `10_SPEC/`, `11_TASKS/`, `12_IPLAN/`, `ICON/`, `CHG/`) live at the `ai_dev_flow/` root. Many guides show a top-level `docs/` prefix for portability; when running commands here, drop the `docs/` prefix.
- BDD layout: Uses nested per-suite folders `04_BDD/BDD-NN_{slug}/` with sectioned `.feature` files.
- Index width: This repo commonly uses `-00_index.md` for indices; follow existing width and do not rename history. New repos should choose a consistent zero width (`00` or `000`) and keep it stable.
- Validators: Use the validators listed in TRACEABILITY_VALIDATION.md (e.g., `python scripts/validate_prd.py`, `./scripts/validate_req_template.sh`). Older `*_template.sh` examples in some guides have been updated here.
- Path mapping example: `docs/02_PRD/PRD-01/...` in generic guides corresponds to `02_PRD/PRD-01/...` in this repo.

### Default Starting Point: MVP Templates (FRAMEWORK DEFAULT)

**MVP templates are the FRAMEWORK DEFAULT for all new document creation.** The framework automatically uses MVP templates unless explicitly configured otherwise.

#### Why MVP is Default
- **Faster iteration**: Streamlined templates for rapid development
- **Reduced overhead**: Fewer required sections, relaxed validation
- **Full traceability**: Same traceability chain as full templates
- **Easy upgrade path**: Migrate to full templates when needed

#### Available MVP Templates (Layers 1-7)
| Layer | Artifact | Default Template |
|-------|----------|-----------------|
| 1 | BRD | `BRD-MVP-TEMPLATE.md` |
| 2 | PRD | `PRD-MVP-TEMPLATE.md` |
| 3 | EARS | `EARS-MVP-TEMPLATE.md` |
| 4 | BDD | `BDD-MVP-TEMPLATE.feature` |
| 5 | ADR | `ADR-MVP-TEMPLATE.md` |
| 6 | SYS | `SYS-MVP-TEMPLATE.md` |
| 7 | REQ | `REQ-MVP-TEMPLATE.md` |

Layers 8-15 use full templates only (no MVP variants).

#### Switching to Full Templates

**Option 1 - Project Setting** (persistent):
```yaml
# In .autopilot.yaml or CLAUDE.md
template_profile: enterprise  # or "full" or "strict"
```

**Option 2 - Prompt Keyword** (per-request):
Say any of: "use full template", "enterprise mode", "regulatory compliance", "comprehensive template"

**Option 3 - Direct Reference** (explicit):
"Create BRD-01 using BRD-TEMPLATE.md" (specify full template by name)

#### Validation Profile
Validators support relaxed MVP validation via `template_profile: mvp` in frontmatter. Set `template_profile: enterprise` for strict validation.

### Units & Conversions (KB vs tokens)

- KB: 1 KB = 1,024 bytes (OS file size).
- Tokens: ~4 characters per token on average (≈0.75 words).
- Estimate tokens from size: tokens ≈ (KB × 1024) ÷ 4.
  - Examples: 10 KB ≈ 2,500 tokens; 20 KB ≈ 5,000; 50 KB ≈ 12,500.
- Estimate size from tokens: KB ≈ (tokens × 4) ÷ 1024.
  - Examples: 10,000 tokens ≈ 39 KB; 50,000 tokens ≈ 195 KB.
- Caveats: Code/JSON and non‑ASCII text increase token counts; tools may compress inputs.

### ID Numbering Rule (Unified)

- Start with 2 digits and expand only as needed; avoid unnecessary leading zeros.
- Correct: `BRD-01`, `BRD-99`, `BRD-102`, `BRD-999`, `BRD-1000`.
- Incorrect: `BRD-001`, `BRD-009`.
- Unified across all doc types: BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS, IPLAN (and ICON).
- Element IDs must match filename digit width (e.g., `BRD-06` ↔ `BRD.06.xx.xx`).
- Reserved infra docs may use `-000` (e.g., `BRD-00_index.md`). Source code and tests follow coding standards, not this rule.
- See details in [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md).

### Index File Digit Width by Artifact Type

This repository uses consistent **2-digit width** (`00`) for all index files across all artifact types.

| Artifact Type | Index File Format | Width | Example |
|---------------|-------------------|-------|---------|
| BRD | BRD-00_index.md | 2-digit | `BRD-00_index.md` |
| PRD | PRD-00_index.md | 2-digit | `PRD-00_index.md` |
| EARS | EARS-00_index.md | 2-digit | `EARS-00_index.md` |
| BDD | BDD-00_index.md | 2-digit | `BDD-00_index.md` |
| ADR | ADR-00_index.md | 2-digit | `ADR-00_index.md` |
| SYS | SYS-00_index.md | 2-digit | `SYS-00_index.md` |
| REQ | REQ-00_index.md | 2-digit | `REQ-00_index.md` |
| IMPL | IMPL-00_index.md | 2-digit | `IMPL-00_index.md` |
| CTR | CTR-00_index.md | 2-digit | `CTR-00_index.md` |
| SPEC | SPEC-00_index.md | 2-digit | `SPEC-00_index.md` |
| TASKS | TASKS-00_index.md | 2-digit | `TASKS-00_index.md` |
| ICON | ICON-00_index.md | 2-digit | `ICON-00_index.md` |
| IPLAN | IPLAN-00_index.md | 2-digit | `IPLAN-00_index.md` |

**Policy for New Repositories**:
- Choose either 2-digit (`00`) or 3-digit (`000`) width consistently
- Apply the same width across ALL artifact types in the project
- Do NOT mix widths (e.g., BRD-00 with PRD-000)
- Once chosen, keep stable throughout project lifetime

## Metadata Management in AI Dev Flow

AI Dev Flow uses **dual metadata approaches** to serve both human and machine audiences:

### 1. YAML Frontmatter (Machine-Readable)

**Purpose**: Enables tooling integration, automated validation, and documentation site generation (e.g., Docusaurus).

**Location**: Top of markdown files, enclosed in `---` markers.

**Required in**: All templates, index files, and published documentation artifacts.

**Example**:
```yaml
---
title: "BRD-02: Partner Ecosystem Integration"
tags:
  - platform-brd
  - shared-architecture
  - layer-1-artifact
custom_fields:
  document_type: brd
  artifact_type: BRD
  layer: 1
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---
```

### 2. Document Control Tables (Human-Readable)

**Purpose**: Provide version history, authorship, and approval tracking for human reviewers.

**Location**: "Document Control" section within markdown body (typically section 1).

**Required in**: All production documents (BRD through IPLAN).

**Example**:
```markdown
## Document Control

| Item | Details |
|------|---------|
| Document ID | BRD-02 |
| Version | 1.2.0 |
| Status | Approved |
| Author | Product Team |
| Last Updated | 2025-11-15 |
| Approved By | Chief Product Officer |
```

### 3. Metadata vs. Traceability Tags

**IMPORTANT**: Metadata (YAML frontmatter) is DIFFERENT from traceability tags (`@artifact: ID`).

| Aspect | YAML Frontmatter | Traceability Tags |
|--------|------------------|-------------------|
| **Purpose** | Document classification, tooling | Audit trail, compliance |
| **Location** | Top of file (lines 1-20) | section 7 (body) |
| **Format** | YAML key-value pairs | `@artifact: ID (Description)` |
| **Validation** | `validate_metadata.py` | `scripts/validate_tags_against_docs.py` |
| **Changeability** | Can be updated | Immutable after approval |

**Learn More**:
- [METADATA_VS_TRACEABILITY.md](./METADATA_VS_TRACEABILITY.md) - Quick reference comparing both systems
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md#metadata-management-approaches) - Detailed methodology
- [scripts/validate_metadata.py](./scripts/validate_metadata.py) - YAML validation tool

**Validation**:
```bash
# Validate YAML frontmatter
python3 scripts/validate_metadata.py .

# Validate traceability tags locally
# See `scripts/validate_tags_against_docs.py`, `scripts/validate_traceability_matrix.py`, and `scripts/validate_cross_document.py`
```

## Complete Development Workflow

**⚠️ See [index.md](./index.md#traceability-flow) for the authoritative workflow diagram with full Mermaid visualization.**

#### SDD Workflow Overview

```mermaid
flowchart LR
    BRD[BRD<br/>Layer 1] --> PRD[PRD<br/>Layer 2]
    PRD --> EARS[EARS<br/>Layer 3]
    EARS --> BDD[BDD<br/>Layer 4]
    BDD --> ADR[ADR<br/>Layer 5]
    ADR --> SYS[SYS<br/>Layer 6]
    SYS --> REQ[REQ<br/>Layer 7]
    REQ --> IMPL[IMPL<br/>Layer 8]
    IMPL --> CTR[CTR<br/>Layer 9]
    CTR --> SPEC[SPEC<br/>Layer 10]
    SPEC --> TASKS[TASKS<br/>Layer 11]
    TASKS --> IPLAN[IPLAN<br/>Layer 12]
    IPLAN --> Code[Code<br/>Layer 13]
    Code --> Tests[Tests<br/>Layer 14]
    Tests --> Val[Validation<br/>Layer 15]
```

### Splitting Rules

- Core: [DOCUMENT_SPLITTING_RULES.md](./DOCUMENT_SPLITTING_RULES.md)
- BDD addendum: [BDD/BDD_SPLITTING_RULES.md](./04_BDD/BDD_SPLITTING_RULES.md)
- CTR addendum: [CTR/CTR_SPLITTING_RULES.md](./09_CTR/CTR_SPLITTING_RULES.md)
- SPEC addendum: [SPEC/SPEC_SPLITTING_RULES.md](./10_SPEC/SPEC_SPLITTING_RULES.md)
- Templates: Use `{TYPE}-SECTION-0-TEMPLATE.md` (index) and `{TYPE}-SECTION-TEMPLATE.md` (sections)

### 16-Layer Architecture with Cumulative Tagging

The AI Dev Flow transforms business requirements into production code through a structured, traceable workflow. Each layer includes cumulative tags from ALL upstream layers, creating complete audit trails for regulatory compliance (regulatory, FDA, ISO).

| Layer | Artifact | Purpose | Tags Required | Key Decision |
|-------|----------|---------|---------------|--------------|
| **0** | Strategy | External business strategy documents | 0 | Strategic direction |
| **1** | BRD | Business objectives and market context | 0 (top level) | WHAT needs to be built |
| **2** | PRD | Product features and user stories | @brd (1) | Product capabilities |
| **3** | EARS | Measurable event-driven requirements | @brd, @prd (2) | Formal requirements |
| **4** | BDD | Executable acceptance tests (Gherkin) | @brd→@ears (3+) | HOW to verify success |
| **5** | ADR | Architectural decisions and rationale | @brd→@bdd (4) | TECHNICAL approach |
| **6** | SYS | System-level requirements | @brd→@adr (5) | System specifications |
| **7** | REQ | Atomic, testable requirements | @brd→@sys (6) | GRANULAR specifications |
| **8** | IMPL | Implementation plans (optional) | @brd→@req (7) | WHO/WHEN to build |
| **9** | CTR | API contracts (optional) | @brd→@impl (8) | INTERFACE definitions |
| **10** | SPEC | YAML technical specifications | @brd→@req (+optional) (7-9) | HOW to build |
| **11** | TASKS | Implementation task breakdown | @brd→@spec (8-10) | EXACT TODOs |
| **11 (shared, optional)** | ICON | Implementation contracts | @brd→@spec (8-10) | Interface definitions |
| **12** | IPLAN | Session-specific plans | @brd→@tasks (9-11) | Session work scope |
| **13** | Code | Source code implementation | @brd→@tasks (9-11) | RUNNABLE artifacts |
| **14** | Tests | Test suite implementation | @brd→@code (10-12) | Quality validation |
| **15** | Validation | Production readiness verification | All upstream (10-15) | PRODUCTION-READY |

**Note**: Layers 8 (IMPL) and 9 (CTR) are optional - include only when needed for project management or API contracts.

#### 16-Layer Architecture Diagram

```mermaid
graph TB
    subgraph "Strategic Layer 0"
        L0[Strategy & Vision]
    end
    subgraph "Business Layers 1-2"
        L1[BRD - Business Requirements]
        L2[PRD - Product Requirements]
    end
    subgraph "Requirements Layers 3-7"
        L3[EARS - Formal Requirements]
        L4[BDD - Behavior Scenarios]
        L5[ADR - Architecture Decisions]
        L6[SYS - System Requirements]
        L7[REQ - Atomic Requirements]
    end
    subgraph "Design Layers 8-10"
        L8[IMPL - Implementation Approach]
        L9[CTR - Contracts/APIs]
        L10[SPEC - Technical Specs]
    end
    subgraph "Implementation Layers 11-15"
        L11[TASKS - Task Breakdown]
        L12[IPLAN - Session Plans]
        L13[Code - Source Code]
        L14[Tests - Test Suite]
        L15[Validation - Quality Gates]
    end

    L0 --> L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    L7 --> L8 --> L9 --> L10 --> L11 --> L12 --> L13 --> L14 --> L15
```

#### Layer Numbering Explained

The 16-layer architecture uses the following structure:

- **Layer 0**: Strategy (pre-artifact foundational layer)
  - Product strategy documents, market analysis, vision statements
  - No formal artifact type, no traceability tags

- **Layers 1-12**: Formal Documentation Artifacts
  - Layer 1: BRD (Business Requirements)
  - Layer 2: PRD (Product Requirements)
  - Layer 3: EARS (Event-Action-Response-State) — Engineering Requirements
  - Layer 4: BDD (Behavior-Driven Development)
  - Layer 5: ADR (Architecture Decision Records)
  - Layer 6: SYS (System Architecture)
  - Layer 7: REQ (Requirements Specifications)
  - Layer 8: IMPL (Implementation Specifications) - optional
  - Layer 9: CTR (Contracts) - optional
  - Layer 10: SPEC (Technical Specifications)
  - Layer 11: TASKS (Task Breakdowns)
  - Layer 12: IPLAN (Implementation Work Plans)

- **Layers 13-15**: Execution Layers
  - Layer 13: Code (source code files)
  - Layer 14: Tests (test implementations)
  - Layer 15: Validation (test results, metrics)

**Important Note on Layer Numbering:**
- **Formal layer numbers (0-15)**: Used in cumulative tagging, templates, and specifications
- **Mermaid diagram groupings**: May use simplified labels (L1-L11) for visual organization
- **Always use formal layer numbers** when implementing cumulative tagging or referencing layers in documentation
- Mermaid subgraph labels (e.g., "Layer 1 - Business") are visual groupings that may combine multiple formal layers for diagram clarity

### Layer Numbering Reference

#### Formal Layer Numbers (Use in Code/Tags/Documentation)

| Layer | Artifact Type | Purpose |
|-------|---------------|---------|
| 0 | Strategy (STRAT) | Strategic business direction |
| 1 | Business Requirements (BRD) | Business needs and goals |
| 2 | Product Requirements (PRD) | Product features and specifications |
| 3 | EARS | Engineering Requirements (Event-Action-Response-State) |
| 4 | BDD | Behavior-driven test scenarios |
| 5 | Architecture Decisions (ADR) | Technical architecture choices |
| 6 | System Requirements (SYS) | System-level specifications |
| 7 | Requirements (REQ) | Atomic requirements |
| 8 | Implementation Specifications (IMPL) | Project management plans |
| 9 | Contracts (CTR) | Interface contracts (dual-file format) |
| 10 | Specifications (SPEC) | Detailed technical specs |
| 11 | Tasks (TASKS) | Development task breakdown |
| 12 | Implementation Work Plans (IPLAN) | Session execution plans |
| 13 | Code | Actual implementation |
| 14 | Tests | Unit/integration tests |
| 15 | Validation | End-to-end validation |

Note: ICON (Implementation Contracts) is an optional artifact that shares Layer 11 alongside TASKS. ICON provides standalone implementation contracts when needed for parallel development.

Important: “Review” and “Production” are outcomes, not formal layers. The formal model is fixed at Layers 0–15.

#### Mermaid Diagram Visual Groupings (L1-L11)

Diagrams use simplified labels for visual clarity:

- **L1**: Business Layer (contains Layers 1-3: BRD, PRD, EARS)
- **L2**: Testing Layer (contains Layer 4: BDD)
- **L3**: Architecture Layer (contains Layers 5-6: ADR, SYS)
- **L4**: Requirements Layer (contains Layer 7: REQ)
- **L5**: Project Management (contains Layer 8: IMPL)
- **L6**: Interface Layer (contains Layer 9: CTR)
- **L7**: Technical Specs (contains Layer 10: SPEC)
- **L8**: Code Generation (contains Layer 11: TASKS)
- **L9**: Session Planning (contains Layer 12: IPLAN)
- **L10**: Code Layer (contains Layer 13: Code)
- **L11**: Validation Layer (contains Layers 14-15: Tests, Validation)

**Important**: Always use formal layer numbers (0-15) in:
- Cumulative tagging implementations
- Documentation references
- Code comments
- Traceability matrices

### Critical Decision Point

**After IMPL (Project Management Layer)**:
- **Interface requirement** (API, event schema, data model) → Create **CTR** (API Contract) → then **SPEC**
- **No interface requirement** (internal logic, business rules) → Create **SPEC** directly

**CTR Format**: Dual-file contract with human-readable `.md` (context, traceability) + machine-readable `.yaml` (OpenAPI/AsyncAPI schema)

#### Critical Decision Point Diagram

```mermaid
flowchart TD
    REQ[REQ - Atomic Requirements] --> IMPL[IMPL - Implementation Approach]
    IMPL --> Decision{Interface<br/>Required?}
    Decision -->|Yes| CTR[CTR - API Contracts]
    Decision -->|No| SPEC[SPEC - Technical Specs]
    CTR --> SPEC
    SPEC --> TASKS[TASKS - Task Breakdown]
```

## Template Directories

<!-- See “Using This Repo” above for path mapping guidance. -->

### Business Layer

**BRD/** - Business Requirements Documents
- High-level business objectives and market context
- Strategic goals and success criteria
- **Files**: [BRD-00_index.md](./01_BRD/BRD-00_index.md) | [Template](./01_BRD/BRD-TEMPLATE.md) | **MVP**: [BRD-MVP-TEMPLATE.md](./01_BRD/BRD-MVP-TEMPLATE.md)

**PRD/** - Product Requirements Documents
- User-facing features and product capabilities
- Business requirements and acceptance criteria
- **Files**: [PRD-00_index.md](./02_PRD/PRD-00_index.md) | [Template](./02_PRD/PRD-TEMPLATE.md) | **MVP**: [PRD-MVP-TEMPLATE.md](./02_PRD/PRD-MVP-TEMPLATE.md)

**EARS/** - Event-Action-Response-State (Engineering Requirements)
- Measurable requirements using WHEN-THE-SHALL-WITHIN format
- Event-driven and state-driven requirements
- **Files**: [EARS-00_index.md](./03_EARS/EARS-00_index.md) | [Template](./03_EARS/EARS-TEMPLATE.md)

### Testing Layer

**BDD/** - Behavior-Driven Development Scenarios
- Executable acceptance tests in Gherkin format
- Business-readable behavioral specifications
- **Files**: [BDD-00_index.md](./04_BDD/BDD-00_index.md) | Main template: [BDD-TEMPLATE.feature](./04_BDD/BDD-TEMPLATE.feature) | Section templates: `BDD-SECTION-TEMPLATE.feature`, `BDD-SUBSECTION-TEMPLATE.feature`, `BDD-AGGREGATOR-TEMPLATE.feature`

### Architecture Layer

**ADR/** - Architecture Decision Records
- Architectural choices and rationale
- Technology selections and trade-offs
- **Files**: [ADR-00_index.md](./05_ADR/ADR-00_index.md) | [Template](./05_ADR/ADR-TEMPLATE.md) | **MVP**: [ADR-MVP-TEMPLATE.md](./05_ADR/ADR-MVP-TEMPLATE.md)

**SYS/** - System Requirements Specifications
- System-level functional requirements and quality attributes
- Performance, security, and operational characteristics
- **Files**: [SYS-00_index.md](./06_SYS/SYS-00_index.md) | [Template](./06_SYS/SYS-TEMPLATE.md) | **MVP**: [SYS-MVP-TEMPLATE.md](./06_SYS/SYS-MVP-TEMPLATE.md)

### Requirements Layer

**REQ/** - Atomic Requirements
- Granular, testable requirements with acceptance criteria
- Organization: Nested per-document folders (DEFAULT for all types)
  - Folder: `REQ/REQ-NN_{slug}/`
  - Primary file (atomic): `REQ/REQ-NN_{slug}/REQ-NN_{slug}.md`
  - Split (optional when large): index + sections `REQ/REQ-NN_{slug}/REQ-NN.0_index.md`, `REQ/REQ-NN.1_{section}.md`, ...
- Files: [REQ-00_index.md](./07_REQ/REQ-00_index.md) | [Template](./07_REQ/REQ-TEMPLATE.md) | **MVP**: [REQ-MVP-TEMPLATE.md](./07_REQ/REQ-MVP-TEMPLATE.md)

### Project Management Layer

**IMPL/** - Implementation Specifications (Layer 8)
- Project management documents organizing work into phases, teams, deliverables
- **Focus**: WHO does WHAT, WHEN - NOT technical specifications (HOW)
- Identifies which CTR, SPEC, TASKS to create
- **Files**: [IMPL-00_index.md](./08_IMPL/IMPL-00_index.md) | [Template](./08_IMPL/IMPL-TEMPLATE.md)
- **Examples**: [IMPL-01_feature_implementation_example.md](./08_IMPL/examples/IMPL-01_feature_implementation_example.md)

### Interface Layer

**CTR/** - API Contracts (CTR)
- Formal interface specifications for component-to-component communication
- **Dual-file format**:
  - `.md` file: Human-readable context, business rationale, traceability links
  - `.yaml` file: Machine-readable schema (OpenAPI/AsyncAPI/JSON Schema)
- **When to use**: Created when REQ specifies interface requirements (APIs, events, data models)
- **Benefits**: Enables parallel development and contract testing
- **Files**: [CTR-00_index.md](./09_CTR/CTR-00_index.md) | [Template .md](./09_CTR/CTR-TEMPLATE.md) + [Template .yaml](./09_CTR/CTR-TEMPLATE.yaml)
- **Examples**: [CTR-01_service_contract_example.md](./09_CTR/CTR-01_service_contract_example.md) + [CTR-01_service_contract_example.yaml](./09_CTR/CTR-01_service_contract_example.yaml)

### Technical Specs (SPEC)

**SPEC/** - Technical Specifications
- YAML: Monolithic per component (code generation source)
- Markdown: Split narrative with `SPEC-{DOC_NUM}.0_index.md` and `SPEC-{DOC_NUM}.{S}_{slug}.md` when needed
- References CTR contracts when implementing interfaces
- **Files**: [SPEC-00_index.md](./10_SPEC/SPEC-00_index.md) | [Template](./10_SPEC/SPEC-TEMPLATE.yaml)
- **Examples**: [SPEC-01_api_client_example.yaml](./10_SPEC/SPEC-01_api_client_example.yaml)

### Code Generation Layer

**TASKS/** - Code Generation Plans (TASKS)
- Exact TODOs to implement SPEC in source code
- Step-by-step guide for AI code generation from YAML specifications
- **1:1 mapping**: Each TASKS document corresponds to one SPEC
- **Files**: [TASKS-00_index.md](./11_TASKS/TASKS-00_index.md) | [Template](./11_TASKS/TASKS-TEMPLATE.md)

### Implementation Contracts (Optional, Layer 11)

**ICON/** - Implementation Contracts (Layer 11, Optional; shares with TASKS)
- Type-safe interface definitions for parallel development coordination
- Protocol interfaces, exception hierarchies, state machines, data models
- **When to use**: 5+ consumer TASKS, >500 lines, platform-level, cross-project
- **Default**: Embed contracts in TASKS section 8 unless criteria met
- **Files**: [ICON-00_index.md](./ICON/ICON-00_index.md) | [Template](./ICON/ICON-TEMPLATE.md)
- **Guide**: [IMPLEMENTATION_CONTRACTS_GUIDE.md](./11_TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md)

### 9. Session Planning Layer

**IPLAN/** - Implementation Work Plans (Layer 12)
- Organize multiple TASKS into session-scoped work packages
- Track progress across related implementation units
- Maintain context between AI coding sessions
- **Files**: Session plans saved via `/save-plan` command

## Document ID Standards

### Scope: Documentation Artifacts Only

**IMPORTANT**: These ID naming standards apply ONLY to **documentation artifacts** in the SDD workflow, NOT to source code files.

#### ✅ Apply To (Documentation):
- Documents in `docs/` directories: BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS, ICON
- BDD feature files (`.feature` format) in `tests/bdd/` directories

#### ❌ Do NOT Apply To (Source Code):
- **Python files**: Follow PEP 8 conventions (`snake_case.py`, `PascalCase` classes)
- **Test files**: Follow pytest conventions (`test_*.py`, `test_*()` functions)
- **Other languages**: Follow language-specific style guides (Java, JavaScript, Go, etc.)

### Documentation Naming Format

Format: `{TYPE}-{NN}_{descriptive_slug}.{ext}`
Note: `NN` denotes a variable-width 2+ digit number (e.g., 01, 12, 105, 1002).

- **TYPE**: Document type prefix (BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS)
- **NNN**: 2+ digit sequence number (01, 02, 03, 100); examples and placeholders may show `NN` to indicate variable width
- **descriptive_slug**: snake_case description
- **ext**: File extension (md, feature, yaml)

Examples:
- `PRD-01_external_api_integration.md`
- `BDD-03.2_risk_limits_requirements.feature`
- `CTR-01_data_validation.md` + `CTR-01_data_validation.yaml` (dual-file format)
- `SPEC-42_real_time_processor.yaml`

**Note**: CTR (API Contracts) requires both `.md` and `.yaml` files with matching slugs.

See [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) for complete rules.

Index Width Policy (This Repository): Index, registry, and general utility documents use `-000` (e.g., `-00_index.md`). Follow the existing width per type in this repo and do not rename historical files. For new repositories, pick a consistent zero width (`00` or `000`) and keep it stable.

General Utility Documents (`{DOC_TYPE}-00_*`): Use `{DOC_TYPE}-00_{slug}.{ext}` for general-purpose or cross-project documents (guides, templates, matrices) that are not tied to a specific numbered artifact.

### Feature-Level Traceability Tags

Internal feature IDs within documents use 3-digit sequential numbering with unified format for globally unique traceability.

| Context | Internal ID | Unified Format | Cross-Reference |
|---------|-------------|----------------|-----------------|
| PRD Features | `001`, `015`, `042` | `PRD.22.01.15` | `@prd: PRD.22.01.15` |
| BRD Objectives | `030`, `006` | `BRD.01.01.30` | `@brd: BRD.01.01.30` |
| EARS Statements | `003`, `007` | `EARS.06.24.03` | `@ears: EARS.06.24.03` |
| SYS Requirements | `001`, `015` | `SYS.08.25.01` | `@sys: SYS.08.25.01` |
| Quality Attributes | `016`, `017` | `SYS.08.25.16` | `@sys: SYS.08.25.16` |

**Format**: `@type: TYPE.NN.TT.SS` (dot separator for all references)

**Examples**:
```markdown
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS-NN
@sys: SYS-NN
@sys: SYS-NN  # Quality attributes may use unified sequential numbering
```

**Global Uniqueness**: `TYPE.NN.TT.SS` format creates globally unique references (e.g., `PRD.22.01.15` is unique across all documents).

Note on ADR references:
- Use `ADR-NN` for document-level references (e.g., `@adr: ADR-NN`).
- Use `ADR.NN.TT.SS` for decision/element-level anchors within ADR documents (e.g., `@adr: ADR.NN.TT.SS`).

## Schema File Reference

| Artifact | Schema File | Layer | Notes |
|----------|-------------|-------|-------|
| BRD | BRD_SCHEMA.yaml | 1 | Optional¹ - advisory validation only |
| PRD | PRD_SCHEMA.yaml | 2 | |
| EARS | EARS_SCHEMA.yaml | 3 | |
| BDD | BDD_SCHEMA.yaml | 4 | |
| ADR | ADR_SCHEMA.yaml | 5 | |
| SYS | SYS_SCHEMA.yaml | 6 | |
| REQ | REQ_SCHEMA.yaml | 7 | |
| IMPL | IMPL_SCHEMA.yaml | 8 | |
| CTR | CTR_SCHEMA.yaml | 9 | |
| SPEC | SPEC_SCHEMA.yaml | 10 | |
| TASKS | TASKS_SCHEMA.yaml | 11 | |
| ICON | ICON_SCHEMA.yaml | 11 | Optional artifact |
| IPLAN | IPLAN_SCHEMA.yaml | 12 | |

¹ BRD schema is OPTIONAL. BRD validation is human-centric with advisory-only automated checks. All validation rules in BRD_SCHEMA.yaml have 'warning' or 'info' severity (not 'error'). See BRD_SCHEMA.yaml header (lines 1-12) for enforcement level details.

## Traceability

Every document maintains bidirectional traceability through **Cumulative Tagging Hierarchy** - each artifact includes tags from ALL upstream layers, creating complete audit trails.

### Cumulative Tagging Hierarchy

**Core Principle**: Each layer N includes tags from layers 1 through N-1 plus its own identifier.

**Tag Format**:
- Hierarchical artifacts (BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS): `@type: TYPE-NN:TYPE.NN.TT.SS` (document ID + element ID)
- File-level artifacts (ADR, SPEC, CTR, IPLAN): `@type: TYPE-NN`
- ICON contracts: `@icon: ICON-NN:ContractName`

**Example Progression**:
```markdown
# Layer 2 (PRD)
@brd: BRD-01:BRD.01.01.30

# Layer 4 (BDD)
@brd: BRD-01:BRD.01.01.30
@prd: PRD-02:PRD.02.03.01
@ears: EARS-03:EARS.03.05.02

# Layer 7 (REQ)
@brd: BRD-01:BRD.01.01.30
@prd: PRD-02:PRD.02.03.01
@ears: EARS-03:EARS.03.05.02
@bdd: BDD-04:BDD.04.01.07
@adr: ADR-33
@sys: SYS-06:SYS.06.02.01

# Layer 13 (Code)
@brd: BRD-01:BRD.01.01.30
... [all upstream tags through @tasks]
@impl-status: complete
```

### Benefits

- **Complete Audit Trail**: Every artifact traces back to original business requirement
- **Regulatory Compliance**: regulatory, FDA, ISO requirements for traceability
- **Impact Analysis**: Instantly identify all downstream artifacts affected by upstream changes
- **Automated Validation**: Scripts enforce cumulative tagging compliance
- **Change Management**: Track complete lineage from requirements through code

### Validation

Note: Script name canonicalization — the canonical script is `scripts/generate_traceability_matrix.py`. Any historical references in this guide to `generate_traceability_matrix.py` refer to the same tool; use the singular script name.

```bash
# Note: In this repo, drop any `docs/` prefix used in generic examples.
# Extract tags from codebase
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate cumulative tagging hierarchy
python scripts/validate_tags_against_docs.py --validate-cumulative --strict

# Generate traceability matrices
python scripts/generate_traceability_matrix.py --auto
```

See [TRACEABILITY.md](./TRACEABILITY.md) and [COMPLETE_TAGGING_EXAMPLE.md](./COMPLETE_TAGGING_EXAMPLE.md) for complete guidelines.

Note on Validation layer (Layer 15): Validation consumes all upstream tags. Documentation presents counts as advisory; the validator enforces a broad acceptable range (10–15) to preserve complete chains.

## Getting Started

### Quick Start Guide

**Step 1: Choose Your Domain**
- Review [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md)
- Identify domain-specific terminology and placeholders

**Step 2: Copy Templates to Your Project**
```bash
# Copy entire framework to your project
cp -r ai_dev_flow/ <your_project>/docs/

# Or copy specific templates as needed
cp ai_dev_flow/07_REQ/REQ-TEMPLATE.md <your_project>/docs/07_REQ/
```

**Step 3: Replace Placeholders**
- Search for `[PLACEHOLDERS]` in templates
- Replace with domain-specific values
- Update examples to match your use cases

**Step 4: Create Your First Document**
1. **Choose Document Type**: Select directory (01_BRD/, 02_PRD/, 07_REQ/, etc.)
2. **Check Index**: Review `{TYPE}-00_index.{ext}` for next available ID
3. **Copy Template**: Use template file from the directory
4. **Fill Content**: Complete all sections with traceability links
5. **Update Index**: Add entry to index file
6. **Validate**: Run validation scripts (if available)

### Template Structure

Each directory contains:
- **Index File**: `{TYPE}-00_index.{ext}` - Master list of all documents
- **Template File**: `{TYPE}-TEMPLATE.{ext}` - Copy for new documents
- **README.md**: Detailed usage guide and best practices
- **Example Files**: Reference implementations showing real-world usage
  - Generic examples with `[PLACEHOLDER]` format
  - Domain-specific examples from original project

### Validation

The framework includes comprehensive validation tooling:

```bash
# Cumulative tagging validation (recommended)
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json
python scripts/validate_tags_against_docs.py --validate-cumulative --strict
python scripts/generate_traceability_matrix.py --auto

# Legacy validation (optional)
python scripts/validate_requirement_ids.py
python scripts/validate_links.py
```

**CI/CD Integration**: See [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md) for pre-commit hooks and GitHub Actions workflows.


### Using Automated Validation Tooling

The framework provides three main validation scripts for enforcing cumulative tagging hierarchy and traceability compliance.

#### 1. Tag Extraction (`extract_tags.py`)

**Purpose**: Scan codebase to extract all traceability tags from source code, documentation, and tests.

**Usage**:
```bash
# Extract tags from all sources
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate format only (no output file)
python scripts/extract_tags.py --validate-only

# Extract from specific artifact type
python scripts/extract_tags.py --type REQ --show-all-upstream
```

**What It Does**:
- Scans files for `@artifact-type: DOC-ID:REQ-ID` patterns
- Validates tag format compliance
- Generates JSON file with all discovered tags
- Reports orphaned or malformed tags

  **Output Example**:
```json
{
  "REQ-NN": {
    "brd": ["BRD-NN"],
    "prd": ["PRD-NN"],
    "ears": ["EARS-NN"],
    "bdd": ["BDD-NN"],
    "adr": ["ADR-NN"],
    "sys": ["SYS-NN"]
  }
}
```

#### 2. Cumulative Tag Validation (`validate_tags_against_docs.py`)

**Purpose**: Enforce cumulative tagging hierarchy - verify each artifact includes ALL required upstream tags.

**Usage**:
```bash
# Full validation with cumulative tagging check
python scripts/validate_tags_against_docs.py \
  --source src/ docs/ tests/ \
  --docs docs/ \
  --validate-cumulative \
  --strict

# Validate specific artifact
python scripts/validate_tags_against_docs.py \
  --artifact REQ-NN \
  --expected-layers brd,prd,ears,bdd,adr,sys \
  --strict

# Check for orphaned tags (tags without corresponding documents)
python scripts/validate_tags_against_docs.py \
  --tags docs/generated/tags.json \
  --strict
```

**What It Checks**:
1. **Layer Detection**: Automatically determines artifact layer from file path
2. **Required Tags**: Ensures all required upstream tags are present (no gaps)
3. **Tag Count**: Validates tag count matches layer requirements
4. **Tag Chain**: Verifies no gaps in cumulative tag chain
5. **Optional Layers**: Correctly handles IMPL (Layer 8) and CTR (Layer 9)

**Expected Tag Counts by Layer**:

See [CUMULATIVE_TAG_REFERENCE.md](./CUMULATIVE_TAG_REFERENCE.md) for complete tag count formulas by layer, including:
- Full reference table (Layers 1-15)
- Handling of optional layers (IMPL, CTR)
- Validation formulas and Python implementation
- Example scenarios for different project configurations

**Quick Reference**:
- Layers 1-9: Fixed count (layer number - 1)
- Layers 10-15: Range based on optional layers (IMPL, CTR)
- Layer 15 (Validation): Advisory count (10-15 tags)

Note: ICON (Implementation Contracts) is optional and does not affect tag counts. If present, `@icon` tags are allowed but excluded from cumulative count and chain validation.

**Output Example**:
```
✅ VALIDATION PASSED

Statistics:
- Total artifacts validated: 147
- Total tags validated: 1,234
- Cumulative tagging compliance: 100%
- No gaps found in tag chains
```

**Error Example**:
```
❌ CUMULATIVE TAGGING ERRORS FOUND: 3

MISSING_REQUIRED_TAGS: 1
  📄 docs/07_REQ/api/REQ-NN_submit_request.md
     ❌ Missing required upstream tags for REQ (Layer 7): bdd

TAG_CHAIN_GAP: 2
  📄 docs/10_SPEC/service.yaml
     ❌ Gap in cumulative tag chain: @bdd (Layer 4) missing but higher layers present
```

#### 3. Traceability Matrix Generation (`generate_traceability_matrix.py`)

**Purpose**: Auto-generate traceability matrices showing bidirectional relationships between artifacts.

**Usage**:
```bash
# Generate all matrices automatically
python scripts/generate_traceability_matrix.py --auto

# Generate matrix for specific artifact type
python scripts/generate_traceability_matrix.py \
  --type REQ \
  --output docs/07_REQ/REQ-00_TRACEABILITY_MATRIX.md

# Show coverage metrics
python scripts/generate_traceability_matrix.py \
  --type BDD \
  --show-coverage
```

**What It Generates**:
- Complete inventory of all artifacts by type
- Upstream traceability (requirements → implementations)
- Downstream traceability (implementations → tests)
- Coverage metrics and gap analysis
- Bidirectional reference validation

**Output Example** (REQ Matrix):
```markdown
# Traceability Matrix: REQ-NN through REQ-NN

## Complete REQ Inventory
| REQ ID | Title | Status | Upstream | Downstream |
|--------|-------|--------|----------|------------|
| REQ-NN | Submit Request | Active | BRD-NN, PRD-NN, EARS-NN, BDD-NN, ADR-NN, SYS-NN | SPEC-NN, TASKS-NN, Code |

## Coverage Metrics
- Total Requirements: 150
- With Complete Upstream: 148 (98.7%)
- With Downstream Implementation: 145 (96.7%)
- Orphaned Requirements: 2 (1.3%)
```

#### 4. Complete Validation Workflow

**Step 1: After Creating/Modifying Artifacts**
```bash
# Extract tags
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate
python scripts/validate_tags_against_docs.py --validate-cumulative --strict
```

**Step 2: Before Committing**
```bash
# Complete validation workflow
python scripts/generate_traceability_matrix.py --auto
```

**Step 3: CI/CD Integration** (see [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md))
```yaml
# .github/workflows/traceability.yml
- name: Validate Cumulative Tagging
  run: python scripts/validate_tags_against_docs.py --validate-cumulative --strict
```

#### Validation Workflow Diagram

```mermaid
flowchart TD
    Start[Start Validation] --> Extract[extract_tags.py<br/>Extract all tags]
    Extract --> Validate[validate_tags_against_docs.py<br/>Check tag validity]
    Validate --> Check{All Valid?}
    Check -->|Yes| Generate[generate_traceability_matrix.py<br/>Create matrix]
    Check -->|No| Fix[Fix invalid tags]
    Fix --> Extract
    Generate --> Report[Validation Report]
```

#### Common Issues and Fixes

**Issue**: "Missing required upstream tags"
```bash
# Fix: Add missing tags to artifact's section 7 Traceability
# Example: REQ-NN missing @bdd tag
```
```markdown
## 7. Traceability

**Required Tags**:
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS-NN
@bdd: BDD-NN  # ← Add this
@adr: ADR-NN
@sys: SYS-NN
```

**Issue**: "Gap in cumulative tag chain"
```bash
# Fix: Ensure no layers are skipped
# If @adr exists, @brd, @prd, @ears, @bdd must all exist
```

**Issue**: "Orphaned tag - referenced document not found"
```bash
# Fix: Either create the referenced document or remove invalid tag
# Verify: ls docs/01_BRD/BRD-NN*.md
```

**Issue**: "Insufficient tag count"
```bash
# Fix: Add all required upstream tags for the artifact's layer
# REQ (Layer 7) needs exactly 6 tags: @brd through @sys
```

#### Dependencies

Install required Python packages:
```bash
pip install pyyaml  # For YAML parsing (SPEC documents)
```

#### Performance

- **extract_tags.py**: ~5-10 seconds for 1,000 files
- **validate_tags_against_docs.py**: ~30 seconds for 100 artifacts with cumulative validation
- **generate_traceability_matrix.py**: ~1-2 minutes for complete matrix suite

#### Next Steps

1. **First Time Setup**: Read [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md)
2. **Complete Example**: Review [COMPLETE_TAGGING_EXAMPLE.md](./COMPLETE_TAGGING_EXAMPLE.md)
3. **Pre-Commit Hooks**: Configure automatic validation before commits
4. **CI/CD**: Add GitHub Actions workflow for pull request validation

## Core Standards Documents

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document identification rules
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability requirements
- [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards) - Link formatting conventions
- [index.md](./index.md) - Detailed directory structure reference

## Schema Definitions

Each artifact type has a corresponding YAML schema file (`{TYPE}_SCHEMA.yaml`) that defines:
- **Metadata Requirements**: YAML frontmatter fields and validation rules
- **Document Structure**: Required/optional sections and numbering patterns
- **Artifact-Specific Patterns**: Type-specific formats (Gherkin, FR-NN, TASK-NN, etc.)
- **Validation Rules**: Error/warning severities and fix instructions
- **Traceability Requirements**: Cumulative tagging hierarchy per layer
- **Error Messages**: Standardized error codes (E001-E0XX, W001-W0XX, I001-I0XX)

### Schema File Reference

| Layer | Artifact | Schema File | Key Patterns |
|-------|----------|-------------|--------------|
| 1 | BRD | [BRD_SCHEMA.yaml](./01_BRD/BRD_SCHEMA.yaml) | Business objectives format |
| 2 | PRD | [PRD_SCHEMA.yaml](./02_PRD/PRD_SCHEMA.yaml) | FR/QA format, template variants |
| 3 | EARS | [EARS_SCHEMA.yaml](./03_EARS/EARS_SCHEMA.yaml) | WHEN-THE-SHALL-WITHIN format |
| 4 | BDD | [BDD_SCHEMA.yaml](./04_BDD/BDD_SCHEMA.yaml) | Gherkin syntax, step patterns |
| 5 | ADR | [ADR_SCHEMA.yaml](./05_ADR/ADR_SCHEMA.yaml) | Context-Decision-Consequences |
| 6 | SYS | [SYS_SCHEMA.yaml](./06_SYS/SYS_SCHEMA.yaml) | FR-NN, unified sequential formats |
| 7 | REQ | [REQ_SCHEMA.yaml](./07_REQ/REQ_SCHEMA.yaml) | 12 sections, interface schemas |
| 8 | IMPL | [IMPL_SCHEMA.yaml](./08_IMPL/IMPL_SCHEMA.yaml) | Phase organization, deliverables |
| 9 | CTR | [CTR_SCHEMA.yaml](./09_CTR/CTR_SCHEMA.yaml) | Dual-file, OpenAPI/AsyncAPI |
| 10 | SPEC | [SPEC_SCHEMA.yaml](./10_SPEC/SPEC_SCHEMA.yaml) | YAML structure, code gen ready |
| 11 | TASKS | [TASKS_SCHEMA.yaml](./11_TASKS/TASKS_SCHEMA.yaml) | TASK-NN, implementation contracts |
| 12 | IPLAN | [IPLAN_SCHEMA.yaml](./12_IPLAN/IPLAN_SCHEMA.yaml) | Session format, bash commands |

### Schema Validation Usage

```bash
# Validate document against schema (planned)
python scripts/validate_artifact.py --schema ai_dev_flow/07_REQ/REQ_SCHEMA.yaml --document docs/07_REQ/REQ-01_example.md

# Validate all documents of a type
python scripts/validate_artifact.py --type REQ --strict
```

### Cumulative Tagging by Layer (from Schemas)

| Layer | Artifact | Required Upstream Tags |
|-------|----------|------------------------|
| 1 | BRD | None (top level) |
| 2 | PRD | @brd |
| 3 | EARS | @brd, @prd |
| 4 | BDD | @brd, @prd, @ears |
| 5 | ADR | @brd, @prd, @ears, @bdd |
| 6 | SYS | @brd, @prd, @ears, @bdd, @adr |
| 7 | REQ | @brd, @prd, @ears, @bdd, @adr, @sys |
| 8 | IMPL | @brd through @req (optional layer) |
| 9 | CTR | @brd through @impl (optional layer) |
| 10 | SPEC | @brd through @req + optional @impl, @ctr |
| 11 | TASKS | @brd through @spec |
| 12 | IPLAN | @brd through @tasks |

## Workflow Guides

### Business Requirements → Production Code

The AI Dev Flow follows a structured progression through 16 layers:

**Documentation Layers (0-12)**:
1. **Strategy** (Layer 0) - External business strategy documents
2. **BRD** (Layer 1) - Business objectives and market context
3. **PRD** (Layer 2) - Product features and user stories
4. **EARS** (Layer 3) - Measurable event-driven requirements
5. **BDD** (Layer 4) - Executable acceptance tests in Gherkin
6. **ADR** (Layer 5) - Architectural decisions and rationale
7. **SYS** (Layer 6) - System-level requirements
8. **REQ** (Layer 7) - Atomic, testable requirements
9. **IMPL** (Layer 8) - Implementation plans (optional)
10. **CTR** (Layer 9) - API contracts (optional)
11. **SPEC** (Layer 10) - YAML technical specifications
12. **TASKS** (Layer 11) - Implementation task breakdown
13. **IPLAN** (Layer 12) - Session-specific plans

**Execution Layers (13-15)**:
14. **Code** (Layer 13) - Source code with cumulative tags
15. **Tests** (Layer 14) - Test suite with cumulative tags
16. **Validation** (Layer 15) - Production readiness verification

**Key Workflow Patterns**:
- **Cumulative Tagging**: Every artifact includes tags from ALL upstream layers
- **Complete Traceability**: Every document links upstream (requirements) and downstream (implementations)
- **Regulatory Compliance**: Complete audit trail for regulatory, FDA, ISO requirements
- **Dual-File Contracts**: CTR uses `.md` (human) + `.yaml` (machine) for parallel development
- **AI Code Generation**: SPEC + TASKS enable deterministic code generation by AI assistants
- **Automated Validation**: Scripts enforce tagging hierarchy and traceability compliance

### AI-Assisted Development

Quick link: AI Assistant Playbook (index): AI_ASSISTANT_PLAYBOOK.md

Templates are optimized for AI code generation:

**Human-Readable**:
- Clear business context and rationale
- Traceability links to requirements and decisions
- Acceptance criteria in natural language

**Machine-Readable**:
- Structured YAML specifications
- Explicit interface definitions (OpenAPI/AsyncAPI)
- Measurable constraints and validation rules
- Complete behavioral specifications

**AI Benefits**:
- Deterministic code generation from YAML SPEC
- Automatic traceability comment injection
- Consistent implementation patterns
- Reduced manual coding effort (48x speed improvement documented)

#### Assistant Output Style (All Tools)

- Professional engineering tone: no marketing or emotional language.
- Token‑efficient: concise bullets, short paragraphs, concrete commands.
- Actionable output: commands, file paths, code identifiers, checklists.
- Emoji policy: informational only, minimal (0–1 typical).
- See Tool Optimization Guide → Style and Tone Guidelines for details and Claude‑specific rules: `AI_TOOL_OPTIMIZATION_GUIDE.md`.

## Best Practices

### Document Creation

1. **One Concept Per File**: Each document addresses one requirement/decision/component
2. **Complete Traceability**: Always link upstream sources and downstream implementations
3. **Measurable Criteria**: Use quantitative thresholds, not subjective terms (avoid "fast", "efficient")
4. **Update Indexes**: Keep index files current when adding new documents
5. **Stable IDs**: Once assigned, document IDs never change (even if content is deprecated)
6. **Descriptive Slugs**: Use `lower_snake_case` slugs that clearly describe the content

### CTR (Contract) Best Practices

1. **Dual Files Required**: Always create both `.md` and `.yaml` with matching slugs
2. **Machine-Readable Schema**: Use OpenAPI 3.x (REST), AsyncAPI 2.x (events), or JSON Schema
3. **Contract-First Development**: Define contracts before implementation to enable parallel work
4. **Version Management**: Include version field in YAML schema for evolution tracking
5. **Consumer-Driven**: Design contracts from consumer perspective, not provider

### SPEC (Specification) Best Practices

1. **Reference CTR**: When implementing interfaces, link to corresponding CTR document
2. **Complete YAML**: Include all classes, methods, parameters, return types
3. **Behavioral Specs**: Document pre/post conditions, invariants, error handling
4. **Traceability Comments**: Include REQ-IDs, ADR references, BDD scenarios
5. **AI-Ready**: Structure for deterministic code generation

### IMPL (Implementation Plan) Best Practices

1. **Project Management Focus**: WHO does WHAT, WHEN - not HOW (technical details)
2. **Deliverable Identification**: List which CTR, SPEC, TASKS documents will be created
3. **Phase Organization**: Break large projects into manageable phases
4. **Team Assignments**: Clearly assign responsibilities to teams/individuals
5. **Dependencies**: Document inter-phase and inter-deliverable dependencies

### General Guidelines

- **Run Validation**: Check links and IDs before committing (if validation scripts available)
- **Placeholder Consistency**: Use `[UPPERCASE_BRACKET]` format for domain-agnostic placeholders
- **Cross-References**: Use relative paths within template directory
- **Token Limits (Tool-Optimized)**: See [AI_TOOL_OPTIMIZATION_GUIDE.md](AI_TOOL_OPTIMIZATION_GUIDE.md) for assistant-specific token guidance and file handling strategies.
- **Update History**: Document version and last updated date in headers

## Directory Organization

```mermaid
graph LR
    subgraph ai_dev_flow["ai_dev_flow/"]
        direction TB

        subgraph docs["Documentation Artifacts"]
            BRD["BRD/ - Business Requirements"]
            PRD["PRD/ - Product Requirements"]
            EARS["EARS/ - EARS Requirements"]
            BDD["BDD/ - BDD Feature Files"]
            ADR["ADR/ - Architecture Decisions"]
            SYS["SYS/ - System Requirements"]
            REQ["REQ/ - Atomic Requirements"]
            IMPL["IMPL/ - Implementation Plans"]
            CTR["CTR/ - API Contracts"]
            SPEC["SPEC/ - Technical Specs"]
            TASKS["TASKS/ - Code Gen Plans"]
            IPLAN["IPLAN/ - Session Plans"]
        end

        subgraph tools["Tooling"]
            scripts["scripts/ - Validation tools"]
            work_plans["work_plans/ - Plan outputs"]
        end

        subgraph guides["Framework Guides"]
            index["index.md"]
            readme["README.md"]
            sdd["SPEC_DRIVEN_DEVELOPMENT_GUIDE.md"]
            trace["TRACEABILITY.md"]
        end
    end

    REQ --> REQ_sub["api/ auth/ data/ risk/"]
    IMPL --> IMPL_sub["examples/"]
```

**Artifact Directories**:

| Directory | Purpose |
|-----------|---------|
| `BRD/` | Business Requirements Documents |
| `PRD/` | Product Requirements Documents |
| `EARS/` | EARS Requirements (Event-driven) |
| `BDD/` | BDD Feature Files (Gherkin) |
| `ADR/` | Architecture Decision Records |
| `SYS/` | System Requirements Specifications |
| `REQ/` | Atomic Requirements (subdirs: api/, auth/, data/, risk/) |
| `IMPL/` | Implementation Plans (subdirs: examples/) |
| `CTR/` | API Contracts - dual-file format (.md + .yaml) |
| `SPEC/` | Technical Specifications (YAML) |
| `TASKS/` | Code Generation Plans |
| `IPLAN/` | Session-specific implementation plans (Layer 12) |

**Tooling & Guides**:

| Path | Purpose |
|------|---------|
| `scripts/` | Validation and tooling scripts |
| `work_plans/` | Implementation plans (/save-plan output) |
| `index.md` | Detailed directory reference with Mermaid workflow |
| `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | Complete SDD methodology |
| `TRACEABILITY.md` | Traceability requirements and conventions |

<!-- Directory Structure Migration History -->
<!-- 2025-01-13: CONTRACTS/ → 09_CTR/ (contracts now use dual-file format) -->
<!-- 2025-01-13: tasks_plans/ → 12_IPLAN/ (implementation plans; filenames no longer use timestamps) -->

## Framework Versions and Updates

**Current Version**: 2.2
**Last Updated**: 2025-11-30

**Version 2.0 - Cumulative Tagging Hierarchy** (November 2025):
- ✅ **16-Layer Architecture**: Expanded from 10 to 16 layers (added Strategy, IPLAN, Code, Tests, Validation)
- ✅ **Cumulative Tagging System**: Each artifact includes tags from ALL upstream layers
- ✅ **Automated Validation**: Enhanced scripts enforce cumulative tagging compliance
- ✅ **Traceability Matrix Templates**: All 13 artifact types have cumulative tagging sections
- ✅ **Complete Example**: COMPLETE_TAGGING_EXAMPLE.md shows end-to-end tagging
- ✅ **Setup Guide**: TRACEABILITY_SETUP.md with CI/CD integration patterns
- ✅ **Regulatory Compliance**: Complete audit trails for regulatory, FDA, ISO
- ✅ **Impact Analysis**: Instant identification of affected downstream artifacts

**Version 1.0 Enhancements** (November 2025):
- Added IMPL (Implementation Plans) for project management layer
- Created DOMAIN_ADAPTATION_GUIDE.md with 5 domain checklists
- Introduced dual-file CTR format (.md + .yaml)
- Added generic examples with placeholder format
- Enhanced TASKS templates for AI code generation

**Framework Evolution**:
- Proven in production: 48x code generation speed improvement
- 16-layer architecture with complete cumulative tagging
- Automated traceability validation and matrix generation
- Complete audit trail from business strategy to production code
- AI-optimized YAML specifications for deterministic generation

## Related Documentation

**Within This Framework**:
- [index.md](./index.md) - Complete directory reference with workflow diagram
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Detailed SDD methodology
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability format standards and cumulative tagging hierarchy
- [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md) - Setup guide for cumulative tagging validation and CI/CD
- [COMPLETE_TAGGING_EXAMPLE.md](./COMPLETE_TAGGING_EXAMPLE.md) - End-to-end example across all 16 layers
- [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) - Domain customization checklists
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document naming conventions

**For Original Project Context** (example references - replace with your project path):
- [CLAUDE.md]({project_root}/CLAUDE.md) - Project-level SDD guidance
- [docs/10_SPEC/]({project_root}/docs/10_SPEC/) - Production specifications
- [docs/src/]({project_root}/docs/src/) - Component implementations

## BDD Tag Examples

The framework supports two BDD tagging styles. Prefer the canonical inline form for best compatibility with validators; link-style is also recognized.

### Canonical Inline Tags (preferred)

```feature
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS-NN
@adr: ADR-NN
@sys: SYS-NN
@req: REQ-NN
@impl-status: in-progress

Feature: Request validation
  Scenario: Submit a valid request
    Given a logged-in user
    When the user submits a valid request
    Then the system accepts the request
```

### Link-Style Tags (also supported)

```feature
@requirement:[REQ-NN](../07_REQ/api/REQ-NN_submit_request.md#REQ-NN)

Feature: Request validation
  Scenario: Submit a valid request
    Given a logged-in user
    When the user submits a valid request
    Then the system accepts the request
```

Notes:
- Both forms are extracted by `scripts/extract_tags.py`.
- Link-style tags capture the document ID; inline tags are recommended for cumulative tagging checks.
- Optional layers (e.g., 08_IMPL/CTR) may be omitted when not applicable.

## Adoption and Support

### Adopting This Framework

1. **Copy templates** to your project: `cp -r ai_dev_flow/ <your_project>/docs/`
2. **Read domain guide**: Review [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md)
3. **Replace placeholders**: Search for `[PLACEHOLDERS]` and customize
4. **Create first document**: Follow Quick Start Guide above
5. **Implement validation**: Add validation scripts as needed

### Questions or Issues

1. Review relevant template README.md in each directory
2. Check [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) for methodology
3. Examine existing examples in subdirectories
4. Reference [index.md](./index.md) for workflow visualization
5. Use validation scripts (if implemented) to check correctness

### Contributing to Framework

If enhancing this framework:
- Maintain `[PLACEHOLDER]` format for domain-agnostic templates
- Update [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) with new domains
<!-- Historical note removed: scripts/make_framework_generic.py is no longer part of this repo -->
- Document version and last updated date in modified files
