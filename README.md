# AI Dev Flow Framework
# AI Dev Flow Framework

**Specification-Driven Development (SDD) Template System for AI-Assisted Software Engineering**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

## Overview

The AI Dev Flow Framework is a comprehensive template system for implementing AI-Driven Specification-Driven Development (SDD). It provides structured workflows, document templates, and traceability mechanisms to transform business requirements into production-ready code through a systematic, traceable approach optimized for AI-assisted development.

> MVP Note: When using the MVP track, all artifacts are single, flat files. Do not use document splitting or `DOCUMENT_SPLITTING_RULES.md`.

## Automation Philosophy: Maximum Velocity to Production

**PRIMARY GOAL: Fastest Transition from Business Idea to Production MVP**

AI Dev Flow eliminates manual bottlenecks through intelligent automation and strategic human oversight.

**Automation Capabilities**:
- **Quality-Gated Automation**: Replace mandatory checkpoints with AI-scored quality validation
  - Auto-approve if quality score ≥ threshold (90-95%)
  - Human review only if score fails
  - Result: Up to 93% automation (12 of 13 production layers)
- **AI Code Generation**: YAML specs → Production-ready code
- **Auto-Fix Testing**: 3 retry attempts reduce manual debugging
- **Strategic Checkpoints**: Only 5 critical decisions need human approval if quality score < threshold (90%)
- **Continuous Pipeline**: Automated validation, security scanning, deployment builds

**Human-in-the-Loop Checkpoints** (Quality Gates):

| Layer | Checkpoint | Why Human Review? |
|-------|------------|------------------|
| L1 (BRD) | Business owner approves | Strategic business alignment |
| L2 (PRD) | Product manager approves | Product vision validation |
| L5 (ADR) | Architect approves | Technical architecture decisions |
| L11 (Code) | Developer reviews | Code quality and security |
| L13 (Deployment) | Ops approves | Production release gating |

**Automated Layers** (No human intervention required):
- L3 (EARS), L4 (BDD), L6 (SYS), L7 (REQ), L8 (CTR), L9 (SPEC), L10 (TASKS), L12 (Tests)

**Result**: Dramatically reduced manual effort while maintaining quality through strategic oversight.

## MVP Delivery Loop: Iterative Product Development

AI Dev Flow supports **continuous product evolution** through iterative MVP cycles:

**The Delivery Loop**:
```
┌─────────────────────────────────────────────────┐
│ MVP v1.0 → Defect Fixes → Production Release   │
│     ↓                                           │
│ MVP v2.0 (Add Features) ← Market Feedback       │
│     ↓                                           │
│ Defect Fixes → Production                       │
│     ↓                                           │
│ MVP v3.0 (Add Features) ← ...                   │
└─────────────────────────────────────────────────┘
```

**Key Benefits**:
- **Rapid Iteration**: Complete L1-L13 pipeline with 90% automation
- **Incremental Features**: Add features as new MVPs, preserve working product
- **Production Focus**: Every MVP targets production deployment
- **Cumulative Traceability**: Each MVP inherits and extends previous version's artifacts

**How Automation Enables the Loop**:

| Stage | Automation Support |
|-------|-------------------|
| **Build MVP v1.0** | Full L1-L13 automation (90% automated) |
| **Fix Defects** | Auto-retry testing (3x), auto-fix capabilities |
| **Deploy to Production** | Automated build, validation, security scans |
| **Add Features (MVP v2.0)** | Reuse or create new BRD/PRD/ADR, auto-generate new REQ→CODE |
| **Iterate** | Cumulative tags enable impact analysis |

**MVP Evolution Example**:
- **MVP 1.0**: User authentication → Production
- **Defect Fixes**: Password reset bugs → Production
- **MVP 2.0**: Add social login (Google, GitHub) → Production
- **MVP 3.0**: Add 2FA and session management → Production

Each cycle leverages automation to maintain velocity while ensuring quality through human checkpoints.

## Default Template Selection (MVP is Default)

**MVP templates are the framework default** for all new document creation. Full templates are available for enterprise/regulatory projects.

### Available MVP Templates (Layers 1-7)
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

### Triggering Full Templates

When full documentation is required, trigger full templates using:

**Method 1 - Project Settings** (in `.autopilot.yaml` or `CLAUDE.md`):
```yaml
template_profile: enterprise  # or "full" or "strict"
```

**Method 2 - Prompt Keywords** (include in your request):
- "use full template"
- "use enterprise template"
- "enterprise mode"
- "full documentation"
- "comprehensive template"
- "regulatory compliance"

### Key Features

- **90%+ Automation**: 12 of 13 production layers generate automatically with quality gates
- **Strategic Human Oversight**: Only 5 critical checkpoints require human approval (if quality score < 90%)
- **Code-from-Specs**: Direct YAML-to-Python code generation from technical specifications
- **Auto-Fix Testing**: Failing tests trigger automatic code corrections (max 3 retries)
- **Continuous Delivery Loop**: MVP → Defects → Production → Next MVP rapid iteration
- **15-Layer Architecture**: Structured progression from strategy to validation (Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → Code → Tests → Validation)
- **Cumulative Tagging Hierarchy**: Each artifact includes tags from ALL upstream layers for complete audit trails
- **REQ v3.0 Support**: Enhanced REQ templates with sections 3-7 (interfaces/schemas/errors/config/quality attributes) for ≥90% SPEC-readiness
- **Tag-Based Auto-Discovery**: Lightweight @tags in code auto-generate bidirectional traceability matrices
- **Namespaced Traceability**: Unified `TYPE.NN.TT.SS` format (e.g., `BRD.01.01.30`) prevents ambiguity
- **Complete Traceability**: Bidirectional links between all artifacts (business → architecture → code)
- **AI-Optimized Templates**: Ready for Claude Code, Gemini, GitHub Copilot, and other AI coding assistants
- **Domain-Agnostic**: Adaptable to any software domain (finance, healthcare, e-commerce, SaaS, IoT)
- **Token-Efficient Design**: Optimized for AI tool context windows (50K-100K tokens per document)
- **Dual-File Contracts**: CTR uses `.md` (human) + `.yaml` (machine) for parallel development
- **Automated Validation**: Scripts for tag extraction, cumulative tagging validation, and matrix generation with CI/CD integration
- **Regulatory Compliance**: Complete audit trails meet SEC, FINRA, FDA, ISO requirements

## 🤖 Agent Swarm Integration (.aidev)

The framework now includes a native **Agent Orchestration System** located in `.aidev/`. This system implements the **BMAD Methodology**, deploying a swarm of 16 specialized AI agents (using Claude Code, Gemini, and Codex) to autonomously generate and validate the documentation artifacts.

### Key Capabilities
*   **16-Layer Swarm**: A dedicated agent role for every layer (e.g., `product-manager` for PRDs, `architect` for ADRs).
*   **Adversarial Pair Architecture**: Every step is executed by one model (e.g., Gemini) and reviewed by another (e.g., Claude) to minimize hallucinations.
*   **CLI-First**: Designed to work with standard CLI tools (`claude`, `gemini`, `codex`).

👉 **[Get Started with the Agent Swarm](.aidev/README.md)**

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
git clone https://github.com/[YOUR_ORG]/ai-dev-flow-framework.git
cd ai-dev-flow-framework
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

## Automation Capabilities

### What Gets Automated

| Capability | Status | Description |
|------------|--------|-------------|
| Document Generation | ✅ 90% | 12 layers auto-generate from upstream |
| Code Generation | ✅ Full | SPEC+TASKS → Production Python code |
| Test Generation | ✅ Full | BDD scenarios → pytest test suites |
| Test Execution | ✅ Full | Unit + Integration + BDD with auto-retry |
| Traceability | ✅ Full | Automated tag extraction and matrix generation |
| Validation | ✅ Full | Contract compliance, security scans, coverage |
| Deployment | ⚠️ Partial | Automated build, optional human-approved deployment |

### What Requires Human Review

- **Business decisions** (BRD, PRD) - Optional if quality score ≥90%
- **Architecture decisions** (ADR) - Optional if quality score ≥90%
- **Code quality** (before testing) - Optional if quality score ≥90%
- **Production deployment** (final gate) - Optional if quality score ≥90%

**Philosophy**: Automate repetitive work, preserve human judgment for critical decisions.

### 3. Explore the Templates

All templates are located in `ai_dev_flow/`:

```bash
cd ai_dev_flow
ls -R
```

### 4. Start Your Project

Choose your entry point based on project context. For new documents, prefer the `-MVP-TEMPLATE` variants (e.g., `BRD/BRD-MVP-TEMPLATE.md`, `PRD/PRD-MVP-TEMPLATE.md`, `ADR/ADR-MVP-TEMPLATE.md`). Use full templates for complex/regulatory projects.

**Option A: Greenfield Project (New)**
```bash
# Use project-init skill (if using Claude Code)
# Or manually create directory structure
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS}
```

**Option B: Existing Project**
```bash
# Copy templates to your project
cp -r ai_dev_flow/* your-project/docs/
```

### 5. Follow the Workflow

1. **Business Requirements** → Start with `BRD/BRD-MVP-TEMPLATE.md` (or full `BRD-TEMPLATE.md`)
2. **Product Requirements** → Create `PRD/PRD-MVP-TEMPLATE.md` (or full `PRD-TEMPLATE.md`)
3. **Formal Requirements** → Use `EARS/EARS-MVP-TEMPLATE.md` (or full `EARS-TEMPLATE.md`)
4. **Behavior Tests** → Write `BDD/BDD-MVP-TEMPLATE.feature` (or full `BDD-TEMPLATE.feature`)
5. **Architecture** → Document with `ADR/ADR-MVP-TEMPLATE.md` (or full `ADR-TEMPLATE.md`)
6. **System Design** → Create `SYS/SYS-MVP-TEMPLATE.md` (or full `SYS-TEMPLATE.md`)
7. **Atomic Requirements** → Define `REQ/REQ-MVP-TEMPLATE.md` (or full `REQ-TEMPLATE.md`)
8. **Implementation Plan** → Organize with `IMPL/IMPL-TEMPLATE.md` (Layer 8 - optional)
9. **API Contracts** → Specify with `CTR/CTR-TEMPLATE.md + .yaml` (Layer 9 - if interfaces)
10. **Technical Specs** → Design with `SPEC/SPEC-TEMPLATE.yaml` (Layer 10)
11. **Code Generation** → Guide with `TASKS/TASKS-TEMPLATE.md` (Layer 11)
12. **Implementation** → Write code with cumulative traceability tags (Layer 12)

### 6. Add Cumulative Traceability Tags (Recommended)

Embed cumulative tags in your code docstrings (each layer includes ALL upstream tags):

```python
"""Order service implementation.

@brd: BRD.01.01.30, BRD.01.01.06
@prd: PRD.02.07.05
@ears: EARS.03.24.01
@bdd: BDD.04.13.01
@adr: ADR-010
@sys: SYS.08.25.02
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

Layer 12: Implementation
└── Code (Source code with cumulative tags)

Layer 13: Testing
└── Tests (Test implementations with cumulative tags)

Layer 14: Validation
└── Validation → Review → Production
```

**Cumulative Tagging**: Each layer includes tags from ALL upstream layers, creating complete audit trails for regulatory compliance.

### Complete Automation Pipeline

The framework supports full automation from requirements to production:

**Phase 1: Business Input** → Human provides initial requirements

**Phase 2: Document Generation (L1-L10)**
- Human review (optional if quality score ≥90%): BRD, PRD, ADR
- Auto-generates: EARS, BDD, SYS, REQ, CTR, SPEC, TASKS
- Quality gates ensure each layer meets 90% readiness before proceeding

**Phase 3: Code Generation (L11)**
- AI generates code from SPEC + TASKS + CTR
- Validates contract compliance and traceability
- Human reviews before testing (optional if quality score ≥90%)

**Phase 4: Test Execution (L12)**
- Auto-generates tests from BDD scenarios
- Runs unit, integration, and behavioral tests
- Auto-fix with max 3 retries
- Enforces 80% coverage minimum

**Phase 5: Validation & Deployment (L13)**
- Tag validation and traceability matrix generation
- Security scanning (bandit, safety)
- Build artifacts
- Human approves deployment to production (optional if quality score ≥90%)

See [SDD_AUTOMATION_WORKFLOW.md](./ai_dev_flow/SDD_AUTOMATION_WORKFLOW.md) for complete automation playbook.

### Template Categories

#### Business Layer Templates
- **BRD-TEMPLATE.md**: Comprehensive business requirements (general purpose)
- **PRD-TEMPLATE.md**: Product requirements with features and KPIs
- **EARS-TEMPLATE.md**: Formal WHEN-THE-SHALL-WITHIN requirements

#### Architecture Layer Templates
- **ADR-TEMPLATE.md**: Architecture decisions with context and consequences
- **SYS-TEMPLATE.md**: System requirements with functional requirements and quality attributes

#### Requirements Layer Templates
- **REQ-TEMPLATE.md**: Atomic requirements with acceptance criteria
- **BDD-TEMPLATE.feature**: Gherkin scenarios for behavior validation

#### Implementation Layer Templates
- **IMPL-TEMPLATE.md**: Implementation plans (WHO/WHEN) - project management [Layer 8]
- **CTR-TEMPLATE.md + .yaml**: API contracts (dual-file format) [Layer 9 - optional]
- **SPEC-TEMPLATE.yaml**: Technical specifications (HOW to build) [Layer 10]
- **TASKS-TEMPLATE.md**: Code generation plans (exact TODOs) [Layer 11]

## Traceability System

### Tag-Based Auto-Discovery with Cumulative Tagging (Recommended)

**Principle:** Code is the single source of truth. Each artifact includes tags from ALL upstream layers. Traceability matrices are auto-generated from these cumulative tags.

#### Cumulative Namespaced Tag Format

Embed cumulative tags in code docstrings using namespaced format:

```python
"""Order placement service implementation.

@brd: BRD.01.01.30, BRD.01.01.06
@prd: PRD.02.07.05
@ears: EARS.03.24.01
@bdd: BDD.04.13.01
@adr: ADR-010
@sys: SYS.08.25.02
@req: REQ-045
@spec: SPEC-003
@tasks: TASKS-015
@impl-status: complete
"""
```

**Format:** `@tag-type: TYPE.NN.TT.SS` (e.g., `@brd: BRD.01.01.30`)

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

**Why Unified Format?**
- `@brd: BRD.30` ❌ Ambiguous (which BRD document?)
- `@brd: BRD-001:30` ❌ Old format (deprecated)
- `@brd: BRD.01.01.30` ✅ Unified format (current standard)

#### Traditional Section 7 (Legacy)

Manual traceability sections in documents remain supported during migration:

```markdown
## 7. Traceability

**Upstream:**
- [BRD-001](../BRD/BRD-001_requirements.md#BRD.01.01.30)

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
| BRD.01.01.30 | src/services/account.py:12 | ✓ Complete |
```

**Reverse Matrix Example:**
```markdown
| Source File | Requirements | Status |
|-------------|-------------|--------|
| src/services/account.py | BRD.01.01.30, SYS.01.25.06 | Complete |
```

### Migration Guide: Section 7 → Tags

**Step 1: Add Tags to New Code**
```python
# Start with new implementations
"""New feature implementation.

@brd: BRD.001.045
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

- `CTR-001_api_contract.md` - Human-readable context, error handling, quality attributes
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

```

### Quality Gates

Pre-commit checklist:

**Cumulative Tagging Projects (v2.0):**
- [ ] All artifacts include cumulative tags from ALL upstream layers
- [ ] Tags use unified format (TYPE.NN.TT.SS)
- [ ] Tag extraction successful: `python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/`
- [ ] Cumulative validation passes: `python ai_dev_flow/scripts/validate_tags_against_docs.py --validate-cumulative --strict`
- [ ] No gaps in cumulative tag chains (e.g., if @adr exists, @brd through @bdd must exist)
- [ ] Traceability matrices generated: `python ai_dev_flow/scripts/generate_traceability_matrices.py --auto`
- [ ] Implementation status tags present (@impl-status: complete|in-progress|pending)

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
├── ai_dev_flow/                       # Template system (v2.2)
│   ├── index.md                       # Workflow overview with Mermaid diagram
│   ├── README.md                      # Framework documentation
│   ├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  # Authoritative SDD methodology
│   ├── ID_NAMING_STANDARDS.md         # Document ID format rules
│   ├── THRESHOLD_NAMING_RULES.md      # Threshold and limit naming standards
│   ├── TRACEABILITY.md                # Cumulative tagging hierarchy
│   ├── TRACEABILITY_SETUP.md          # Validation setup and CI/CD integration
│   ├── TRACEABILITY_VALIDATION.md     # Validation procedures
│   ├── TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md  # Complete matrix template
│   ├── COMPLETE_TAGGING_EXAMPLE.md    # End-to-end cumulative tagging example
│   ├── DOMAIN_ADAPTATION_GUIDE.md     # Domain customization guide
│   ├── DOMAIN_SELECTION_QUESTIONNAIRE.md  # Domain selection tool
│   ├── FINANCIAL_DOMAIN_CONFIG.md     # Financial sector configuration
│   ├── SOFTWARE_DOMAIN_CONFIG.md      # Generic software configuration
│   ├── GENERIC_DOMAIN_CONFIG.md       # Minimal configuration template
│   ├── CONTRACT_DECISION_QUESTIONNAIRE.md  # CTR decision guide
│   ├── WHEN_TO_CREATE_IMPL.md         # IMPL decision guide
│   ├── PLATFORM_VS_FEATURE_BRD.md     # BRD type selection guide
│   ├── TOOL_OPTIMIZATION_GUIDE.md     # AI tool optimization
│   ├── AI_ASSISTANT_RULES.md          # Rules for AI assistants
│   ├── PROJECT_SETUP_GUIDE.md         # Single-project setup guide
│   ├── PROJECT_KICKOFF_TASKS.md       # Project initialization checklist
│   ├── QUICK_REFERENCE.md             # Quick reference guide
│   ├── MATRIX_TEMPLATE_COMPLETION_GUIDE.md  # How to fill traceability matrices
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
│   └── scripts/                       # Validation and automation scripts
│       ├── extract_tags.py            # Extract tags from codebase
│       ├── validate_tags_against_docs.py  # Validate cumulative tagging
│       ├── generate_traceability_matrices.py  # Generate matrices
│       ├── generate_traceability_matrix.py    # Generate single matrix
│       ├── validate_traceability_matrix.py    # Validate matrix structure
│       ├── validate_traceability_matrix_enforcement.py  # Matrix enforcement
│       ├── update_traceability_matrix.py      # Update existing matrices
│       ├── validate_requirement_ids.py  # Validate REQ-ID format
│       ├── validate_req_spec_readiness.py  # REQ SPEC-readiness scoring
│       ├── validate_documentation_paths.py  # Path consistency validation
│       ├── validate_links.py          # Markdown link validation
│       ├── validate_brd_template.sh   # BRD template compliance
│       ├── validate_req_template.sh   # REQ template compliance
│       └── README.md                  # Complete scripts documentation
├── scripts/                           # Project setup scripts (root level)
│   ├── setup_project_hybrid.sh        # Automated hybrid project setup
│   └── standardize_workflow_refs.sh   # Standardize workflow references
├── work_plans/                        # Implementation plans
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
Layer 12: Code Implementation (cumulative tags @brd→@tasks)
    ↓
Layer 13: Test Suite (cumulative tags @brd→@code)
    ↓
Layer 14: Production Validation (all upstream tags)
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

## Automation & Workflow

**MVP Autopilot Guide**:
- [AUTOPILOT/MVP_AUTOPILOT.md](./AUTOPILOT/MVP_AUTOPILOT.md) - Complete automation guide for MVP workflow
- [AUTOPILOT/MVP_GITHUB_CICD_INTEGRATION_PLAN.md](./AUTOPILOT/MVP_GITHUB_CICD_INTEGRATION_PLAN.md) - CI/CD integration plan
- [AUTOPILOT/MVP_PIPELINE_END_TO_END_USER_GUIDE.md](./AUTOPILOT/MVP_PIPELINE_END_TO_END_USER_GUIDE.md) - End-to-end user guide

**Configuration**:
- [AUTOPILOT/config/default.yaml](./AUTOPILOT/config/default.yaml) - Default configuration
- [AUTOPILOT/config/quality_gates.yaml](./AUTOPILOT/config/quality_gates.yaml) - Quality gate settings

**Scripts**:
- [AUTOPILOT/scripts/mvp_autopilot.py](./AUTOPILOT/scripts/mvp_autopilot.py) - Main orchestration script
- [AUTOPILOT/scripts/validate_metadata.py](./AUTOPILOT/scripts/validate_metadata.py) - Metadata validator
- [AUTOPILOT/scripts/validate_quality_gates.py](./AUTOPILOT/scripts/validate_quality_gates.py) - Quality gate checker (Python)
- [AUTOPILOT/scripts/validate_quality_gates.sh](./AUTOPILOT/scripts/validate_quality_gates.sh) - Quality gate validator (shell)

**Makefile**:
- [Makefile](./Makefile) - Standardized commands for common operations

**Docker Support**:
- [Dockerfile](./Dockerfile) - Docker configuration
- [docker-compose.yml](./docker-compose.yml) - Docker Compose setup

**Quick Start**:

```bash
# Local development
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root . \
  --intent "My MVP" \
  --slug my_mvp \
  --auto-fix \
  --report markdown

# GitHub Actions
make docs  # Runs mvp-autopilot.yml workflow
```

---
## License

MIT License - See LICENSE file for details

## References

### Core Documentation
- [Workflow Guide](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [Index](./ai_dev_flow/index.md) - Template overview with workflow diagram
- [Quick Reference](./ai_dev_flow/QUICK_REFERENCE.md) - Quick reference for common tasks
- [ID Standards](./ai_dev_flow/ID_NAMING_STANDARDS.md) - Naming conventions
- [Threshold Naming Rules](./ai_dev_flow/THRESHOLD_NAMING_RULES.md) - Threshold and limit naming standards
- [Traceability](./ai_dev_flow/TRACEABILITY.md) - Cumulative tagging hierarchy
- [Traceability Setup](./ai_dev_flow/TRACEABILITY_SETUP.md) - Validation automation and CI/CD integration
- [Traceability Validation](./ai_dev_flow/TRACEABILITY_VALIDATION.md) - Validation procedures
- [Complete Tagging Example](./ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md) - End-to-end cumulative tagging
- [Traceability Matrix Template](./ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md) - Complete matrix examples
- [Matrix Completion Guide](./ai_dev_flow/MATRIX_TEMPLATE_COMPLETION_GUIDE.md) - How to fill matrices

### Multi-Project Setup
- [Multi-Project Setup Guide](./MULTI_PROJECT_SETUP_GUIDE.md) - Complete hybrid approach documentation
- [Quick Reference](./MULTI_PROJECT_QUICK_REFERENCE.md) - Common commands and patterns
- Setup Script: `scripts/setup_project_hybrid.sh` - Automated project configuration

### Domain Adaptation
- [Domain Adaptation Guide](./ai_dev_flow/DOMAIN_ADAPTATION_GUIDE.md) - Adapting framework to specific domains
- [Domain Selection Questionnaire](./ai_dev_flow/DOMAIN_SELECTION_QUESTIONNAIRE.md) - Domain selection tool
- [Financial Domain Config](./ai_dev_flow/FINANCIAL_DOMAIN_CONFIG.md) - Financial sector configuration
- [Software Domain Config](./ai_dev_flow/SOFTWARE_DOMAIN_CONFIG.md) - Generic software configuration
- [Generic Domain Config](./ai_dev_flow/GENERIC_DOMAIN_CONFIG.md) - Minimal configuration template

### Decision Guides
- [When to Create IMPL](./ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL vs direct REQ→SPEC
- [Contract Decision Questionnaire](./ai_dev_flow/CONTRACT_DECISION_QUESTIONNAIRE.md) - When to create CTR
- [Platform vs Feature BRD](./ai_dev_flow/PLATFORM_VS_FEATURE_BRD.md) - BRD type selection
- [CTR Policy](./ai_dev_flow/ADR/ADR-CTR_SEPARATE_FILES_POLICY.md) - Dual-file format

### AI Tool Optimization
- [Tool Optimization Guide](./ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md) - Claude Code, Gemini, Copilot
- [AI Assistant Rules](./ai_dev_flow/AI_ASSISTANT_RULES.md) - Rules for AI assistants

### Validation Scripts (v2.2)

**Core Validation (15 scripts)**:
- `ai_dev_flow/scripts/extract_tags.py` - Extract @tags from source files
- `ai_dev_flow/scripts/validate_tags_against_docs.py` - Validate cumulative tagging hierarchy (use `--validate-cumulative`)
- `ai_dev_flow/scripts/generate_traceability_matrices.py` - Generate bidirectional matrices
- `ai_dev_flow/scripts/validate_traceability_matrix.py` - Validate matrix structure
- `ai_dev_flow/scripts/validate_traceability_matrix_enforcement.py` - Enforce matrix rules
- `ai_dev_flow/scripts/update_traceability_matrix.py` - Update existing matrices
- `ai_dev_flow/scripts/validate_requirement_ids.py` - Validate REQ-ID format
- `ai_dev_flow/scripts/validate_req_spec_readiness.py` - REQ SPEC-readiness scoring
- `ai_dev_flow/scripts/validate_documentation_paths.py` - Path consistency validation
- `ai_dev_flow/scripts/validate_links.py` - Markdown link validation
- `ai_dev_flow/scripts/validate_brd_template.sh` - BRD template compliance
- `ai_dev_flow/scripts/validate_req_template.sh` - REQ template compliance
- `ai_dev_flow/scripts/generate_traceability_matrix.py` - Generate single matrix (legacy)
- `ai_dev_flow/scripts/README.md` - Complete scripts documentation

### Project Setup Scripts
- `scripts/setup_project_hybrid.sh` - Automated multi-project hybrid setup

## Support

- **Issues**: [GitHub Issues](https://github.com/[YOUR_ORG]/ai-dev-flow-framework/issues)
- **Documentation**: [ai_dev_flow/](./ai_dev_flow/)
- **Examples**: See `ai_dev_flow/*/examples/` directories

## Acknowledgments

Developed for AI-assisted software engineering workflows optimized for:
- Claude Code (Anthropic)
- Gemini CLI (Google)
- GitHub Copilot (Microsoft)

---

**Version**: 2.2
**Last Updated**: 2025-11-20
**Maintained by**: Vladimir M.

## Changelog

### Version 2.2 (2025-11-20)
- ✅ **Validation Scripts Expansion**: Grew from 3 to 15 validation scripts
  - Added `validate_req_spec_readiness.py` - REQ SPEC-readiness scoring
  - Added `validate_documentation_paths.py` - Path consistency validation
  - Added `validate_links.py` - Markdown link validation
  - Added `validate_traceability_matrix_enforcement.py` - Matrix enforcement rules
  - Added `validate_brd_template.sh` - BRD template compliance
  - Added `validate_req_template.sh` - REQ template compliance
- ✅ **Domain Adaptation**: Added comprehensive domain configuration guides
  - `FINANCIAL_DOMAIN_CONFIG.md` - Financial sector-specific guidance
  - `SOFTWARE_DOMAIN_CONFIG.md` - Generic software project guidance
  - `GENERIC_DOMAIN_CONFIG.md` - Minimal configuration template
  - `DOMAIN_SELECTION_QUESTIONNAIRE.md` - Domain selection tool
- ✅ **Enhanced Documentation**:
  - `PLATFORM_VS_FEATURE_BRD.md` - BRD type selection guidance
  - `TRACEABILITY_SETUP.md` - Enhanced setup guide
  - `TRACEABILITY_VALIDATION.md` - Validation procedures
  - Updated `index.md` with 7 categorized documentation sections
- ✅ **Decision Frameworks**: Contract and IMPL decision questionnaires
- ✅ **Tool Optimization**: Token limits guide for Claude Code, Gemini CLI, GitHub Copilot

### Version 2.1 (2025-11-19)
- Updated REQ references to v3.0 (REQ v3.0 sections 3-7 for SPEC-ready ≥90%)

### Version 2.0 (2025-11-13) - Cumulative Tagging Hierarchy
- ✅ **15-Layer Architecture**: Expanded from 10 to 15 layers (Strategy → Validation)
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
- ✅ **Directory Updates**: CONTRACTS → CTR (dual-file format)
- ✅ **Regulatory Compliance**: Complete audit trails for SEC, FINRA, FDA, ISO
- ✅ **Impact Analysis**: Instant identification of affected downstream artifacts

### Version 1.1.0 (2025-11-12)
- Added tag-based auto-discovery traceability system
- Introduced unified tag format (TYPE.NN.TT.SS)
- Added automated validation scripts
- Updated quality gates for tag-based and traditional projects
- Added CI/CD integration examples for traceability validation
- Legacy Section 7 approach still supported during migration

### Version 1.0.0 (2025-11-09)
- Initial release with 10-layer SDD workflow
- Complete template system for all artifact types
- Traditional Section 7 traceability

---

## Project Example: Trading Nexus (merged)

# Trading Nexus

**AI-Powered Options Trading Intelligence Platform**

[![Status](https://img.shields.io/badge/status-development-yellow)]()
[![Framework](https://img.shields.io/badge/framework-Google%20ADK-blue)]()
[![Protocol](https://img.shields.io/badge/tools-MCP-green)]()

---

## Overview

Trading Nexus is a comprehensive AI trading platform that combines:

- **Multi-LLM Ensemble**: 5 voting agents across 200+ models via AI Gateway
- **MCP-First Architecture**: Unified tool protocol with ecosystem leverage
- **Google ADK Framework**: Production-grade agent orchestration
- **GCP Cloud-Native**: Serverless, scale-to-zero infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TRADING NEXUS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │  22+ Agents     │    │   MCP Tools     │    │   AI Gateway    │        │
│   │  (Google ADK)   │───►│  (IB, Data,     │───►│  (200+ Models)  │        │
│   │                 │    │   SEC, etc.)    │    │                 │        │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                              │
│   Strategies: Earnings Plays │ Covered Calls │ Cash-Secured Puts │ Hedging │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Earnings Trading** | Systematic analysis with multi-agent consensus |
| **Income Strategies** | Covered calls, cash-secured puts, iron condors |
| **Multi-LLM Voting** | 5 agents (Claude, GPT-4, Gemini, DeepSeek, Llama) |
| **Risk Management** | 7 circuit breaker types, position limits |
| **Continuous Learning** | Graph RAG with bias detection |
| **Full Observability** | Metrics, logging, performance tracking |

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Agent Framework** | Google ADK (LlmAgent, ParallelAgent, SequentialAgent) |
| **Tool Protocol** | MCP (Model Context Protocol) |
| **AI Gateway** | LiteLLM (200+ models, cost optimization) |
| **Broker** | Interactive Brokers |
| **Infrastructure** | GCP (Cloud Run, Firestore, BigQuery) |
| **Knowledge** | Neo4j (Graph) + ChromaDB (Vectors) |

## Cost Estimate

| Phase | Monthly Cost |
|-------|--------------|
| Development | $175 |
| Active Trading | $375 |
| Production | $525 |

*See [docs/COST_ANALYSIS.md](docs/COST_ANALYSIS.md) for detailed breakdown.*

## Documentation

| Document | Description |
|----------|-------------|
| [**TRADING_NEXUS_SPECIFICATION.md**](docs/TRADING_NEXUS_SPECIFICATION.md) | Complete technical specification |

The specification covers:
- System architecture
- 22+ agent hierarchy
- Agent ensemble engine
- Google ADK implementation
- MCP tool architecture
- Infrastructure design
- 16-week roadmap
- Success metrics

## Quick Start

```bash
# Install Google ADK
pip install google-adk litellm

# Start development UI
adk web

# Access at http://localhost:4200
```

## Project Structure

```
trading-nexus/
├── docs/
│   └── TRADING_NEXUS_SPECIFICATION.md  # Complete specification
├── agents/                              # ADK agent definitions
│   ├── earnings_agent.py
│   ├── ensemble.py
│   └── ...
├── tools/                               # MCP server implementations
│   ├── ib_mcp_server/
│   └── browser_mcp_server/
├── config/                              # Agent configurations
└── tests/                               # Test suites
```

## Roadmap

| Phase | Duration | Focus |
|-------|----------|-------|
| **Foundation** | Weeks 1-4 | ADK setup, infrastructure |
| **Ensemble** | Weeks 5-8 | Voting agents, consensus |
| **MCP Integration** | Weeks 9-12 | Third-party MCPs, Graph RAG |
| **Production** | Weeks 13-16 | Strategy agents, hardening |

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent Framework | Google ADK | Native GCP, multi-agent, Dev UI |
| Tool Protocol | MCP | Industry standard, 2000+ servers |
