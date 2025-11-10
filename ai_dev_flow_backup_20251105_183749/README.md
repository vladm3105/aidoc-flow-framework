# AI Dev Flow - Specification-Driven Development Templates

Purpose: Enable AI-assisted software development through structured, traceable requirements and specifications.

## Overview

This directory provides comprehensive templates for Specification-Driven Development (SDD), transforming business needs into production-ready code through a systematic, traceable workflow. All templates follow strict ID naming conventions and maintain bidirectional traceability.

## Complete Development Workflow

**⚠️ See [index.md](./index.md#traceability-flow) for the authoritative workflow diagram with full Mermaid visualization.**

### Quick Reference

The AI Dev Flow follows a 10-layer architecture transforming business requirements into production code:

1. **Business Layer**: BRD → PRD → EARS
2. **Testing Layer**: BDD
3. **Architecture Layer**: ADR → SYS
4. **Requirements Layer**: REQ
5. **Project Management Layer**: IMPL
6. **Interface Layer**: CTR (if interface requirement)
7. **Implementation Layer**: SPEC
8. **Code Generation Layer**: TASKS
9. **Execution Layer**: Code → Tests
10. **Validation Layer**: Validation → Review → Production

**Key Decision Point**: After IMPL, if the requirement involves an interface (API, event schema, data model), create CTR before SPEC. Otherwise, go directly to SPEC.

## Template Directories

### Business Layer
- **brds/** - Business Requirements Documents
  - High-level business objectives and market context
  - Strategic goals and success criteria
  - [BRD-000_index.md](./brds/BRD-000_index.md) | [Templates](./brds/)

- **prd/** - Product Requirements Documents
  - User-facing features and product capabilities
  - Business requirements and acceptance criteria
  - [PRD-000_index.md](./prd/PRD-000_index.md) | [Template](./prd/PRD-TEMPLATE.md)

- **ears/** - Easy Approach to Requirements Syntax
  - Measurable requirements using WHEN-THE-SHALL-WITHIN format
  - Event-driven and state-driven requirements
  - [EARS-000_index.md](./ears/EARS-000_index.md) | [Template](./ears/EARS-TEMPLATE.md)

### Requirements Layer
- **bbds/** - Behavior-Driven Development Scenarios
  - Executable acceptance tests in Gherkin format
  - Business-readable behavioral specifications
  - [BDD-000_index.md](./bbds/BDD-000_index.md) | [Template](./bbds/BDD-TEMPLATE.feature)

- **reqs/** - Atomic Requirements
  - Granular, testable requirements with acceptance criteria
  - Organized by functional domain (api/, risk/, ml/, data/)
  - [REQ-000_index.md](./reqs/REQ-000_index.md) | [Template](./reqs/REQ-TEMPLATE.md)

### Architecture Layer
- **adrs/** - Architecture Decision Records
  - Architectural choices and rationale
  - Technology selections and trade-offs
  - [ADR-000_index-TEMPLATE.md](./adrs/ADR-000_index-TEMPLATE.md) | [Template](./adrs/ADR-TEMPLATE.md)

- **sys/** - System Requirements Specifications
  - System-level functional and non-functional requirements
  - Performance, security, and operational characteristics
  - [SYS-000_index.md](./sys/SYS-000_index.md) | [Template](./sys/SYS-TEMPLATE.md)

### Project Management Layer
- **impl_plans/** - Implementation Plans
  - Project management documents organizing work into phases, teams, and deliverables
  - WHO does WHAT, WHEN - NOT technical specifications (HOW)
  - Identifies which CTR, SPEC, TASKS to create
  - [IMPL-000_index.md](./impl_plans/IMPL-000_index.md) | [Template](./impl_plans/IMPL-TEMPLATE.md) | [Example](./impl_plans/examples/IMPL-001_risk_management_system.md)

### Design Layer
- **contracts/** - API Contracts (CTR)
  - Formal interface specifications for component-to-component communication
  - Dual-file format: `.md` (human-readable context) + `.yaml` (machine-readable schema)
  - Created when REQ specifies interface requirements
  - Enables parallel development and contract testing
  - [CTR-000_index.md](./contracts/CTR-000_index.md) | [Templates](./contracts/CTR-TEMPLATE.md) + [.yaml](./contracts/CTR-TEMPLATE.yaml)

- **specs/** - Technical Specifications
  - Implementation-ready YAML specifications
  - Behavioral specifications and operational characteristics
  - References CTR contracts when implementing interfaces
  - [SPEC-000_index.md](./specs/SPEC-000_index.md) | [Template](./specs/SPEC-TEMPLATE.yaml)

### Code Generation Layer
- **ai_tasks/** - Code Generation Plans (TASKS)
  - Exact TODOs to implement SPEC in source code
  - Step-by-step guide for generating code from YAML specifications
  - Each TASKS document corresponds to one SPEC
  - [TASKS-000_index.md](./ai_tasks/TASKS-000_index.md) | [Template](./ai_tasks/TASKS-TEMPLATE.md)

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

### Creating New Documents

1. **Choose Document Type**: Select appropriate directory (brds/, prd/, reqs/, etc.)
2. **Check Index**: Review `{TYPE}-000_index.{ext}` for next available ID
3. **Copy Template**: Use template file from the directory
4. **Fill Content**: Complete all sections with traceability links
5. **Update Index**: Add entry to index file
6. **Validate**: Run validation scripts

### Template Usage

Each directory contains:
- **Index File**: `{TYPE}-000_index.{ext}` - Lists all documents of that type
- **Template File**: `{TYPE}-TEMPLATE.{ext}` - Copy for new documents
- **README.md**: Detailed usage guide and best practices
- **Example Files**: Reference implementations (where applicable)

### Validation

Before committing:
```bash
python scripts/validate_requirement_ids.py
python scripts/complete_traceability_matrix.py
python scripts/check_broken_references.py
```

## Core Standards Documents

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document identification rules
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability requirements
- [Traceability Format Standards](./TRACEABILITY.md#traceability-format-standards) - Link formatting conventions
- [index.md](./index.md) - Detailed directory structure reference

## Workflow Guides

### Business Requirements → Technical Implementation

1. **BRD** defines business objectives
2. **PRD** translates to product features
3. **EARS** creates measurable requirements
4. **BDD** writes acceptance tests
5. **ADR** documents architecture decisions
6. **SYS** specifies system requirements
7. **REQ** breaks down atomic requirements
8. **IMPL** organizes project work (WHO/WHEN)
9. **CTR** defines API contracts (if interface requirement)
10. **SPEC** provides YAML implementation details (HOW)
11. **TASKS** provides exact TODOs for code generation

### AI-Assisted Development

Templates are optimized for AI code generation:
- Structured YAML specifications
- Clear interface definitions
- Explicit constraints and acceptance criteria
- Measurable success conditions
- Complete traceability chains

## Best Practices

1. **One Concept Per File**: Each document addresses one requirement/decision/component
2. **Complete Traceability**: Always link upstream sources and downstream implementations
3. **Measurable Criteria**: Use quantitative thresholds, not subjective terms
4. **Update Indexes**: Keep index files current with all documents
5. **Run Validation**: Check links and IDs before committing

## Directory Organization

```
docs_templates/ai_dev_flow/
├── adrs/              # Architecture Decision Records
├── ai_tasks/          # Code Generation Plans (TASKS)
├── bbds/              # BDD Feature Files
├── brds/              # Business Requirements Documents
├── contracts/         # API Contracts (CTR) - dual-file format
├── ears/              # EARS Requirements
├── impl_plans/        # Implementation Plans (IMPL) - project management
│   └── examples/     # Reference implementation plan examples
├── prd/               # Product Requirements Documents
├── reqs/              # Atomic Requirements
│   ├── api/          # API integration requirements
│   ├── risk/         # Risk management requirements
│   ├── ml/           # ML model requirements
│   └── data/         # Data architecture requirements
├── specs/             # Technical Specifications (YAML)
│   ├── services/     # Service specifications
│   ├── agents/       # Agent specifications
│   └── infrastructure/ # Infrastructure specifications
├── sys/               # System Requirements Specifications
├── index.md           # Detailed directory reference
├── README.md          # This file
└── *.md              # Core standards documents
```

## Related Documentation

- **Project Root**: [CLAUDE.md](/opt/data/trading/CLAUDE.md) - Project-level SDD guidance
- **Active Specs**: [docs/specs/](/opt/data/trading/docs/specs/) - Production specifications
- **Implementation Guides**: [docs/src/](/opt/data/trading/docs/src/) - Component implementations

## Support

For questions or issues:
1. Review relevant template README.md
2. Check [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
3. Examine existing examples in the directory
4. Validate using provided scripts
