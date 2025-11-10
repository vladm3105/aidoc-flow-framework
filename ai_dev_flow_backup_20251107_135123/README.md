# AI Dev Flow - Universal Specification-Driven Development Framework

**Purpose**: Enable AI-assisted software development across any project domain through structured, traceable requirements and specifications.

**Status**: Production-ready framework with generic templates, domain adaptation guidance, and validation tooling.

**Version**: 1.0 | **Last Updated**: 2025-11-05

## Overview

This directory provides a **universal, reusable framework** for Specification-Driven Development (SDD), transforming business needs into production-ready code through a systematic, traceable workflow.

### Why AI Dev Flow?

**Traditional Development Challenges**:
- Requirements drift from implementation over time
- Manual traceability is incomplete and outdated
- Inconsistent documentation across teams
- AI code generation requires unstructured guidance

**AI Dev Flow Solutions**:
- ✅ **Domain-Agnostic**: Adaptable to any software project (e-commerce, SaaS, IoT, healthcare, finance)
- ✅ **Complete Traceability**: Bidirectional links from business requirements to production code
- ✅ **AI-Optimized**: YAML specifications designed for deterministic code generation
- ✅ **10-Layer Architecture**: Structured progression from business needs to deployment
- ✅ **Dual-File Contracts**: Human-readable `.md` + machine-readable `.yaml`
- ✅ **Strict ID Standards**: Consistent naming and organization across all documents
- ✅ **Example-Driven**: Generic examples with `[PLACEHOLDER]` format for easy customization
- ✅ **Validation Tooling**: Scripts for ID validation, traceability checks, reference verification

**📚 New to this framework?** Start with [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) for domain-specific guidance (financial, healthcare, e-commerce, SaaS, IoT, or generic software).

## Complete Development Workflow

**⚠️ See [index.md](./index.md#traceability-flow) for the authoritative workflow diagram with full Mermaid visualization.**

### 10-Layer Architecture

The AI Dev Flow transforms business requirements into production code through a structured, traceable workflow:

| Layer | Documents | Purpose | Key Decision |
|-------|-----------|---------|--------------|
| **1. Business** | BRD → PRD → EARS | Define business objectives and measurable requirements | WHAT needs to be built |
| **2. Testing** | BDD | Define acceptance criteria in executable Gherkin format | HOW to verify success |
| **3. Architecture** | ADR → SYS | Document architectural decisions and system specifications | TECHNICAL approach |
| **4. Requirements** | REQ | Break down into atomic, testable requirements | GRANULAR specifications |
| **5. Project Mgmt** | IMPL | Organize work into phases, teams, deliverables | WHO/WHEN to build |
| **6. Interface** | CTR (optional) | Define API contracts for component communication | INTERFACE definitions |
| **7. Implementation** | SPEC | YAML specifications for code generation | HOW to build |
| **8. Code Generation** | TASKS | AI-structured implementation steps | EXACT TODOs |
| **9. Execution** | Code → Tests | Generated implementation and test suites | RUNNABLE artifacts |
| **10. Validation** | Validation → Review → Prod | Verify acceptance criteria and deploy | PRODUCTION-READY |

### Critical Decision Point

**After IMPL (Project Management Layer)**:
- **Interface requirement** (API, event schema, data model) → Create **CTR** (API Contract) → then **SPEC**
- **No interface requirement** (internal logic, business rules) → Create **SPEC** directly

**CTR Format**: Dual-file contract with human-readable `.md` (context, traceability) + machine-readable `.yaml` (OpenAPI/AsyncAPI schema)

## Template Directories

### 1. Business Layer

**brds/** - Business Requirements Documents
- High-level business objectives and market context
- Strategic goals and success criteria
- **Files**: [BRD-000_index.md](./brds/BRD-000_index.md) | [Template](./brds/BRD-template.md)

**prd/** - Product Requirements Documents
- User-facing features and product capabilities
- Business requirements and acceptance criteria
- **Files**: [PRD-000_index.md](./prd/PRD-000_index.md) | [Template](./prd/PRD-TEMPLATE.md)

**ears/** - Easy Approach to Requirements Syntax
- Measurable requirements using WHEN-THE-SHALL-WITHIN format
- Event-driven and state-driven requirements
- **Files**: [EARS-000_index.md](./ears/EARS-000_index.md) | [Template](./ears/EARS-TEMPLATE.md)

### 2. Testing Layer

**bbds/** - Behavior-Driven Development Scenarios
- Executable acceptance tests in Gherkin format
- Business-readable behavioral specifications
- **Files**: [BDD-000_index.md](./bbds/BDD-000_index.md) | [Template](./bbds/BDD-TEMPLATE.feature)

### 3. Architecture Layer

**adrs/** - Architecture Decision Records
- Architectural choices and rationale
- Technology selections and trade-offs
- **Files**: [ADR-000_index-TEMPLATE.md](./adrs/ADR-000_index-TEMPLATE.md) | [Template](./adrs/ADR-TEMPLATE.md)

**sys/** - System Requirements Specifications
- System-level functional and non-functional requirements
- Performance, security, and operational characteristics
- **Files**: [SYS-000_index.md](./sys/SYS-000_index.md) | [Template](./sys/SYS-TEMPLATE.md)

### 4. Requirements Layer

**reqs/** - Atomic Requirements
- Granular, testable requirements with acceptance criteria
- **Organization**: Subdirectories by functional domain
  - `api/` - API integration requirements (examples: REQ-001_api_integration_example.md)
  - `auth/` - Authentication/authorization (examples: REQ-003_access_control_example.md)
  - `data/` - Data architecture (examples: REQ-002_data_validation_example.md)
  - `risk/` - Risk management (legacy: REQ-003_position_limit_enforcement.md)
- **Files**: [REQ-000_index.md](./reqs/REQ-000_index.md) | [Template](./reqs/REQ-TEMPLATE.md)

### 5. Project Management Layer

**impl_plans/** - Implementation Plans
- Project management documents organizing work into phases, teams, deliverables
- **Focus**: WHO does WHAT, WHEN - NOT technical specifications (HOW)
- Identifies which CTR, SPEC, TASKS to create
- **Files**: [IMPL-000_index.md](./impl_plans/IMPL-000_index.md) | [Template](./impl_plans/IMPL-TEMPLATE.md)
- **Examples**: [IMPL-001_risk_management_system.md](./impl_plans/examples/IMPL-001_risk_management_system.md) | [IMPL-001_feature_implementation_example.md](./impl_plans/IMPL-001_feature_implementation_example.md)

### 6. Interface Layer

**contracts/** - API Contracts (CTR)
- Formal interface specifications for component-to-component communication
- **Dual-file format**:
  - `.md` file: Human-readable context, business rationale, traceability links
  - `.yaml` file: Machine-readable schema (OpenAPI/AsyncAPI/JSON Schema)
- **When to use**: Created when REQ specifies interface requirements (APIs, events, data models)
- **Benefits**: Enables parallel development and contract testing
- **Files**: [CTR-000_index.md](./contracts/CTR-000_index.md) | [Template .md](./contracts/CTR-TEMPLATE.md) + [Template .yaml](./contracts/CTR-TEMPLATE.yaml)
- **Examples**: [CTR-001_service_contract_example.md](./contracts/CTR-001_service_contract_example.md) + [CTR-001_service_contract_example.yaml](./contracts/CTR-001_service_contract_example.yaml)

### 7. Implementation Layer

**specs/** - Technical Specifications
- Implementation-ready YAML specifications for code generation
- Behavioral specifications and operational characteristics
- References CTR contracts when implementing interfaces
- **Files**: [SPEC-000_index.md](./specs/SPEC-000_index.md) | [Template](./specs/SPEC-TEMPLATE.yaml)
- **Examples**: [SPEC-001_api_client_example.yaml](./specs/SPEC-001_api_client_example.yaml)

### 8. Code Generation Layer

**ai_tasks/** - Code Generation Plans (TASKS)
- Exact TODOs to implement SPEC in source code
- Step-by-step guide for AI code generation from YAML specifications
- **1:1 mapping**: Each TASKS document corresponds to one SPEC
- **Files**: [TASKS-000_index.md](./ai_tasks/TASKS-000_index.md) | [Template](./ai_tasks/TASKS-TEMPLATE.md)

## Document ID Standards

All documents follow strict naming conventions:

Format: `{TYPE}-{NNN}_{descriptive_slug}.{ext}`

- **TYPE**: Document type prefix (BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS)
- **NNN**: Three-digit sequence number (001, 002, 003)
- **descriptive_slug**: snake_case description
- **ext**: File extension (md, feature, yaml)

Examples:
- `PRD-001_alpha_vantage_integration.md`
- `BDD-003_risk_limits_requirements.feature`
- `CTR-001_position_risk_validation.md` + `CTR-001_position_risk_validation.yaml` (dual-file format)
- `SPEC-042_real_time_processor.yaml`

**Note**: CTR (API Contracts) requires both `.md` and `.yaml` files with matching slugs.

See [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) for complete rules.

## Traceability

Every document maintains bidirectional traceability through tags and links:

### Upstream Traceability
Documents link to their source requirements:
```markdown
@prd:[PRD-001](../prd/PRD-001_component.md)
@sys:[SYS-001](../sys/SYS-001_component.md)
```

### Downstream Traceability
Documents link to implementations and tests:
```markdown
@contract:[CTR-001](../contracts/CTR-001_component_api.md#CTR-001)
@spec:[SPEC-001](../specs/services/SPEC-001_component.yaml)
@bdd:[BDD-001](../bbds/BDD-001_requirements.feature#scenarios)
```

See [TRACEABILITY.md](./TRACEABILITY.md) for complete guidelines.

## Getting Started

### Quick Start Guide

**Step 1: Choose Your Domain**
- Review [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md)
- Identify domain-specific terminology and placeholders

**Step 2: Copy Templates to Your Project**
```bash
# Copy entire framework to your project
cp -r docs_templates/ai_dev_flow/ <your_project>/docs/

# Or copy specific templates as needed
cp docs_templates/ai_dev_flow/reqs/REQ-TEMPLATE.md <your_project>/docs/reqs/
```

**Step 3: Replace Placeholders**
- Search for `[PLACEHOLDERS]` in templates
- Replace with domain-specific values
- Update examples to match your use cases

**Step 4: Create Your First Document**
1. **Choose Document Type**: Select directory (brds/, prd/, reqs/, etc.)
2. **Check Index**: Review `{TYPE}-000_index.{ext}` for next available ID
3. **Copy Template**: Use template file from the directory
4. **Fill Content**: Complete all sections with traceability links
5. **Update Index**: Add entry to index file
6. **Validate**: Run validation scripts (if available)

### Template Structure

Each directory contains:
- **Index File**: `{TYPE}-000_index.{ext}` - Master list of all documents
- **Template File**: `{TYPE}-TEMPLATE.{ext}` - Copy for new documents
- **README.md**: Detailed usage guide and best practices
- **Example Files**: Reference implementations showing real-world usage
  - Generic examples with `[PLACEHOLDER]` format
  - Domain-specific examples from original project

### Validation (Optional)

If implementing validation tooling:
```bash
# ID validation
python scripts/validate_requirement_ids.py

# Traceability matrix generation
python scripts/complete_traceability_matrix.py

# Broken reference detection
python scripts/check_broken_references.py
```

**Note**: Framework includes `scripts/make_framework_generic.py` for maintaining placeholder consistency.

## Core Standards Documents

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document identification rules
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability requirements
- [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards) - Link formatting conventions
- [index.md](./index.md) - Detailed directory structure reference

## Workflow Guides

### Business Requirements → Production Code

The AI Dev Flow follows a linear progression through 10 layers:

1. **BRD** - Define business objectives and market context
2. **PRD** - Translate business needs to product features
3. **EARS** - Create measurable event-driven requirements
4. **BDD** - Write executable acceptance tests in Gherkin
5. **ADR** - Document architectural decisions and rationale
6. **SYS** - Specify system-level requirements
7. **REQ** - Break down into atomic, testable requirements
8. **IMPL** - Organize project work (WHO/WHEN/deliverables)
9. **CTR** - Define API contracts (if interface requirement exists)
10. **SPEC** - Provide YAML implementation details (HOW to build)
11. **TASKS** - Generate exact TODOs for AI code generation

**Key Workflow Patterns**:
- **Complete Traceability**: Every document links upstream (requirements) and downstream (implementations)
- **Dual-File Contracts**: CTR uses `.md` (human) + `.yaml` (machine) for parallel development
- **AI Code Generation**: SPEC + TASKS enable deterministic code generation by AI assistants

### AI-Assisted Development

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
- Deterministic code generation from YAML specs
- Automatic traceability comment injection
- Consistent implementation patterns
- Reduced manual coding effort (48x speed improvement documented)

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
- **Token Limits (Tool-Optimized)**:
  - **Claude Code** (Primary): Up to 50,000 tokens (200KB) standard, 100,000 tokens (400KB) maximum
  - **Gemini CLI** (Secondary): Use file read tool (not `@`) for files >10,000 tokens
  - **GitHub Copilot**: Keep <30KB or create companion summaries
  - See: [TOOL_OPTIMIZATION_GUIDE.md](TOOL_OPTIMIZATION_GUIDE.md) and [Gemini_CLI_Large_File_Workarounds.md](../Gemini_CLI_Large_File_Workarounds.md)
- **Update History**: Document version and last updated date in headers

## Directory Organization

```
docs_templates/ai_dev_flow/
├── brds/              # Business Requirements Documents
├── prd/               # Product Requirements Documents
├── ears/              # EARS Requirements (Event-driven)
├── bbds/              # BDD Feature Files (Gherkin)
├── adrs/              # Architecture Decision Records
├── sys/               # System Requirements Specifications
├── reqs/              # Atomic Requirements
│   ├── api/          # API integration requirements
│   ├── auth/         # Authentication/authorization requirements
│   ├── data/         # Data architecture requirements
│   └── risk/         # Risk management requirements (legacy examples)
├── impl_plans/        # Implementation Plans (project management)
│   └── examples/     # Reference implementation plan examples
├── contracts/         # API Contracts (CTR) - dual-file format (.md + .yaml)
├── specs/             # Technical Specifications (YAML)
├── ai_tasks/          # Code Generation Plans (TASKS)
├── scripts/           # Validation and tooling scripts
│   └── make_framework_generic.py  # Placeholder maintenance tool
├── index.md           # Detailed directory reference with Mermaid workflow
├── README.md          # This file (framework overview)
├── DOMAIN_ADAPTATION_GUIDE.md  # Domain-specific customization guide
├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  # Complete SDD methodology
├── ID_NAMING_STANDARDS.md      # Document identification standards
├── TRACEABILITY.md             # Traceability requirements and conventions
├── WHEN_TO_CREATE_IMPL.md      # Guidance on IMPL document usage
└── [other standards documents]
```

## Framework Versions and Updates

**Current Version**: 1.0
**Last Updated**: 2025-11-05

**Recent Enhancements**:
- Added IMPL (Implementation Plans) for project management layer
- Created DOMAIN_ADAPTATION_GUIDE.md with 5 domain checklists
- Introduced dual-file CTR format (.md + .yaml)
- Added generic examples with placeholder format
- Enhanced TASKS templates for AI code generation

**Framework Evolution**:
- Proven in production: 48x code generation speed improvement
- 10-layer architecture validated through real-world usage
- Complete traceability from business needs to deployed code
- AI-optimized YAML specifications for deterministic generation

## Related Documentation

**Within This Framework**:
- [index.md](./index.md) - Complete directory reference with workflow diagram
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Detailed SDD methodology
- [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) - Domain customization checklists
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document naming conventions
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability format standards

**For Original Project Context** (if using within trading project):
- [CLAUDE.md](/opt/data/trading/CLAUDE.md) - Project-level SDD guidance
- [docs/specs/](/opt/data/trading/docs/specs/) - Production specifications
- [docs/src/](/opt/data/trading/docs/src/) - Component implementations

## Adoption and Support

### Adopting This Framework

1. **Copy templates** to your project: `cp -r docs_templates/ai_dev_flow/ <your_project>/docs/`
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
- Run `scripts/make_framework_generic.py` to ensure consistency
- Document version and last updated date in modified files
