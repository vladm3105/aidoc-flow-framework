# AI Dev Flow - Universal Specification-Driven Development Framework

**Purpose**: Enable AI-assisted software development across any project domain through structured, traceable requirements and specifications.

**Status**: Production-ready framework with generic templates, domain adaptation guidance, cumulative tagging hierarchy, and automated validation tooling.

**Version**: 2.0 | **Last Updated**: 2025-11-13

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
- ✅ **Cumulative Tagging Hierarchy**: Each artifact includes tags from ALL upstream layers for complete audit trails
- ✅ **AI-Optimized**: YAML specifications designed for deterministic code generation
- ✅ **16-Layer Architecture**: Structured progression from strategy through validation
- ✅ **Dual-File Contracts**: Human-readable `.md` + machine-readable `.yaml`
- ✅ **Strict ID Standards**: Consistent naming and organization across all documents
- ✅ **Example-Driven**: Generic examples with `[PLACEHOLDER]` format for easy customization
- ✅ **Automated Validation**: Scripts for tag validation, traceability matrix generation, cumulative hierarchy enforcement

**📚 New to this framework?** Start with [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) for domain-specific guidance (financial, healthcare, e-commerce, SaaS, IoT, or generic software).

## Complete Development Workflow

**⚠️ See [index.md](./index.md#traceability-flow) for the authoritative workflow diagram with full Mermaid visualization.**

### 16-Layer Architecture with Cumulative Tagging

The AI Dev Flow transforms business requirements into production code through a structured, traceable workflow. Each layer includes cumulative tags from ALL upstream layers, creating complete audit trails for regulatory compliance (SEC, FINRA, FDA, ISO).

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
| **12** | tasks_plans | Session-specific plans | @brd→@tasks (9-11) | Session work scope |
| **13** | Code | Source code implementation | @brd→@tasks (9-11) | RUNNABLE artifacts |
| **14** | Tests | Test suite implementation | @brd→@code (10-12) | Quality validation |
| **15** | Validation | Production readiness verification | All upstream (10-15) | PRODUCTION-READY |

**Note**: Layers 8 (IMPL) and 9 (CTR) are optional - include only when needed for project management or API contracts.

### Critical Decision Point

**After IMPL (Project Management Layer)**:
- **Interface requirement** (API, event schema, data model) → Create **CTR** (API Contract) → then **SPEC**
- **No interface requirement** (internal logic, business rules) → Create **SPEC** directly

**CTR Format**: Dual-file contract with human-readable `.md` (context, traceability) + machine-readable `.yaml` (OpenAPI/AsyncAPI schema)

## Template Directories

### 1. Business Layer

**BRD/** - Business Requirements Documents
- High-level business objectives and market context
- Strategic goals and success criteria
- **Files**: [BRD-000_index.md](./BRD/BRD-000_index.md) | [Template](./BRD/BRD-template.md)

**PRD/** - Product Requirements Documents
- User-facing features and product capabilities
- Business requirements and acceptance criteria
- **Files**: [PRD-000_index.md](./PRD/PRD-000_index.md) | [Template](./PRD/PRD-TEMPLATE.md)

**EARS/** - Easy Approach to Requirements Syntax
- Measurable requirements using WHEN-THE-SHALL-WITHIN format
- Event-driven and state-driven requirements
- **Files**: [EARS-000_index.md](./EARS/EARS-000_index.md) | [Template](./EARS/EARS-TEMPLATE.md)

### 2. Testing Layer

**BDD/** - Behavior-Driven Development Scenarios
- Executable acceptance tests in Gherkin format
- Business-readable behavioral specifications
- **Files**: [BDD-000_index.md](./BDD/BDD-000_index.md) | [Template](./BDD/BDD-TEMPLATE.feature)

### 3. Architecture Layer

**ADR/** - Architecture Decision Records
- Architectural choices and rationale
- Technology selections and trade-offs
- **Files**: [ADR-000_index-TEMPLATE.md](./ADR/ADR-000_index-TEMPLATE.md) | [Template](./ADR/ADR-TEMPLATE.md)

**SYS/** - System Requirements Specifications
- System-level functional and non-functional requirements
- Performance, security, and operational characteristics
- **Files**: [SYS-000_index.md](./SYS/SYS-000_index.md) | [Template](./SYS/SYS-TEMPLATE.md)

### 4. Requirements Layer

**REQ/** - Atomic Requirements
- Granular, testable requirements with acceptance criteria
- **Organization**: Subdirectories by functional domain
  - `api/` - API integration requirements (examples: REQ-001_api_integration_example.md)
  - `auth/` - Authentication/authorization (examples: REQ-003_access_control_example.md)
  - `data/` - Data architecture (examples: REQ-002_data_validation_example.md)
  - `risk/` - Risk management (legacy: REQ-003_position_limit_enforcement.md)
- **Files**: [REQ-000_index.md](./REQ/REQ-000_index.md) | [Template](./REQ/REQ-TEMPLATE.md)

### 5. Project Management Layer

**IMPL/** - Implementation Plans
- Project management documents organizing work into phases, teams, deliverables
- **Focus**: WHO does WHAT, WHEN - NOT technical specifications (HOW)
- Identifies which CTR, SPEC, TASKS to create
- **Files**: [IMPL-000_index.md](./IMPL/IMPL-000_index.md) | [Template](./IMPL/IMPL-TEMPLATE.md)
- **Examples**: [IMPL-001_risk_management_system.md](./IMPL/examples/IMPL-001_risk_management_system.md) | [IMPL-001_feature_implementation_example.md](./IMPL/IMPL-001_feature_implementation_example.md)

### 6. Interface Layer

**CONTRACTS/** - API Contracts (CTR)
- Formal interface specifications for component-to-component communication
- **Dual-file format**:
  - `.md` file: Human-readable context, business rationale, traceability links
  - `.yaml` file: Machine-readable schema (OpenAPI/AsyncAPI/JSON Schema)
- **When to use**: Created when REQ specifies interface requirements (APIs, events, data models)
- **Benefits**: Enables parallel development and contract testing
- **Files**: [CTR-000_index.md](./CONTRACTS/CTR-000_index.md) | [Template .md](./CONTRACTS/CTR-TEMPLATE.md) + [Template .yaml](./CONTRACTS/CTR-TEMPLATE.yaml)
- **Examples**: [CTR-001_service_contract_example.md](./CONTRACTS/CTR-001_service_contract_example.md) + [CTR-001_service_contract_example.yaml](./CONTRACTS/CTR-001_service_contract_example.yaml)

### 7. Implementation Layer

**SPEC/** - Technical Specifications
- Implementation-ready YAML specifications for code generation
- Behavioral specifications and operational characteristics
- References CTR contracts when implementing interfaces
- **Files**: [SPEC-000_index.md](./SPEC/SPEC-000_index.md) | [Template](./SPEC/SPEC-TEMPLATE.yaml)
- **Examples**: [SPEC-001_api_client_example.yaml](./SPEC/SPEC-001_api_client_example.yaml)

### 8. Code Generation Layer

**TASKS/** - Code Generation Plans (TASKS)
- Exact TODOs to implement SPEC in source code
- Step-by-step guide for AI code generation from YAML specifications
- **1:1 mapping**: Each TASKS document corresponds to one SPEC
- **Files**: [TASKS-000_index.md](./TASKS/TASKS-000_index.md) | [Template](./TASKS/TASKS-TEMPLATE.md)

### 9. Session Planning Layer

**tasks_plans/** - Session-Specific Implementation Plans
- Organize multiple TASKS into session-scoped work packages
- Track progress across related implementation units
- Maintain context between AI coding sessions
- **Files**: Session plans saved via `/save-plan` command

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

Every document maintains bidirectional traceability through **Cumulative Tagging Hierarchy** - each artifact includes tags from ALL upstream layers, creating complete audit trails.

### Cumulative Tagging Hierarchy

**Core Principle**: Each layer N includes tags from layers 1 through N-1 plus its own identifier.

**Tag Format**: `@artifact-type: DOC-ID:REQ-ID`

**Example Progression**:
```markdown
# Layer 2 (PRD)
@brd: BRD-009:FR-015

# Layer 4 (BDD)
@brd: BRD-009:FR-015
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-002

# Layer 7 (REQ)
@brd: BRD-009:FR-015
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-002
@bdd: BDD-015:scenario-place-order
@adr: ADR-033
@sys: SYS-012:FUNC-001

# Layer 13 (Code)
@brd: BRD-009:FR-015
... [all upstream tags through @tasks]
@impl-status: complete
```

### Benefits

- **Complete Audit Trail**: Every artifact traces back to original business requirement
- **Regulatory Compliance**: SEC, FINRA, FDA, ISO requirements for traceability
- **Impact Analysis**: Instantly identify all downstream artifacts affected by upstream changes
- **Automated Validation**: Scripts enforce cumulative tagging compliance
- **Change Management**: Track complete lineage from requirements through code

### Validation

```bash
# Extract tags from codebase
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate cumulative tagging hierarchy
python scripts/validate_tags_against_docs.py --validate-cumulative --strict

# Generate traceability matrices
python scripts/generate_traceability_matrices.py --auto
```

See [TRACEABILITY.md](./TRACEABILITY.md) and [COMPLETE_TAGGING_EXAMPLE.md](./COMPLETE_TAGGING_EXAMPLE.md) for complete guidelines.

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
cp docs_templates/ai_dev_flow/REQ/REQ-TEMPLATE.md <your_project>/docs/REQ/
```

**Step 3: Replace Placeholders**
- Search for `[PLACEHOLDERS]` in templates
- Replace with domain-specific values
- Update examples to match your use cases

**Step 4: Create Your First Document**
1. **Choose Document Type**: Select directory (BRD/, PRD/, REQ/, etc.)
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

### Validation

The framework includes comprehensive validation tooling:

```bash
# Cumulative tagging validation (recommended)
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json
python scripts/validate_tags_against_docs.py --validate-cumulative --strict
python scripts/generate_traceability_matrices.py --auto

# Legacy validation (optional)
python scripts/validate_requirement_ids.py
python scripts/check_broken_references.py
```

**CI/CD Integration**: See [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md) for pre-commit hooks and GitHub Actions workflows.

**Note**: Framework includes `scripts/make_framework_generic.py` for maintaining placeholder consistency.

## Core Standards Documents

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document identification rules
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability requirements
- [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards) - Link formatting conventions
- [index.md](./index.md) - Detailed directory structure reference

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
13. **tasks_plans** (Layer 12) - Session-specific plans

**Implementation Layers (13-15)**:
14. **Code** (Layer 13) - Source code with cumulative tags
15. **Tests** (Layer 14) - Test suite with cumulative tags
16. **Validation** (Layer 15) - Production readiness verification

**Key Workflow Patterns**:
- **Cumulative Tagging**: Every artifact includes tags from ALL upstream layers
- **Complete Traceability**: Every document links upstream (requirements) and downstream (implementations)
- **Regulatory Compliance**: Complete audit trail for SEC, FINRA, FDA, ISO requirements
- **Dual-File Contracts**: CTR uses `.md` (human) + `.yaml` (machine) for parallel development
- **AI Code Generation**: SPEC + TASKS enable deterministic code generation by AI assistants
- **Automated Validation**: Scripts enforce tagging hierarchy and traceability compliance

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
- Deterministic code generation from YAML SPEC
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
├── BRD/              # Business Requirements Documents
├── PRD/               # Product Requirements Documents
├── EARS/              # EARS Requirements (Event-driven)
├── BDD/              # BDD Feature Files (Gherkin)
├── ADR/              # Architecture Decision Records
├── SYS/               # System Requirements Specifications
├── REQ/              # Atomic Requirements
│   ├── api/          # API integration requirements
│   ├── auth/         # Authentication/authorization requirements
│   ├── data/         # Data architecture requirements
│   └── risk/         # Risk management requirements (legacy examples)
├── IMPL/        # Implementation Plans (project management)
│   └── examples/     # Reference implementation plan examples
├── CONTRACTS/         # API Contracts (CTR) - dual-file format (.md + .yaml)
├── SPEC/             # Technical Specifications (YAML)
├── TASKS/          # Code Generation Plans (TASKS)
├── tasks_plans/       # Session-specific implementation plans (Layer 12)
├── scripts/           # Validation and tooling scripts
│   ├── extract_tags.py                    # Tag extraction from codebase
│   ├── validate_tags_against_docs.py      # Cumulative tagging validation
│   ├── generate_traceability_matrices.py  # Matrix generation
│   ├── add_cumulative_tagging_to_matrices.py  # Matrix template updater
│   └── make_framework_generic.py          # Placeholder maintenance tool
├── work_plans/        # Implementation plans (/save-plan command output)
├── index.md           # Detailed directory reference with Mermaid workflow
├── README.md          # This file (framework overview)
├── DOMAIN_ADAPTATION_GUIDE.md  # Domain-specific customization guide
├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  # Complete SDD methodology
├── ID_NAMING_STANDARDS.md      # Document identification standards
├── TRACEABILITY.md             # Traceability requirements and conventions
├── TRACEABILITY_SETUP.md       # Cumulative tagging setup and CI/CD integration
├── COMPLETE_TAGGING_EXAMPLE.md # End-to-end cumulative tagging example
├── WHEN_TO_CREATE_IMPL.md      # Guidance on IMPL document usage
└── [other standards documents]
```

## Framework Versions and Updates

**Current Version**: 2.0
**Last Updated**: 2025-11-13

**Version 2.0 - Cumulative Tagging Hierarchy** (November 2025):
- ✅ **16-Layer Architecture**: Expanded from 10 to 16 layers (added Strategy, tasks_plans, Code, Tests, Validation)
- ✅ **Cumulative Tagging System**: Each artifact includes tags from ALL upstream layers
- ✅ **Automated Validation**: Enhanced scripts enforce cumulative tagging compliance
- ✅ **Traceability Matrix Templates**: All 13 artifact types have cumulative tagging sections
- ✅ **Complete Example**: COMPLETE_TAGGING_EXAMPLE.md shows end-to-end tagging
- ✅ **Setup Guide**: TRACEABILITY_SETUP.md with CI/CD integration patterns
- ✅ **Regulatory Compliance**: Complete audit trails for SEC, FINRA, FDA, ISO
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

**For Original Project Context** (if using within trading project):
- [CLAUDE.md](/opt/data/trading/CLAUDE.md) - Project-level SDD guidance
- [docs/SPEC/](/opt/data/trading/docs/SPEC/) - Production specifications
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
