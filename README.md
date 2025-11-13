# AI Dev Flow Framework

**Specification-Driven Development (SDD) Template System for AI-Assisted Software Engineering**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

## Overview

The AI Dev Flow Framework is a comprehensive template system for implementing AI-Driven Specification-Driven Development (SDD). It provides structured workflows, document templates, and traceability mechanisms to transform business requirements into production-ready code through a systematic, traceable approach optimized for AI-assisted development.

### Key Features

- **10-Layer Workflow**: Structured progression from business requirements to production code
- **Tag-Based Auto-Discovery**: Lightweight @tags in code auto-generate bidirectional traceability matrices
- **Namespaced Traceability**: Explicit DOCUMENT-ID:REQUIREMENT-ID format prevents ambiguity
- **Complete Traceability**: Bidirectional links between all artifacts (business → architecture → code)
- **AI-Optimized Templates**: Ready for Claude Code, Gemini, GitHub Copilot, and other AI coding assistants
- **Multiple Entry Points**: 3 BRD templates for different project contexts (general, simplified, trading-specific)
- **Token-Efficient Design**: Optimized for AI tool context windows (50K-100K tokens per document)
- **Contract-First Development**: Optional API contract layer (CTR) for parallel development
- **Automated Validation**: Scripts for tag extraction, validation, and matrix generation with CI/CD integration

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
12. **Implementation** → Write code with traceability tags

### 5. Add Traceability Tags (Recommended)

Embed tags in your code docstrings:

```python
"""Service implementation.

@brd: BRD-001:FR-030, BRD-001:NFR-006
@sys: SYS-008
@spec: SPEC-003
@test: BDD-003:scenario-1
@impl-status: complete
"""
```

Then auto-generate matrices:

```bash
# Extract, validate, and generate matrices
python scripts/generate_traceability_matrices.py --auto

# View generated matrices
ls docs/generated/matrices/
```

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

### Tag-Based Auto-Discovery (Recommended)

**Principle:** Code is the single source of truth. Traceability matrices are auto-generated from lightweight tags.

#### Namespaced Tag Format

Embed tags in code docstrings using namespaced format:

```python
"""Market data service implementation.

@brd: BRD-001:FR-030, BRD-001:NFR-006
@sys: SYS-008
@spec: SPEC-003
@test: BDD-003:scenario-realtime, BDD-008:scenario-cache
@impl-status: complete
"""
```

**Format:** `@tag-type: DOCUMENT-ID:REQUIREMENT-ID`

**Tag Types:**
- `@brd:` - Business Requirements Document references
- `@prd:` - Product Requirements Document references
- `@sys:` - System Requirements references
- `@spec:` - Specification references
- `@req:` - Requirements Document references
- `@test:` - Test scenario references
- `@impl-status:` - Implementation status (pending|in-progress|complete|deprecated)

**Benefits:**
- ✅ Single source of truth (code)
- ✅ Automated validation (scripts check correctness)
- ✅ No sync drift (tags can't become stale)
- ✅ Bidirectional matrices auto-generated
- ✅ CI/CD enforceable (pre-commit hooks)

**Why Namespaced?**
- `@brd: FR-030` ❌ Ambiguous (which BRD document?)
- `@brd: BRD-001:FR-030` ✅ Explicit (FR-030 in BRD-001)

#### Traditional Section 7 (Legacy)

Manual traceability sections in documents remain supported during migration:

```markdown
## 7. Traceability

**Upstream:**
- [BRD-001](../BRD/BRD-001_requirements.md#FR-030)

**Downstream:**
- [SPEC-003](../SPEC/SPEC-003_implementation.yaml)
```

**Migration:** New projects should use tag-based approach. Existing projects can migrate gradually.

### ID Naming Standards

All documents follow standardized ID formats:

- **Format**: `TYPE-XXX` or `TYPE-XXX-YY`
- **Examples**: `BRD-001`, `REQ-003-02`, `ADR-1000`
- **Rules**:
  - XXX: 3-4 digit sequential number (001-999, then 1000-9999)
  - YY: 2-3 digit sub-document number (optional, 01-99)
  - Zero-padding maintained until range exceeded

### Traceability Matrices

**AUTO-GENERATED** from code tags (recommended) or manually maintained:

- `TYPE-000_TRACEABILITY_MATRIX.md`
- Tracks upstream sources (what drove this document)
- Tracks downstream artifacts (what derives from this document)
- **Generation**: `python scripts/generate_traceability_matrices.py --auto`

**Forward Matrix Example:**
```markdown
| Requirement | Implementing Files | Status |
|-------------|-------------------|--------|
| BRD-001:FR-030 | src/services/account.py:12 | ✓ Complete |
```

**Reverse Matrix Example:**
```markdown
| Source File | Requirements | Status |
|-------------|-------------|--------|
| src/services/account.py | FR-030, NFR-006 | Complete |
```

### Migration Guide: Section 7 → Tags

**Step 1: Add Tags to New Code**
```python
# Start with new implementations
"""New feature implementation.

@brd: BRD-001:FR-045
@spec: SPEC-005
@impl-status: in-progress
"""
```

**Step 2: Gradually Tag Existing Code**
- Prioritize high-value files (core services, critical paths)
- Add tags during code reviews or maintenance
- Use coverage reports to track progress

**Step 3: Validate Tags**
```bash
# Check tag format and document references
python scripts/validate_tags_against_docs.py --strict
```

**Step 4: Generate Matrices**
```bash
# Auto-generate bidirectional matrices
python scripts/generate_traceability_matrices.py --auto
```

**Step 5: Phase Out Section 7**
- Once tag coverage >80%, Section 7 becomes optional
- Keep Section 7 in documents, remove from code
- Let auto-generated matrices be the source of truth

**Coexistence:** Both approaches work together during migration. Section 7 in documents + tags in code.

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

### Tag-Based Automation (Recommended)

Located in `scripts/` (when integrated with your project):

```bash
# Extract tags from all source files
python scripts/extract_tags.py --source src/ docs/ --output docs/generated/tags.json

# Validate tags against actual documents
python scripts/validate_tags_against_docs.py --tags docs/generated/tags.json --strict

# Generate bidirectional traceability matrices
python scripts/generate_traceability_matrices.py --tags docs/generated/tags.json --auto

# Complete workflow (extract + validate + generate)
python scripts/generate_traceability_matrices.py --auto
```

**CI/CD Integration:**
```yaml
# .github/workflows/traceability.yml
- name: Validate Traceability Tags
  run: python scripts/validate_tags_against_docs.py --strict
```

### Legacy Validation Scripts

For projects using traditional Section 7:

```bash
# Validate requirement IDs and format
python scripts/validate_requirement_ids.py

# Check for broken cross-references
python scripts/check_broken_references.py

# Generate traceability matrix manually
python scripts/complete_traceability_matrix.py
```

### Quality Gates

Pre-commit checklist:

**Tag-Based Projects:**
- [ ] All code files have @brd/@sys/@spec tags in docstrings
- [ ] Tags use namespaced format (DOCUMENT-ID:REQUIREMENT-ID)
- [ ] Tag validation passes: `python scripts/validate_tags_against_docs.py --strict`
- [ ] Traceability matrices generated: `python scripts/generate_traceability_matrices.py --auto`
- [ ] Implementation status tags present (@impl-status: complete|in-progress|pending)

**Traditional Projects:**
- [ ] IDs comply with naming standards (XXX or XXX-YY format)
- [ ] No ID collisions (each XXX unique)
- [ ] All cross-references use valid markdown links
- [ ] Section 7 Traceability complete in all documents

**All Projects:**
- [ ] IMPL decision validated (created if complex, skipped if simple)
- [ ] CTR decision validated (created if interface, skipped if internal)
- [ ] SPEC interfaces match CTR contracts (if applicable)
- [ ] CTR dual-file format (both .md and .yaml exist)
- [ ] BDD scenarios have traceability references
- [ ] File size under 50,000 tokens standard, 100,000 maximum

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
- [Traceability](./ai_dev_flow/TRACEABILITY.md) - Tag-based and traditional traceability
- [Traceability Setup](./ai_dev_flow/TRACEABILITY_SETUP.md) - Automation and validation setup
- [Traceability Matrix Template](./ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md) - Complete matrix examples

### Decision Guides
- [When to Create IMPL](./ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL vs direct REQ→SPEC
- [CTR Policy](./ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - Dual-file format

### AI Tool Optimization
- [Tool Optimization Guide](./ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md) - Claude Code, Gemini, Copilot

### Validation Scripts
- `scripts/extract_tags.py` - Extract @tags from source files
- `scripts/validate_tags_against_docs.py` - Validate tags against documents
- `scripts/generate_traceability_matrices.py` - Generate bidirectional matrices
- `scripts/validate_requirement_ids.py` - Validate ID format (legacy + tags)

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

**Version**: 1.1.0
**Last Updated**: 2025-11-12
**Maintained by**: Vladimir M.

## Changelog

### Version 1.1.0 (2025-11-12)
- Added tag-based auto-discovery traceability system
- Introduced namespaced tag format (DOCUMENT-ID:REQUIREMENT-ID)
- Added automated validation scripts (extract_tags.py, validate_tags_against_docs.py, generate_traceability_matrices.py)
- Updated quality gates for tag-based and traditional projects
- Added CI/CD integration examples for traceability validation
- Legacy Section 7 approach still supported during migration

### Version 1.0.0 (2025-11-09)
- Initial release with 10-layer SDD workflow
- Complete template system for all artifact types
- Traditional Section 7 traceability
