---
name: doc-flow
description: AI-Driven Specification-Driven Development (SDD) workflow for transforming business requirements into production-ready code
---

# doc-flow Cline Rule

## Prerequisites

**⚠️ For New Projects (Greenfield)**: If starting a brand new project with no existing folder structure, use the **`project-init`** skill FIRST to initialize project structure, select domain, create folders, and configure setup. Then return here to begin workflow execution.

**For Existing Projects**: If project is already initialized (docs/ folders exist, domain configured), proceed directly with this rule.

---

## Purpose
Provide Cline with structured guidance on implementing the AI-Driven Specification-Driven Development (SDD) workflow defined in `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` as the **authoritative development standard**. This rule enables complete traceability from business requirements to production code through formal artifacts, with clear separation between strategy (Product Owner voice), project documentation, and development templates.

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

## Directory Structure and Roles

**Critical Context**: This project has three key directories with distinct roles:

### 📁 `option_strategy/` - WHAT (Product Owner Voice)
**Primary Authority**: Authoritative trading strategy and business logic

- `integrated_strategy_algo_v5.md` - Bot-executable algorithm specifications
- `Integrated_strategy_desc.md` - Strategic framework and market regimes
- `delta_hedging.md` - Portfolio-level risk management
- `greeks_adjustment.md` - Position-level Greeks management
- `stock_selection/` - Entry criteria and scoring algorithms
- Performance targets, state machines, risk budgets

**Golden Rule**: All trading logic must trace back to these strategy documents.

### 📚 `docs/` - PROJECT DOCUMENTATION
**Implementation Documentation**: Requirements, architecture, specifications

- `docs/BRD/` - Business Requirements Documents
- `docs/PRD/` - Product Requirements Documents
- `docs/ADR/` - Architecture Decision Records (HOW)
- `docs/BDD/` - BDD acceptance tests (Behavior-Driven Development)
- `docs/CTR/` - API Contracts (dual-file format: .md + .yaml)
- `docs/IMPL/` - Implementation Plans (Project Management: WHO/WHEN)
- `docs/SPEC/` - YAML technical specifications
- `docs/TASKS/` - Code Generation Plans (AI-structured implementation tasks)

**Purpose**: Document how strategy is implemented through architecture and code.

### 📝 `docs_templates/ai_dev_flow/` - AUTHORITATIVE DEVELOPMENT STANDARD
**Development Standard and Templates**: The single source of truth for SDD workflow

- **Status**: Authoritative development standard for this project
- **Contents**: Complete SDD workflow (BRD → PRD → SYS → EARS → REQ → ADR → BDD → SPEC → TASKS → Code)
- **Templates**: `{TYPE}-TEMPLATE.{ext}` for each artifact type (BRD, PRD, EARS, REQ, ADR, BDD, SPEC, TASKS)
- **Indices**: `{TYPE}-000_index.{ext}` listing all documents of each type
- **READMEs**: Detailed usage guides and best practices for each artifact type
- **Standards**: ID naming, traceability format, cross-referencing rules
- **Examples**: Reference implementations with full traceability chains

**Purpose**: Define the complete development methodology with templates, standards, and examples for creating all artifacts.

### ⚠️ CRITICAL: Archived Documents Restriction

**STRICTLY PROHIBITED: DO NOT access, reference, link to, or use ANY files or directories containing the word "archived" in their path.**

**Automatic Filtering Rules:**
- ❌ Skip any path containing `archived`, `Archived`, `ARCHIVED`, or `archive`
- ❌ Ignore files in directories with "archived" in the name
- ❌ Do not read, suggest, or reference archived content
- ❌ Do not use archived documents even if they appear in search results

**Active Documentation Only:**
- ✅ `option_strategy/` (current V5 strategy - excludes archived subdirs)
- ✅ `docs/` (active project documentation)
- ✅ `docs_templates/` (authoritative templates and standards)

**If archived content is needed:**
- Stop immediately
- Inform user that content is in archived location
- Request explicit permission before proceeding

**Examples of Prohibited Paths:**
- ❌ `archived/` (any files or subdirectories)
- ❌ `option_strategy/archived_v3_strategy/`
- ❌ `option_strategy/archived_v4_strategy/`
- ❌ `option_strategy/iron_condor/archived_pre_earnings/`
- ❌ `docs/specs_backup_archived_20241015/`
- ❌ Any path matching `**/archived*/**` or `**/archive*/**`

## Information Flow Hierarchy

**Changes flow DOWN (never UP):**
```
📁 option_strategy/ (WHAT - Product Owner Voice)
    ├── Strategy business logic
    └── Performance targets
              ↓
              ↓ Referenced by
              ↓
📚 docs/ (WHY + HOW - Project Documentation)
    ├── Requirements (WHY)
    ├── Architecture (HOW)
    └── Specifications (IMPLEMENTATION)
              ↓
              ↓ Generates
              ↓
💻 Source Code (Python/Infrastructure)

📝 docs_templates/ feeds into 📚 docs/ for consistency
```

**Golden Rules**:
- Strategy → Documentation → Code (one-way flow)
- Code cannot change strategy
- Always use templates from `docs_templates/` when creating docs in `docs/`
- All trading logic must reference `option_strategy/` sections

## Core Workflow Chain

**Reference**: `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (Authoritative Standard)

```
Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → Code → Tests → Validation
                                                                   ↓
                                                           [IF INTERFACE REQUIREMENT]
```

**Workflow Steps** (per authoritative guide):
1. **BRD** (Business Requirements Document) - High-level business needs
2. **PRD** (Product Requirements Document) - User needs and features
3. **EARS** (Easy Approach to Requirements Syntax) - Formal WHEN-THE-SHALL-WITHIN statements
4. **BDD** (Behavior-Driven Development) - Executable Gherkin scenarios
5. **ADR** (Architecture Decision Records) - Architectural decisions with rationale
6. **SYS** (System Requirements) - Technical interpretation of business requirements
7. **REQ** (Atomic Requirements) - Single, testable requirements decomposed from EARS and SYS
8. **IMPL** (Implementation Plans) - Project management: WHO does WHAT, WHEN (identifies which CTR, SPEC, TASKS to create)
9. **CTR** (API Contracts) - [IF INTERFACE REQUIREMENT] Formal interface specifications for component-to-component communication
10. **SPEC** (Technical Specifications) - YAML implementation blueprints: HOW to build (references CTR contracts when implementing interfaces)
11. **TASKS** (Code Generation Plans) - AI-structured task breakdowns with exact TODOs to implement SPEC
12. **Code** - Python implementation matching SPEC exactly
13. **Tests** - Test suites (unit, integration, BDD execution, contract tests)
14. **Validation** - BDD scenario verification, contract validation, and traceability checks

**When to Create CTR**: Create API contracts when REQ specifies interface requirements for component-to-component communication. Skip CTR for purely internal logic with no external interfaces. CTR uses dual-file format (.md + .yaml) to provide both human-readable context and machine-readable schemas.

**IMPL vs SPEC Distinction**:
- **IMPL**: Project management document organizing work (WHO does WHAT, WHEN) - NOT technical specifications
- **SPEC**: Technical implementation specification (HOW to build components) - YAML format for code generation

**Flow Visualization** (corrected per SPEC_DRIVEN_DEVELOPMENT_GUIDE.md):
```mermaid
flowchart TD
    Strategy[option_strategy/: Trading Business Logic] --> BRD[BRD: Business Requirements]
    BRD --> PRD[PRD: Product Requirements]
    PRD --> EARS[EARS: Formal WHEN-THE-SHALL-WITHIN Requirements]
    EARS --> BDD[BDD: Executable Test Scenarios]
    BDD --> ADR[ADR: Architecture Decisions]
    ADR --> SYS[SYS: System Requirements]
    SYS --> REQ[REQ: Atomic Requirements]
    REQ --> IMPL[IMPL: Implementation Plans<br/>Project Mgmt: WHO/WHEN]
    IMPL --> CTR[CTR: API Contracts<br/>IF INTERFACE REQUIREMENT]
    CTR --> SPEC[SPEC: Technical Implementation YAML<br/>HOW to Build]
    SPEC --> TASKS[TASKS: Code Generation Plans<br/>Exact TODOs to Implement SPEC]
    TASKS --> Code[Code: Python Implementation]
    Code --> Tests[Tests: Test Suites + Contract Tests]
    Tests --> Validation[Validation: BDD + Contract + Traceability]
    Templates[docs_templates/ai_dev_flow/<br/>AUTHORITATIVE STANDARD] -.->|provides templates| BRD
    Templates -.-> PRD
    Templates -.-> EARS
    Templates -.-> BDD
    Templates -.-> ADR
    Templates -.-> SYS
    Templates -.-> REQ
    Templates -.-> IMPL
    Templates -.-> CTR
    Templates -.-> SPEC
    Templates -.-> TASKS

    style Strategy fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px
    style BRD fill:#e1f5fe
    style PRD fill:#ffe0b2
    style EARS fill:#f3e5f5
    style BDD fill:#e8f5e8
    style ADR fill:#fce4ec
    style SYS fill:#fff3e0
    style REQ fill:#f3e5f5
    style IMPL fill:#fff9c4
    style CTR fill:#e3f2fd
    style SPEC fill:#e1f5f7
    style TASKS fill:#f1f8e9
    style Code fill:#f9fbe7
    style Tests fill:#e8f5e8
    style Validation fill:#fff3e0
    style Templates fill:#fff9c4,stroke:#f57f17,stroke-width:3px
```

**Important Traceability Notes:**
- **Strategy First**: All requirements must reference `option_strategy/` business logic
- **Authoritative Standard**: `docs_templates/ai_dev_flow/` defines the complete SDD methodology
- **Templates Required**: ALWAYS use templates from `docs_templates/ai_dev_flow/{TYPE}-TEMPLATE.{ext}` when creating any artifact
- **One-Way Flow**: Changes flow from strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → code (never reverse)
- **Order Matters**: Follow the exact sequence defined in `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

## Key Instructions

**⚠️ CRITICAL**: All instructions below are defined in `docs_templates/ai_dev_flow/` (authoritative standard). When in doubt, consult the source documents in that directory.

### 1. Document ID Standards
**Authoritative Reference**: `docs_templates/ai_dev_flow/ID_NAMING_STANDARDS.md`

**Universal Numbering Pattern (All Document Types):**
- **Primary Number (XXX)**: 3-4 digit sequential number for atomic logical document (001-999, then 1000-9999 when needed)
- **Sub-Document Number (YY)**: 2-3 digit sequential number within atomic document [OPTIONAL] (01-99, then 100-999 when needed)
- **Format**: `TYPE-XXX` or `TYPE-XXX-YY` (e.g., `REQ-001`, `BRD-009-02`, `ADR-1000`)
- **Zero-Padding**: Always pad to minimum digit count (001, 01) until exceeding range
- **Uniqueness Rule**: Each XXX number is unique and can be used EITHER as:
  - Atomic document: `TYPE-XXX_{slug}.md` (e.g., `BRD-001_foundation.md`)
  - Multi-document group: `TYPE-XXX-01_{slug}.md`, `TYPE-XXX-02_{slug}.md`, etc.
  - ❌ INVALID: Cannot have both `BRD-009_{slug}.md` AND `BRD-009-01_{slug}.md` (XXX=009 collision)
  - ✅ VALID: Can have `BRD-009-01_{slug}.md` AND `BRD-009-02_{slug}.md` (same XXX, different YY)

**File Naming Patterns:**
- BRD: `BRD/BRD-XXX_{slug}.md` or `BRD-XXX-YY_{slug}.md` (Business Requirements Documents) - **NEW location: docs/BRD/**
- PRD: `PRD/PRD-XXX_{slug}.md` or `PRD-XXX-YY_{slug}.md` (Product Requirements) - **NEW location: docs/PRD/**
- SYS: `SYS/SYS-XXX_{slug}.md` or `SYS-XXX-YY_{slug}.md` (System Requirements) - **Template location: docs_templates/ai_dev_flow/SYS/**
- EARS: `EARS/EARS-XXX_{slug}.md` or `EARS-XXX-YY_{slug}.md` (Formal Requirements) - **Template location: docs_templates/ai_dev_flow/EARS/**
- REQ: `REQ/{domain}/{subdomain}/REQ-XXX_{slug}.md` or `REQ-XXX-YY_{slug}.md` (Atomic Requirements) - **Template location: docs_templates/ai_dev_flow/REQ/**
- ADR: `ADR/ADR-XXX_{slug}.md` or `ADR-XXX-YY_{slug}.md` (Architecture Decisions) - **NEW location: docs/ADR/**
- BDD: `BDD/BDD-XXX_{slug}.feature` or `BDD-XXX-YY_{slug}.feature` (Behavior-Driven Tests) - **NEW location: docs/BDD/**
- CTR: `CTR/CTR-XXX_{slug}.md` + `CTR-XXX_{slug}.yaml` or `CTR-XXX-YY_{slug}.{md,yaml}` (API Contracts - dual-file format) - **NEW location: docs/CTR/**
- SPEC: `SPEC/SPEC-XXX_{slug}.yaml` or `SPEC-XXX-YY_{slug}.yaml` (Technical Specifications, references CTR contracts) - **NEW location: docs/SPEC/**
- TASKS: `TASKS/TASKS-XXX_{slug}.md` or `TASKS-XXX-YY_{slug}.md` (Code Generation Plans) - **NEW location: docs/TASKS/**
- IMPL: `IMPL/IMPL-XXX_{slug}.md` or `IMPL-XXX-YY_{slug}.md` (Implementation Plans) - **NEW location: docs/IMPL/**

**ID Format Rules:**
- H1 headers contain full document IDs: `# REQ-003: Position Limit Enforcement` or `# BRD-009-01: Prerequisites`
- SPEC YAML uses `id:` field with lowercase_snake_case: `position_limit_service`
- Categories encoded in folder paths, not ID prefixes
- Sub-numbering (-YY) used ONLY when single logical document requires multiple related files with sequential reading order
- Each XXX number must be unique (no collisions between atomic and multi-doc patterns)

**⚠️ CRITICAL: Document ID Independence**

- **ID Numbers Do NOT Match Content**: A document's ID number does NOT necessarily correspond to related documents in other artifact types
  - Example: BRD-009 covers "Broker Integration" but PRD-009 might cover "Cash-Secured Put Workflow" (unrelated)
  - The corresponding PRD for broker integration might be PRD-016 or any other number

- **Always Use Index Files for Discovery**: To find documents by topic/content:
  - Index files use ID `000` in their identifier (e.g., PRD-000, REQ-000, ADR-000)
  - Index filenames include "index" in the name
  - Index files contain descriptions and summaries of all documents of that artifact type
  - Organized by domain, category, or functional area

**Best Practice for Cline**:
1. When searching for related documents, **find and read the index file first** (ID: 000, name contains "index")
2. Search index descriptions for keywords related to your topic
3. Do NOT assume document IDs match across artifact types
4. Use traceability tags within documents to find explicitly linked artifacts
5. Verify document content matches your topic before assuming relationship

### 2. Traceability Requirements
**Authoritative Reference**: `docs_templates/ai_dev_flow/TRACEABILITY.md`

**Traceability Section (Required):**
- Every document must include a `## Traceability` section (typically Section 7)
- Standard fields:
  - **Upstream Sources**: Prior artifacts this document derives from
  - **Downstream Artifacts**: Artifacts that depend on this document
  - **Anchors/IDs**: Primary anchor(s) in this file (e.g., `# REQ-003`)
  - **Code Path(s)**: Where related implementation resides

**Traceability Template:**
```markdown
## Traceability
- Upstream Sources: [link], [link]
- Downstream Artifacts: [link], [link]
- Anchors/IDs: `# <PRIMARY-ID-IF-ANY>`
- Code Path(s): `path/to/file.py`
```

**Cross-Reference Link Format (Mandatory):**
- Use markdown links with standardized paths: `[ADR-033](../ADR/ADR-033_risk_architecture.md#ADR-033)`
- Include anchors: `#ADR-033`, `#BDD-003`, `#CTR-001`
- Use relative paths from current file location
- Examples:
  - From docs/BRD/: `[ADR-033](../ADR/ADR-033_risk_architecture.md#ADR-033)`
  - From docs/SPEC/: `[CTR-001](../CTR/CTR-001_api_contract.md#CTR-001)`
  - From docs/TASKS/: `[BDD-003](../BDD/BDD-003_behavior_test.feature#scenario-1)`
- Validate all links resolve before committing
- Prefer stable ID anchors over line anchors

### 3. Development Workflow Steps
**Authoritative Reference**: `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

**Technology Stack Reference**:
Before making any technology decisions in ADRs, specifications, or implementation plans:
1. Read `/opt/data/trading/docs/ADR/ADR-000_technology_stack.md` for approved project-wide technologies
2. Ensure consistency with core technologies: Google ADK, MCP, A2A Protocol, GCP infrastructure
3. If proposing new technology not in ADR-000, create a new ADR justifying the addition

**Step-by-Step Process:**

**PREREQUISITE: Review Strategy Documents (option_strategy/)**
   - **ALWAYS START HERE**: Read relevant sections from `option_strategy/`
   - Reading order:
     1. `option_strategy/README.md` - Performance targets, strategy goals
     2. `option_strategy/Integrated_strategy_desc.md` - Strategic framework
     3. `option_strategy/integrated_strategy_algo_v5.md` - Bot-executable algorithm
     4. `option_strategy/delta_hedging.md` + `greeks_adjustment.md` - Risk management
     5. `option_strategy/stock_selection/` - Entry criteria
   - **Critical**: Every requirement must cite specific strategy document sections

1. **Define Business Requirements (BRD)**
   - Input: High-level business objectives, market context, strategic goals, **strategy documents**
   - Output: BRD with business case, stakeholder needs, success criteria, **Architecture Decision Requirements**
   - Focus: Business objectives, market requirements, strategic alignment
   - **Architecture Approach**: Identify architectural topics requiring decisions; do NOT reference specific ADR numbers (ADRs created in later phase)
   - Templates: `docs_templates/ai_dev_flow/BRD/BRD-template.md` (3 templates available)
   - **Traceability**: Must reference `option_strategy/` sections

2. **Capture Product Requirements (PRD)**
   - Input: Business needs from BRD, stakeholder priorities
   - Output: PRD with problem/goals/non-goals/KPIs, **Architecture Decision Requirements**
   - Focus: Product features, user needs, measurable success criteria
   - **Architecture Approach**: Document what architectural decisions are needed and why; do NOT reference specific ADR numbers (ADRs created in later phase)

3. **Formalize Requirements (EARS)**
   - Input: PRD objectives translated to precise behavioral statements
   - Output: EARS statements using WHEN-THE-SHALL-WITHIN format
   - Types: Event-driven, State-driven, Unwanted Behavior, Ubiquitous
   - Example: `WHEN [position limit exceeded] THE [system] SHALL [reject trade] WITHIN [100ms]`

4. **Specify Behavior (BDD)**
   - Input: EARS statements expressed as executable scenarios
   - Output: Gherkin feature files with Given-When-Then scenarios
   - Tagging: `@requirement:[REQ-...]` and `@adr:[ADR-...]`
   - Scenario Types: Success paths, error conditions, edge cases

5. **Record Architectural Decisions (ADR)**
   - Input: Technical alternatives evaluated, **Architecture Decision Requirements from BRD/PRD**
   - Output: ADR with context, decision, consequences, alternatives
   - **Relationship to BRD/PRD**: BRD/PRD documents identify WHAT decisions are needed; ADRs document WHICH option was chosen and WHY
   - Lifecycle: Proposed → Accepted → Superseded
   - Template: Context, Decision, Consequences, Verification, Alternatives, Relations
   - Location: `docs/ADR/` - NEW standardized location (moved from `docs/adrs/`)
   - **Technology Stack**: Reference ADR-000_technology_stack.md in `docs/ADR/` for approved technologies before proposing new tech choices

6. **Create System Requirements (SYS)**
   - Input: ADR architecture decisions and constraints
   - Output: SYS with functional/non-functional requirements, system flows
   - Focus: Technical interpretation of business requirements within architectural framework

7. **Define Atomic Requirements (REQ)**
   - Input: EARS statements and SYS requirements decomposed into granular requirements
   - Output: REQ files with description, acceptance criteria, verification
   - Structure: One requirement per file
   - Organization: `REQ/{domain}/{subdomain}/REQ-NNN_*.md`

8. **Plan Implementation (IMPL)** [CONDITIONAL - see decision guide]
   - **Decision Guide**: [WHEN_TO_CREATE_IMPL.md](../../docs_templates/ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - When to create IMPL vs skip to CTR/SPEC
   - **Create IMPL When**: Duration ≥2 weeks, teams ≥3, components ≥5, critical budget/timeline, external dependencies
   - **Skip IMPL When**: Single component, duration <2 weeks, single developer, low risk
   - Input: REQ atomic requirements, ADR architecture decisions
   - Output: IMPL document organizing work into phases, teams, deliverables
   - Focus: Project management (WHO does WHAT, WHEN) - NOT technical specifications
   - Identifies: Which CTR, SPEC, TASKS documents need to be created
   - Purpose: Coordinate team activities and track deliverables

9. **Define API Contracts (CTR) [IF INTERFACE REQUIREMENT]**
   - **Policy**: [ADR-CTR_SEPARATE_FILES_POLICY.md](../../docs_templates/ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - MANDATORY dual-file format
   - **Decision Guide**: [WHEN_TO_CREATE_IMPL.md](../../docs_templates/ai_dev_flow/WHEN_TO_CREATE_IMPL.md#when-to-create-ctr-after-impl) - CTR creation criteria
   - **Create CTR When**: Public APIs, event schemas, data models, version compatibility requirements
   - **Skip CTR When**: Internal logic only, no external interface, no serialization
   - Input: Interface-focused REQ, ADR architecture decisions, IMPL deliverables list (if IMPL exists)
   - Output: Dual-file contract (CTR-NNN_slug.md + CTR-NNN_slug.yaml)
   - Process: Define contract in markdown (context), define schema in YAML (JSON Schema), update traceability
   - Validation: Both files must exist, slugs must match, schema must be valid OpenAPI/AsyncAPI

10. **Author Technical Specifications (SPEC)**
    - Input: REQ acceptance criteria, ADR constraints, BDD scenarios, CTR contracts (if applicable), IMPL deliverables
    - Output: YAML blueprints for code generation (HOW to build)
    - Sections: Interface implementations (references CTR), behavioral specs, operational requirements, performance targets
    - Contract Reference: Use `contract_ref:` field when implementing CTR
    - Machine-readable format for automated code generation
    - **Distinction**: SPEC defines HOW to build; IMPL defines WHO builds WHEN

11. **Plan Implementation Tasks (TASKS)**
    - Input: SPEC interfaces (including CTR references), behavioral specifications, IMPL schedules
    - Output: AI-structured implementation guidance with exact TODOs to implement SPEC
    - Structure: Scope, Plan, Constraints, Acceptance
    - Purpose: Break work into parallel tasks with clear acceptance criteria
    - **One TASKS per SPEC**: Each TASKS document corresponds to one SPEC

12. **Implement Code**
    - Input: SPEC interfaces, CTR contracts (if implementing interface), TASKS plans, BDD scenarios
    - Output: Source code matching SPEC and CTR exactly
    - Requirements: Interface compliance (from SPEC/CTR), BDD validation, contract tests, observability
    - Traceability: Docstring links to all artifacts including CTR

13. **Verify Implementation**
    - Methods: BDD execution, interface validation (against SPEC), contract testing (against CTR), performance benchmarking, integration testing
    - Output: Verification that implementation satisfies all requirements, matches SPEC interfaces, and complies with CTR contracts
    - Automation: Automated verification with traceable results, contract test frameworks (Pact, Spring Cloud Contract)

14. **Validate Traceability**
    - Checks: Link resolution, ID format compliance, tagging consistency, requirement coverage, contract/SPEC alignment
    - CTR Validation: Both .md and .yaml files exist, slugs match, schema valid
    - Tools: `python scripts/validate_requirement_ids.py`
    - Pre-commit: Automated validation before commit

### 4. Documentation Standards
**Authoritative Reference**: `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (Appendix sections)

**Language Requirements:**
- Objective, factual language only
- No promotional content or subjective claims
- Document implementation complexity (scale 1-5)
- Include resource requirements and constraints
- Specify failure modes and error conditions

**Code Separation:**
- No Python code blocks in markdown documentation
- Use Mermaid flowcharts for logic representation
- Create separate `.py` files for code examples
- Reference format: `[See Code Example: filename.py - function_name()]`

**Token Efficiency (Tool-Optimized):**
- Claude Code: Maximum 50,000 tokens (200KB) standard, 100,000 tokens (400KB) absolute maximum
- Gemini CLI: Use file read tool (not `@`) for files >10,000 tokens - no splitting needed
- GitHub Copilot: Keep <30KB or create companion summaries
- Create sequential files only when exceeding 100,000 tokens or logical boundaries
- One sentence per function description maximum
- Use tabular format for parameter specifications
- Employ bullet points for configuration options
- See: [TOOL_OPTIMIZATION_GUIDE.md](../../TOOL_OPTIMIZATION_GUIDE.md)

### 5. Quality Gates (Definition of Done)

**Pre-Commit Checklist:**
- [ ] Document Control section completed with all required metadata (project name, version, date, owner, preparer, status)
- [ ] Document Revision History table initialized with at least initial version entry
- [ ] IDs comply with `ID_NAMING_STANDARDS.md` (XXX or XXX-YY format, H1 anchors, zero-padding)
- [ ] No ID collisions: each XXX number used only once (either atomic TYPE-XXX OR multi-doc TYPE-XXX-YY group, never both)
- [ ] All cross-references use markdown links with valid paths and anchors
- [ ] **IMPL decision validated**: Followed `WHEN_TO_CREATE_IMPL.md` decision criteria (created IMPL if complex project, skipped if simple task)
- [ ] **CTR decision validated**: Followed `WHEN_TO_CREATE_IMPL.md` CTR criteria (created CTR if interface requirement, skipped if internal logic)
- [ ] SPEC interfaces match CTR contracts (if applicable) and implementation exactly
- [ ] **CTR dual-file format**: Both .md and .yaml exist with matching slugs (MANDATORY per ADR-CTR if CTR created)
- [ ] CTR YAML schema validation passes (if applicable)
- [ ] BDD scenarios tagged with `@requirement` and `@adr` links
- [ ] Non-functional requirements defined (latency, error handling, logging)
- [ ] Observability requirements specified (logs, metrics, traces)
- [ ] Code docstrings include full traceability chain (including CTR if applicable)
- [ ] Contract tests pass (if implementing CTR)
- [ ] Validation scripts pass: `python scripts/validate_requirement_ids.py`
- [ ] No broken links or missing anchors
- [ ] File size under 50,000 tokens (Claude Code) or 100,000 tokens maximum
- [ ] For Gemini CLI users: Note to use file read tool (not `@`) if >10,000 tokens

### 6. Example: Position Risk Limits Flow

**Complete Artifact Chain:**
- **Strategy**: `option_strategy/integrated_strategy_algo_v5.md` - Risk budget and position limits business logic
- **BRD**: Business requirements document (if applicable)
- **PRD**: Product requirements for position risk limits
- **SYS**: System requirements specification
- **EARS**: Formal WHEN-THE-SHALL-WITHIN requirements
- **REQ**: [REQ-003_position_limit_enforcement.md](../../docs_templates/ai_dev_flow/REQ/risk/lim/REQ-003_position_limit_enforcement.md)
- **ADR**: Architecture decision for risk limit enforcement
- **BDD**: Gherkin feature file with test scenarios
- **CTR**: [CTR-001_position_risk_validation.md + .yaml](../../docs_templates/ai_dev_flow/CTR/) (if interface requirement)
  - Markdown: Contract context, definitions, error handling, NFRs, versioning
  - YAML: JSON Schema request/response definitions, error codes, endpoint specifications
- **SPEC**: YAML technical specification referencing CTR contract
  - `contract_ref: CTR-001_position_risk_validation` - Links to contract
  - `requirements_source:` - Links to REQ-003
  - `architecture:` - Links to ADR
  - `verification:` - Links to BDD scenarios and contract tests
- **TASKS**: Implementation plan for AI-assisted development
- **Code**: `position_limit_service.py` (implements CTR contract interface)
  - Docstring includes CTR traceability
  - Contract tests validate compliance

### 7. Validation Commands

**Required Validations:**
```bash
# Validate requirement IDs and format
python scripts/validate_requirement_ids.py

# Check broken references (if available)
python scripts/check_broken_references.py

# Generate traceability matrix (if available)
python scripts/complete_traceability_matrix.py
```

### 8. Cline Best Practices

**When Creating New Artifacts:**
1. **START WITH STRATEGY**: Read relevant `option_strategy/` documents FIRST
2. **Check Technology Stack** (for ADRs/SPECs): Read `docs/ADR/ADR-000_technology_stack.md` for approved technologies
3. **Use Templates**: Browse `docs_templates/ai_dev_flow/` for applicable template
4. **Reading order**: Strategy → Technology Stack (if applicable) → Template → Index → Workflow → Implementation Guide → Referenced artifacts
5. Reserve next sequential ID number before creating file
6. Include universal tag header at top of file
7. Follow document structure from templates
8. **Fill Document Control Section**: Complete project metadata (name, version, date, owner, preparer, status) and initialize Document Revision History table
9. **Add Strategy References**: Link to specific `option_strategy/` sections in Traceability
10. **CREATE/UPDATE TRACEABILITY MATRIX** ⚠️ **MANDATORY**:
   - File: `docs/[TYPE]/[TYPE]-000_TRACEABILITY_MATRIX.md`
   - Template: `docs_templates/ai_dev_flow/[TYPE]/[TYPE]-000_TRACEABILITY_MATRIX-TEMPLATE.md`
   - Update within same commit as artifact creation
   - Add upstream sources (which docs drove this)
   - Add downstream artifacts (which docs/code derive from this)
   - Matrix must be created/updated BEFORE committing artifact
11. Validate all cross-references resolve
12. Run validation scripts before committing

**Understanding Document Roles:**
- **IMPL**: Answers "WHO does WHAT, WHEN" - project management coordination
- **SPEC**: Answers "HOW to build" - technical implementation blueprints
- **TASKS**: Answers "WHAT exact steps" - AI-readable TODOs to implement SPEC
- **CTR**: Answers "WHAT interface" - formal contracts between components (dual-file: .md + .yaml)

**Directory Context Rules:**
- Creating docs in `docs/`: Use templates from `docs_templates/`
- Implementing trading logic: Reference `option_strategy/` sections (current V5 only)
- Creating new strategy: Only with explicit user permission (Product Owner role)
- Infrastructure/DevOps: Strategy references not required
- **STRICTLY PROHIBITED: Any path containing "archived"**: Skip automatically, inform user, request permission

**Task Decomposition:**
- Provide 3-6 linear steps per task
- Minimal scope per task
- Name exact files and symbols
- Include "do not touch" constraints
- State precise acceptance criteria

**Change Management:**
- Upstream changes (PRD/EARS/REQ): Update ADR/BDD/SPEC; re-run validations
- SPEC changes: Update Code + BDD; maintain backward compatibility
- Code changes: Update BDD scenarios; verify traceability
- Always update traceability sections and code docstrings

### 9. Traceability Matrix Enforcement (MANDATORY)

#### Policy

**CRITICAL RULE**: EVERY time you create or update a document of ANY artifact type (BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS), you MUST:

1. **Check for existing traceability matrix**: Look for `[TYPE]-000_TRACEABILITY_MATRIX.md`
2. **Create if missing**: Use template from `docs_templates/ai_dev_flow/[TYPE]/[TYPE]-000_TRACEABILITY_MATRIX-TEMPLATE.md`
3. **Update if exists**: Add new document entry with:
   - Document ID and title
   - Upstream sources (documents that drove this artifact)
   - Downstream artifacts (documents/code derived from this)
   - Status and completion percentage
4. **Validate bidirectional links**: Ensure all references resolve correctly

#### Quality Gate

**Hard Requirement**: Pull requests will be rejected if traceability matrix is not updated.

**Zero Exceptions**: This applies to ALL artifact types without exception.

#### Example Workflow

**Scenario**: User requests "Create PRD-001 for IB MCP Server"

**Cline Actions**:
```bash
1. ✅ Read BRD-001 (upstream source)
2. ✅ Create PRD-001_ib_mcp_server_product.md
3. ✅ **Create/Update PRD-000_TRACEABILITY_MATRIX.md** ← MANDATORY STEP
   - Add PRD-001 entry to Section 2 (Complete PRD Inventory)
   - Link upstream: BRD-001 (Section 3.1)
   - Link downstream: EARS-001 (to be created), BDD-XXX (to be created)
   - Status: Draft, Completion: 0%
4. ✅ Update PRD-000_index.md
5. ✅ Validate all links resolve
6. ✅ Commit all 3 files together (artifact + matrix + index)
7. ✅ Report to user: "Created PRD-001, updated traceability matrix, updated index"
```

#### Matrix Contents

Each traceability matrix tracks:

**Section 2: Complete Inventory**: All documents of this type with status
**Section 3: Upstream Traceability**: Which documents drove creation (BRD → PRD → EARS, etc.)
**Section 4: Downstream Traceability**: Which documents/code derive from this (PRD → EARS → BDD → REQ)
**Section 5: Cross-Dependencies**: Relationships between documents of same type
**Section 8: Implementation Status**: Completion percentage and validation status

#### Templates Location

All artifact types have traceability matrix templates:

```
docs_templates/ai_dev_flow/
├── BRD/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── PRD/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── EARS/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── ADR/ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── SYS/SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── IMPL/IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── CTR/CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md
├── SPEC/SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md
└── TASKS/TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md
```

#### Why This Matters

**Impact Analysis**: When BRD-001 changes, matrix shows affected PRDs, EARS, BDD, REQ, SPEC, Code
**Coverage Validation**: Ensures no orphaned requirements (100% traceability)
**Regulatory Compliance**: Audit trails required for SEC, FINRA, FDA, ISO compliance
**Change Management**: Know exactly what breaks when upstream requirements change
**Quality Assurance**: Automated validation prevents missing links

## Related Resources

**⭐ Primary Reference - Authoritative Development Standard:**

All documentation below is located in `docs_templates/ai_dev_flow/` - the **single source of truth** for SDD methodology.

**Core Standards:**
- **Main Guide**: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete 13-step workflow
- **Authoritative Workflow Diagram**: [index.md](../../docs_templates/ai_dev_flow/index.md#traceability-flow) - Complete Mermaid diagram (single source of truth)
- **ID Standards**: [ID_NAMING_STANDARDS.md](../../docs_templates/ai_dev_flow/ID_NAMING_STANDARDS.md) - File naming, ID format rules
- **Traceability**: [TRACEABILITY.md](../../docs_templates/ai_dev_flow/TRACEABILITY.md) - Cross-reference format, link standards
- **When to Create IMPL**: [WHEN_TO_CREATE_IMPL.md](../../docs_templates/ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL vs direct REQ→SPEC decision guide
- **Phase 1 Completion**: [WORKFLOW_FIXES_PHASE1_COMPLETE.md](../../docs_templates/ai_dev_flow/WORKFLOW_FIXES_PHASE1_COMPLETE.md) - Recent fixes and standardization
- **README**: [README.md](../../docs_templates/ai_dev_flow/README.md) - Getting started guide

**Project Documentation:**
- Core Principles: [PROJECT_CORE_PRINCIPLES.md](../../PROJECT_CORE_PRINCIPLES.md)
- Claude Instructions: [CLAUDE.md](../../CLAUDE.md)
- SDD Framework: [docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md](../../docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md)

**Templates and READMEs** (all in `docs_templates/ai_dev_flow/`):

**⚠️ Important Path Distinction:**
- **Templates**: Located in `docs_templates/ai_dev_flow/{lowercase_dir}/` (lowercase directory names)
- **Production Documents**: Created in `docs/{UPPERCASE_DIR}/` (uppercase directory names)
- **Example**: Copy template from `docs_templates/ai_dev_flow/ADR/ADR-TEMPLATE.md` → Create document in `docs/ADR/ADR-033_risk_architecture.md`

Each artifact type directory contains:
- **Index File**: `{TYPE}-000_index.{ext}` - Lists all documents of that type
- **Template File**: `{TYPE}-TEMPLATE.{ext}` - **ALWAYS use this as starting point for new documents**
- **README.md**: Detailed usage guide and best practices

**Available Templates** (location: `docs_templates/ai_dev_flow/{artifact_type}/`):
- **BRD** (`BRD/`): **3 templates available** for different use cases
  - `BRD-template.md` - Comprehensive business requirements (general purpose)
  - `BRD-template-2.md` - Alternative format (simplified structure)
  - `BRD-trading-template.md` - Trading-specific requirements (options trading focus)
  - Index: `BRD-000_index.md`
  - **Usage**: Choose template based on project context (general, simplified, or trading-focused)
  - **Document Control**: All templates include Document Control section with project metadata and Document Revision History table
- **PRD** (`PRD/`): `PRD-TEMPLATE.md`, Index: `PRD-000_index.md`, README
- **SYS** (`SYS/`): `SYS-TEMPLATE.md`, Index: `SYS-000_index.md`, README
- **EARS** (`EARS/`): `EARS-TEMPLATE.md`, Index: `EARS-000_index.md`, README
- **REQ** (`REQ/`): `REQ-TEMPLATE.md`, Index: `REQ-000_index.md`, README
  - Organized by domain: `api/`, `risk/`, `ml/`, `data/`
- **ADR** (`ADR/`): `ADR-TEMPLATE.md`, Index: `ADR-000_index-TEMPLATE.md`, README
  - **Document Control**: Template includes Document Control section with project metadata and Document Revision History table
- **BDD** (`BDD/`): `BDD-TEMPLATE.feature`, Index: `BDD-000_index.feature`, README
  - **Document Control**: Template includes Document Control section with project metadata and Document Revision History table
- **CTR** (`CTR/`): `CTR-TEMPLATE.md`, `CTR-TEMPLATE.yaml` (dual-file), Index: `CTR-000_index.md`, README
  - **MANDATORY dual-file format**: Both .md and .yaml required per contract (see ADR-CTR)
  - **Document Control**: Template includes Document Control section with project metadata and Document Revision History table
  - Policy: [ADR-CTR_SEPARATE_FILES_POLICY.md](../../docs_templates/ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - Authoritative policy
  - Optional organization: subdirectories by service type (agents/, mcp/, infra/, shared/)
  - Examples: [CTR-001_risk_validator_api.md/.yaml](../../docs_templates/ai_dev_flow/CTR/examples/) - Complete reference implementation
- **SPEC** (`SPEC/`): `SPEC-TEMPLATE.yaml`, Index: `SPEC-000_index.md`, README
  - Organized by type: `services/`, `agents/`, `infrastructure/`
  - References CTR contracts via `contract_ref:` field
- **TASKS** (`TASKS/`): `TASKS-TEMPLATE.md`, Index: `TASKS-000_index.md`, README

## Quick Reference

**Reading Order for New Components:**

1. Specification Index
2. Component Type Workflow (Agent/MCP/Infrastructure)
3. Implementation Guide with YAML spec
4. Referenced Requirements
5. Referenced ADRs
6. Business Logic

**Development ROI:**

- Traditional: 70 hours/component
- SDD: 1.5 hours/component
- Speed increase: 48x faster
- Consistency: 100% (template-based)
- Traceability: Automatic, bidirectional

## Usage Example

When asked to implement a new feature:

1. **Start**: "I'll use the doc-flow rule to implement this using SDD methodology per `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`"
2. **Read Strategy**: Review relevant `option_strategy/` documents FIRST (Product Owner voice)
3. **Read Standard**: Review `docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` for workflow steps
4. **Find Templates**: Browse `docs_templates/ai_dev_flow/{artifact_type}/` for applicable templates
5. **Create Artifacts**: Generate in CORRECT order: BRD → PRD → **EARS** → BDD → ADR → SYS → REQ → IMPL [IF COMPLEX] → **CTR** [IF INTERFACE] → SPEC → TASKS
6. **Use Templates**: ALWAYS copy from `{TYPE}-TEMPLATE.{ext}` for each new document (both .md and .yaml for CTR)
7. **Link**: Add traceability tags to each artifact (including strategy references and CTR contracts)
8. **Validate**: Run validation scripts (`python scripts/validate_requirement_ids.py`), verify CTR dual-file format
9. **Implement**: Generate code from SPEC (implementing CTR contracts if applicable)
10. **Verify**: Execute BDD tests, contract tests, and traceability validation

**Example invocation:**

```text
User: "Implement position risk limit validation"
Cline: "I'll use the doc-flow rule to implement this feature following the authoritative SDD methodology defined in docs_templates/ai_dev_flow/.

Step 1: Read strategy business logic
- option_strategy/integrated_strategy_algo_v5.md - for risk budget algorithms (Section 4.2)
- option_strategy/delta_hedging.md - for portfolio-level limits

Step 2: Read development standard
- docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md - for complete workflow

Step 3: Create artifact chain using templates from docs_templates/ai_dev_flow/
- BRD-015 (copy template → create in docs/BRD/)
  - Includes "Architecture Decision Requirements" section listing topics needing ADRs
  - Does NOT reference specific ADR numbers (ADRs created later)
- PRD-015 (copy template → create in docs/PRD/)
  - Includes "Architecture Decision Requirements" section
  - Does NOT reference specific ADR numbers (ADRs created later)
- EARS-015 (copy template) ← After PRD
- BDD-003 (copy template → create in docs/BDD/) ← After EARS
- ADR-033 (copy template → create in docs/ADR/) ← **NOW CREATE ADRs based on topics identified in BRD/PRD**
- SYS-015 (copy template) ← After ADR
- REQ-003 (copy template) ← After SYS
- IMPL-005 (copy template → create in docs/IMPL/) ← IF complex project (see WHEN_TO_CREATE_IMPL.md)
- CTR-001 (copy both templates → create in docs/CTR/) ← IF interface requirement
- SPEC-015 (copy template → create in docs/SPEC/, reference CTR-001 if applicable)
- TASKS-015 (copy template → create in docs/TASKS/)

Each artifact will include full traceability to upstream strategy documents, CTR contracts (if applicable), and downstream implementation."
```

**What NOT to do:**

```text
User: "Implement position risk limit validation"
Cline: "Let me check the archived/ folder for examples..." ❌ STRICTLY PROHIBITED

Correct: "Let me check option_strategy/ for current V5 strategy requirements..." ✅ CORRECT
```

**Archived Content Detection:**

- If search/glob results include paths with "archived": Filter them out automatically
- If only archived content found: Inform user and request permission
- Never suggest archived content as alternative without explicit user request
