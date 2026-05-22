---
name: doc-flow
description: AI-Driven Specification-Driven Development (SDD) workflow orchestrator - guides skill selection and general SDD methodology
tags:
  - sdd-workflow
  - layer-0-artifact
  - shared-architecture
  - required-both-approaches
  - ai-assistant
custom_fields:
  layer: 0
  artifact_type: META
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: []
  downstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN, REF]
---

# doc-flow (Orchestrator)

## Purpose

This skill serves as the **orchestrator** for the AI-Driven Specification-Driven Development (SDD) workflow. It provides:

1. **Skill Selection Guidance**: Helps determine which artifact-specific skill to use
2. **Workflow Overview**: Complete 8-layer SDD architecture
3. **General SDD Principles**: Specification-driven methodology fundamentals
4. **Integration Guidance**: How skills work together

**For Artifact Creation**: Use the specific artifact skill (doc-brd, doc-prd, doc-ears, doc-bdd, doc-adr, doc-spec, doc-tdd, doc-iplan, doc-ref, doc-naming).

**Authoritative Reference**: [framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

---

## Prerequisites

**⚠️ For New Projects (Greenfield)**: If starting a brand new project with no existing folder structure, use the **`project-init`** skill FIRST to initialize project structure, select domain, create folders, and configure setup. Then return here to begin workflow execution.

**For Existing Projects**: If project is already initialized (docs/ folders exist, domain configured), proceed directly with this skill.

---

## Skill Selection Decision Tree

### "Which Skill Do I Need?"

Answer these questions to find the right skill:

**Q1: What stage are you at in the workflow?**

- **Starting new project with business requirements** → Use `doc-brd` skill
- **Have BRD, need product requirements** → Use `doc-prd` skill
- **Have PRD, need formal requirements** → Use `doc-ears` skill
- **Have EARS, need test scenarios** → Use `doc-bdd` skill
- **Have BDD, need architecture decisions** → Use `doc-adr` skill
- **Have ADR, need technical specifications** → Use `doc-spec` skill
- **Have SPEC, need test case definitions** → Use `doc-tdd` skill
- **Have TDD, need an implementation plan** → Use `doc-iplan` skill
- **Have IPLAN, ready to code** → Implement code per IPLAN
- **Need supplementary documentation (overview, glossary, guides)** → Use `doc-ref` skill

**Q2: What are you trying to do?**

- **Define business needs and objectives** → `doc-brd`
- **Define product features and KPIs** → `doc-prd`
- **Write formal WHEN-THE-SHALL-WITHIN requirements** → `doc-ears`
- **Create Gherkin test scenarios** → `doc-bdd`
- **Document architecture decisions** → `doc-adr`
- **Write technical specifications (interfaces, data models, behavior contracts)** → `doc-spec`
- **Define test cases and quality thresholds** → `doc-tdd`
- **Plan the executable implementation (file manifest, commands, handoff)** → `doc-iplan`
- **Create supplementary documentation (project overview, glossary, guides)** → `doc-ref`
- **General guidance or unsure** → Stay with `doc-flow` (this skill)

---

## Complete SDD Workflow (8 Layers)

**Authoritative Reference**: [framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

### Workflow Sequence

```
Strategy (Layer 0)
  ↓
BRD (Layer 1) → doc-brd skill
  ↓
PRD (Layer 2) → doc-prd skill
  ↓
EARS (Layer 3) → doc-ears skill
  ↓
BDD (Layer 4) → doc-bdd skill
  ↓
ADR (Layer 5) → doc-adr skill
  ↓
SPEC (Layer 6) → doc-spec skill
  ↓
TDD (Layer 7) → doc-tdd skill
  ↓
IPLAN (Layer 8) → doc-iplan skill
  ↓
Code
```

### Layer Descriptions

| Layer | Artifact | Purpose | Skill |
|-------|----------|---------|-------|
| 0 | **Strategy** | Business owner documents | External (strategy/) |
| 1 | **BRD** | Business requirements | `doc-brd` |
| 2 | **PRD** | Product requirements | `doc-prd` |
| 3 | **EARS** | Formal requirements (WHEN-THE-SHALL) | `doc-ears` |
| 4 | **BDD** | Gherkin test scenarios | `doc-bdd` |
| 5 | **ADR** | Architecture decisions | `doc-adr` |
| 6 | **SPEC** | Technical specifications (interfaces, data models, behavior contracts) | `doc-spec` |
| 7 | **TDD** | Test case definitions, BDD-to-test mapping, quality thresholds | `doc-tdd` |
| 8 | **IPLAN** | Implementation plan (file manifest, commands, handoff, audit trail) | `doc-iplan` |
| — | **Code** | Source implementation (output target) | Implementation |

**Note**: SPEC behavior contracts (interfaces, data models) live inside the SPEC layer (Layer 6); system-architecture concerns are captured by ADR (Layer 5) and SPEC (Layer 6); atomic/formal requirements live in EARS (Layer 3). There are no separate system, requirement, or contract document layers.

---

## General SDD Principles

### 1. Specification-Driven Development Philosophy

**Core Principle**: Formalize before implementing

- **Traditional Approach**: Code first, document later (or never)
- **SDD Approach**: Document first, generate code from specifications

**Why SDD Works**:
- **Clarity**: Requirements are explicit before coding begins
- **Traceability**: Every line of code traces to business requirements
- **Validation**: Tests defined before implementation
- **Consistency**: Templates ensure uniform structure
- **Speed**: Code generation from YAML specifications (48x faster)

### 2. Information Flow Hierarchy

**Changes flow DOWN (never UP)**:

```
strategy/ (WHAT - Product Owner Voice)
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

📝 framework/ feeds into 📚 docs/ for consistency
```

**Golden Rules**:
- Strategy → Documentation → Code (one-way flow)
- Code cannot change strategy
- Always use templates from `framework/` when creating docs in `docs/`
- All business logic must reference `strategy/` sections

### 3. Directory Structure and Roles

**Critical Context**: This project has three key directories with distinct roles:

#### `strategy/` - WHAT (Product Owner Voice)
**Primary Authority**: Authoritative business strategy and domain logic

- `core_algorithm.md` - Primary algorithm specifications
- `strategy_overview.md` - Strategic framework and operating modes
- `risk_management.md` - Risk management policies
- `business_rules.md` - Domain-specific business rules
- `selection_criteria/` - Entry criteria and scoring algorithms
- Performance targets, state machines, resource budgets

**Golden Rule**: All business logic must trace back to these strategy documents.

#### 📚 `docs/` - PROJECT DOCUMENTATION
**Implementation Documentation**: Requirements, architecture, specifications

- `docs/01_BRD/` - Business Requirements Documents
  - **Nested folder structure**: `docs/01_BRD/BRD-NN/BRD-NN.S_slug.md`
- `docs/02_PRD/` - Product Requirements Documents
  - **Nested folder structure**: `docs/02_PRD/PRD-NN/PRD-NN.S_slug.md`
- `docs/03_EARS/` - Formal requirements (WHEN-THE-SHALL-WITHIN)
- `docs/04_BDD/` - BDD acceptance tests (Behavior-Driven Development)
- `docs/05_ADR/` - Architecture Decision Records (HOW)
  - **Nested folder structure**: `docs/05_ADR/ADR-NN/ADR-NN.S_slug.md`
- `docs/06_SPEC/` - YAML technical specifications
- `docs/07_TDD/` - Test case definitions and quality thresholds
- `docs/08_IPLAN/` - Implementation plans (executable file manifest)

**Note**: BRD, PRD, ADR use section-based nested folders by default. Other types use flat structure.

**Purpose**: Document how strategy is implemented through architecture and code.

#### 📝 `framework/` - AUTHORITATIVE DEVELOPMENT STANDARD
**Development Standard and Templates**: The single source of truth for SDD workflow

- **Status**: Authoritative development standard for this project
- **Contents**: Complete SDD workflow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code)
- **Templates**: `{TYPE}-TEMPLATE.yaml` for each artifact type (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN)
- **Indices**: `{TYPE}-00_index.{md,yaml}` listing all documents of each type
- **READMEs**: Detailed usage guides and best practices for each artifact type
- **Standards**: ID naming, traceability format, cross-referencing rules
- **Examples**: Reference implementations with full traceability chains

**Purpose**: Define the complete development methodology with templates, standards, and examples for creating all artifacts.

#### ⚠️ CRITICAL: Archived Documents Restriction

**STRICTLY PROHIBITED: DO NOT access, reference, link to, or use ANY files or directories containing the word "archived" in their path.**

**Automatic Filtering Rules:**
- ❌ Skip any path containing `archived`, `Archived`, `ARCHIVED`, or `archive`
- ❌ Ignore files in directories with "archived" in the name
- ❌ Do not read, suggest, or reference archived content
- ❌ Do not use archived documents even if they appear in search results

**Active Documentation Only:**
- `strategy/` (current strategy - excludes archived subdirs)
- `docs/` (active project documentation)
- `framework/` (authoritative templates and standards)

**If archived content is needed:**
- Stop immediately
- Inform user that content is in archived location
- Request explicit permission before proceeding

### 4. Traceability Importance

**Complete Audit Trail**: Every artifact must trace back to original business requirements

**Benefits**:
- **Impact Analysis**: Know what breaks when requirements change
- **Regulatory Compliance**: Industry-specific audit requirements (ISO, SOC2, etc.)
- **Change Management**: Track all changes through artifact chain
- **Coverage Metrics**: Measure implementation completeness
- **Quality Assurance**: Declarative validation prevents gaps

**Implementation**:
- Cumulative tagging hierarchy (see SHARED_CONTENT.md)
- Traceability section in every document
- Bidirectional traceability matrices
- The artifact skill's own validation checklist (see `framework/governance/`)

### 5. Upstream Artifact Policy (CRITICAL)

**⚠️ MANDATORY RULE**: Do NOT create missing upstream artifacts. Skip functionality instead.

**Policy Statement**:
If a required upstream artifact is missing, the downstream functionality **MUST NOT be implemented**. This enforces the SDD document hierarchy where every implementation must have proper business/product justification through the complete artifact chain.

**Decision Rules**:

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | **Skip that functionality** - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

**Rationale**:
- **Prevents orphaned code**: No implementation without business justification
- **Enforces governance**: Changes must flow through proper channels
- **Maintains audit trail**: Every feature traces to business need
- **Reduces technical debt**: No undocumented "nice-to-have" features

**When Upstream is Missing**:
1. **Stop** - Do not proceed with implementation
2. **Report** - Inform user which upstream artifact is missing
3. **Advise** - Recommend creating upstream artifacts first through proper channels
4. **Skip** - Move on to functionality that has complete upstream chain

**Reference**: [framework/governance/TRACEABILITY.md]({project_root}/framework/governance/TRACEABILITY.md)

---

## Integration with Other Skills

### Core Workflow Skills

**`project-init`** - Initialize new project structure
- Use BEFORE doc-flow for greenfield projects
- Creates folder structure, domain setup, baseline files
- Reference: `../project-init/SKILL.md`

**`trace-check`** - Validate traceability after artifact creation
- Use AFTER doc-flow to verify bidirectional links
- Validates cumulative tagging, ID formats, link resolution
- Detects orphaned artifacts and traceability gaps
- Reference: `../trace-check/SKILL.md`

**`doc-naming`** - Unified ID naming standards enforcement
- Use for ID format validation across all artifact types
- Validates 4-segment element IDs (TYPE.NN.SS.xxxx)
- Enforces variable-length DOC_NUM (2+ digits)
- Reference: `../doc-naming/SKILL.md`

**`doc-validator`** - Cross-document validation orchestrator
- Validates traceability across all layers
- Detects gaps, broken links, and format violations
- Runs auto-fix actions for common issues
- Reference: `../doc-validator/SKILL.md`

### Planning & Architecture

**`adr-roadmap`** - Generate implementation roadmaps from ADRs
- Use AFTER creating ADR artifacts
- Creates timeline, risk assessment, dependency mapping
- Reference: `../adr-roadmap/SKILL.md`

**`project-mngt`** - MVP/MMP/MMR planning
- Use for strategic release planning
- Integrates with IPLAN artifacts
- Reference: `../project-mngt/SKILL.md`

### Typical Workflow Integration

```text
1. project-init    → Initialize project (greenfield only)
2. doc-brd         → Create BRD
3. doc-prd         → Create PRD
4. doc-ears        → Create EARS
5. doc-bdd         → Create BDD
6. doc-adr         → Create ADR
7. doc-spec        → Create SPEC
8. doc-tdd         → Create TDD
9. doc-iplan       → Create IPLAN
10. Implementation → Execute based on IPLAN
11. trace-check    → Validate traceability
```

---

## Shared Standards

**CRITICAL**: All artifact-specific skills share common standards defined in:

**`../doc-flow/SHARED_CONTENT.md`**

This document contains:
1. Document ID Naming Standards
2. Traceability Section Format
3. Cumulative Tagging Hierarchy
4. Quality Gates & Validation
5. Traceability Matrix Enforcement
6. Documentation Standards
7. Document Control Section Requirements

**All artifact skills (doc-brd through doc-iplan, plus doc-ref, doc-naming) import these shared standards.**

### Diagram Standards (Global Requirement)

**All diagrams MUST use Mermaid syntax.** Text-based diagrams (ASCII art, box drawings) are prohibited.

- **Authority Document**: `framework/governance/DIAGRAM_STANDARDS.md`
- **Syntax Generation**: `mermaid-gen` skill
- **File Management**: `charts-flow` skill (SVG conversion, embedding)

**Allowed Exception**: Directory tree structures (using `├── └── │`) are permitted as they represent file structure, not diagrams.

---

## Validation Overview

The framework is spec-only — it ships no runtime validation scripts. Each
artifact skill **is** the validator: it carries a declarative validation
checklist and defers to the governance standards and the layer's own README.

### Validation Authorities

| Concern | Authority |
|---------|-----------|
| ID & naming format | `framework/governance/ID_NAMING_STANDARDS.md` |
| Traceability & cumulative tags | `framework/governance/TRACEABILITY.md` |
| Per-layer creation/validation rules | `framework/layers/<NN>_<X>/README.md` |
| Quality gates (≥90% ready score) | the artifact skill's own checklist (see SHARED_CONTENT.md §4) |

**Per-artifact validation skills**: each family ships a `doc-<type>-validator`
skill (e.g. `doc-brd-validator`, `doc-spec-validator`, `doc-iplan-validator`)
that runs the declarative checklist for that artifact type.

---

## Cross-Document Validation (MANDATORY)

**CRITICAL**: After creating each artifact, run the artifact skill's
declarative cross-document validation checklist before proceeding to the next
layer. Validation is performed by the skills themselves, not external scripts.

### Validation Phases

| Phase | Trigger | Performed by |
|-------|---------|--------------|
| Phase 1 | Per-document | `doc-<type>-validator` skill on the new document |
| Phase 2 | Per-layer complete | `doc-validator` across the completed layer |
| Phase 3 | Final (all layers) | `doc-validator` + `trace-check` across the full chain |

### Automatic Validation Loop

```
LOOP:
  1. Run the doc-<type>-validator checklist on {doc_path}
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Layer-Specific Upstream Requirements

| Layer | Artifact | Required Upstream Tags | Tag Count |
|-------|----------|------------------------|-----------|
| 1 | BRD | (none - root) | 0 |
| 2 | PRD | @brd | 1 |
| 3 | EARS | @brd, @prd | 2 |
| 4 | BDD | @brd, @prd, @ears | 3 |
| 5 | ADR | @brd, @prd, @ears, @bdd | 4 |
| 6 | SPEC | @brd, @prd, @ears, @bdd, @adr | 5 |
| 7 | TDD | @brd, @prd, @ears, @bdd, @adr, @spec | 6 |
| 8 | IPLAN | @brd, @prd, @ears, @bdd, @adr, @spec, @tdd | 7 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing cumulative tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.SS.xxxx (4-segment) or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-004 | Link target file missing | WARNING |
| XDOC-005 | Anchor in link not found | WARNING |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-008 | Circular reference detected | ERROR |
| XDOC-009 | Missing traceability section | ERROR |
| XDOC-010 | Orphaned document (no upstream refs) | WARNING |

### Quality Gate

**Blocking**: YES - Cannot proceed to next layer until Phase 1 validation passes with 0 errors for the current artifact.

---

## Related Resources

### Core Standards (framework/)

**Primary References - Authoritative Development Standard:**

- **Main Guide**: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete 8-layer workflow
- **Quick Reference**: [QUICK_REFERENCE.md]({project_root}/framework/QUICK_REFERENCE.md) - At-a-glance workflow summary
- **Layer Registry**: [LAYER_REGISTRY.yaml]({project_root}/framework/registry/LAYER_REGISTRY.yaml) - Authoritative layer list + upstream/downstream chains
- **ID Standards**: [ID_NAMING_STANDARDS.md]({project_root}/framework/governance/ID_NAMING_STANDARDS.md) - File naming, ID format rules
- **Traceability**: [TRACEABILITY.md]({project_root}/framework/governance/TRACEABILITY.md) - Cross-reference format, link standards
- **Governance Core**: [DOC_GOVERNANCE_CORE.md]({project_root}/framework/governance/DOC_GOVERNANCE_CORE.md) - Quality gates and governance rules
- **README**: [README.md]({project_root}/framework/README.md) - Getting started guide

### Templates Location

**All templates located in `framework/layers/<NN>_<X>/`:**

- **BRD** (`layers/01_BRD/`): `BRD-TEMPLATE.yaml`
- **PRD** (`layers/02_PRD/`): `PRD-TEMPLATE.yaml`
- **EARS** (`layers/03_EARS/`): `EARS-TEMPLATE.yaml`
- **BDD** (`layers/04_BDD/`): `BDD-TEMPLATE.yaml`
- **ADR** (`layers/05_ADR/`): `ADR-TEMPLATE.yaml`
- **SPEC** (`layers/06_SPEC/`): `SPEC-TEMPLATE.yaml`
- **TDD** (`layers/07_TDD/`): `TDD-TEMPLATE.yaml`
- **IPLAN** (`layers/08_IPLAN/`): `IPLAN-TEMPLATE.yaml`

**Each layer directory also contains:**
- Index file: `{TYPE}-00_index.{md,yaml}`
- README.md: Usage guide, creation rules, and validation requirements

---

## Quick Reference Card

### Decision Matrix

| You Have | You Need | Use This Skill |
|----------|----------|----------------|
| Nothing | Business requirements | `doc-brd` |
| BRD | Product requirements | `doc-prd` |
| PRD | Formal requirements | `doc-ears` |
| EARS | Test scenarios | `doc-bdd` |
| BDD | Architecture decisions | `doc-adr` |
| ADR | Technical specifications | `doc-spec` |
| SPEC | Test case definitions | `doc-tdd` |
| TDD | Implementation plan | `doc-iplan` |
| IPLAN | Code | Implement! |
| Any stage | Supplementary documentation | `doc-ref` |

### Development ROI

- Traditional: 70 hours/component
- SDD: 1.5 hours/component
- Speed increase: 48x faster
- Consistency: 100% (template-based)
- Traceability: Automatic, bidirectional

---

## Usage Example

**User**: "I need to implement position risk limit validation"

**Assistant**: "I'll guide you through the SDD workflow. Let me check what artifacts you have:

**Current Status Check**:
- Do you have a BRD documenting business requirements? [If no → **SKIP** this functionality]
- Do you have a PRD with product requirements? [If no → **SKIP** this functionality]
- Do you have EARS formal requirements? [If no → **SKIP** this functionality]
- Do you have BDD test scenarios? [If no → **SKIP** this functionality]
- Do you have ADR architecture decisions? [If no → **SKIP** this functionality]
- Do you have a SPEC technical specification? [If no → **SKIP** this functionality]
- Do you have a TDD test-case definition? [If no → **SKIP** this functionality]

**⚠️ CRITICAL: Upstream Artifact Policy**:
If ANY required upstream artifact is missing, **do NOT create it** and **do NOT implement the downstream functionality**. The SDD workflow enforces strict document hierarchy - functionality without proper business/product justification should not exist.

**Next Steps**:
Based on your current progress, I'll recommend the appropriate skill to use next. Each skill will guide you through creating that specific artifact type with proper templates, traceability, and validation."

---

**For detailed artifact creation guidance, use the specific artifact skill (doc-brd, doc-prd, doc-ears, doc-bdd, doc-adr, doc-spec, doc-tdd, doc-iplan, doc-ref, doc-naming).**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22T00:00:00 | Migrated to the 8-layer SDD model (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code); retired the three intermediate legacy layers and the two optional legacy layers, folding their concerns into ADR, SPEC, and EARS; renamed the test-spec layer to TDD and the task-breakdown layer to IPLAN; repointed paths to framework/layers and framework/governance |
| 1.4 | 2026-02-10T15:00:00 | Updated version history dates to ISO 8601 format |
| 1.3 | 2026-01-17T00:00:00 | Updated to 15-layer architecture (Layers 0-14) |
| 1.2 | 2025-12-29T00:00:00 | Fixed workflow sequence; Added doc-naming and doc-validator to Integration section |
| 1.1 | 2025-11-30T00:00:00 | Added REF documents |
| 1.0 | 2025-11-01T00:00:00 | Initial skill creation |
