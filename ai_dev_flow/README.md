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

**Status**: Active framework with MVP templates, domain adaptation guidance, cumulative tagging, and validation tooling.

**Version**: 2.4 | **Last Updated**: 2026-02-05

## Overview

This directory provides a structured, traceable framework for Specification-Driven Development (SDD), enabling AI-assisted delivery using MVP templates by default.

### Framework Purpose

- **Blueprint**: Early layers (BRD, PRD, ADR, SYS) capture business objectives and architectural decisions.
- **Instruction Set**: Downstream layers (REQ, SPEC, TASKS) translate those decisions into granular, implementation-ready guidance for AI assistants.
- **Governance**: The traceability chain from BRD through TASKS documents decisions and checks for consistent implementation.
- **Delivery Loop**: Continuous MVP iteration - Create MVP → Fix Defects → Production → Add Features as new MVP → Repeat
 - Enables rapid product evolution with 1-2 week cycles
  - Automation accelerates each cycle (90%+ layers automated)
  - Cumulative traceability preserves knowledge across iterations

### Why AI Dev Flow?

**Traditional Development Challenges**:
- Requirements drift from implementation over time
- Manual traceability is incomplete and outdated
- Inconsistent documentation across teams
- AI code generation requires unstructured guidance
- Slow transition from idea to production MVP

**AI Dev Flow Solutions**:
- ✅ **90%+ Automation**: 13 of 14 production layers generate automatically with quality gates
- ✅ **Strategic Human Oversight**: Only 5 critical checkpoints require human approval (if quality score < 90%)
- ✅ **Code-from-Specs**: Direct YAML-to-Python code generation from technical specifications
- ✅ **Auto-Fix Testing**: Failing tests trigger automatic code corrections (max 3 retries)
- ✅ **Continuous Delivery Loop**: MVP → Defects → Production → Next MVP rapid iteration
- ✅ **Domain-Agnostic**: Adaptable to any software project (e-commerce, SaaS, IoT, healthcare, finance)
- ✅ **Complete Traceability**: Bidirectional links from business requirements to production code
- ✅ **Cumulative Tagging Hierarchy**: Each artifact includes tags from ALL upstream layers for complete audit trails
- ✅ **AI-Optimized**: YAML specifications designed for deterministic code generation
- ✅ **15-Layer Architecture**: Structured progression from strategy through validation (including TSPEC for TDD)
- ✅ **Dual-File Contracts (CTR only)**: Human-readable `.md` + machine-readable `.yaml` for API contracts
- ✅ **Example-Driven**: Generic examples with `[PLACEHOLDER]` format for easy customization
- ✅ **Automated Validation**: Scripts for tag validation, traceability matrix generation, cumulative hierarchy enforcement

**📚 New to this framework?** Start with [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) for domain-specific guidance (financial, healthcare, e-commerce, SaaS, IoT, or generic software).

## Roles & Automation in AI Dev Flow

The framework orchestrates three key participants to transform business ideas into production code:

### Human Role: Strategic Decision-Making and Quality Validation

**Philosophy**: Humans make strategic decisions, AI handles execution.

**5 Critical Checkpoints** (only if quality score < 90%):
- **BRD Approval** (Layer 1) - Business alignment and strategic direction
- **PRD Approval** (Layer 2) - Product vision and feature validation
- **ADR Approval** (Layer 5) - Architecture decisions and technical rationale
- **Code Review** (Layer 12) - Code quality, security, and best practices
- **Production Deployment** (Layer 14) - Final gate before live release

**Responsibilities**:
- Provides business requirements and strategic direction
- Selects project domain (financial, software, healthcare, etc.)
- Can override AI recommendations at quality gates
- Reviews and approves critical decisions when automation score is below threshold

**Quality-Gated Automation**: Human review is optional if quality score ≥ 90%. Only 5 checkpoints require manual intervention out of 13 production layers.

---

### AI Assistant Role: Framework-Aware Automation and Guidance

**Philosophy**: Follows framework rules to execute systematic, traceable development.

**Execution Rules**: Follows 18+ rules defined in [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md)

**Key Capabilities**:

| Capability | Description |
|------------|-------------|
| **Layer-by-Layer Generation** | Creates all documentation artifacts (BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TASKS) with traceability enforcement |
| **Domain Configuration** | Loads domain-specific templates and applies placeholder replacements |
| **Contract Decisions** | Runs contract questionnaire to determine if CTR layer is needed |
| **Code Generation** | Converts YAML SPECs + TASKS → Python code with cumulative traceability tags |
| **Test Automation** | Generates tests from BDD scenarios, runs with auto-fix (3 retries) |
| **Quality Validation** | Runs validation scripts, checks SPEC-readiness scoring, enforces quality gates |
| **Cross-Document Validation** | 3-phase validation (per-document, per-layer, layer transition) with auto-fix |
| **Traceability Management** | Generates bidirectional matrices from cumulative tags |

**Critical Execution Order**:
1. Domain Selection → Ask user for project domain
2. Folder Structure Creation → Create all directories before any documents
3. Domain Configuration → Load and apply domain-specific settings
4. Template Initialization → Copy templates and replace placeholders
5. Contract Decision → Run contract questionnaire
6. Index File Setup → Initialize all index files
7. Document Creation → Begin generating project documents

---

### Autopilot: YAML-Only Automated Workflow Orchestration

**Philosophy**: Maximize automation through machine-parseable YAML templates.

**Key Differentiator**: Exclusively uses YAML templates (`*-MVP-TEMPLATE.yaml`) for machine parsing, not markdown.

**Performance Advantages**:

| Operation | MD Template | YAML Template | Improvement |
|-----------|-------------|---------------|-------------|
| Parse single doc | ~50ms | ~10ms | 5x faster |
| Parse 100 docs | ~5s | ~1s | 5x faster |
| Extract traceability | Regex (complex) | Key access (direct) | 3x faster |
| Validate schema | After parse | During parse | Earlier errors |

**Core Features**:

- **90%+ Automation**: Full SDD workflow from BRD to Production with quality-gated auto-approval
- **Quality-Gated Automation**: Auto-approves if quality score ≥ 90%, human review only when score fails
- **Direct YAML→Dict Mapping**: Zero transformation between templates and code
- **Type-Safe Schema Validation**: Errors detected during load, not after parsing
- **CI/CD Ready**: Integrates with GitHub Actions, supports `--auto-fix` validation

**Automated Workflow**:
```
Layer Transitions → Code Generation → Test Execution → Traceability Matrix Generation
```

**Trigger Methods**:

| Method | Command |
|--------|---------|
| **Local CLI** | `python AUTOPILOT/scripts/mvp_autopilot.py --intent "My MVP" --slug my_mvp` |
| **CI/CD** | GitHub Actions workflow `mvp-autopilot.yml` |
| **GitHub CLI** | `make docs` (runs mvp-autopilot.yml workflow) |

**YAML Template Authority**:
- Autopilot loads ONLY `*-MVP-TEMPLATE.yaml` files (never markdown)
- MD templates serve as human-readable reference documentation
- Single schema validates both MD and YAML document formats
- See [AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md](./AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md) for complete usage

---

### How They Work Together

```mermaid
flowchart TD
    Input[Human Input<br/>Business Requirements] --> AI[AI Assistant / Autopilot]
    
    subgraph "AI Assistant / Autopilot"
        AI --> Layer1[Generate BRD]
        Layer1 --> Layer2[Generate PRD]
        Layer2 --> Layer3[Generate EARS]
        Layer3 --> Layer4[Generate BDD]
        Layer4 --> Layer5[Generate ADR]
        Layer5 --> Layer6[Generate SYS]
        Layer6 --> Layer7[Generate REQ]
        Layer7 --> Layer8[Generate CTR]
        Layer8 --> Layer9[Generate SPEC]
        Layer9 --> Layer10[Generate TASKS]
    end
    
    Layer10 --> Code[Generate Code<br/>from SPEC+TASKS]
    Code --> Tests[Generate & Run Tests<br/>with Auto-Fix]
    
    Tests --> Quality{Quality Score ≥ 90%?}
    Quality -->|Yes| Auto[Auto-Approve]
    Quality -->|No| Human[Human Review]
    
    Auto --> Deploy[Production Deployment]
    Human --> Review[Review & Approve]
    Review --> Deploy
    
    style Input fill:#e1f5fe
    style AI fill:#fff9c4
    style Code fill:#dcedc8
    style Tests fill:#dcedc8
    style Human fill:#ffccbc
    style Auto fill:#c8e6c9
    style Deploy fill:#c8e6c9
```

**Key Differentiation**:

| Aspect | Human | AI Assistant | Autopilot |
|--------|-------|--------------|------------|
| **Scope** | Strategic decisions | Framework execution | Full workflow automation |
| **Trigger** | Initial requirements | User prompts | CLI or CI/CD |
| **Templates** | N/A | MD + YAML | YAML only |
| **Decisions** | 5 critical checkpoints | 18+ execution rules | Quality-gated auto-approval |
| **Output** | Business goals | Artifacts + code | Complete MVP |

---

## Using This Repo

- **📚 Dual-Format Architecture**: [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](./DUAL_MVP_TEMPLATES_ARCHITECTURE.md) - Complete explanation of MD vs YAML templates, YAML schemas, and authority hierarchy
- Docs root: In this repository, artifact folders (`01_BRD/`, `02_PRD/`, `03_EARS/`, `04_BDD/`, `05_ADR/`, `06_SYS/`, `07_REQ/`, `08_CTR/`, `09_SPEC/`, `11_TASKS/`, `CHG/`) live at the `ai_dev_flow/` root. Many guides show a top-level `docs/` prefix for portability; when running commands here, drop the `docs/` prefix.
- BDD layout: Uses nested per-suite folders `04_BDD/BDD-NN_{slug}/` with sectioned `.feature` files.
- Index width: This repo commonly uses `-00_index.md` for indices; follow existing width and do not rename history. New repos should choose a consistent zero width (`00` or `000`) and keep it stable.
- Validators: Use the validators listed in TRACEABILITY_VALIDATION.md (e.g., `python 02_PRD/scripts/validate_prd.py`, `./07_REQ/scripts/validate_req_template.sh`). Older `*_template.sh` examples in some guides have been updated here.
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

#### MVP Template Profile (Default)
- Default: `custom_fields.template_profile: mvp` (relaxed, MVP drafting)
- Strict: omit the field or set `custom_fields.template_profile: enterprise` when a project explicitly requires strict validation.

Full/archived templates are not used in the MVP-facing workflow.

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
- Unified across all doc types: BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS.
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
| CTR | CTR-00_index.md | 2-digit | `CTR-00_index.md` |
| SPEC | SPEC-00_index.md | 2-digit | `SPEC-00_index.md` |
| TASKS | TASKS-00_index.md | 2-digit | `TASKS-00_index.md` |

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

**Required in**: All production documents (BRD through TASKS).

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
    REQ --> CTR[CTR<br/>Layer 8]
    CTR --> SPEC[SPEC<br/>Layer 9]
    SPEC --> TSPEC[TSPEC<br/>Layer 10]
    TSPEC --> TASKS[TASKS<br/>Layer 11]
    TASKS --> Code[Code<br/>Layer 12]
    Code --> Tests[Tests<br/>Layer 13]
    Tests --> Val[Validation<br/>Layer 14]
```

### Splitting Rules

- Core: [DOCUMENT_SPLITTING_RULES.md](./DOCUMENT_SPLITTING_RULES.md)
- Templates: Use `{TYPE}-SECTION-0-TEMPLATE.md` (index) and `{TYPE}-SECTION-TEMPLATE.md` (sections)

### 15-Layer Architecture with Cumulative Tagging

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
| **8** | CTR | API contracts (optional) | @brd→@req (7) | INTERFACE definitions |
| **9** | SPEC | YAML technical specifications | @brd→@req (+optional ctr) (7-8) | HOW to build |
| **10** | TSPEC | Test specifications (TDD) | @brd→@spec (8-9) | TEST-FIRST specifications |
| **11** | TASKS | Implementation task breakdown | @brd→@tspec (9-10) | EXACT TODOs + execution commands |
| **12** | Code | Source code implementation | @brd→@tasks (10-11) | RUNNABLE artifacts |
| **13** | Tests | Test suite implementation | @brd→@code (11-12) | Quality validation |
| **14** | Validation | Production readiness verification | All upstream (11-14) | PRODUCTION-READY |

**Note**: Layer 8 (CTR) is optional - include only when needed for external API contracts.

#### 15-Layer Architecture Diagram

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
        L8[CTR - Contracts/APIs]
        L9[SPEC - Technical Specs]
        L10[TSPEC - Test Specifications]
    end
    subgraph "Implementation Layers 11-14"
        L11[TASKS - Task Breakdown + Execution]
        L12[Code - Source Code]
        L13[Tests - Test Suite]
        L14[Validation - Quality Gates]
    end

    L0 --> L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    L7 --> L8 --> L9 --> L10 --> L11 --> L12 --> L13 --> L14
```

#### Layer Numbering Explained

The 15-layer architecture uses the following structure:

- **Layer 0**: Strategy (pre-artifact foundational layer)
  - Product strategy documents, market analysis, vision statements
  - No formal artifact type, no traceability tags

- **Layers 1-11**: Formal Documentation Artifacts
  - Layer 1: BRD (Business Requirements)
  - Layer 2: PRD (Product Requirements)
  - Layer 3: EARS (Event-Action-Response-State) — Engineering Requirements
  - Layer 4: BDD (Behavior-Driven Development)
  - Layer 5: ADR (Architecture Decision Records)
  - Layer 6: SYS (System Architecture)
  - Layer 7: REQ (Requirements Specifications)
  - Layer 8: CTR (Contracts) - optional
  - Layer 9: SPEC (Technical Specifications)
  - Layer 10: TSPEC (Test Specifications) — TDD test specs (UTEST, ITEST, STEST, FTEST)
  - Layer 11: TASKS (Task Breakdowns with execution commands)

- **Layers 12-14**: Execution Layers
  - Layer 12: Code (source code files)
  - Layer 13: Tests (test implementations)
  - Layer 14: Validation (test results, metrics)

**Important Note on Layer Numbering:**
- **Formal layer numbers (0-14)**: Used in cumulative tagging, templates, and specifications
- **Mermaid diagram groupings**: May use simplified labels (L1-L10) for visual organization
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
| 8 | Contracts (CTR) | Interface contracts (dual-file format) |
| 9 | Specifications (SPEC) | Detailed technical specs |
| 10 | Test Specifications (TSPEC) | TDD test specs (UTEST, ITEST, STEST, FTEST) |
| 11 | Tasks (TASKS) | Development task breakdown + execution commands |
| 12 | Code | Actual implementation |
| 13 | Tests | Unit/integration tests |
| 14 | Validation | End-to-end validation |

Important: "Review" and "Production" are outcomes, not formal layers. The formal model is fixed at Layers 0–14.

#### Mermaid Diagram Visual Groupings (L1-L10)

Diagrams use simplified labels for visual clarity:

- **L1**: Business Layer (contains Layers 1-3: BRD, PRD, EARS)
- **L2**: Testing Layer (contains Layer 4: BDD)
- **L3**: Architecture Layer (contains Layers 5-6: ADR, SYS)
- **L4**: Requirements Layer (contains Layer 7: REQ)
- **L5**: Interface Layer (contains Layer 8: CTR)
- **L6**: Technical Specs (contains Layer 9: SPEC)
- **L7**: Test Specifications (contains Layer 10: TSPEC)
- **L8**: Code Generation (contains Layer 11: TASKS)
- **L9**: Code Layer (contains Layer 12: Code)
- **L10**: Validation Layer (contains Layers 13-14: Tests, Validation)

**Important**: Always use formal layer numbers (0-14) in:
- Cumulative tagging implementations
- Documentation references
- Code comments
- Traceability matrices

### Critical Decision Point

**After REQ (Requirements Layer)**:
- **Interface requirement** (API, event schema, data model) → Create **CTR** (API Contract) → then **SPEC**
- **No interface requirement** (internal logic, business rules) → Create **SPEC** directly

**CTR Format**: Dual-file contract with human-readable `.md` (context, traceability) + machine-readable `.yaml` (OpenAPI/AsyncAPI schema)

#### Critical Decision Point Diagram

```mermaid
flowchart TD
    REQ[REQ - Atomic Requirements] --> Decision{Interface<br/>Required?}
    Decision -->|Yes| CTR[CTR - API Contracts]
    Decision -->|No| SPEC[SPEC - Technical Specs]
    CTR --> SPEC
    SPEC --> TASKS[TASKS - Task Breakdown]
```

## Template Directories

<!-- See “Using This Repo” above for path mapping guidance. -->

### Business Layer

**01_BRD/** - Business Requirements Documents
- High-level business objectives and market context
- Strategic goals and success criteria
- **Files**: [BRD-00_index.md](./01_BRD/BRD-00_index.md) | [BRD-MVP-TEMPLATE.md](./01_BRD/BRD-MVP-TEMPLATE.md) (default; full template archived)

**02_PRD/** - Product Requirements Documents
- User-facing features and product capabilities
- Business requirements and acceptance criteria
- **Files**: [PRD-00_index.md](./02_PRD/PRD-00_index.md) | [PRD-MVP-TEMPLATE.md](./02_PRD/PRD-MVP-TEMPLATE.md) (default; full template archived)

**03_EARS/** - Event-Action-Response-State (Engineering Requirements)
- Measurable requirements using WHEN-THE-SHALL-WITHIN format
- Event-driven and state-driven requirements
- **Files**: [EARS-00_index.md](./03_EARS/EARS-00_index.md) | [EARS-MVP-TEMPLATE.md](./03_EARS/EARS-MVP-TEMPLATE.md) (default; full template archived)

### Testing Layer

**04_BDD/** - Behavior-Driven Development Scenarios
- Executable acceptance tests in Gherkin format
- Business-readable behavioral specifications

### Architecture Layer

**05_ADR/** - Architecture Decision Records
- Architectural choices and rationale
- Technology selections and trade-offs
- **Files**: [ADR-00_index.md](./05_ADR/ADR-00_index.md) | [ADR-MVP-TEMPLATE.md](./05_ADR/ADR-MVP-TEMPLATE.md) (default; full template archived)

**06_SYS/** - System Requirements Specifications
- System-level functional requirements and quality attributes
- Performance, security, and operational characteristics
- **Files**: [SYS-00_index.md](./06_SYS/SYS-00_index.md) | [SYS-MVP-TEMPLATE.md](./06_SYS/SYS-MVP-TEMPLATE.md) (default; full template archived)

### Requirements Layer

**07_REQ/** - Atomic Requirements
- Granular, testable requirements with acceptance criteria
- Organization: Nested per-document folders (DEFAULT for all types)
  - Folder: `07_REQ/REQ-NN_{slug}/`
  - Primary file (atomic): `07_REQ/REQ-NN_{slug}/REQ-NN_{slug}.md`
  - Split (optional when large): index + sections `07_REQ/REQ-NN_{slug}/REQ-NN.0_index.md`, `REQ-NN.1_{section}.md`, ...
- Files: [REQ-00_index.md](./07_REQ/REQ-00_index.md) | [REQ-MVP-TEMPLATE.md](./07_REQ/REQ-MVP-TEMPLATE.md) (default; full template archived)

### Interface Layer

**08_CTR/** - API Contracts (CTR)
- Formal interface specifications for component-to-component communication
- **Dual-file format**:
  - `.md` file: Human-readable context, business rationale, traceability links
  - `.yaml` file: Machine-readable schema (OpenAPI/AsyncAPI/JSON Schema)
- **When to use**: Created when REQ specifies interface requirements (APIs, events, data models)
- **Benefits**: Enables parallel development and contract testing
- **Examples**: [CTR-01_service_contract_example.md](./08_CTR/examples/CTR-01_service_contract_example.md) + [CTR-01_service_contract_example.yaml](./08_CTR/examples/CTR-01_service_contract_example.yaml)

### Technical Specs (SPEC)

**09_SPEC/** - Technical Specifications
- YAML: Monolithic per component (code generation source)
- Markdown: Split narrative with `SPEC-{DOC_NUM}.0_index.md` and `SPEC-{DOC_NUM}.{S}_{slug}.md` when needed
- References CTR contracts when implementing interfaces
- **Files**: [SPEC-00_index.md](./09_SPEC/SPEC-00_index.md) | [Template](./09_SPEC/SPEC-MVP-TEMPLATE.yaml)
- **Examples**: [SPEC-01_api_client_example.yaml](./09_SPEC/SPEC-01_api_client_example.yaml)

### Code Generation Layer

**11_TASKS/** - Code Generation Plans (TASKS)
- Exact TODOs to implement SPEC in source code
- Step-by-step guide for AI code generation from YAML specifications
- **1:1 mapping**: Each TASKS document corresponds to one SPEC
- **Files**: [TASKS-00_index.md](./11_TASKS/TASKS-00_index.md) | [Template](./11_TASKS/TASKS-TEMPLATE.md)

## Document ID Standards

### Scope: Documentation Artifacts Only

**IMPORTANT**: These ID naming standards apply ONLY to **documentation artifacts** in the SDD workflow, NOT to source code files.

#### ✅ Apply To (Documentation):
- Documents in `docs/` directories: BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS
- BDD feature files (`.feature` format) in `tests/bdd/` directories

#### ❌ Do NOT Apply To (Source Code):
- **Python files**: Follow PEP 8 conventions (`snake_case.py`, `PascalCase` classes)
- **Test files**: Follow pytest conventions (`test_*.py`, `test_*()` functions)
- **Other languages**: Follow language-specific style guides (Java, JavaScript, Go, etc.)

### Documentation Naming Format

Format: `{TYPE}-{NN}_{descriptive_slug}.{ext}`
Note: `NN` denotes a variable-width 2+ digit number (e.g., 01, 12, 105, 1002).

- **TYPE**: Document type prefix (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS)
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
| BRD | BRD_MVP_SCHEMA.yaml | 1 | Optional¹ - advisory validation only |
| PRD | PRD_MVP_SCHEMA.yaml | 2 | |
| EARS | EARS_MVP_SCHEMA.yaml | 3 | |
| BDD | BDD_MVP_SCHEMA.yaml | 4 | |
| ADR | ADR_MVP_SCHEMA.yaml | 5 | |
| SYS | SYS_MVP_SCHEMA.yaml | 6 | |
| REQ | REQ_MVP_SCHEMA.yaml | 7 | |
| CTR | CTR_MVP_SCHEMA.yaml | 8 | |
| SPEC | SPEC_MVP_SCHEMA.yaml | 9 | |
| TASKS | TASKS_MVP_SCHEMA.yaml | 10 | |

¹ BRD schema is OPTIONAL. BRD validation is human-centric with advisory-only automated checks. All validation rules in BRD_MVP_SCHEMA.yaml have 'warning' or 'info' severity (not 'error'). See BRD_MVP_SCHEMA.yaml header (lines 1-12) for enforcement level details.

## Traceability

Every document maintains bidirectional traceability through **Cumulative Tagging Hierarchy** - each artifact includes tags from ALL upstream layers, creating complete audit trails.

### Cumulative Tagging Hierarchy

**Core Principle**: Each layer N includes tags from layers 1 through N-1 plus its own identifier.

**Tag Format**:
- Hierarchical artifacts (BRD, PRD, EARS, BDD, SYS, REQ, TASKS): `@type: TYPE-NN:TYPE.NN.TT.SS` (document ID + element ID)
- File-level artifacts (ADR, SPEC, CTR): `@type: TYPE-NN`

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

# Layer 11 (Code)
@brd: BRD-01:BRD.01.01.30
... [all upstream tags through @tasks]
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

Note on Validation layer (Layer 14): Validation consumes all upstream tags. Documentation presents counts as advisory; the validator enforces a broad acceptable range (10–14) to preserve complete chains.

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
cp ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.md <your_project>/docs/07_REQ/
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
python 07_REQ/scripts/validate_requirement_ids.py
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
5. **Optional Layers**: Correctly handles CTR (Layer 8)

**Expected Tag Counts by Layer**:

See [CUMULATIVE_TAG_REFERENCE.md](./CUMULATIVE_TAG_REFERENCE.md) for complete tag count formulas by layer, including:
- Full reference table (Layers 1-13)
- Handling of optional layers (CTR)
- Validation formulas and Python implementation
- Example scenarios for different project configurations

**Quick Reference**:
- Layers 1-8: Fixed count (layer number - 1)
- Layers 9-13: Range based on optional layer (CTR)
- Layer 14 (Validation): Advisory count (10-14 tags)


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
   📄 docs/09_SPEC/service.yaml

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

Each artifact type has a corresponding YAML schema file (`{TYPE}_MVP_SCHEMA.yaml`) that defines:
- **Metadata Requirements**: YAML frontmatter fields and validation rules
- **Document Structure**: Required/optional sections and numbering patterns
- **Artifact-Specific Patterns**: Type-specific formats (Gherkin, FR-NN, TASK-NN, etc.)
- **Validation Rules**: Error/warning severities and fix instructions
- **Traceability Requirements**: Cumulative tagging hierarchy per layer
- **Error Messages**: Standardized error codes (E001-E0XX, W001-W0XX, I001-I0XX)

### Schema File Reference

| Layer | Artifact | Schema File | Key Patterns |
|-------|----------|-------------|--------------|
| 1 | BRD | [BRD_MVP_SCHEMA.yaml](./01_BRD/BRD_MVP_SCHEMA.yaml) | Business objectives format |
| 2 | PRD | [PRD_MVP_SCHEMA.yaml](./02_PRD/PRD_MVP_SCHEMA.yaml) | FR/QA format, template variants |
| 3 | EARS | [EARS_MVP_SCHEMA.yaml](./03_EARS/EARS_MVP_SCHEMA.yaml) | WHEN-THE-SHALL-WITHIN format |
| 4 | BDD | [BDD_MVP_SCHEMA.yaml](./04_BDD/BDD_MVP_SCHEMA.yaml) | Gherkin syntax, step patterns |
| 5 | ADR | [ADR_MVP_SCHEMA.yaml](./05_ADR/ADR_MVP_SCHEMA.yaml) | Context-Decision-Consequences |
| 6 | SYS | [SYS_MVP_SCHEMA.yaml](./06_SYS/SYS_MVP_SCHEMA.yaml) | FR-NN, unified sequential formats |
| 7 | REQ | [REQ_MVP_SCHEMA.yaml](./07_REQ/REQ_MVP_SCHEMA.yaml) | 12 sections, interface schemas |
| 8 | CTR | [CTR_MVP_SCHEMA.yaml](./08_CTR/CTR_MVP_SCHEMA.yaml) | Dual-file, OpenAPI/AsyncAPI |
| 9 | SPEC | [SPEC_MVP_SCHEMA.yaml](./09_SPEC/SPEC_MVP_SCHEMA.yaml) | YAML structure, code gen ready |
| 10 | TSPEC | [TSPEC templates](./10_TSPEC/) | UTEST, ITEST, STEST, FTEST test specs |
| 11 | TASKS | [TASKS_MVP_SCHEMA.yaml](./11_TASKS/TASKS_MVP_SCHEMA.yaml) | TASK-NN, implementation contracts |

### Schema Validation Usage

```bash
# Validate document against schema (planned)
python scripts/validate_artifact.py --schema ai_dev_flow/07_REQ/REQ_MVP_SCHEMA.yaml --document docs/07_REQ/REQ-01_example.md

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
| 8 | CTR | @brd through @req (optional layer) |
| 9 | SPEC | @brd through @req + optional @ctr |
| 10 | TASKS | @brd through @spec |

## Change Management

The framework implements a formal **4-Gate Change Management System** for validating changes at layer boundaries.

### 4-Gate System Overview

| Gate | Layers | Purpose | Entry Point For |
|------|--------|---------|-----------------|
| **GATE-01** | L1-L4 | Business/Product validation | Upstream changes |
| **GATE-05** | L5-L8 | Architecture/Contract validation | Midstream/External changes |
| **GATE-09** | L9-L11 | Design/Test validation (TDD) | Design changes |
| **GATE-12** | L12-L14 | Implementation validation | Downstream/Feedback changes |

### Change Levels

| Level | Description | Process | Example |
|-------|-------------|---------|---------|
| **L1 Patch** | Bug fixes, typos | Edit in place | Fix null pointer |
| **L2 Minor** | Feature adds, enhancements | Lightweight CHG | Add export feature |
| **L3 Major** | Architecture pivots, breaking changes | Full CHG process | Switch to microservices |

### Emergency Bypass

For P1 incidents or critical security (CVSS >= 9.0):
- Hotfix deployment with post-incident documentation
- Retroactive gate validation within 72 hours
- Post-mortem with action items

### Validation Commands

```bash
# Validate gate requirements
./CHG/scripts/validate_gate01.sh <CHG_FILE>
./CHG/scripts/validate_all_gates.sh <CHG_FILE>

# Determine routing
python CHG/scripts/validate_chg_routing.py <CHG_FILE>
```

**Documentation**: See [CHG/CHANGE_MANAGEMENT_GUIDE.md](./CHG/CHANGE_MANAGEMENT_GUIDE.md) for complete change management procedures.

---

## Workflow Guides

### Business Requirements → Production Code

The AI Dev Flow follows a structured progression through 15 layers:

**Documentation Layers (0-10)**:
1. **Strategy** (Layer 0) - External business strategy documents
2. **BRD** (Layer 1) - Business objectives and market context
3. **PRD** (Layer 2) - Product features and user stories
4. **EARS** (Layer 3) - Measurable event-driven requirements
5. **BDD** (Layer 4) - Executable acceptance tests in Gherkin
6. **ADR** (Layer 5) - Architectural decisions and rationale
7. **SYS** (Layer 6) - System-level requirements
8. **REQ** (Layer 7) - Atomic, testable requirements
9. **CTR** (Layer 8) - API contracts (optional)
10. **SPEC** (Layer 9) - YAML technical specifications
11. **TSPEC** (Layer 10) - TDD test specifications (UTEST, ITEST, STEST, FTEST)
12. **TASKS** (Layer 11) - Implementation task breakdown with execution commands

**Execution Layers (12-14)**:
13. **Code** (Layer 12) - Source code with cumulative tags
14. **Tests** (Layer 13) - Test suite with cumulative tags
15. **Validation** (Layer 14) - Production readiness verification

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
            BRD["01_BRD/ - Business Requirements"]
            PRD["02_PRD/ - Product Requirements"]
            EARS["03_EARS/ - EARS Requirements"]
            BDD["04_BDD/ - BDD Feature Files"]
            ADR["05_ADR/ - Architecture Decisions"]
            SYS["06_SYS/ - System Requirements"]
            REQ["07_REQ/ - Atomic Requirements"]
            CTR["08_CTR/ - API Contracts"]
            SPEC["09_SPEC/ - Technical Specs"]
            TASKS["11_TASKS/ - Code Gen Plans + Execution"]
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
```

**Artifact Directories**:

| Directory | Purpose |
|-----------|---------|
| `01_BRD/` | Business Requirements Documents |
| `02_PRD/` | Product Requirements Documents |
| `03_EARS/` | EARS Requirements (Event-driven) |
| `04_BDD/` | BDD Feature Files (Gherkin) |
| `05_ADR/` | Architecture Decision Records |
| `06_SYS/` | System Requirements Specifications |
| `07_REQ/` | Atomic Requirements (subdirs: api/, auth/, data/, risk/) |
| `08_CTR/` | API Contracts - dual-file format (.md + .yaml) |
| `09_SPEC/` | Technical Specifications (YAML) |
| `11_TASKS/` | Code Generation Plans |

**Tooling & Guides**:

| Path | Purpose |
|------|---------|
| `scripts/` | Validation and tooling scripts |
| `work_plans/` | Implementation plans (/save-plan output) |
| `index.md` | Detailed directory reference with Mermaid workflow |
| `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | Complete SDD methodology |
| `TRACEABILITY.md` | Traceability requirements and conventions |

<!-- Directory Structure Migration History -->
<!-- 2025-01-13: CONTRACTS/ → 08_CTR/ (contracts now use dual-file format) -->

## Framework Versions and Updates

**Current Version**: 2.4
**Last Updated**: 2026-02-05

**Version 2.4 - 4-Gate Change Management System** (February 2026):
- ✅ **4-Gate CHG System**: Formal validation gates at layer boundaries (GATE-01, GATE-05, GATE-09, GATE-12)
- ✅ **Change Source Workflows**: 5 change sources (Upstream, Midstream, Downstream, External, Feedback)
- ✅ **Emergency Bypass**: P1 incident and critical security (CVSS >= 9.0) handling
- ✅ **Gate Validation Scripts**: Bash scripts for each gate with error catalogs
- ✅ **Routing Logic**: Python-based CHG routing determination
- ✅ **Approval Matrix**: Level-based approval requirements per gate
- ✅ **Post-Mortem Template**: Structured incident analysis for emergency bypasses

**Version 2.0 - Cumulative Tagging Hierarchy** (November 2025):
- ✅ **14-Layer Architecture**: Expanded from 10 to 15 layers (added Strategy, Code, Tests, Validation)
- ✅ **Cumulative Tagging System**: Each artifact includes tags from ALL upstream layers
- ✅ **Automated Validation**: Enhanced scripts enforce cumulative tagging compliance
- ✅ **Traceability Matrix Templates**: All 13 artifact types have cumulative tagging sections
- ✅ **Complete Example**: COMPLETE_TAGGING_EXAMPLE.md shows end-to-end tagging
- ✅ **Setup Guide**: TRACEABILITY_SETUP.md with CI/CD integration patterns
- ✅ **Regulatory Compliance**: Complete audit trails for regulatory, FDA, ISO
- ✅ **Impact Analysis**: Instant identification of affected downstream artifacts

**Version 1.0 Enhancements** (November 2025):
- Added CTR (API Contracts) dual-file format for interface definitions
- Created DOMAIN_ADAPTATION_GUIDE.md with 5 domain checklists
- Introduced dual-file CTR format (.md + .yaml)
- Added generic examples with placeholder format
- Enhanced TASKS templates for AI code generation

**Framework Evolution**:
- 15-layer architecture with complete cumulative tagging
- Automated traceability validation and matrix generation
- Complete audit trail from business strategy to production code
- AI-optimized YAML specifications for deterministic generation

## Related Documentation

**Within This Framework**:
- [index.md](./index.md) - Complete directory reference with workflow diagram
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Detailed SDD methodology
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability format standards and cumulative tagging hierarchy
- [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md) - Setup guide for cumulative tagging validation and CI/CD
- [COMPLETE_TAGGING_EXAMPLE.md](./COMPLETE_TAGGING_EXAMPLE.md) - End-to-end example across all 15 layers
- [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) - Domain customization checklists
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document naming conventions

**Change Management**:
- [CHG/CHANGE_MANAGEMENT_GUIDE.md](./CHG/CHANGE_MANAGEMENT_GUIDE.md) - Change management procedures
- [CHG/CHANGE_CLASSIFICATION_GUIDE.md](./CHG/CHANGE_CLASSIFICATION_GUIDE.md) - L1/L2/L3 decision guide
- [CHG/gates/](./CHG/gates/) - 4-Gate system documentation
- [CHG/workflows/](./CHG/workflows/) - Change source workflow guides

**Automation & Workflow**:
- [AUTOPILOT/MVP_AUTOPILOT.md](./AUTOPILOT/MVP_AUTOPILOT.md) - Complete automation guide for MVP workflow
- [MVP_WORKFLOW_GUIDE.md](./MVP_WORKFLOW_GUIDE.md) - Workflow patterns and execution steps
- [MVP_AUTOMATION_DESIGN.md](./MVP_AUTOMATION_DESIGN.md) - Automation architecture and design patterns
- [AUTOPILOT/MVP_GITHUB_CICD_INTEGRATION_PLAN.md](./AUTOPILOT/MVP_GITHUB_CICD_INTEGRATION_PLAN.md) - CI/CD integration plan
- [AUTOPILOT/MVP_PIPELINE_END_TO_END_USER_GUIDE.md](./AUTOPILOT/MVP_PIPELINE_END_TO_END_USER_GUIDE.md) - End-to-end user guide

**For Original Project Context** (example references - replace with your project path):
- [CLAUDE.md]({project_root}/CLAUDE.md) - Project-level SDD guidance
- [docs/09_SPEC/]({project_root}/docs/09_SPEC/) - Production specifications
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
- Optional layers (e.g., 08_CTR) may be omitted when not applicable.

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
