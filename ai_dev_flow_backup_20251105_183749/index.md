# AI Dev Flow Template Index

This directory provides comprehensive templates for the AI-Driven Specification-Driven Development (SDD) workflow. All artifacts follow numeric ID standards and use relative markdown links for traceability.

## Document Structure

The AI Dev Flow organizes documentation through a hierarchical, traceable structure:

### Business Layer

- **BRD** (`brds/`): Business Requirements Documents defining business objectives and constraints
  - Templates: [BRD-template.md](./brds/BRD-template.md), [BRD-template-2.md](./brds/BRD-template-2.md), [BRD-trading-template.md](./brds/BRD-trading-template.md)
- **PRD** (`prd/`): Product Requirements Documents translating business needs to product features
  - Index: [PRD-000_index.md](./prd/PRD-000_index.md)
  - Template: [PRD-TEMPLATE.md](./prd/PRD-TEMPLATE.md)
- **EARS** (`ears/`): Event Analysis Requirements Specification for event-driven requirements
  - Index: [EARS-000_index.md](./ears/EARS-000_index.md)
  - Template: [EARS-TEMPLATE.md](./ears/EARS-TEMPLATE.md)

### Requirements Layer

- **REQ** (`reqs/`): Formal requirements with functional/non-functional specifications
  - Index: [REQ-000_index.md](./reqs/REQ-000_index.md)
  - Template: [REQ-TEMPLATE.md](./reqs/REQ-TEMPLATE.md)
  - Organization: `api/`, `risk/`, `ml/`, `data/` subdirectories
  - Examples:
    - [REQ-001](./reqs/api/av/REQ-001_alpha_vantage_integration.md) (Alpha Vantage Integration)
    - [REQ-002](./reqs/api/ib/REQ-002_ib_gateway_integration.md) (IB Gateway Integration)
    - [REQ-003](./reqs/risk/lim/REQ-003_position_limit_enforcement.md) (Position Risk Limits)

### Architecture Layer

- **ADR** (`adrs/`): Architecture Decision Records documenting key architectural choices
  - Index: [ADR-000_index-TEMPLATE.md](./adrs/ADR-000_index-TEMPLATE.md)
  - Template: [ADR-TEMPLATE.md](./adrs/ADR-TEMPLATE.md)
- **SYS** (`sys/`): System Requirements Specifications consolidating requirements into system designs
  - Index: [SYS-000_index.md](./sys/SYS-000_index.md)
  - Template: [SYS-TEMPLATE.md](./sys/SYS-TEMPLATE.md)

### Project Management Layer

- **IMPL** (`impl_plans/`): Implementation Plans organizing work into phases, teams, and deliverables
  - Index: [IMPL-000_index.md](./impl_plans/IMPL-000_index.md)
  - Template: [IMPL-TEMPLATE.md](./impl_plans/IMPL-TEMPLATE.md)
  - Purpose: Project management (WHO does WHAT, WHEN) - NOT technical specifications
  - Identifies deliverables: which CTR, SPEC, TASKS to create
  - Example: [IMPL-001](./impl_plans/examples/IMPL-001_risk_management_system.md) (Risk Management System)

### Design Layer

- **CTR** (`contracts/`): API Contracts defining component-to-component interfaces
  - Index: [CTR-000_index.md](./contracts/CTR-000_index.md)
  - Templates: [CTR-TEMPLATE.md](./contracts/CTR-TEMPLATE.md), [CTR-TEMPLATE.yaml](./contracts/CTR-TEMPLATE.yaml)
  - Dual-file format: `.md` (human-readable context) + `.yaml` (machine-readable schema)
  - Created when REQ specifies interface requirements
  - Enables parallel development and contract testing
  - Optional organization: subdirectories by service type (agents/, mcp/, infra/)
- **SPEC** (`specs/`): Technical specifications ready for code generation (HOW to build)
  - Index: [SPEC-000_index.md](./specs/SPEC-000_index.md)
  - Template: [SPEC-TEMPLATE.yaml](./specs/SPEC-TEMPLATE.yaml)
  - YAML format with classes, methods, algorithms
  - References CTR contracts when implementing interfaces

### Testing Layer

- **BDD** (`bbds/`): Behavior-Driven Development feature files defining acceptance criteria
  - Index: [BDD-000_index.feature](./bbds/BDD-000_index.feature)
  - Template: [BDD-TEMPLATE.feature](./bbds/BDD-TEMPLATE.feature)

### Code Generation Layer

- **TASKS** (`ai_tasks/`): Code generation plans with exact TODOs to implement SPEC in source code
  - Index: [TASKS-000_index.md](./ai_tasks/TASKS-000_index.md)
  - Template: [TASKS-TEMPLATE.md](./ai_tasks/TASKS-TEMPLATE.md)
  - Purpose: Step-by-step guide to generate code from YAML SPEC
  - Each TASKS document corresponds to one SPEC

## Traceability Flow

**⚠️ AUTHORITATIVE WORKFLOW**: This is the single source of truth for the AI Dev Flow traceability chain. All template diagrams reference this section.

```mermaid
flowchart TD
    %% Business Layer
    BRD[BRD<br/>Business Requirements<br/>High-level business needs]
    PRD[PRD<br/>Product Requirements<br/>User needs and features]
    EARS[EARS<br/>Event Analysis Requirements<br/>Event-driven specifications]

    %% Testing Layer
    BDD[BDD<br/>Behavior-Driven Development<br/>Test scenarios and acceptance criteria]

    %% Architecture Layer
    ADR[ADR<br/>Architecture Decision Records<br/>Technical decisions and rationale]
    SYS[SYS<br/>System Requirements<br/>Technical system specifications]

    %% Requirements Layer
    REQ[REQ<br/>Atomic Requirements<br/>Granular, testable requirements]

    %% Project Management Layer
    IMPL[IMPL<br/>Implementation Plans<br/>WHO/WHEN - Phases, teams, deliverables]

    %% Interface Layer
    CTR[CTR<br/>API Contracts<br/>Interface definitions between components<br/>Dual format: .md + .yaml]

    %% Implementation Layer
    SPEC[SPEC<br/>Technical Specifications<br/>HOW - Implementation blueprints<br/>YAML format with full details]

    %% Code Generation Layer
    TASKS[TASKS<br/>Code Generation Plans<br/>AI-structured implementation steps]

    %% Execution Layer
    Code[Code<br/>Python Implementation<br/>Generated from SPEC + TASKS]
    Tests[Tests<br/>Test Suites<br/>Unit, Integration, E2E tests]

    %% Validation Layer
    Validation[Validation<br/>BDD Test Execution<br/>Verify acceptance criteria]
    Review[Human Review<br/>Architecture Review<br/>Code quality check]
    Prod[Production-Ready Code<br/>Deployed to environment]

    %% Primary Flow
    BRD --> PRD
    PRD --> EARS
    EARS --> BDD
    BDD --> ADR
    ADR --> SYS
    SYS --> REQ
    REQ --> IMPL

    %% Interface Branch Decision
    IMPL --> CTR
    IMPL --> SPEC
    CTR --> SPEC

    %% Implementation Flow
    SPEC --> TASKS
    TASKS --> Code
    Code --> Tests
    Tests --> Validation
    Validation --> Review
    Review --> Prod

    %% Styling
    classDef businessLayer fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef testingLayer fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef architectureLayer fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px
    classDef requirementsLayer fill:#ffccbc,stroke:#e64a19,stroke-width:2px
    classDef projectLayer fill:#b3e5fc,stroke:#0277bd,stroke-width:2px
    classDef interfaceLayer fill:#f8bbd0,stroke:#c2185b,stroke-width:2px
    classDef implementationLayer fill:#dcedc8,stroke:#689f38,stroke-width:2px
    classDef codegenLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef executionLayer fill:#d1c4e9,stroke:#512da8,stroke-width:2px

    class BRD,PRD,EARS businessLayer
    class BDD testingLayer
    class ADR,SYS architectureLayer
    class REQ requirementsLayer
    class IMPL projectLayer
    class CTR interfaceLayer
    class SPEC implementationLayer
    class TASKS codegenLayer
    class Code,Tests,Validation,Review,Prod executionLayer
```

### Workflow Explanation

**Business Layer** → **Testing Layer** → **Architecture Layer** → **Requirements Layer** → **Project Management Layer** → **Interface Layer** → **Implementation Layer** → **Code Generation Layer** → **Execution Layer**

**Key Decision Point**: After IMPL, if the requirement involves an interface (API, event schema, data model), create CTR before SPEC. Otherwise, go directly to SPEC.

Each document maintains bidirectional traceability:

- **Upstream**: Links to source documents (requirements, decisions)
- **Downstream**: Links to derived documents (implementations, tests)

## Document ID Standards

All documents follow strict ID conventions defined in [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md):

- **Format**: `{TYPE}-{NNN}_{descriptive_slug}.{ext}`
- **Numbering**: Sequential from 001, stable once assigned
- **Slugs**: lower_snake_case, descriptive but concise
- **Index Files**: `{TYPE}-000_index.{ext}` for each document type
- **CTR Exception**: Dual-file format requires both `.md` and `.yaml` with matching slugs
  - Example: `CTR-001_position_risk_validation.md` + `CTR-001_position_risk_validation.yaml`

## Core Standards Documents

- **Workflow Guide**: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- **ID Naming**: [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document identification standards
- **Traceability**: [TRACEABILITY.md](./TRACEABILITY.md) - Traceability requirements and conventions
- **Traceability Style**: [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards) - Style guide for traceability links

## Creating New Documents

1. Identify document type and functional area
2. Check relevant index file (`{TYPE}-000_index.md`) for next available ID
3. Copy appropriate template from the directory
4. Name file following ID standards: `{TYPE}-{NNN}_{slug}.{ext}`
5. Fill in all template sections with complete traceability links
6. Update index file with new document entry
7. Validate traceability using validation scripts

## Validation

Validate document structure and traceability:

```bash
python scripts/validate_requirement_ids.py
python scripts/complete_traceability_matrix.py
python scripts/check_broken_references.py
```

## Best Practices

- **Link Format**: Use relative paths within templates directory
- **Traceability**: Always include upstream and downstream references
- **Completeness**: Fill all template sections; mark N/A if not applicable
- **Consistency**: Follow ID naming conventions strictly
- **Updates**: Update index files when adding new documents
- **Validation**: Run validation scripts after changes
