
Development Principles Guide

## The AI-Driven Specification-Driven Development Workflow

**⚠️ For the complete authoritative workflow diagram, see [index.md](./index.md#traceability-flow).**

### Workflow Overview

The SDD workflow transforms business needs into production-ready code through traceable artifacts organized in 16 layers (Layer 0: Strategy through Layer 15: Validation):

**Strategy Layer** (Layer 0) → **Business Layer** (BRD → PRD → EARS) → **Testing Layer** (BDD) → **Architecture Layer** (ADR → SYS) → **Requirements Layer** (REQ) → **Project Management Layer** (IMPL) → **Interface Layer** (CTR - optional) → **Implementation Layer** (SPEC) → **Code Generation Layer** (TASKS) → **Implementation Plans Layer** (IPLAN) → **Execution Layer** (Code → Tests) → **Validation Layer** (Validation → Review → Production)

**Key Decision Point**: After IMPL, if the requirement involves an interface (API, event schema, data model), create CTR before SPEC. Otherwise, go directly to SPEC.

#### Visual Workflow Diagram

**Cumulative Tagging**: Each artifact includes tags from ALL upstream artifacts (see diagram annotations below)

```mermaid
graph LR
    subgraph L1["Layer 1: Business"]
        BRD["BRD<br/><small>(0 tags)</small>"] --> PRD["PRD<br/><small>(@brd)</small>"] --> EARS["EARS<br/><small>(@brd, @prd)</small>"]
    end

    subgraph L2["Layer 2: Testing"]
        BDD["BDD<br/>Behavior Tests<br/><small>(@brd, @prd, @ears)</small>"]
    end

    subgraph L3["Layer 3: Architecture"]
        ADR["ADR<br/><small>(@brd through @bdd)</small>"] --> SYS["SYS<br/><small>(@brd through @adr)</small>"]
    end

    subgraph L4["Layer 4: Requirements"]
        REQ["REQ<br/>Atomic Requirements<br/><small>(@brd through @sys)</small>"]
    end

    subgraph L5["Layer 5: Project Management"]
        IMPL["IMPL<br/><i>WHO/WHEN</i><br/><small>(@brd through @req)</small>"]
    end

    subgraph L6["Layer 6: Interface"]
        CTR["CTR<br/><i>optional</i><br/><small>(@brd through @impl)</small>"]
    end

    subgraph L7["Layer 7: Implementation"]
        SPEC["SPEC<br/><i>YAML</i><br/><small>(@brd through @req + opt)</small>"]
    end

    subgraph L8["Layer 8: Code Generation"]
        TASKS["TASKS<br/>Generation Plans<br/><small>(@brd through @spec)</small>"]
    end

    subgraph L9["Layer 9: Implementation Plans"]
        TP["IPLAN<br/>Session Context<br/><small>(@brd through @tasks)</small>"]
    end

    subgraph L13["Layer 13: Code"]
        CODE["Code<br/><small>(@brd through @tasks)</small>"]
    end

    subgraph L14["Layer 14: Tests"]
        TESTS["Tests<br/><small>(@brd through @code)</small>"]
    end

    subgraph L15["Layer 15: Validation"]
        VAL["Validation<br/><small>(all upstream)</small>"] --> REV[Review] --> PROD[Production]
    end

    CODE --> TESTS

    EARS --> BDD
    BDD --> ADR
    SYS --> REQ
    REQ --> IMPL
    IMPL --> CTR
    CTR --> SPEC
    SPEC --> TASKS
    TASKS --> TP
    TP --> CODE
    TESTS --> VAL
    PROD -.-> BRD

    style BRD fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    style PRD fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    style EARS fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    style BDD fill:#fff3cd,stroke:#f9a825,stroke-width:2px
    style ADR fill:#d4edda,stroke:#388e3c,stroke-width:2px
    style SYS fill:#d4edda,stroke:#388e3c,stroke-width:2px
    style REQ fill:#f8d7da,stroke:#d32f2f,stroke-width:2px
    style IMPL fill:#d1ecf1,stroke:#0097a7,stroke-width:2px
    style CTR fill:#e2e3e5,stroke:#616161,stroke-width:2px
    style SPEC fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style TASKS fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style TP fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style CODE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style TESTS fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style VAL fill:#e0f2f1,stroke:#00897b,stroke-width:2px
    style REV fill:#e0f2f1,stroke:#00897b,stroke-width:2px
    style PROD fill:#e0f2f1,stroke:#00897b,stroke-width:2px
```

**Layer Descriptions** (Formal Layer Numbers 0-15):
- **Layers 1-3 - Business** (Blue): BRD (L1) → PRD (L2) → EARS (L3) - Strategic direction and product vision
- **Layer 4 - Testing** (Yellow): BDD - Acceptance criteria and test scenarios
- **Layers 5-6 - Architecture** (Green): ADR (L5) → SYS (L6) - Technical decisions and system design
- **Layer 7 - Requirements** (Red): REQ - Detailed atomic requirements
- **Layer 8 - Project Management** (Cyan): IMPL - Implementation planning (WHO/WHEN) - optional
- **Layer 9 - Interface** (Gray): CTR - API contracts (created when needed) - optional
- **Layer 10 - Technical Specifications** (Orange): SPEC - Technical specifications (YAML)
- **Layer 11 - Code Generation** (Pink): TASKS - Detailed implementation tasks
- **Layer 12 - Implementation Plans** (Light Blue): IPLAN - Session context with bash commands
- **Layer 13 - Code** (Purple): Source code implementation
- **Layer 14 - Tests** (Green): Test execution and verification
- **Layer 15 - Validation** (Teal): Validation → Review → Production (Quality gates and deployment)

**Note on Layer Numbering:**
- **Formal layer numbers**: 0-15 (used in cumulative tagging, templates, specifications)
- **Mermaid diagram groupings**: L1-L9, L13-L15 (visual organization for diagrams)
- When implementing cumulative tagging, always use formal layer numbers (0-15)
- The full 16-layer architecture includes optional layers (IMPL at layer 8, CTR at layer 9) which may not always be present

See [index.md](./index.md#traceability-flow) for additional workflow visualizations and [TRACEABILITY.md](./TRACEABILITY.md) for complete traceability guidelines.


# Important Traceability Condition
PRDs should reference the documentation in this directory, but the documentation itself should not reference PRDs. The documentation is the authoritative source for requirements and features.
# Spec-Driven Development (SDD) Guide — Examples
@requirement:[REQ-003](./REQ/risk/lim/REQ-003_position_limit_enforcement.md#REQ-003)
@adr:[ADR-033](./ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033)
@spec:[position_limit_service](./SPEC/services/SPEC-003_position_limit_service.yaml)

Status: Example-scoped standard for ai_dev_flow. Aligns with `.project_instructions/DOCUMENT_ID_CORE_RULES.md`, `docs/DOCUMENT_ID_CORE_RULES.md`, `TRACEABILITY.md`, and `ID_NAMING_STANDARDS.md`.

## Purpose
- Establish a clear, repeatable, and testable process to move from product intent to code using specifications as the source of truth.
- Ensure every behavior is traceable: PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → Code.

## Concept
- Define behavior, interfaces, constraints, and verification in unambiguous specifications before coding.
- Complementary to TDD/BDD: the spec drives tests and code; BDD verifies acceptance; TDD covers units.

## Principles
- Single Source of Truth: The technical specification defines the implementation.
- One-Doc-Per-ID: Each REQ/ADR/SPEC file holds one document; filenames include IDs.
- Specification-First: Technical specifications precede implementation.
- Complete Traceability: All cross-references use markdown link format with anchors.
- Executable Examples: Provide concrete I/O examples in SPEC for deterministic codegen.
- Non-Functional First-Class: Performance, reliability, observability, and security are explicit in SPEC.
- Minimal, Reviewable Diffs: Small steps; verify at each gate.
- Change via ADR: Architectural changes recorded and linked.
- **Document Structure Simplicity**: Keep documents as single comprehensive files with clear section headings. Only split into multiple files when file exceeds 1,000 lines AND has multiple distinct audience needs OR complex dependency chains requiring separate documentation. Use table of contents for navigation within single documents.
- Document ID Independence: IDs are sequential within artifact type; consult index files (ID: 000) to discover documents by topic or content

## Document Discovery and ID Independence

**⚠️ CRITICAL: Document IDs are independent of document content**

- **ID Numbers Do Not Match Content**: A document's ID number (e.g., PRD-009, REQ-015, BDD-003) does NOT necessarily correspond to related documents in other artifact types
- **Always Try to Find and Use Index Files**: To find documents by topic/content, consult the index file for each artifact type
  - Index files use ID `000` in their identifier (e.g., PRD-000, REQ-000, ADR-000)
  - Index filenames include "index" in the name
  - Index files contain descriptions and summaries of all documents of that artifact type
  - Organized by domain, category, or functional area depending on artifact type

**Example Scenario**:
- BRD-009 covers "[EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration Pilot"
- PRD-009 might cover "[STRATEGY_NAME] Workflow" (completely unrelated topic)
- The corresponding PRD for [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] integration might be PRD-016 or any other number
- **Solution**: Find and read the PRD index file (ID: 000, filename contains "index") to search descriptions for [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] integration keywords

**Best Practice for AI Assistants**:
1. When searching for related documents, **find and read the index file first** (ID: 000, name contains "index")
2. Search index descriptions and summaries for keywords related to your topic
3. Do NOT assume document IDs match across artifact types
4. Use traceability tags within documents to find explicitly linked artifacts
5. Verify document content matches your topic before assuming relationship

## Required Artifacts (with ID standards)

### Product Requirements Documents (PRD)
- **Purpose**: Capture business requirements and product strategy before technical implementation
- **File Format**: `PRD-NNN_descriptive_title.md`
- **Contents**: Problem statement, goals, non-goals, KPIs, acceptance criteria
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Starting point of development workflow - defines "what" needs to be built
- **Key Sections**:
  - Problem: Current state issues and business impact
  - Goals: Measurable outcomes and success criteria
  - Non-Goals: Explicit scope boundaries
  - KPIs: Quantitative business metrics
  - Acceptance: Business-focused validation criteria

### System Requirements (SYS)
- **Purpose**: Technical interpretation of business requirements
- **File Format**: `SYS-NNN_descriptive_title.md`
- **Contents**: Functional and non-functional requirements, system flows
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Bridge between business PRDs and technical EARS requirements

### EARS Requirements (EARS)
- **Purpose**: Precise, testable requirements using structured WHEN-THE-SHALL-WITHIN syntax
- **File Format**: `EARS-NNN_descriptive_title.md`
- **Statement Types**:
  - Event-driven: `WHEN [condition] THE [system] SHALL [action] WITHIN [timeframe]`
  - State-driven: `WHILE [condition] THE [system] SHALL [behavior] WITHIN [constraint]`
  - Unwanted Behavior: `IF [condition] THE [system] SHALL [prevention] WITHIN [timeframe]`
  - Ubiquitous: `THE [system] SHALL [requirement] WITHIN [constraint]`
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Transforms PRDs/SYS into formal, measurable requirements

### Atomic Requirements (REQ)
- **Purpose**: Break complex requirements into single, testable statements
- **File Format**: `REQ/{domain}/{subdomain}/REQ-NNN_descriptive_title.md`
- **Structure**:
  - Description: Precise SHALL statement defining one behavior
  - Acceptance Criteria: Measurable validation conditions
  - Related ADRs: Architecture decisions implementing the requirement
  - Source Requirements: Links to upstream PRD/EARS requirements
  - Verification: Method to prove requirement satisfaction
- **Hierarchical Organization**: Grouped by functional domains (api, risk, data, etc.)
- **Key Characteristics**: One atomic requirement per file, measurable criteria, BDD scenario linkage

### API Contracts (CTR)
- **Purpose**: Formal interface specifications for component-to-component communication
- **File Format (Dual)**: `CTR/CTR-NNN_descriptive_slug.md` + `CTR-NNN_descriptive_slug.yaml`
- **When to Create**: When REQ specifies interface requirements between components/services
- **Structure**:
  - Markdown (.md): Human-readable context, requirements satisfied, NFRs, versioning, traceability
  - YAML (.yaml): Machine-readable request/response schemas, error codes, performance targets
- **Key Sections**:
  - Contract Definition: Interface overview, parties (provider/consumer), communication pattern
  - Interface Specification: Request/response schemas using JSON Schema
  - Error Handling: Complete error taxonomy with codes and retry policies
  - Non-Functional Requirements: Latency, idempotency, rate limiting, [SAFETY_MECHANISM - e.g., rate limiter, error threshold] settings
  - Versioning Strategy: Semantic versioning rules, deprecation policy
- **Organization**: Optional subdirectories by service type (`agents/`, `mcp/`, `infra/`, `shared/`)
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: After REQ, before SPEC - enables parallel development with contract-first approach
- **Benefits**: Parallel development, early validation, prevents implementation drift, testable interfaces

### Architecture Decision Records (ADR)
- **Purpose**: Document architectural decisions with rationale and consequences
- **File Format**: `ADR-NNN_descriptive_title.md`
- **Template Structure**:
  - Context: Problem, background, driving forces, constraints
  - Decision: Chosen solution and implementation approach
  - Consequences: Positive/negative impacts, trade-offs, risks
  - Verification: BDD scenarios validating architectural approach
  - Alternatives: Rejected options with specific reasons
  - Relations: Dependencies, supersedes, impacts on other decisions
- **Lifecycle**: Proposed → Accepted → Superseded/Deprecated
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Decision artifacts bridge requirements with implementation

### Behavior-Driven Development (BDD)
- **Purpose**: Executable specifications written in natural language
- **File Format**: `BDD-NNN_descriptive_requirements.feature`
- **Scenario Types**: Success path, alternative path, error path, edge cases
- **Gherkin Syntax**: Given-When-Then structure for behavioral specifications
- **Key Features**:
  - Feature statements with business value
  - Tagged scenarios for traceability (`@requirement`, `@adr`)
  - Background setup shared across scenarios
  - Example tables for data-driven scenarios
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Operational requirements validating technical implementation

### Technical Specifications (SPEC)
- **Purpose**: Machine-readable technical blueprints for implementation
- **File Format**: `SPEC/{domain}/SPEC-NNN_{component_name}.yaml`
- **Core Sections**:
  - Interface definitions (functions, classes, schemas)
  - Behavioral specifications (states, error handling, circuit breakers)
  - Operational requirements (caching, rate limiting, observability)
  - Performance specifications (latency, throughput, resource limits)
  - Verification mapping (BDD scenarios, load tests, integration tests)
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: YAML implementation specifications translated into executable code

### AI Tasks (TASKS)
- **Purpose**: Structured implementation guidance for AI-assisted development
- **File Format**: `TASKS-NNN_descriptive_component_tasks.md`
- **Structure**:
  - Scope: Clearly bounded implementation responsibility
  - Plan: Numbered sequence of development activities
  - Constraints: Technical boundaries and limitations
  - Acceptance: Verification requirements for completion
- **[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: Implementation roadmap connecting specifications to code

### Code Implementation
- **Purpose**: Executable realization of specifications
- **File Structure**: `src/{module_name}/` implementing SPEC-defined interfaces
- **Requirements**: Exact match to SPEC interfaces, contract compliance (if implementing CTR), BDD scenario validation
- **Traceability**: Docstring links to all artifacts (PRD, EARS, REQ, ADR, CTR if applicable, BDD, SPEC)

## Universal Tag Header (Required)

All artifacts (Markdown/YAML/Feature/Code) must include lightweight traceability tags to declare upstream dependencies.

### Tag Format: Namespaced Auto-Discovery

**Structure:** `@tag-type: DOCUMENT-ID:REQUIREMENT-ID`

**Tag Types:**
- `@brd:` - Business Requirements Document references
- `@prd:` - Product Requirements Document references
- `@ears:` - EARS requirements references
- `@sys:` - System Requirements references
- `@adr:` - Architecture Decision Record references
- `@req:` - Requirements Document references (V2)
- `@spec:` - Specification references
- `@contract:` - Contract references (CTR)
- `@test:` - Test scenario references (BDD)
- `@impl-status:` - Implementation status (pending|in-progress|complete|deprecated)

**Format Rules:**
- **Multi-requirement documents:** Use namespace format: `BRD-001:FR-030`
- **Single-document references:** Namespace optional: `SPEC-003` or `SPEC-003:main`
- **Multiple references:** Comma-separated: `BRD-001:FR-030, BRD-001:NFR-006`
- **Multiple documents:** `BRD-001:FR-020, BRD-002:FR-105`

**Examples:**

Python docstring:
```python
"""Market data service implementation.

@brd: BRD-001:FR-010, BRD-001:FR-011, BRD-001:NFR-005
@prd: PRD-003
@req: REQ-003:interface-spec
@adr: ADR-033
@contract: CTR-001
@spec: SPEC-002
@test: BDD-002:scenario-realtime, BDD-008:scenario-cache
@impl-status: complete
"""
```

Markdown document:
```markdown
@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-003
@req: REQ-003
@adr: ADR-033
@contract: CTR-001
@spec: SPEC-002
@test: BDD-001:scenario-enforcement
@impl-status: complete
```

YAML comment header:
```yaml
# @brd: BRD-001:FR-010, BRD-001:NFR-005
# @req: REQ-003:data-schema
# @spec: SPEC-002
# @impl-status: complete
```

Gherkin feature file:
```gherkin
# @brd: BRD-001:FR-030
# @req: REQ-003
# @spec: SPEC-002

Feature: Position Limit Enforcement
```

## Tagging Goals
- End-to-end traceability: Connect REQ → ADR → CTR → BDD → SPEC → Code in a verifiable chain.
- Machine-readability: Use consistent tag syntax so scripts can validate IDs/links and build indexes.
- Impact analysis: Reveal upstream sources and downstream dependents to assess change ripple effects.
- Quality gates: Enable automated checks (ID format, link existence, required references) before commit.
- Consistency and discoverability: Standardized, grep-friendly headers make related artifacts easy to find.
- Auditability and compliance: Provide clear linkage for decisions, verification, and implementation.

## Auto-Discovery Validation

Tags enable automated traceability validation. Code becomes the single source of truth, matrices are auto-generated.

**Validation Workflow:**
```bash
# Extract all tags from codebase
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate tags reference real documents
python scripts/validate_tags_against_docs.py --tags docs/generated/tags.json --strict

# Generate bidirectional matrices
python scripts/generate_traceability_matrices.py --tags docs/generated/tags.json --output docs/generated/matrices/

# CI/CD enforcement
pre-commit run validate-traceability-tags
```

**Benefits Over Manual Section 7:**
- ✅ Single source of truth: Code contains tags
- ✅ Automated validation: Scripts check correctness
- ✅ No drift: Tags embedded in code cannot become stale
- ✅ Bidirectional: Forward/reverse matrices auto-generated
- ✅ CI/CD enforceable: Pre-commit hooks validate tags
- ✅ Namespace clarity: Explicit document identification (BRD-001:FR-030)

**Tag Validation Rules:**
1. **Format Check:** All @brd/@prd/@req tags must use DOCUMENT-ID:REQUIREMENT-ID format
2. **Document Exists:** DOCUMENT-ID must reference existing file in docs/{TYPE}/
3. **Requirement Exists:** REQUIREMENT-ID must exist within the document
4. **No Orphans:** All tags must resolve to actual requirements
5. **Implementation Status:** @impl-status must be one of: pending|in-progress|complete|deprecated

## Cumulative Tagging Hierarchy

### Overview

Cumulative tagging ensures complete traceability chains from business requirements through validation. Each artifact type must include tags from ALL upstream artifacts in the hierarchy, creating explicit dependency chains for impact analysis and compliance auditing.

### Mandatory Hierarchy

```
Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → [IMPL] → [CTR] → SPEC → TASKS → IPLAN → Code → Tests → Validation
```

### Cumulative Inheritance Rules

**Principle**: Each layer inherits ALL tags from upstream layers and adds its own.

**Example**: A SPEC file includes tags from: BRD, PRD, EARS, BDD, ADR, SYS, REQ, and optionally IMPL/CTR if they exist in the chain.

**Format**: `@artifact-type: DOCUMENT-ID:REQUIREMENT-ID`

**Usage**:
- Embed tags in document metadata sections (markdown documents)
- Embed tags in code docstrings (implementation files)
- Embed tags in test files (BDD scenarios already use tags, unit tests use docstrings)
- Use tags for automated traceability matrix generation

### Cumulative Tagging Table

| Layer | Artifact Type | Required Tags | Tracking Method | Notes |
|-------|---------------|---------------|-----------------|-------|
| 0 | **Strategy** | None | External | Business owner documents, no formal artifact |
| 1 | **BRD** | None | Formal Template | Top level, no upstream dependencies |
| 2 | **PRD** | `@brd` | Formal Template | References parent BRD |
| 3 | **EARS** | `@brd`, `@prd` | Formal Template | Cumulative: BRD + PRD |
| 4 | **BDD** | `@brd`, `@prd`, `@ears` | Formal Template + Gherkin Tags | Cumulative: BRD through EARS |
| 5 | **ADR** | `@brd`, `@prd`, `@ears`, `@bdd` | Formal Template | Cumulative: BRD through BDD |
| 6 | **SYS** | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr` | Formal Template | Cumulative: BRD through ADR |
| 7 | **REQ** | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys` | Formal Template | Cumulative: BRD through SYS |
| 8 | **IMPL** | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req` | Formal Template | Cumulative: BRD through REQ |
| 9 | **CTR** | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@impl` | Formal Template | Cumulative: BRD through IMPL (optional layer) |
| 10 | **SPEC** | All upstream through `@req` + optional `@impl`, `@ctr` | Formal Template (YAML) | Full upstream chain |
| 11 | **TASKS** | All upstream through `@spec` | Formal Template | Include optional IMPL/CTR if present |
| 12 | **IPLAN** | All upstream through `@tasks` | Project Files | All formal artifact tags |
| 13 | **Code** | **ALL tags** including `@iplan` | Docstring Tags | Complete traceability chain |
| 14 | **Tests** | All upstream through `@code` | Docstring Tags + BDD | All upstream + code reference |
| 15 | **Validation** | **ALL tags from all documents** | Embedded Tags + CI/CD | Complete audit trail |

### Tag Format Specification

**Basic Format**:
```
@artifact-type: DOCUMENT-ID:REQUIREMENT-ID
```

**Components**:
- **Artifact Type**: Lowercase artifact name (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@impl`, `@ctr`, `@spec`, `@tasks`, `@iplan`)
- **Document ID**: Standard ID format (e.g., `BRD-001`, `REQ-003`, `SPEC-005`)
- **Requirement ID**: Specific requirement within document (e.g., `FR-030`, `NFR-006`, `PERF-001`)
- **Separator**: Colon (`:`) between document and requirement
- **Multiple Values**: Comma-separated

**Examples**:
```markdown
## Traceability Tags

@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec, REQ-004:validation-logic
@impl: IMPL-001:phase1
@ctr: CTR-001
@spec: SPEC-003
@tasks: TASKS-001:task-3
```

**Code Docstring Example**:
```python
"""
Position Limit Service

Implements real-time position limit validation and enforcement.

## Traceability Tags

@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec
@impl: IMPL-001:phase1
@ctr: CTR-001
@spec: SPEC-003
@tasks: TASKS-001:task-3
@iplan: IPLAN-001
"""
```

### Validation Rules

**Mandatory Checks**:
1. **Complete Chain**: Each artifact must include ALL upstream tags
2. **Format Compliance**: All tags follow `@type: ID:REQ-ID` format
3. **Document Exists**: Referenced DOCUMENT-ID must exist in repository
4. **Requirement Exists**: REQUIREMENT-ID must exist within referenced document
5. **No Orphans**: All tags resolve to actual artifacts
6. **Layer Validation**: Artifact at layer N must have tags from layers 1 through N-1

**Validation Commands**:
```bash
# Validate tag format and completeness
python scripts/validate_tags_against_docs.py --strict

# Check cumulative tag chains
python scripts/validate_tags_against_docs.py --check-cumulative

# Generate traceability matrix from tags
python scripts/generate_traceability_matrices.py --tags docs/generated/tags.json
```

### Benefits of Cumulative Tagging

**Complete Traceability**:
- Single code file shows entire upstream dependency chain
- Impact analysis from any artifact to all affected downstream artifacts
- Compliance auditing with complete BRD-to-Code trace

**Automated Validation**:
- Scripts validate complete tag chains
- CI/CD enforces tag presence and correctness
- Automated traceability matrix generation

**Change Management**:
- Identify all affected artifacts when upstream document changes
- Verify downstream artifacts updated after requirement changes
- Maintain audit trail for regulatory compliance

**Developer Clarity**:
- Code clearly shows business requirements it implements
- Test files explicitly reference requirements under test
- Specifications document complete upstream context

## Artifact Tracking Methods

The SDD workflow employs different tracking methods for different artifact types based on their nature and usage patterns. Understanding these methods is essential for maintaining complete traceability.

### Tracking Method Categories

**1. External (Business Owner)**
- Artifact exists outside the framework
- No formal template or tagging required
- Referenced by downstream artifacts

**2. Formal Templates (No Tags)**
- Top-level artifacts with no upstream dependencies
- Use formal templates from framework
- No tags required as they are root documents

**3. Formal Templates (With Cumulative Tags)**
- Middle-tier artifacts with formal templates
- Must include ALL upstream tags (cumulative inheritance)
- Tags embedded in document Traceability section

**4. Project Files (With All Tags)**
- Implementation execution context
- Include complete upstream tag chain
- Support automation and CI/CD integration

**5. Code (Docstring Tags)**
- Implementation files
- ALL upstream tags in docstrings
- Enables automated traceability extraction

**6. Tests (BDD + Docstring Tags)**
- Test specifications and implementations
- BDD uses Gherkin tags
- Unit/integration tests use docstring tags

**7. Embedded Tags + CI/CD**
- Validation artifacts
- Tags embedded in validation documents
- Automated enforcement through CI/CD pipelines

### Artifact Type Tracking Matrix

| Layer | Artifact Type | Tracking Method | Formal Template | Tags Required | Tag Count | Notes |
|-------|---------------|-----------------|-----------------|---------------|-----------|-------|
| 0 | Strategy | External | No | No | 0 | Business owner documents |
| 1 | BRD | Formal Template | Yes | No | 0 | Top level, no upstream |
| 2 | PRD | Formal Template + Tags | Yes | Yes | 1 | @brd |
| 3 | EARS | Formal Template + Tags | Yes | Yes | 2 | @brd, @prd |
| 4 | BDD | Formal Template + Tags | Yes (Gherkin) | Yes | 3 | @brd, @prd, @ears |
| 5 | ADR | Formal Template + Tags | Yes | Yes | 4 | @brd through @bdd |
| 6 | SYS | Formal Template + Tags | Yes | Yes | 5 | @brd through @adr |
| 7 | REQ | Formal Template + Tags | Yes | Yes | 6 | @brd through @sys |
| 8 | IMPL | Formal Template + Tags | Yes | Yes | 7 | @brd through @req |
| 9 | CTR | Formal Template + Tags | Yes (Dual: .md + .yaml) | Yes | 8 | @brd through @impl (optional) |
| 10 | SPEC | Formal Template + Tags | Yes (YAML) | Yes | 7-9 | @brd through @req + optional |
| 11 | TASKS | Formal Template + Tags | Yes | Yes | 8-10 | @brd through @spec |
| 12 | IPLAN | Project Files + Tags | No (Project-specific) | Yes | 9-11 | All formal artifact tags |
| 13 | Code | Docstring Tags | No (Implementation) | Yes | 10-12 | ALL upstream tags |
| 14 | Tests | BDD + Docstring Tags | Mixed | Yes | 11-13 | All upstream + code |
| 15 | Validation | Embedded Tags + CI/CD | Mixed | Yes | ALL | Complete audit trail |

### Example: Complete Tag Chain in Code

**Code Implementation with Full Traceability**:

```python
"""
Position Limit Validation Service

Implements real-time position limit enforcement with portfolio heat monitoring
and automated trade rejection for risk management compliance.

Business Context:
Satisfies regulatory requirements for position limit monitoring and prevents
excessive portfolio concentration risk through automated validation.

## Traceability Tags

@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003, EARS-001:STATE-002
@bdd: BDD-003:scenario-realtime-quote, BDD-003:scenario-reject-trade
@adr: ADR-033
@sys: SYS-008:PERF-001, SYS-008:RELIABILITY-002
@req: REQ-003:interface-spec, REQ-004:validation-logic
@impl: IMPL-001:phase1
@ctr: CTR-001
@spec: SPEC-003
@tasks: TASKS-001:task-3, TASKS-001:task-5
@iplan: IPLAN-001

@impl-status: complete
@test-coverage: 95%
@performance: p95=45ms
"""

class PositionLimitService:
    """
    Validates position limits against portfolio heat thresholds.

    Implements CTR-001 position_risk_validation interface.
    """

    def validate_position_limit(self, position: Position) -> ValidationResult:
        """
        Validate position against configured limits.

        Implements: REQ-003:interface-spec, EARS-001:EVENT-003
        Tests: BDD-003:scenario-realtime-quote
        Performance: p95 < 50ms (SYS-008:PERF-001)
        """
        # Implementation
        pass
```

**Test File with Complete Traceability**:

```python
"""
Position Limit Validation Service Tests

Tests all scenarios from BDD-003 and validates REQ-003 acceptance criteria.

## Traceability Tags

@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec
@spec: SPEC-003
@tasks: TASKS-001:task-3
@code: src/services/position_limit_service.py

@test-type: integration
@test-scope: position-limits
"""

def test_validate_position_limit_within_threshold():
    """
    Test: Position within limit is approved

    BDD Scenario: BDD-003:scenario-realtime-quote
    Requirement: REQ-003:interface-spec, EARS-001:EVENT-003
    """
    # Test implementation
    pass
```

### Benefits of Mixed Tracking Methods

**Flexibility**:
- Formal templates for structured artifacts
- Tags for automation and validation
- External references for business context
- Code docstrings for implementation traceability

**Automation**:
- Scripts extract tags from all sources
- Automated validation of tag completeness
- Generated traceability matrices
- CI/CD enforcement of tag presence

**Clarity**:
- Each artifact type uses appropriate method
- Consistent tagging format across all types
- Clear documentation of tracking approach
- Complete audit trail from strategy to validation

## Workflow (Spec → Code)

### 1. Capture Business Intent (PRD)
- **Input**: Business needs, market requirements, stakeholder priorities
- **Output**: PRD document with problem/goals/non-goals/KPIs
- **Guidelines**: Focus on business value; avoid technical implementation details; set measurable success criteria

### 2. Formalize Requirements (EARS)
- **Input**: PRD objectives translated to precise behavioral statements
- **Output**: EARS statements using WHEN-THE-SHALL-WITHIN format
- **Types**:
  - Event-driven: `WHEN [condition] THE [system] SHALL [action] WITHIN [timeframe]`
  - State-driven: `WHILE [condition] THE [system] SHALL [behavior] WITHIN [constraint]`
  - Unwanted Behavior: `IF [condition] THE [system] SHALL [prevention] WITHIN [timeframe]`
  - Ubiquitous: `THE [system] SHALL [requirement] WITHIN [constraint]`
- **Guidelines**: One concept per statement; include quantitative constraints; enable testability

### 3. Define Atomic Requirements (REQ)
- **Input**: EARS statements decomposed into individual verifiable behaviors
- **Output**: REQ files with descriptions, acceptance criteria, verification methods
- **Structure (V2 Template)**:
  - Description: Precise SHALL statement defining one behavior
  - Context: Business rationale and use case scenario
  - **Interface Specifications**: Protocol/ABC definitions with type annotations
  - **Data Schemas**: JSON Schema + Pydantic models + Database schemas
  - **Error Handling**: Exception catalog with recovery strategies
  - **Configuration Specifications**: YAML configurations with validation
  - Non-Functional Requirements: Performance, reliability, security targets
  - Implementation Guidance: Algorithms, patterns, architectural patterns
  - Acceptance Criteria: Measurable validation conditions with verification methods
  - Verification Methods: BDD scenarios, unit tests, integration tests, security tests
  - Traceability: Upstream sources (BRD/PRD/SYS/EARS) and downstream artifacts (ADR/SPEC/Code)
  - Related ADRs: Architecture decisions implementing the requirement
- **Organization**: Hierarchical by functional domains (`REQ/{domain}/{subdomain}/`)
- **Guidelines**:
  - Atomic principle (one requirement per file)
  - Include error and edge cases
  - **SPEC-Ready Criteria**: REQs should contain 90%+ of information needed for automated SPEC generation
  - Use concrete examples instead of placeholders
  - Target 400-500 lines per domain-focused REQ with complete technical specifications
  - Include Mermaid state machines for complex workflows

#### What Makes a REQ SPEC-Ready?

A SPEC-ready REQ contains ≥90% of the technical information required to generate a complete SPEC without additional research:

**Core Requirements**:
- ✅ **Interface Specifications**: Protocol/ABC definitions with complete type annotations, docstrings, and parameter descriptions
- ✅ **Data Schemas**: JSON Schema + Pydantic models with validators + SQLAlchemy database models
- ✅ **Error Handling**: Exception catalog with HTTP codes, error codes, recovery strategies, and state machines
- ✅ **Configuration Specifications**: YAML examples with realistic values, environment variables, validation schemas
- ✅ **Non-Functional Requirements**: Quantified performance targets (p50/p95/p99), reliability requirements, security constraints
- ✅ **No Placeholders**: All examples use concrete values, realistic data, domain-specific patterns

**REQ → SPEC Data Flow**:
```
REQ (Requirement Layer)                    SPEC (Implementation Layer)
├─ Interface Specifications          →    interfaces: (copy signatures)
│  └─ Protocol/ABC with type hints         └─ Add implementation notes
├─ Data Schemas                      →    schemas: (copy JSON Schema/Pydantic)
│  ├─ JSON Schema                          └─ Add validation rules
│  ├─ Pydantic models
│  └─ SQLAlchemy models              →    data_model: (copy DB schema)
├─ Error Handling                    →    errors: (copy exception catalog)
│  ├─ Exception catalog                    └─ Add retry policies
│  └─ State machines                  →    behavioral_specifications:
│                                          └─ Add circuit breaker config
├─ Configuration Specifications      →    configuration: (copy YAML)
│  └─ YAML + validation                    └─ Add deployment overrides
└─ NFRs                              →    performance: (copy targets)
   └─ Performance targets                  └─ Add monitoring config
```

**Why SPEC-Ready REQs Matter**:
- **Automated SPEC Generation**: AI agents can translate REQ → SPEC with minimal human intervention
- **Consistency**: Standardized structure ensures complete technical specifications
- **Traceability**: Clear lineage from requirements to implementation specifications
- **Reduced Iteration**: Fewer clarification cycles between requirements and implementation phases

### 4. Record Architectural Decisions (ADR)
- **Input**: Technical alternatives evaluated for requirement satisfaction
- **Output**: ADR with selected solution, context, consequences, alternatives
- **Template Structure**:
  - Context: Problem, background, constraints
  - Decision: Chosen approach and implementation
  - Consequences: Benefits, trade-offs, risks, dependencies
  - Verification: BDD scenarios validating architectural approach
  - Alternatives: Rejected options with specific rejection reasons
  - Relations: Dependencies, supersedes, subsequent decisions
- **Lifecycle**: Proposed (draft) → Accepted (implemented) → Superseded/Deprecated
- **Guidelines**: Document due diligence; avoid straw-man alternatives; include rollback plans

### 5. Specify Behavior (BDD)
- **Input**: REQ acceptance criteria expressed as executable scenarios
- **Output**: Gherkin feature files with Given-When-Then scenarios
- **Scenario Types**: Success paths, alternative paths, error conditions, edge cases
- **Tagging**: `@requirement:[REQ-...](...)` and `@adr:[ADR-...](...)` links
- **Guidelines**: Business language; declarative over imperative; tagged with traceability links

### 6. Author Technical Specifications (SPEC)
- **Input**: REQ acceptance criteria with interface/schema/error definitions, ADR constraints
- **Output**: YAML blueprints defining implementation specifications
- **Core Sections**:
  - Interface definitions with function/class signatures and data schemas (from REQ Section 3)
  - Behavioral specifications (states, error handling, circuit breakers) (from REQ Section 5)
  - Operational requirements (caching, rate limiting, observability) (from REQ Section 6)
  - Performance targets with quantitative metrics (from REQ Section 7)
  - Verification mapping to BDD scenarios and load tests
- **REQ V2 → SPEC Translation**:
  - Copy interface signatures from REQ Section 3 (Interface Specifications)
  - Copy data schemas from REQ Section 4 (JSON Schema, Pydantic, SQLAlchemy)
  - Copy error catalog from REQ Section 5 (exception types, HTTP codes, recovery strategies)
  - Copy configuration templates from REQ Section 6 (YAML structures with validation)
  - Reference NFRs from REQ Section 7 (performance targets, security requirements)
  - Add implementation-specific details (retry policies, circuit breaker thresholds, caching strategies)
- **Guidelines**:
  - Machine-readable; complete specifications; feasibility of automated code generation
  - SPEC should be 95%+ derivable from REQ V2 content
  - Add operational details not present in REQ (deployment config, monitoring queries, runbook procedures)

### 6.5. Define API Contracts (CTR) [IF INTERFACE REQUIREMENT]
- **When**: Create CTR when REQ specifies interface requirements for component-to-component communication
- **Skip If**: REQ is purely internal logic with no external interfaces
- **Input**: Interface-focused REQ, ADR architecture decisions
- **Output**: Dual-file contract (CTR-NNN_slug.md + CTR-NNN_slug.yaml)
- **Process**:
  1. Identify upstream REQ/ADR specifying interface needs
  2. Reserve next CTR-NNN from CTR-000_index.md
  3. Copy CTR-TEMPLATE.md + CTR-TEMPLATE.yaml
  4. Complete markdown file:
     - Contract Definition: Interface overview, provider/consumer parties, communication pattern
     - Interface Specification: Detailed request/response structure
     - Error Handling: Complete error taxonomy with retry policies
     - Non-Functional Requirements: Latency, idempotency, rate limiting
     - Versioning Strategy: Semantic versioning rules, deprecation policy
     - Section 7 Traceability: Upstream REQ/ADR links, downstream SPEC placeholders
  5. Complete YAML file:
     - contract_id (lowercase_snake_case matching slug)
     - endpoints with JSON Schema request/response definitions
     - error_codes with HTTP status and retry behavior
     - non_functional requirements (max_latency_ms, idempotent, circuit_breaker)
     - upstream_requirements, upstream_adrs
  6. Update CTR-000_index.md catalog
  7. Update upstream REQ to link to CTR
  8. Validate both files, verify slugs match
- **Benefits**:
  - Parallel Development: Provider and consumer teams work independently
  - Early Validation: Contract testing before full implementation
  - Drift Prevention: Schema validation ensures compliance
  - Clear Ownership: Explicit provider/consumer responsibilities
- **Guidelines**: Contract-first when multiple teams involved; versioning for breaking changes; include examples in markdown

### 7. Plan Implementation Scope (TASKS)
- **Input**: SPEC technical specifications, CTR contracts (if applicable), interface definitions
- **Output**: AI-structured implementation guidance with scope, plan, constraints, acceptance
- **Structure**:
  - Scope: Clearly bounded implementation responsibility
  - Plan: Numbered sequence of development activities
  - Constraints: Technical boundaries and limitations
  - Acceptance: Verification requirements for completion
- **Guidelines**: Task decomposition for parallel work; acceptanceCriteria for verification

### 8. Implement Code
- **Input**: SPEC specifications, CTR contracts (if applicable), TASKS implementation plans
- **Output**: Source code matching specifications and contracts exactly
- **Requirements**:
  - Exact match to SPEC interfaces
  - Contract compliance (if implementing CTR provider/consumer)
  - BDD scenario validation
  - Observability per SPEC requirements
  - Docstring traceability to all artifacts (including CTR if applicable)
- **Guidelines**: Test-driven implementation; contract testing; continuous compliance validation

### 9. Verify Implementation
- **Input**: Code, BDD tests, CTR contracts (if applicable), SPEC performance targets
- **Output**: Verification that implementation satisfies all requirements and contracts
- **Methods**:
  - BDD scenario execution with acceptance criteria
  - Contract testing (provider/consumer validation if CTR exists)
  - Performance benchmarking against SPEC targets (when measurable)
  - Integration testing with dependent components
  - Manual verification of error conditions and edge cases
- **Guidelines**: Automated verification preferred; contract tests validate interfaces; traceable test results

### 10. Validate Traceability
- **Input**: All artifacts in the development chain
- **Output**: Confirmed linkage and consistency across all documents
- **Checks**:
  - Cross-reference link resolution
  - ID format compliance
  - Tagging consistency (Gherkin tags, YAML comments, docstrings)
  - Requirement coverage completeness
  - Impact analysis accuracy
- **Guidelines**: Pre-commit validation using automated tools where available

## Quality Gates (Definition of Done)

**Pre-Commit Checklist:**
- [ ] IDs comply with ID_NAMING_STANDARDS.md
- [ ] All cross-references use markdown links
- [ ] **Traceability tags validated** ⚠️ **MANDATORY**
  - [ ] All code files must have @brd:/@req:/@spec: tags
  - [ ] Tag format validation passes: `python scripts/extract_tags.py --validate-only`
  - [ ] Tags reference existing documents: `python scripts/validate_tags_against_docs.py --strict`
  - [ ] Matrices auto-generated: `python scripts/generate_traceability_matrices.py --auto`
  - [ ] No orphaned tags
  - [ ] Implementation status defined (@impl-status)
- [ ] BDD scenarios tagged with @requirement and @adr links
- [ ] Validation scripts pass

**Document-Specific Requirements:**
- **REQ V2**:
  - [ ] Section 3: Interface Specifications present (Protocol/ABC with type annotations)
  - [ ] Section 4: Data Schemas complete (JSON Schema + Pydantic + SQLAlchemy)
  - [ ] Section 5: Error Handling Specifications defined (exception catalog + state machines)
  - [ ] Section 6: Configuration Specifications provided (YAML + validation + env vars)
  - [ ] No placeholders (all examples use concrete values)
  - [ ] SPEC-Ready Score ≥90% (run `validate_req_spec_readiness.py`)
  - [ ] Mermaid state machines for complex workflows
  - [ ] NFRs quantified (performance targets with p50/p95/p99)
- CTR (if applicable):
  - Both .md and .yaml files exist with matching slugs
  - YAML contract_id uses lowercase_snake_case matching slug
  - Upstream REQ/ADR links present in Section 7 Traceability
  - Schema validation passes (valid JSON Schema in YAML)
  - Contract version follows semantic versioning
- SPEC: Interface definitions and data schemas are complete and unambiguous.
- BDD: Scenarios tagged with valid `@requirement`, `@adr`, and `@contract` (if applicable) links.
- Non-Functional: Latency/timeouts, error taxonomy, logging/metrics defined in spec/contract.
- Observability: Key logs/metrics/traces named and fields enumerated.
- Code: Docstring lists PRD/EARS/REQ/ADR/CTR(if applicable)/BDD/SPEC links; symbol names match spec; contract compliance validated.

## AI Assistant Best Practices
- Provide Inputs: Tech Spec excerpt, concrete examples, constraints, target file paths.
- Task List: 3–6 linear steps; minimal scope; name exact files/symbols; include "do not touch" constraints.
- Acceptance: State precise outputs and commands to validate (e.g., link check, BDD tests).
- Diffs: Prefer minimal, reviewable changes; justify deviations against spec if unavoidable.

## Change Management
- Upstream Changes (PRD/EARS/REQ): Update ADR/BDD/Spec; re-run validations.
- Spec Changes: Update Code + BDD; maintain backward compatibility or bump versions.
- Always update Traceability sections and code docstrings to keep links current.

## References
- Core Rules: [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) (project-wide compliance checklist: IDs numeric, links resolve, no promotional language)
- Example ID Standards: [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md)
- Traceability Style: [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards)
- Example Flow Index: [TRACEABILITY.md](./TRACEABILITY.md)
- Master Index: [index.md](./index.md)

## Example Mapping ([RESOURCE_INSTANCE - e.g., database connection, workflow instance] Risk Limits)
- PRD: [PRD-003](./PRD/PRD-003_position_risk_limits.md)
- SYS: [SYS-003](./SYS/SYS-003_position_risk_limits.md)
- EARS: [EARS-003](./EARS/EARS-003_position_limit_enforcement.md)
- BDD: [risk_limits_requirements.feature](./BDD/risk_limits_requirements.feature)
- ADR: [ADR-033](./ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033)
- **REQ V2**: [REQ-003](./REQ/risk/lim/REQ-003_position_limit_enforcement.md#REQ-003) ← Contains complete interface/schema/error/config specifications
- CTR: [CTR-001](./CTR/CTR-001_position_risk_validation.md#CTR-001) + [CTR-001.yaml](./CTR/CTR-001_position_risk_validation.yaml) ← Contract for [RESOURCE_INSTANCE - e.g., database connection, workflow instance] validation interface
- SPEC: [position_limit_service.yaml](./SPEC/services/position_limit_service.yaml) ← 95% derived from REQ-003 V2 content
- TASKS: [position_limit_service_tasks.md](./TASKS/position_limit_service_tasks.md)
- Code: `option_strategy/risk/position_limit_service.py`

### Example: REQ V2 → SPEC Workflow

**Scenario**: API Integration for Market Data

**Step 1: Create REQ V2** (REQ-001_api_integration_example.md)
- Section 3: Define `MarketDataAPIClient` Protocol with 5 async methods (connect, get_quote, get_chain, disconnect, health_check)
- Section 4: Provide JSON Schema + Pydantic models (QuoteRequest, QuoteResponse, OptionChainRequest) with validators
- Section 5: Document 8 exception types (ConnectionError, AuthenticationError, RateLimitError, etc.) with HTTP codes
- Section 6: Provide complete YAML configuration (endpoints, authentication, retry_policy, rate_limits, circuit_breaker)
- Section 7: Specify NFRs (p95 latency <100ms, 99.9% uptime, rate limit 60 req/min)

**Step 2: Generate SPEC** (SPEC-001_market_data_client.yaml)
```yaml
# @requirement:[REQ-001](../REQ/api/REQ-001_api_integration_example.md#REQ-001)

id: market_data_client
interfaces:
  - name: MarketDataAPIClient
    # Copy from REQ-001 Section 3
    methods:
      - name: connect
        parameters:
          - credentials: APICredentials
          - timeout: float = 5.0
        returns: ConnectionResult
        raises: [ConnectionError, AuthenticationError]

schemas:
  # Copy from REQ-001 Section 4
  QuoteRequest: {$ref: "../REQ/api/REQ-001_api_integration_example.md#json-schema"}
  QuoteResponse: {$ref: "../REQ/api/REQ-001_api_integration_example.md#pydantic-model"}

errors:
  # Copy from REQ-001 Section 5
  - error_code: "API_001"
    exception: ConnectionError
    http_status: 503
    retry_strategy: exponential_backoff

configuration:
  # Copy from REQ-001 Section 6
  endpoints:
    base_url: "${MARKET_DATA_API_URL}"
  retry_policy:
    max_attempts: 3
    backoff_multiplier: 2
  # Add SPEC-specific operational details
  monitoring:
    - metric: api_request_duration_ms
      alert_threshold: 150
    - metric: api_error_rate
      alert_threshold: 0.05

performance:
  # Reference REQ-001 Section 7 NFRs
  max_latency_p95_ms: 100
  target_availability: 0.999
```

**Result**: SPEC is 95% complete from REQ V2 content, requiring only operational monitoring details

## Validation Commands
- **REQ V2 Validation**: `python scripts/validate_req_spec_readiness.py --req-file REQ/api/REQ-001.md`
  - Checks for interface definitions with type signatures
  - Validates schema completeness (JSON Schema/Pydantic)
  - Verifies error catalog with recovery strategies
  - Confirms configuration examples present
  - Generates SPEC-Ready Score (0-100%)
- Validate requirement IDs: `python scripts/validate_requirement_ids.py`
  - Enhanced to validate REQ V2 mandatory sections
- Check links (repo-level tools if available): `python scripts/check_broken_references.py`
- Generate matrices (if available): `python scripts/complete_traceability_matrix.py`

## Traceability Matrix Management (MANDATORY)

### Policy

**CRITICAL**: Traceability matrices are NOT optional. They are mandatory quality infrastructure for SDD workflow compliance.

**Enforcement Rule**: Every time you create or update ANY artifact document (BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS), you MUST create or update the corresponding traceability matrix in the SAME commit.

**Update Frequency**: Within same commit as artifact creation/update

**Quality Gate**: Pull requests rejected if matrix not updated

### Purpose
Traceability matrices provide comprehensive visibility into:
- **Coverage Metrics**: Document completion status across all artifact types
- **Upstream-Downstream Relationships**: Bidirectional linkage for impact analysis
- **Change Impact Analysis**: Identify all affected artifacts before making changes
- **Compliance and Audit Trails**: Complete documentation chain for regulatory requirements
- **Team Coordination**: Clear visibility of dependencies across teams and phases
- **Quality Assurance**: Identify orphaned documents and missing artifacts

### Matrix Types

Each document type has its own dedicated traceability matrix template:

| Document Type | Template Location | Matrix File | MANDATORY |
|---------------|------------------|-------------|-----------|
| **BRD** | `BRD/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `BRD/BRD-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **PRD** | `PRD/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `PRD/PRD-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **EARS** | `EARS/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `EARS/EARS-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **BDD** | `BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `BDD/BDD-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **ADR** | `ADR/ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `ADR/ADR-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **SYS** | `SYS/SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `SYS/SYS-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **REQ** | `REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `REQ/REQ-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **IMPL** | `IMPL/IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `IMPL/IMPL-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **CTR** | `CTR/CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `CTR/CTR-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **SPEC** | `SPEC/SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `SPEC/SPEC-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **TASKS** | `TASKS/TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | `TASKS/TASKS-000_TRACEABILITY_MATRIX.md` | ✅ YES |
| **Complete** | `TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` | `TRACEABILITY_MATRIX_COMPLETE.md` | ✅ YES |

### Mandatory Matrix Update Workflow

**Every time you create or update an artifact document, follow these steps:**

1. **Check for Matrix File**: Look for `[TYPE]-000_TRACEABILITY_MATRIX.md` in artifact folder
2. **Create if Missing**: Copy template from `ai_dev_flow/[TYPE]/[TYPE]-000_TRACEABILITY_MATRIX-TEMPLATE.md`
3. **Update Matrix Sections**:
   - Section 2: Add document to inventory with ID, title, status, date
   - Section 3: Document upstream sources (which documents drove this artifact)
   - Section 4: Document downstream artifacts (which documents/code derive from this - even if "To Be Created")
   - Section 8: Update implementation status and completion percentage
4. **Validate Matrix**: Run `python scripts/validate_traceability_matrix.py --type [TYPE]`
5. **Commit Together**: Commit artifact + matrix + index in same commit

### Matrix Sections to Update

When updating a traceability matrix, you MUST update these sections:

- **Section 2 (Complete Inventory)**: Add new document entry with:
  - Document ID, title, status, date
  - Upstream sources (BRD, PRD, EARS, etc.)
  - Downstream artifacts (SPEC, Code, Tests, etc.)

- **Section 3 (Upstream Traceability)**: Document which artifacts drove creation
  - BRD → PRD
  - PRD → EARS
  - EARS → BDD, ADR
  - REQ → IMPL, CTR, SPEC

- **Section 4 (Downstream Traceability)**: Document which artifacts derive from this
  - BRD → PRD, EARS
  - PRD → EARS, BDD
  - SPEC → Code, Tests
  - Even if artifacts don't exist yet, document as "To Be Created"

- **Section 8 (Implementation Status)**: Update completion percentage and validation status

### Validation Requirements

Before committing, verify:
- [ ] Matrix file exists for artifact type
- [ ] New document appears in matrix inventory (Section 2)
- [ ] Upstream sources documented (Section 3)
- [ ] Downstream artifacts documented (Section 4)
- [ ] All references resolve correctly
- [ ] No orphaned artifacts (documents missing from matrix)
- [ ] Validation script passes: `python scripts/validate_traceability_matrix.py --type [TYPE] --strict`

### Why This Is Critical

**Impact Analysis**: When BRD-001 changes, matrix shows affected PRDs, EARS, BDD, REQ, SPEC, Code

**Regulatory Compliance**: SEC, FINRA, FDA, ISO audits require complete traceability

**Quality Assurance**: Automated validation prevents orphaned requirements and missing implementations

**Change Management**: Know exactly what breaks when upstream requirements change

**Automated Validation**: Enable pre-commit hooks and CI/CD quality gates

### Failure Modes If Matrix Missing

**Consequences**:
- ❌ Cannot determine impact of requirement changes
- ❌ Orphaned requirements (no implementation)
- ❌ Failed regulatory audits (incomplete audit trail)
- ❌ Manual validation required (expensive, error-prone)
- ❌ Pull requests rejected by automated checks
- ❌ Project delays due to quality gate failures
5. **Update Regularly**: Incremental updates as new documents are created

### Automated Matrix Generation

Use validation scripts for automated matrix management:

```bash
# Generate new matrix
python scripts/generate_traceability_matrix.py --type ADR --output docs/ADR/

# Validate existing matrix
python scripts/validate_traceability_matrix.py --matrix docs/ADR/TRACEABILITY_MATRIX_ADR.md

# Update matrix incrementally
python scripts/update_traceability_matrix.py --matrix docs/ADR/TRACEABILITY_MATRIX_ADR.md
```

## Documentation Standards (No Marketing, Code Separation)
- Objective tone only: exclude promotional language, subjective claims, and business benefits.
- Do not include Python code blocks in documentation; prefer Mermaid flowcharts or structured pseudocode.
- Use flowcharts for logic with decision points and error paths; keep diagrams concise.
- Reference code with explicit paths and optional symbol hints: `[See Code Example: option_strategy/risk/position_limit_service.py - validate_position_limit()]`.

## Non-Functional Requirements Templates
- **Performance**: Add to SPEC performance section, e.g., latency_p95_ms: 50, throughput: 1000 rps; to ADR impact analysis, e.g., "p95 latency < 50 ms, trade-off: reduced batch size".
- **Reliability**: SYS/REQ: "System availability > 99.9%"; ADR: [SAFETY_MECHANISM - e.g., rate limiter, error threshold] on >5 failures/1min; SPEC: retry_policy with exponential backoff.
- **Security**: ADR: "Input validation per OWASP; no secrets in logs"; SPEC: errors for auth failures, observability: log correlation_id only (avoid PII).
- **Observability**: SPEC: logs with fields [correlation_id, error_code, timestamp]; ADR: "Alert on >10% reject rate, monitor via Cloud Monitoring".
- **Compliance Checklist**: 
  - [ ] NFRs quantified in SYS/REQ (e.g., uptime, latency bounds).
  - [ ] Security in ADR/SPEC (validation, secrets policy).
  - [ ] Observability in SPEC (log fields, metrics).
  - [ ] Trace to PROJECT_CORE_RULES: numeric IDs, absolute link validation.

## Token Efficiency and File Segmentation

### Token Limits by AI Coding Tool

**Claude Code (Recommended - Primary Tool):**
- Standard: Up to 50,000 tokens (200KB) per file
- Maximum: 100,000 tokens (400KB) for comprehensive guides
- Optimal: 20-40KB files use 20-30% of context window
- Can handle 30-50 files simultaneously
- Benefits: Single-file comprehensive documentation, no artificial splitting required

**Gemini CLI (Alternative - Secondary Tool):**
- `@` Reference: Limited to 10,000 tokens (40KB) per file
- File Read Tool: No practical limit - use for files >10,000 tokens
- Method: Don't use `@large_file.md`, instead: "Read large_file.md and..."
- See: [Gemini_CLI_Large_File_Workarounds.md](../Gemini_CLI_Large_File_Workarounds.md)

**GitHub Copilot:**
- Recommended: Keep files <30KB (7,500 tokens)
- Strategy: Create companion summary files for large documents
- Working set: Maximum 10 files in Copilot Edits mode

### File Splitting Guidelines

- Split only when file exceeds 100,000 tokens (Claude Code practical limit)
- Split at logical boundaries (separate concerns, modules, functional areas)
- Do NOT split solely for tool compatibility - use appropriate tool features instead
- Each split file must be independently understandable (minimal context header and links back to index)
- Maintain an index page listing split files and their dependencies
- Example: For complex SPEC exceeding 100K tokens, create SPEC-003_part1.yaml (interfaces/state), SPEC-003_part2.yaml (performance/verification); reference as [SPEC-003_part1.yaml](./SPEC/services/SPEC-003_part1.yaml), with [index.md](./index.md) enumerating splits and dependencies
- Estimate tokens using tools like `wc -w` or AI token counters for maintenance
- External References: Paths to project files are placeholders; verify existence or update to local copies for standalone use

## Developer Checklist (Copyable)
- PRD/EARS/BDD/ADR/SYS/REQ updated; H1 contains IDs and anchors.
- **REQ V2 Completeness**:
  - [ ] Section 3: Interface Specifications (Protocol/ABC with type annotations)
  - [ ] Section 4: Data Schemas (JSON Schema + Pydantic + SQLAlchemy)
  - [ ] Section 5: Error Handling (exception catalog + state machines)
  - [ ] Section 6: Configuration (YAML + validation + env vars)
  - [ ] No placeholders (concrete examples only)
  - [ ] SPEC-Ready Score ≥90% (`validate_req_spec_readiness.py`)
- ADR updated with Impact Analysis and Implementation Assessment sections.
- Tech Spec updated: `id` equals filename; includes upstream/downstream links, interfaces, data model, states, errors, performance, observability.
- BDD scenarios tagged with markdown-link format `@requirement:[REQ-...](...)` and `@adr:[ADR-...](...)`.
- AI tasks file includes scope, plan, constraints, acceptance criteria, and traceability links.
- Security implications documented (input validation, secrets policy references, correlation id handling).
- Run validators:
  - `python scripts/validate_req_spec_readiness.py --req-file REQ/{domain}/REQ-NNN.md`
  - `python scripts/validate_requirement_ids.py`
  - Manual link checks

## Appendix: Claude Instructions (Merged)

### General Instructions for Eliminating Marketing Language in Technical Documentation

This is an AI-Driven Specification-Driven Development approach.
This project implements **AI-Driven SDD (Specification-Driven Development)**, where AI assistants autonomously transform specifications into production code. 

**Primary Constraint:**
```
Generate technical documentation using objective, factual language only.
Exclude promotional content, subjective claims, and business benefits.
Focus exclusively on functional specifications and implementation details.
Use minimal tokens while maintaining technical accuracy.
Evaluate all suggestions with realistic assessment of implementation complexity and impact.
Maintain file size under 50,000 tokens (Claude Code) or 100,000 tokens maximum.
  - For Gemini CLI: Use file read tool (not @) for files >10,000 tokens
  - Create sequential files only when exceeding Claude Code limits or logical boundaries
Python code in documentation: Optional based on size (<50 lines inline, >50 lines separate .py files)
Use flowcharts for complex logic visualization.
```

**Explicit Prohibitions:**
- No time estimates or marketing performance claims
- No product benefits or advantages
- No comparative statements
- No subjective qualifiers (amazing, powerful, efficient, easy)
- No user experience predictions
- No business value propositions
- No redundant explanations or verbose descriptions
- No idealistic or oversimplified implementation scenarios
- No Python code blocks within documentation files

NFR clarification (allowed)
- It is acceptable to specify non-functional requirement targets (e.g., latency, availability, resource limits) as engineering constraints.
- State targets quantitatively and contextually (e.g., "p95 latency < 50 ms during trading hours").
- Avoid promotional phrasing; present NFRs as measurable constraints, not benefits.

### Code Separation Requirements

**Documentation Content Standards:**
- Replace Python code blocks with flowchart representations
- Use Mermaid diagram syntax for flowcharts and process flows
- Create algorithm descriptions using structured pseudocode notation
- Reference external code files using standardized linking format
- Maintain logical flow documentation without implementation details

**Code File Management:**
- Create separate `.py` files for all code examples
- Name code files: `[component]_example_[sequence].py`
- Include inline documentation within code files using docstrings
- Provide function-level explanations as comments
- Create code manifest file listing all example files with descriptions

**Reference System:**
- Use format: `[See Code Example: filename.py - function_name()]`
- Include brief functional description in reference
- Specify input/output parameters in documentation
- Map flowchart steps to corresponding code file sections
- Maintain bidirectional reference between docs and code

**Flowchart Requirements:**
- Use Mermaid syntax for all process diagrams
- Include decision points and error handling paths
- Specify data transformation steps clearly
- Document conditional logic branches
- Include validation and error handling flows

### File Management Requirements

**Document Structure Philosophy:**
- **Default: Single Comprehensive File** - Keep documents as single files with clear section headings and table of contents
- **Split Only When Necessary** - Multi-file structure justified ONLY when:
  - File exceeds 1,000 lines (approximately 50K) AND
  - Has multiple distinct audience needs (e.g., prerequisites doc for architects, phase gates for PMs, main spec for developers) OR
  - Complex dependency chains require separate documentation (e.g., critical prerequisite blocking multiple downstream components)
- **Navigation Strategy**: Use markdown table of contents and section anchors within single files rather than splitting prematurely
- **Maintenance Cost**: Multiple files increase cognitive load, synchronization risk, and cross-reference complexity

**Token Limitation Standards (Tool-Optimized):**
- **Claude Code**: Maximum 50,000 tokens (200KB) standard, 100,000 tokens (400KB) absolute maximum
- **Gemini CLI**: Use file read tool (not `@`) for files >10,000 tokens - no splitting needed
- **GitHub Copilot**: Keep <30KB or create companion summary files
- Create numbered sequential files only when exceeding 100,000 tokens (doc_001.md, doc_002.md, etc.)
- Include cross-reference index in first file when splitting
- Maintain logical content boundaries between files (functional modules, not arbitrary splits)
- Ensure each file remains functionally complete for AI assistant processing
- See [TOOL_OPTIMIZATION_GUIDE.md](TOOL_OPTIMIZATION_GUIDE.md) for detailed tool selection guidance

**File Segmentation Strategy (When Multi-File is Justified):**
- Segment by functional modules or API endpoints
- Maintain related functions within same file when possible
- Create manifest file listing all related documentation files
- Include file dependency mapping for multi-file documentation sets
- Use consistent naming convention: [component]_[sequence]_[type].md

**Example: BRD-009 Multi-Document Structure (Justified Case):**
- BRD-009-01_prerequisites.md (20K) - Audience: Architects, PMs - Focus: Critical path dependencies
- BRD-009-02_broker_integration_pilot.md (51K) - Audience: Developers - Focus: Full technical requirements
- BRD-009-03_phase_gates_quick_reference.md (12K) - Audience: PMs, QA - Focus: Go/no-go checklists
- **Justification**: BRD-009 is Phase 1 critical prerequisite blocking 6 downstream BRDs, requires separate phase gate documentation, serves 3 distinct audiences with different information needs

**AI Assistant Compatibility:**
- Structure each file for independent processing by AI systems
- Include minimal context headers in each file for standalone comprehension
- Maintain consistent formatting across all sequential files
- Provide clear file relationship indicators
- Ensure token counting includes all formatting and structural elements

### Realistic Evaluation Requirements

**Implementation Assessment:**
- Document actual complexity level (low/medium/high/critical)
- Identify prerequisite dependencies and constraints
- Specify resource requirements (CPU, memory, network, storage)
- Document potential failure modes and error conditions
- Include rollback procedures for suggested changes
- Assess compatibility with existing system architecture

**Impact Analysis Standards:**
- Quantify measurable effects where possible (latency, throughput, resource usage)
- Document trade-offs and limitations explicitly
- Identify affected system components and downstream dependencies
- Specify testing requirements before implementation
- Document maintenance overhead and ongoing operational costs

**Practical Considerations:**
- Include deployment complexity assessment
- Document required skill level for implementation
- Specify monitoring and observability requirements
- Identify potential security implications
- Document scaling limitations and boundaries

### Token Efficiency Requirements

**Content Optimization:**
- Use concise technical terminology instead of explanatory phrases
- Employ abbreviated syntax documentation format
- Remove redundant sentences and filler content
- Consolidate related information into structured lists
- Use flowcharts instead of code descriptions where applicable

**Format Constraints:**
- Maximum one sentence per function description
- Use tabular format for parameter specifications
- Employ bullet points for configuration options
- Implement reference-style linking for repeated concepts
- Use abbreviated notation systems (HTTP status codes, RFC references)

### Language Requirements

**Use Technical Precision:**
- Replace "improves performance" with "reduces execution time by X milliseconds"
- Replace "easy to use" with "requires N configuration parameters"
- Replace "powerful features" with "implements X, Y, Z functionality"
- Replace "saves time" with "automates process X"

**Realistic Assessment Language:**
- Replace "will solve" with "may address under conditions X, Y, Z"
- Replace "optimizes" with "modifies behavior with trade-off A for benefit B"
- Replace "enhances" with "changes functionality from X to Y"
- Replace "streamlines" with "reduces steps from N to M with complexity increase in area Z"

### Content Filtering Rules

**Eliminate These Patterns:**
- Benefit statements ("This will help you...")
- Efficiency claims ("Faster than...")
- Ease-of-use assertions ("Simply..." "Just...")
- Future-oriented promises ("You'll be able to...")
- Superlative adjectives ("best," "optimal," "superior")
- Verbose introductory paragraphs
- Repetitive explanatory text
- Marketing-oriented section headers
- Oversimplified implementation descriptions
- Unrealistic success assumptions
- Inline Python code blocks

**Enforce These Standards:**
- Imperative verb forms for procedures
- Passive voice for system behaviors
- Conditional statements for error handling
- Precise data type specifications
- Explicit scope limitations
- Minimal character count per information unit
- Realistic complexity assessments
- Measurable impact criteria
- Practical implementation constraints
- Flowchart-based logic representation

### Implementation Template

```
INSTRUCTION: Generate API documentation for [function]
CONSTRAINTS: 
- Use RFC specification format
- Include only verifiable technical properties
- Omit subjective assessments
- Provide measurable parameters only
- Document error codes and conditions
- Specify exact input/output formats
- Minimize token usage while preserving technical accuracy
- Use structured formats over prose descriptions
- Employ reference notation for standard protocols
- Limit explanatory text to essential technical details only
- Include realistic complexity assessment (1-5 scale)
- Document implementation prerequisites and dependencies
- Specify resource requirements and constraints
- Include failure scenarios and mitigation strategies
- Provide quantifiable impact metrics where measurable
- Maintain file size under 50,000 tokens (Claude Code) or 100,000 tokens maximum
- For Gemini CLI: Use file read tool (not `@`) for files >10,000 tokens
- Create sequential files only when exceeding 100,000 tokens or logical boundaries
- Structure for AI assistant compatibility across tools (Claude Code, Gemini CLI, GitHub Copilot)
- Code blocks: Optional (<50 lines inline, >50 lines in separate .py files)
- Use Mermaid flowcharts for complex logic visualization
- Reference external code files using standardized format: `[See Code Example: filename.py - function_name()]`
- Create separate Python files for all code examples
```

**Code Reference Format:**
```
[Code Reference: authentication_example_001.py]
Function: validate_token()
Purpose: JWT token validation with [DEADLINE - e.g., session timeout, cache expiry] check
Input: token_string, secret_key
Output: validation_result, user_payload
Flowchart: See Section 3.2.1
```

**File Structure Requirements:**
- Documentation files: [component]_[sequence_number]_[content_type].md
- Code files: [component]_example_[sequence].py
- Flowchart integration: Use Mermaid syntax within documentation
- Token counting: Include all markdown formatting in token calculation
- Cross-reference format: "See file [filename] section [section_id]"
- Manifest structure: List all files with content summary and token count
- Index format: Functional mapping to specific files and sections

**Evaluation Framework:**
- Implementation complexity: Scale 1-5 with specific criteria
- Resource impact: Quantified CPU/memory/network/storage requirements
- Risk assessment: High/medium/low with specific failure modes
- Dependencies: Explicit list of required components and versions
- Testing scope: Required validation procedures before deployment
- Maintenance burden: Ongoing operational requirements

**Token Budget Guidelines:**
- Function descriptions: Maximum 10 tokens
- Parameter definitions: Maximum 5 tokens per parameter
- Error documentation: Use standardized error code references
- Flowchart elements: Mermaid syntax only, no explanatory prose
- Complexity assessment: Maximum 15 tokens
- Impact analysis: Maximum 20 tokens per major system component
- File overhead (headers, formatting): Maximum 200 tokens per file
- Cross-reference elements: Maximum 5 tokens per reference
- Code references: Maximum 25 tokens per reference block


**Traceability Validation:**
- Every requirement traces to product strategy section
- Every ADR satisfies at least one requirement
- Every BDD scenario tagged with requirement ID
- Every specification references requirements and ADRs
- Traceability matrix shows complete chain for all components
- Zero orphaned requirements, ADRs, or specifications
- All cross-references validated and functional

** Documentation Standards:**
- All files comply with 10K token limit
- No Python code blocks in markdown (use Mermaid flowcharts)
- Objective language throughout (no promotional content)
- Complexity ratings on all implementation guides
- Resource requirements documented for all components

Apply these constraints consistently across all Claude Code documentation generation tasks.
