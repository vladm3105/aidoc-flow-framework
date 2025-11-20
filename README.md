# AI Dev Flow Framework

**Specification-Driven Development (SDD) Template System for AI-Assisted Software Engineering**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

## Overview

The AI Dev Flow Framework is a comprehensive template system for implementing AI-Driven Specification-Driven Development (SDD). It provides structured workflows, document templates, and traceability mechanisms to transform business requirements into production-ready code through a systematic, traceable approach optimized for AI-assisted development.

### Key Features

- **16-Layer Architecture**: Structured progression from strategy to validation (Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → IPLAN → Code → Tests → Validation)
- **Cumulative Tagging Hierarchy**: Each artifact includes tags from ALL upstream layers for complete audit trails
- **Tag-Based Auto-Discovery**: Lightweight @tags in code auto-generate bidirectional traceability matrices
- **Namespaced Traceability**: Explicit DOCUMENT-ID:REQUIREMENT-ID format prevents ambiguity
- **Complete Traceability**: Bidirectional links between all artifacts (business → architecture → code)
- **AI-Optimized Templates**: Ready for Claude Code, Gemini, GitHub Copilot, and other AI coding assistants
- **Domain-Agnostic**: Adaptable to any software domain (finance, healthcare, e-commerce, SaaS, IoT)
- **Token-Efficient Design**: Optimized for AI tool context windows (50K-100K tokens per document)
- **Dual-File Contracts**: CTR uses `.md` (human) + `.yaml` (machine) for parallel development
- **Automated Validation**: Scripts for tag extraction, cumulative tagging validation, and matrix generation with CI/CD integration
- **Regulatory Compliance**: Complete audit trails meet SEC, FINRA, FDA, ISO requirements

## Quality Gates and Traceability Validation

The framework includes automated quality gates that ensure each layer in the 16-layer SDD workflow meets maturity thresholds before progressing to downstream artifacts. Quality gates prevent immature artifacts from affecting subsequent development stages.

### Quality Gate Architecture

**Automatic Validation Points:**
- **Ready Score Gates**: Each artifact includes a maturity score (e.g., `EARS-Ready Score: ✅ 95% ≥90%`)
- **Cumulative Tag Enforcement**: All artifacts must include traceability tags from upstream layers
- **Pre-commit Blocking**: Git hooks validate artifacts before commits

**Pre-commit Quality Gates:**
- `./scripts/validate_quality_gates.sh docs/PRD/PRD-001.md` - Validates individual artifact readiness
- Automatic validation during `git commit` on changes to `docs/` directory
- Refer to [`TRACEABILITY_VALIDATION.md`](./ai_dev_flow/TRACEABILITY_VALIDATION.md) for complete specification

### Quality Gate Workflow By Layer

Each layer transition has specific quality requirements:

| **From→To** | **Quality Gate** | **Validation Command** |
|-------------|------------------|----------------------|
| **BRD→PRD** | `EARS-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/BRD/BRD-001.md` |
| **PRD→EARS** | `BDD-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/PRD/PRD-001.md` |
| **EARS→BDD** | `ADR-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/EARS/EARS-001.md` |
| **BDD→ADR** | `SYS-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/BDD/BDD-001.feature` |
| **ADR→SYS** | `REQ-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/ADR/ADR-001.md` |
| **SYS→REQ** | `SPEC-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/SYS/SYS-001.md` |
| **REQ→IMPL** | `IMPL-Ready Score ≥90%` | `./scripts/validate_quality_gates.sh docs/REQ/risk/lim/REQ-001.md` |
| **IMPL→SPEC** | `TASKS-Ready Score ≥90%` (SPEC) | `./scripts/validate_quality_gates.sh docs/SPEC/SPEC-001.yaml` |
| **CTR→SPEC** | Contract file validation | `./scripts/validate_quality_gates.sh docs/CTR/CTR-001.md` |

**Pre-commit Hook Integration:**
```bash
# Automatic validation on git commit
git add docs/SYS/SYS-001.md
git commit -m "Add SYS requirements"
# Output: ✅ Quality gates passed! Ready for next layer transition.
```

### Git Pre-commit Hook Activation

To enable quality gates, the pre-commit hook must be active:

```bash
# Verify hook is active
ls -la .git/hooks/pre-commit
# Should show executable permissions

# If not active, make executable
chmod +x .git/hooks/pre-commit
```

**What Quality Gates Prevent:**
- ✅ Undervalidating artifacts proceeding to next layer
- ✅ Cumulatived traceability tag violations
- ✅ Missing upstream dependencies
- ✅ Regulator Paygrade compliance (SEC, FINRA, FDA, ISO audit requirements)
- ✅ Implications from premature artifacts propagating downstream

### Outcome Metrics

Quality gates provide quantitative measures of framework effectiveness:

- **Maturity Index**: Percentage of artifacts with ≥90% ready scores
- **Traceability Compliance**: Bidirectional linking coverage percentage
- **Development Velocity**: Reduced iteration cycles through early quality validation
- **Regulatory Readiness**: Automated audit trail validation

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/vladm3105/aidoc-flow-framework.git
cd aidoc-flow-framework
```

### 2. Multi-Project Setup (Recommended)

For organizations managing multiple projects with shared framework resources:

```bash
# Setup hybrid shared/custom resources for a project
./scripts/setup_project_hybrid.sh /path/to/your/project

# See detailed documentation:
# - Full guide: MULTI_PROJECT_SETUP_GUIDE.md
# - Quick reference: MULTI_PROJECT_QUICK_REFERENCE.md
```

**Benefits:**
- Single source of truth for skills, templates, and validation scripts
- Zero duplication across projects
- Instant framework updates across all projects
- Project-specific customizations supported

### 3. Explore the Templates

All templates are located in `ai_dev_flow/`:

```bash
cd ai_dev_flow
ls -R
```

### 4. Start Your Project

Choose your entry point based on project context:

**Option A: Greenfield Project (New)**
```bash
# Use project-init skill (if using Claude Code)
# Or manually create directory structure
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS,IPLAN}
```

**Option B: Existing Project**
```bash
# Copy templates to your project
cp -r ai_dev_flow/* your-project/docs/
```

### 5. Follow the Workflow

1. **Business Requirements** → Start with `BRD/BRD-TEMPLATE.md` (Layer 1)
2. **Product Requirements** → Create `PRD/PRD-TEMPLATE.md` (Layer 2)
3. **Formal Requirements** → Use `EARS/EARS-TEMPLATE.md` (Layer 3)
4. **Behavior Tests** → Write `BDD/BDD-TEMPLATE.feature` (Layer 4)
5. **Architecture** → Document with `ADR/ADR-TEMPLATE.md` (Layer 5)
6. **System Design** → Create `SYS/SYS-TEMPLATE.md` (Layer 6)
7. **Atomic Requirements** → Define `REQ/REQ-TEMPLATE.md` (Layer 7)
8. **Implementation Plan** → Organize with `IMPL/IMPL-TEMPLATE.md` (Layer 8 - optional)
9. **API Contracts** → Specify with `CTR/CTR-TEMPLATE.md + .yaml` (Layer 9 - if interfaces)
10. **Technical Specs** → Design with `SPEC/SPEC-TEMPLATE.yaml` (Layer 10)
11. **Code Generation** → Guide with `TASKS/TASKS-TEMPLATE.md` (Layer 11)
12. **Session Planning** → Create `IPLAN/IPLAN-NNN_*.md` (Layer 12 - via /save-plan)
13. **Implementation** → Write code with cumulative traceability tags (Layer 13)

### 6. Add Cumulative Traceability Tags (Recommended)

Embed cumulative tags in your code docstrings (each layer includes ALL upstream tags):

```python
"""Order service implementation.

@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-002:FEATURE-005
@ears: EARS-003:EVENT-001
@bdd: BDD-004:scenario-place-order
@adr: ADR-010
@sys: SYS-008:FUNC-002
@req: REQ-045
@spec: SPEC-003
@tasks: TASKS-015
@impl-status: complete
"""
```

Then validate and auto-generate matrices:

```bash
# Extract tags from codebase
python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate cumulative tagging hierarchy
python ai_dev_flow/scripts/validate_tags_against_docs.py --validate-cumulative --strict

# Generate traceability matrices
python ai_dev_flow/scripts/generate_traceability_matrices.py --auto

# View generated matrices
ls docs/generated/matrices/
```

## Documentation Structure

### 16-Layer Architecture with Cumulative Tagging

The SDD workflow organizes artifacts into 16 distinct layers with cumulative tagging hierarchy:

```
Layer 0: Strategy Layer
└── External strategy documents (product roadmaps, market analysis)

Layer 1: Business Requirements
└── BRD (Business Requirements Documents)

Layer 2: Product Requirements
└── PRD (Product Requirements Documents)

Layer 3: Formal Requirements
└── EARS (Event Analysis Requirements Specification)

Layer 4: Testing Requirements
└── BDD (Behavior-Driven Development - Gherkin scenarios)

Layer 5: Architecture Decisions
└── ADR (Architecture Decision Records)

Layer 6: System Requirements
└── SYS (System Requirements Specifications)

Layer 7: Atomic Requirements
└── REQ (Requirements Specifications)

Layer 8: Project Management [OPTIONAL]
└── IMPL (Implementation Plans)

Layer 9: Interface Contracts [OPTIONAL - IF INTERFACE REQUIREMENT]
└── CTR (API Contracts - dual-file .md + .yaml)

Layer 10: Technical Specifications
└── SPEC (YAML Technical Specifications)

Layer 11: Task Breakdown
└── TASKS (Code Generation Plans)

Layer 12: Session Planning
└── IPLAN (Session-Specific Implementation Plans)

Layer 13: Implementation
└── Code (Source code with cumulative tags)

Layer 14: Testing
└── Tests (Test implementations with cumulative tags)

Layer 15: Validation
└── Validation → Review → Production
```

**Cumulative Tagging**: Each layer includes tags from ALL upstream layers, creating complete audit trails for regulatory compliance.

### Template Categories

#### Business Layer Templates
- **BRD-TEMPLATE.md**: Comprehensive business requirements (general purpose)
- **PRD-TEMPLATE.md**: Product requirements with features and KPIs
- **EARS-TEMPLATE.md**: Formal WHEN-THE-SHALL-WITHIN requirements

#### Architecture Layer Templates
- **ADR-TEMPLATE.md**: Architecture decisions with context and consequences
- **SYS-TEMPLATE.md**: System requirements with functional/non-functional specs

#### Requirements Layer Templates
- **REQ-TEMPLATE.md**: Atomic requirements with acceptance criteria
- **BDD-TEMPLATE.feature**: Gherkin scenarios for behavior validation

#### Implementation Layer Templates
- **IMPL-TEMPLATE.md**: Implementation plans (WHO/WHEN) - project management [Layer 8]
- **CTR-TEMPLATE.md + .yaml**: API contracts (dual-file format) [Layer 9 - optional]
- **SPEC-TEMPLATE.yaml**: Technical specifications (HOW to build) [Layer 10]
- **TASKS-TEMPLATE.md**: Code generation plans (exact TODOs) [Layer 11]
- **IPLAN**: Session-specific implementation plans [Layer 12]

## Traceability System

### Tag-Based Auto-Discovery with Cumulative Tagging (Recommended)

**Principle:** Code is the single source of truth. Each artifact includes tags from ALL upstream layers. Traceability matrices are auto-generated from these cumulative tags.

#### Cumulative Namespaced Tag Format

Embed cumulative tags in code docstrings using namespaced format:

```python
"""Order placement service implementation.

@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-002:FEATURE-005
@ears: EARS-003:EVENT-001
@bdd: BDD-004:scenario-place-order
@adr: ADR-010
@sys: SYS-008:FUNC-002
@req: REQ-045
@spec: SPEC-003
@tasks: TASKS-015
@impl-status: complete
"""
```

**Format:** `@tag-type: DOCUMENT-ID:REQUIREMENT-ID`

**Tag Types (Cumulative Hierarchy):**
- `@brd:` - Business Requirements Document references (Layer 1)
- `@prd:` - Product Requirements Document references (Layer 2)
- `@ears:` - EARS requirements (Layer 3)
- `@bdd:` - BDD test scenarios (Layer 4)
- `@adr:` - Architecture Decision Records (Layer 5)
- `@sys:` - System Requirements references (Layer 6)
- `@req:` - Atomic Requirements (Layer 7)
- `@impl:` - Implementation Plans (Layer 8 - optional)
- `@ctr:` - API Contracts (Layer 9 - optional)
- `@spec:` - Technical Specifications (Layer 10)
- `@tasks:` - Task breakdowns (Layer 11)
- `@impl-status:` - Implementation status (pending|in-progress|complete|deprecated)

**Benefits:**
- ✅ Complete audit trail from strategy to code
- ✅ Regulatory compliance (SEC, FINRA, FDA, ISO)
- ✅ Impact analysis (identify all affected artifacts)
- ✅ Automated cumulative validation (scripts enforce hierarchy)
- ✅ No sync drift (tags can't become stale)
- ✅ Bidirectional matrices auto-generated
- ✅ CI/CD enforceable (pre-commit hooks)

**Why Cumulative?**
- Each layer N includes tags from layers 1 through N-1
- Complete traceability chain from business requirements to implementation
- Instant impact analysis when upstream requirements change

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

> **Note**: Path examples above use relative paths within a project structure. Adjust paths based on your project's directory organization.

**Migration:** New projects should use tag-based approach. Existing projects can migrate gradually.

### ID Naming Standards

**SCOPE**: These standards apply ONLY to **documentation artifacts**, NOT source code.

#### ✅ Apply To:
- Documentation files in `docs/` directories (BRD, PRD, REQ, ADR, SPEC, CTR, etc.)
- BDD feature files (`.feature`) in test directories

#### ❌ Do NOT Apply To:
- **Source code files**: Follow language-specific conventions (PEP 8 for Python, etc.)
- **Test files**: Follow testing framework conventions (pytest, Jest, JUnit, etc.)

All documentation follows standardized ID formats:

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
python ai_dev_flow/scripts/validate_tags_against_docs.py --strict
```

**Step 4: Generate Matrices**
```bash
# Auto-generate bidirectional matrices
python ai_dev_flow/scripts/generate_traceability_matrices.py --auto
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

### Cumulative Tag Automation (v2.0 - Recommended)

**Validation Scripts Location**: `ai_dev_flow/scripts/` (copy to your project or use directly from framework)

```bash
# Extract cumulative tags from all source files
python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate cumulative tagging hierarchy (ENFORCES all upstream tags present)
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --source src/ docs/ tests/ \
  --validate-cumulative \
  --strict

# Generate bidirectional traceability matrices
python ai_dev_flow/scripts/generate_traceability_matrices.py --auto

# Complete workflow (extract + validate cumulative + generate)
python ai_dev_flow/scripts/generate_traceability_matrices.py --auto
```

**CI/CD Integration:**
```yaml
# .github/workflows/traceability.yml
- name: Validate Cumulative Tagging Hierarchy
  run: |
    python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json
    python ai_dev_flow/scripts/validate_tags_against_docs.py --validate-cumulative --strict
```

### Legacy Validation Scripts

For projects using traditional Section 7:

```bash
# Validate requirement IDs and format
python ai_dev_flow/scripts/validate_requirement_ids.py

# Validate traceability matrices
python ai_dev_flow/scripts/validate_traceability_matrix.py --matrix path/to/matrix.md --input path/to/docs/

# Update traceability matrices incrementally
python ai_dev_flow/scripts/update_traceability_matrix.py --matrix path/to/matrix.md --input path/to/docs/

# Validate IPLAN naming conventions
python ai_dev_flow/scripts/validate_iplan_naming.py
```

### Quality Gates

Pre-commit checklist:

**Cumulative Tagging Projects (v2.0):**
- [ ] All artifacts include cumulative tags from ALL upstream layers
- [ ] Tags use namespaced format (DOCUMENT-ID:REQUIREMENT-ID)
- [ ] Tag extraction successful: `python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/`
- [ ] Cumulative validation passes: `python ai_dev_flow/scripts/validate_tags_against_docs.py --validate-cumulative --strict`
- [ ] No gaps in cumulative tag chains (e.g., if @adr exists, @brd through @bdd must exist)
- [ ] Traceability matrices generated: `python ai_dev_flow/scripts/generate_traceability_matrices.py --auto`
- [ ] Implementation status tags present (@impl-status: complete|in-progress|pending)
- [ ] IPLAN files follow naming convention: `IPLAN-NNN_slug_YYYYMMDD_HHMMSS.md`

**Traditional Projects (Legacy):**
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
- [ ] Layer numbering correct (0-15, not simplified diagram labels)

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
aidoc-flow-framework/
├── README.md                          # This file
├── MULTI_PROJECT_SETUP_GUIDE.md       # Multi-project hybrid setup guide
├── MULTI_PROJECT_QUICK_REFERENCE.md   # Quick reference for common multi-project tasks
├── ai_dev_flow/                       # Template system (v2.0)
│   ├── index.md                       # Workflow overview with Mermaid diagram
│   ├── README.md                      # Framework documentation
│   ├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  # Authoritative SDD methodology
│   ├── ID_NAMING_STANDARDS.md         # Document ID format rules
│   ├── TRACEABILITY.md                # Cumulative tagging hierarchy
│   ├── TRACEABILITY_SETUP.md          # Validation setup and CI/CD integration
│   ├── TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md  # Complete matrix template
│   ├── COMPLETE_TAGGING_EXAMPLE.md    # End-to-end cumulative tagging example
│   ├── DOMAIN_ADAPTATION_GUIDE.md     # Domain customization guide
│   ├── CONTRACT_DECISION_QUESTIONNAIRE.md  # CTR decision guide
│   ├── WHEN_TO_CREATE_IMPL.md         # IMPL decision guide
│   ├── TOOL_OPTIMIZATION_GUIDE.md     # AI tool optimization
│   ├── AI_ASSISTANT_RULES.md          # Rules for AI assistants
│   ├── PROJECT_SETUP_GUIDE.md         # Single-project setup guide
│   ├── PROJECT_KICKOFF_TASKS.md       # Project initialization checklist
│   ├── QUICK_REFERENCE.md             # Quick reference guide
│   ├── BRD/                           # Business requirements templates (Layer 1)
│   ├── PRD/                           # Product requirements templates (Layer 2)
│   ├── EARS/                          # Formal requirements templates (Layer 3)
│   ├── BDD/                           # Behavior-driven test templates (Layer 4)
│   ├── ADR/                           # Architecture decision templates (Layer 5)
│   ├── SYS/                           # System requirements templates (Layer 6)
│   ├── REQ/                           # Atomic requirements templates (Layer 7)
│   ├── IMPL/                          # Implementation plan templates (Layer 8)
│   ├── CTR/                           # API contract templates - dual-file (Layer 9)
│   ├── SPEC/                          # Technical specification templates (Layer 10)
│   ├── TASKS/                         # Code generation templates (Layer 11)
│   ├── IPLAN/                         # Session planning templates (Layer 12)
│   └── scripts/                       # Validation and automation scripts
│       ├── extract_tags.py            # Extract tags from codebase
│       ├── validate_tags_against_docs.py  # Validate cumulative tagging
│       ├── generate_traceability_matrices.py  # Generate matrices
│       ├── generate_traceability_matrix.py    # Generate single matrix (legacy)
│       ├── validate_traceability_matrix.py    # Validate matrix (legacy)
│       ├── update_traceability_matrix.py      # Update matrix (legacy)
│       ├── validate_iplan_naming.py   # Validate IPLAN naming conventions
│       ├── validate_requirement_ids.py  # Validate requirement ID format
│       ├── add_cumulative_tagging_to_matrices.py  # Update templates
│       ├── batch_update_matrix_templates.py  # Batch update templates
│       ├── make_framework_generic.py  # Placeholder maintenance
│       └── README.md                  # Scripts documentation
├── scripts/                           # Project setup scripts (root level)
│   ├── setup_project_hybrid.sh        # Automated hybrid project setup
│   └── standardize_workflow_refs.sh   # Standardize workflow references
├── work_plans/                        # Implementation plans (IPLAN output)
└── docs/                              # Additional documentation
```

## Example Workflow

### Complete Artifact Chain with Cumulative Tagging

```
Layer 0: Strategy Document (no tags)
    ↓
Layer 1: BRD-001: Business Requirements
    ↓
Layer 2: PRD-001: Product Requirements (@brd)
    ↓
Layer 3: EARS-001: Formal Requirements (@brd, @prd)
    ↓
Layer 4: BDD-001: Behavior Tests (@brd, @prd, @ears)
    ↓
Layer 5: ADR-001: Architecture Decision (@brd→@bdd)
    ↓
Layer 6: SYS-001: System Requirements (@brd→@adr)
    ↓
Layer 7: REQ-001: Atomic Requirement (@brd→@sys)
    ↓
Layer 8: IMPL-001: Implementation Plan [OPTIONAL] (@brd→@req)
    ↓
Layer 9: CTR-001: API Contract (.md + .yaml) [IF INTERFACE] (@brd→@impl)
    ↓
Layer 10: SPEC-001: Technical Specification (YAML) (@brd→@req + optional impl/ctr)
    ↓
Layer 11: TASKS-001: Code Generation Plan (@brd→@spec)
    ↓
Layer 12: IPLAN-001: Session Plan (@brd→@tasks)
    ↓
Layer 13: Code Implementation (cumulative tags @brd→@tasks)
    ↓
Layer 14: Test Suite (cumulative tags @brd→@code)
    ↓
Layer 15: Production Validation (all upstream tags)
```

**Each layer includes ALL upstream tags** for complete audit trail and regulatory compliance.

## Use Cases

### Financial Trading Systems
- Use `BRD-TEMPLATE.md` with domain-specific customization
- Example: Options trading strategy implementation
- Full traceability from strategy documents to production code

### General Software Projects
- Use `BRD-TEMPLATE.md` for comprehensive business requirements
- Customize based on project complexity using domain adaptation guide
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
- [Traceability](./ai_dev_flow/TRACEABILITY.md) - Cumulative tagging hierarchy
- [Traceability Setup](./ai_dev_flow/TRACEABILITY_SETUP.md) - Validation automation and CI/CD integration
- [Complete Tagging Example](./ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md) - End-to-end cumulative tagging
- [Traceability Matrix Template](./ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md) - Complete matrix examples

### Multi-Project Setup
- [Multi-Project Setup Guide](./MULTI_PROJECT_SETUP_GUIDE.md) - Complete hybrid approach documentation
- [Quick Reference](./MULTI_PROJECT_QUICK_REFERENCE.md) - Common commands and patterns
- Setup Script: `scripts/setup_project_hybrid.sh` - Automated project configuration

### Decision Guides
- [When to Create IMPL](./ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL vs direct REQ→SPEC
- [CTR Policy](./ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - Dual-file format

### AI Tool Optimization
- [Tool Optimization Guide](./ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md) - Claude Code, Gemini, Copilot

### Validation Scripts (v2.0)
- `ai_dev_flow/scripts/extract_tags.py` - Extract @tags from source files
- `ai_dev_flow/scripts/validate_tags_against_docs.py` - Validate cumulative tagging hierarchy (use `--validate-cumulative`)
- `ai_dev_flow/scripts/generate_traceability_matrices.py` - Generate bidirectional matrices
- `ai_dev_flow/scripts/generate_traceability_matrix.py` - Generate single matrix (legacy)
- `ai_dev_flow/scripts/validate_traceability_matrix.py` - Validate matrix (legacy)
- `ai_dev_flow/scripts/update_traceability_matrix.py` - Update matrix (legacy)
- `ai_dev_flow/scripts/add_cumulative_tagging_to_matrices.py` - Update matrix templates with cumulative sections
- `ai_dev_flow/scripts/validate_iplan_naming.py` - Validate IPLAN naming conventions
- `ai_dev_flow/scripts/validate_requirement_ids.py` - Validate ID format (legacy + tags)
- `ai_dev_flow/scripts/README.md` - Complete scripts documentation

### Project Setup Scripts
- `scripts/setup_project_hybrid.sh` - Automated multi-project hybrid setup

## Support

- **Issues**: [GitHub Issues](https://github.com/vladm3105/aidoc-flow-framework/issues)
- **Documentation**: [ai_dev_flow/](./ai_dev_flow/)
- **Examples**: See `ai_dev_flow/*/examples/` directories

## Acknowledgments

Developed for AI-assisted software engineering workflows optimized for:
- Claude Code (Anthropic)
- Gemini CLI (Google)
- GitHub Copilot (Microsoft)

---

**Version**: 2.0
**Last Updated**: 2025-11-13
**Maintained by**: Vladimir M.

## Changelog

### Version 2.0 (2025-11-13) - Cumulative Tagging Hierarchy
- ✅ **16-Layer Architecture**: Expanded from 10 to 16 layers (Strategy → Validation)
- ✅ **Cumulative Tagging System**: Each artifact includes tags from ALL upstream layers
- ✅ **Automated Validation**: Enhanced scripts enforce cumulative tagging compliance
  - `extract_tags.py` - Extract tags from codebase
  - `validate_tags_against_docs.py` - Validate cumulative hierarchy with `--validate-cumulative`
  - `generate_traceability_matrices.py` - Auto-generate bidirectional matrices
- ✅ **Traceability Matrix Templates**: All 13 artifact types include cumulative tagging sections
- ✅ **Complete Documentation**:
  - `COMPLETE_TAGGING_EXAMPLE.md` - End-to-end cumulative tagging example
  - `TRACEABILITY_SETUP.md` - Setup guide with CI/CD integration
  - `DOMAIN_ADAPTATION_GUIDE.md` - Domain customization checklists
- ✅ **Layer 12 (IPLAN)**: Session-specific implementation plans (`IPLAN-NNN_*_YYYYMMDD_HHMMSS.md`)
- ✅ **Directory Updates**: CONTRACTS → CTR (dual-file format), TASKS_PLANS → IPLAN
- ✅ **Regulatory Compliance**: Complete audit trails for SEC, FINRA, FDA, ISO
- ✅ **Impact Analysis**: Instant identification of affected downstream artifacts

### Version 1.1.0 (2025-11-12)
- Added tag-based auto-discovery traceability system
- Introduced namespaced tag format (DOCUMENT-ID:REQUIREMENT-ID)
- Added automated validation scripts
- Updated quality gates for tag-based and traditional projects
- Added CI/CD integration examples for traceability validation
- Legacy Section 7 approach still supported during migration

### Version 1.0.0 (2025-11-09)
- Initial release with 10-layer SDD workflow
- Complete template system for all artifact types
- Traditional Section 7 traceability
