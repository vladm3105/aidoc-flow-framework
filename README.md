# AI Dev Flow Framework

**Specification-Driven Development (SDD) Template System for AI-Assisted Software Engineering**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

## Overview

The AI Dev Flow Framework is a comprehensive template system for implementing AI-Driven Specification-Driven Development (SDD). It provides structured workflows, document templates, and traceability mechanisms to transform business requirements into production-ready code through a systematic, traceable approach optimized for AI-assisted development.

### Key Features

- **10-Layer Workflow**: Structured progression from business requirements to production code
- **Complete Traceability**: Bidirectional links between all artifacts (business → architecture → code)
- **AI-Optimized Templates**: Ready for Claude Code, Gemini, GitHub Copilot, and other AI coding assistants
- **Multiple Entry Points**: 3 BRD templates for different project contexts (general, simplified, trading-specific)
- **Token-Efficient Design**: Optimized for AI tool context windows (50K-100K tokens per document)
- **Contract-First Development**: Optional API contract layer (CTR) for parallel development
- **Automated Validation**: Scripts for ID validation, broken link checking, and traceability verification

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/vladm3105/ai-doc-flow-framework.git
cd ai-doc-flow-framework
```

### 2. Explore the Templates

All templates are located in `ai_dev_flow/`:

```bash
cd ai_dev_flow
ls -R
```

### 3. Start Your Project

Choose your entry point based on project context:

**Option A: Greenfield Project (New)**
```bash
# Use project-init skill (if using Claude Code)
# Or manually create directory structure
mkdir -p docs/{BRD,PRD,EARS,ADR,SYS,REQ,BDD,IMPL,CONTRACTS,SPEC,TASKS}
```

**Option B: Existing Project**
```bash
# Copy templates to your project
cp -r ai_dev_flow/* your-project/docs/
```

### 4. Follow the Workflow

1. **Business Requirements** → Start with `BRD/BRD-template.md`
2. **Product Requirements** → Create `PRD/PRD-TEMPLATE.md`
3. **Formal Requirements** → Use `EARS/EARS-TEMPLATE.md`
4. **Behavior Tests** → Write `BDD/BDD-TEMPLATE.feature`
5. **Architecture** → Document with `ADR/ADR-TEMPLATE.md`
6. **System Design** → Create `SYS/SYS-TEMPLATE.md`
7. **Atomic Requirements** → Define `REQ/REQ-TEMPLATE.md`
8. **Implementation Plan** → Organize with `IMPL/IMPL-TEMPLATE.md` (optional)
9. **API Contracts** → Specify with `CONTRACTS/CTR-TEMPLATE.md/.yaml` (if interfaces)
10. **Technical Specs** → Design with `SPEC/SPEC-TEMPLATE.yaml`
11. **Code Generation** → Guide with `TASKS/TASKS-TEMPLATE.md`
12. **Implementation** → Write code with full traceability

## Documentation Structure

### Workflow Layers

The SDD workflow organizes artifacts into 10 distinct layers:

```
Layer 1: Business Layer
├── BRD (Business Requirements Documents)
├── PRD (Product Requirements Documents)
└── EARS (Event Analysis Requirements Specification)

Layer 2: Testing Layer
└── BDD (Behavior-Driven Development)

Layer 3: Architecture Layer
├── ADR (Architecture Decision Records)
└── SYS (System Requirements Specifications)

Layer 4: Requirements Layer
└── REQ (Atomic Requirements)

Layer 5: Project Management Layer
└── IMPL (Implementation Plans) [OPTIONAL]

Layer 6: Interface Layer
└── CTR (API Contracts) [IF INTERFACE REQUIREMENT]

Layer 7: Implementation Layer
└── SPEC (Technical Specifications - YAML)

Layer 8: Code Generation Layer
└── TASKS (Code Generation Plans)

Layer 9: Execution Layer
└── Code + Tests

Layer 10: Validation Layer
└── Validation → Review → Production
```

### Template Categories

#### Business Layer Templates
- **BRD-template.md**: Comprehensive business requirements (general purpose)
- **BRD-template-2.md**: Simplified business requirements (lean projects)
- **BRD-trading-template.md**: Trading-specific business requirements (financial systems)
- **PRD-TEMPLATE.md**: Product requirements with features and KPIs
- **EARS-TEMPLATE.md**: Formal WHEN-THE-SHALL-WITHIN requirements

#### Architecture Layer Templates
- **ADR-TEMPLATE.md**: Architecture decisions with context and consequences
- **SYS-TEMPLATE.md**: System requirements with functional/non-functional specs

#### Requirements Layer Templates
- **REQ-TEMPLATE.md**: Atomic requirements with acceptance criteria
- **BDD-TEMPLATE.feature**: Gherkin scenarios for behavior validation

#### Implementation Layer Templates
- **IMPL-TEMPLATE.md**: Implementation plans (WHO/WHEN) - project management
- **CTR-TEMPLATE.md + .yaml**: API contracts (dual-file format)
- **SPEC-TEMPLATE.yaml**: Technical specifications (HOW to build)
- **TASKS-TEMPLATE.md**: Code generation plans (exact TODOs)

## Traceability System

### ID Naming Standards

All documents follow standardized ID formats:

- **Format**: `TYPE-XXX` or `TYPE-XXX-YY`
- **Examples**: `REQ-001`, `BRD-009-02`, `ADR-1000`
- **Rules**:
  - XXX: 3-4 digit sequential number (001-999, then 1000-9999)
  - YY: 2-3 digit sub-document number (optional, 01-99)
  - Zero-padding maintained until range exceeded

### Cross-Reference Format

Standard markdown links with anchors:

```markdown
[ADR-033](../ADR/ADR-033_risk_architecture.md#ADR-033)
[REQ-001](../REQ/api/ib/REQ-001_connection.md#REQ-001)
[BDD-007](../BDD/BDD-007_behavior_test.feature#scenario-1)
```

### Traceability Matrices

Each artifact type includes a traceability matrix:

- `TYPE-000_TRACEABILITY_MATRIX.md`
- Tracks upstream sources (what drove this document)
- Tracks downstream artifacts (what derives from this document)
- **MANDATORY**: Update matrix with each artifact creation

## Key Concepts

### When to Create IMPL

**Create IMPL When**:
- Duration ≥2 weeks
- Teams ≥3
- Components ≥5
- Critical budget/timeline
- External dependencies

**Skip IMPL When**:
- Single component
- Duration <2 weeks
- Single developer
- Low risk

Reference: `ai_dev_flow/WHEN_TO_CREATE_IMPL.md`

### When to Create CTR (API Contracts)

**Create CTR When**:
- Public APIs
- Event schemas
- Data models
- Version compatibility requirements

**Skip CTR When**:
- Internal logic only
- No external interface
- No serialization

Reference: `ai_dev_flow/WHEN_TO_CREATE_IMPL.md#when-to-create-ctr`

### Dual-File CTR Format

API contracts require BOTH files:

- `CTR-001_api_contract.md` - Human-readable context, error handling, NFRs
- `CTR-001_api_contract.yaml` - Machine-readable JSON Schema, OpenAPI/AsyncAPI

Policy: `ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md`

## Token Limits (AI Tool Optimized)

### Claude Code (Primary)
- Standard: 50,000 tokens (200KB)
- Maximum: 100,000 tokens (400KB)

### Gemini CLI (Secondary)
- Use file read tool (not `@`) for files >10,000 tokens
- No splitting needed

### GitHub Copilot
- Keep <30KB or create companion summaries

### General Rules
- Create sequential files (doc_001.md, doc_002.md) only when exceeding 100,000 tokens
- Reference: `ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md`

## Documentation Standards

### Language Requirements
- Objective, factual language only
- No promotional content or subjective claims
- Document implementation complexity (scale 1-5)
- Include resource requirements and constraints
- Specify failure modes and error conditions

### Code Separation
- No Python code blocks in markdown documentation
- Use Mermaid flowcharts for logic representation
- Create separate `.py` files for code examples
- Reference format: `[See Code Example: filename.py - function_name()]`

### Content Filtering

**Eliminate**:
- Benefit statements ("This will help you...")
- Efficiency claims ("Faster than...")
- Ease-of-use assertions ("Simply..." "Just...")
- Superlative adjectives (best, optimal, superior)

**Enforce**:
- Imperative verb forms for procedures
- Conditional statements for error handling
- Precise data type specifications
- Measurable impact criteria

## Validation Tools

### Available Scripts

Located in `scripts/` (when integrated with your project):

```bash
# Validate requirement IDs and format
python scripts/validate_requirement_ids.py

# Check for broken cross-references
python scripts/check_broken_references.py

# Generate traceability matrix
python scripts/complete_traceability_matrix.py
```

### Quality Gates

Pre-commit checklist:
- [ ] IDs comply with naming standards (XXX or XXX-YY format)
- [ ] No ID collisions (each XXX unique)
- [ ] All cross-references use valid markdown links
- [ ] IMPL decision validated (created if complex, skipped if simple)
- [ ] CTR decision validated (created if interface, skipped if internal)
- [ ] SPEC interfaces match CTR contracts (if applicable)
- [ ] CTR dual-file format (both .md and .yaml exist)
- [ ] BDD scenarios tagged with `@requirement` and `@adr`
- [ ] File size under 50,000 tokens standard, 100,000 maximum
- [ ] Traceability matrix updated (MANDATORY)

## Integration with AI Coding Tools

### Claude Code

Use the `doc-flow` skill for guided workflow:

```
User: "Implement position risk limit validation using doc-flow"
Assistant: [Launches doc-flow skill, creates full artifact chain]
```

### Gemini CLI

For files >10,000 tokens, use file read tool:

```bash
gemini read path/to/large_file.md
```

### GitHub Copilot

Keep documents <30KB or create companion summaries for context.

## Project Structure

```
ai-doc-flow-framework/
├── README.md                          # This file
├── ai_dev_flow/                       # Template system
│   ├── index.md                       # Workflow overview
│   ├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  # Authoritative guide
│   ├── ID_NAMING_STANDARDS.md         # ID format rules
│   ├── TRACEABILITY.md                # Cross-reference standards
│   ├── WHEN_TO_CREATE_IMPL.md         # Decision guide
│   ├── TOOL_OPTIMIZATION_GUIDE.md     # AI tool optimization
│   ├── BRD/                           # Business requirements templates
│   │   ├── BRD-template.md
│   │   ├── BRD-template-2.md
│   │   └── BRD-trading-template.md
│   ├── PRD/                           # Product requirements templates
│   ├── EARS/                          # Formal requirements templates
│   ├── ADR/                           # Architecture decision templates
│   ├── SYS/                           # System requirements templates
│   ├── REQ/                           # Atomic requirements templates
│   ├── BDD/                           # Behavior-driven test templates
│   ├── IMPL/                          # Implementation plan templates
│   ├── CONTRACTS/                     # API contract templates (dual-file)
│   ├── SPEC/                          # Technical specification templates
│   └── TASKS/                         # Code generation templates
├── work_plans/                        # Implementation plans
└── docs/                              # Additional documentation
```

## Example Workflow

### Complete Artifact Chain

```
Strategy Document
    ↓
BRD-001: Business Requirements
    ↓
PRD-001: Product Requirements
    ↓
EARS-001: Formal Requirements (WHEN-THE-SHALL-WITHIN)
    ↓
BDD-001: Behavior Tests (Gherkin scenarios)
    ↓
ADR-001: Architecture Decision
    ↓
SYS-001: System Requirements
    ↓
REQ-001: Atomic Requirement
    ↓
IMPL-001: Implementation Plan [OPTIONAL]
    ↓
CTR-001: API Contract (.md + .yaml) [IF INTERFACE]
    ↓
SPEC-001: Technical Specification (YAML)
    ↓
TASKS-001: Code Generation Plan
    ↓
Code Implementation
    ↓
Test Validation (BDD + Unit + Integration + Contract)
```

## Use Cases

### Financial Trading Systems
- Use `BRD-trading-template.md` for trading-specific requirements
- Example: Options trading strategy implementation
- Full traceability from strategy documents to production code

### General Software Projects
- Use `BRD-template.md` for comprehensive business requirements
- Or `BRD-template-2.md` for simplified lean approach
- Scales from small prototypes to enterprise systems

### Microservices Architecture
- Use CTR dual-file format for service contracts
- Define interfaces before implementation
- Enable parallel development across teams

### Regulatory Compliance Projects
- Complete audit trails via traceability matrices
- Document all architectural decisions (ADR)
- Track requirements through implementation

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Follow existing template structure
4. Update traceability documentation
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## References

### Core Documentation
- [Workflow Guide](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [Index](./ai_dev_flow/index.md) - Template overview with workflow diagram
- [ID Standards](./ai_dev_flow/ID_NAMING_STANDARDS.md) - Naming conventions
- [Traceability](./ai_dev_flow/TRACEABILITY.md) - Cross-reference format

### Decision Guides
- [When to Create IMPL](./ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL vs direct REQ→SPEC
- [CTR Policy](./ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - Dual-file format

### AI Tool Optimization
- [Tool Optimization Guide](./ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md) - Claude Code, Gemini, Copilot

## Support

- **Issues**: [GitHub Issues](https://github.com/vladm3105/ai-doc-flow-framework/issues)
- **Documentation**: [ai_dev_flow/](./ai_dev_flow/)
- **Examples**: See `ai_dev_flow/*/examples/` directories

## Acknowledgments

Developed for AI-assisted software engineering workflows optimized for:
- Claude Code (Anthropic)
- Gemini CLI (Google)
- GitHub Copilot (Microsoft)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-09
**Maintained by**: Vladimir M.
