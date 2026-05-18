# UCx Framework Implementation Plan

**Version**: 1.2
**Updated**: 2026-03-09
**Status**: Approved

### Change Log
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-09 | Initial plan |
| 1.1 | 2026-03-09 | Added gaps: UCC/UCRem prompts for all layers, validator integration, testing |
| 1.2 | 2026-03-09 | Expanded Phase 6 documentation (40 tasks across 5 categories) |

## Overview

Consolidate document creation, review, and remediation into a unified multi-persona framework called **UCx** (Unified Context).

| Phase | Acronym | Purpose | Status |
|-------|---------|---------|--------|
| Creation | **UCC** | Multi-persona document authoring | NEW |
| Review | **UCR** | Multi-persona document validation (includes schema validation) | EXISTS |
| Remediation | **UCRem** | Multi-persona fix generation | EXISTS |

### Architecture Decision: Validators Integrated into UCR

Validators (schema/structure checks) are **integrated into UCR** for a unified approach:

```
┌─────────────────────────────────────────────────────────────┐
│                    UCx Framework                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────┐   │
│  │    UCC      │    │    UCR      │    │    UCRem      │   │
│  │  (Create)   │───▶│  (Review)   │───▶│ (Remediate)   │   │
│  │             │    │ + Validate  │    │               │   │
│  └─────────────┘    └─────────────┘    └───────────────┘   │
│         │                  │                   │            │
│         │                  │                   ▼            │
│         ▼                  │           ┌───────────────┐   │
│  ┌─────────────┐           │           │    Fixer      │   │
│  │  Templates  │           │           │  (Apply Fix)  │   │
│  │ (MVP-TEMPL) │           │           └───────────────┘   │
│  └─────────────┘           │                               │
│                            ▼                               │
│              ┌──────────────────────┐                      │
│              │  Validation Layers:  │                      │
│              │  1. Schema (YAML)    │                      │
│              │  2. Structure (Sects)│                      │
│              │  3. Content (UCR)    │                      │
│              └──────────────────────┘                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    skills/                            │  │
│  │  (Single source of truth for persona knowledge)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Directory Restructure

### 1.1 Rename AI_EXPERTS to UCX

**Framework Location:**
```
/opt/data/ucx_framework/ai_dev_ssd_flow/
├── AI_EXPERTS/          # RENAME TO: UCX/
```

**Project Location:**
```
/opt/data/b-local/b-local-docs/docs/
├── AI_EXPERTS/          # RENAME TO: UCX/
```

### 1.2 New Directory Structure

```
UCX/
├── README.md                      # Framework overview
├── CHANGELOG.md                   # Version history
├── ucx.sh                         # Unified entry point (optional)
│
├── skills/                        # SINGLE SOURCE OF TRUTH
│   ├── architect.md
│   ├── auditor.md
│   ├── business_analyst.md
│   ├── devils_advocate.md
│   ├── integration_expert.md
│   ├── operator.md
│   ├── product_owner.md
│   ├── qa_lead.md
│   ├── requirements_specialist.md
│   ├── strategist.md
│   ├── tech_lead.md
│   └── ux_strategist.md
│
├── creation/                      # UCC (NEW)
│   ├── run_ucc.sh                 # Creation runner script
│   ├── UCC_PROMPT_BRD.md          # L1: Business Requirements
│   ├── UCC_PROMPT_PRD.md          # L2: Product Requirements
│   ├── UCC_PROMPT_EARS.md         # L3: EARS Requirements
│   ├── UCC_PROMPT_BDD.md          # L4: BDD Scenarios
│   ├── UCC_PROMPT_ADR.md          # L5: Architecture Decisions
│   ├── UCC_PROMPT_SYS.md          # L6: System Requirements
│   ├── UCC_PROMPT_REQ.md          # L7: Atomic Requirements
│   ├── UCC_PROMPT_CTR.md          # L8: Data Contracts
│   ├── UCC_PROMPT_SPEC.md         # L9: Specifications
│   ├── UCC_PROMPT_TSPEC.md        # L10: Test Specifications
│   ├── UCC_PERSONAS.md            # Author persona definitions
│   └── UCC_OUTPUT_SCHEMA.md       # Output format reference
│
├── review/                        # UCR (MOVE + ENHANCE)
│   ├── run_ucr.sh                 # Review runner script
│   ├── UCR_PROMPT_BRD.md          # L1
│   ├── UCR_PROMPT_PRD.md          # L2
│   ├── UCR_PROMPT_EARS.md         # L3
│   ├── UCR_PROMPT_BDD.md          # L4
│   ├── UCR_PROMPT_ADR.md          # L5
│   ├── UCR_PROMPT_SYS.md          # L6
│   ├── UCR_PROMPT_REQ.md          # L7
│   ├── UCR_PROMPT_CTR.md          # L8
│   ├── UCR_PROMPT_SPEC.md         # L9
│   ├── UCR_PROMPT_TSPEC.md        # L10
│   ├── UCR_PERSONAS.md            # Reviewer persona definitions
│   ├── UCR_OUTPUT_TEMPLATE.md     # Output format
│   └── validators/                # Schema validators (integrated)
│       ├── validate_brd.sh
│       ├── validate_prd.sh
│       └── ...
│
├── remediation/                   # UCRem (MOVE + EXPAND)
│   ├── run_ucrem.sh               # Remediation runner script
│   ├── UCRem_PROMPT_BRD.md        # L1
│   ├── UCRem_PROMPT_PRD.md        # L2
│   ├── UCRem_PROMPT_EARS.md       # L3
│   ├── UCRem_PROMPT_BDD.md        # L4
│   ├── UCRem_PROMPT_ADR.md        # L5
│   ├── UCRem_PROMPT_SYS.md        # L6
│   ├── UCRem_PROMPT_REQ.md        # L7
│   ├── UCRem_PROMPT_CTR.md        # L8
│   ├── UCRem_PROMPT_SPEC.md       # L9
│   ├── UCRem_PROMPT_TSPEC.md      # L10
│   ├── UCRem_PERSONAS.md          # Fixer persona definitions
│   ├── UCRem_REPORT_SCHEMA.md     # Fix entry schema
│   └── UCRem_REPORT_TEMPLATE.md   # Output template
│
├── templates/                     # Template symlinks
│   └── -> ai_dev_flow/{TYPE}/*-MVP-TEMPLATE.md
│
├── docs/                          # Documentation
│   ├── UNIFIED_CONTEXT_FRAMEWORK.md   # UCx overview
│   ├── PERSONA_DESIGN_GUIDE.md
│   ├── HOW_TO_USE.md
│   └── CROSS_LAYER_WORKFLOW.md    # Layer dependencies
│
└── examples/
    └── beelocal_fintech/          # Domain example
```

### 1.3 Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 1.1.1 | Rename `AI_EXPERTS/` to `UCX/` in framework | S | - |
| 1.1.2 | Create subdirectories: `creation/`, `review/`, `remediation/`, `docs/`, `templates/` | S | 1.1.1 |
| 1.1.3 | Move existing UCR files to `review/` | S | 1.1.2 |
| 1.1.4 | Move existing UCRem files to `remediation/` | S | 1.1.2 |
| 1.1.5 | Create `templates/` symlinks to ai_dev_flow MVP templates | S | 1.1.2 |
| 1.1.6 | Update all internal references in moved files | M | 1.1.3, 1.1.4 |
| 1.1.7 | Create backward compatibility symlink `AI_EXPERTS -> UCX` | S | 1.1.1 |
| 1.1.8 | Update b-local project symlinks | S | 1.1.6 |

---

## Phase 2: UCC (Creation) System

### 2.1 Creation Persona Mapping

Each document type uses specific author personas:

| Layer | Document | Author Personas |
|-------|----------|-----------------|
| L1 | BRD | architect, product_owner, business_analyst, strategist, tech_lead |
| L2 | PRD | product_owner, ux_strategist, tech_lead, qa_lead, architect |
| L3 | EARS | requirements_specialist, tech_lead, qa_lead, devils_advocate |
| L4 | BDD | qa_lead, tech_lead, devils_advocate, operator |
| L5 | ADR | architect, tech_lead, strategist, devils_advocate, operator |
| L6 | SYS | architect, tech_lead, operator, integration_expert |
| L7 | REQ | requirements_specialist, tech_lead, integration_expert |
| L8 | CTR | architect, tech_lead, integration_expert |
| L9 | SPEC | tech_lead, architect, operator, integration_expert |
| L10 | TSPEC | qa_lead, tech_lead, operator |

### 2.2 Cross-Layer Dependencies

```
L1 BRD ──┬──▶ L2 PRD ──▶ L3 EARS ──▶ L4 BDD
         │
         └──▶ L5 ADR ──▶ L6 SYS ──▶ L7 REQ ──┬──▶ L8 CTR
                                              │
                                              └──▶ L9 SPEC ──▶ L10 TSPEC
```

UCC must handle upstream dependencies:
- `--from-ref` - Load reference documents (REF files)
- `--from-upstream` - Load upstream artifact (BRD for PRD, PRD for EARS, etc.)

### 2.3 UCC Prompt Structure

```markdown
# UCC Prompt: {DOC_TYPE} Creation

You are a **Unified Context Creation (UCC)** system. Your task is to
author a complete {DOC_TYPE} document using multiple expert personas.

## Author Personas

Each persona contributes their domain expertise:

### 1. {PERSONA_1}
- **Focus**: {focus_area}
- **Contribution**: {what_they_add}
- **Quality Gate**: {what_they_verify}

### 2. {PERSONA_2}
...

## Input Sources

You will receive:
1. Reference documents (REF files, upstream artifacts)
2. Project context (domain, constraints, requirements)
3. Template structure (required sections from MVP template)

## Output Requirements

1. Follow {DOC_TYPE} MVP template structure exactly
2. Each section reviewed by relevant persona
3. Cross-references validated by Integration Expert
4. Edge cases identified by Devil's Advocate
5. Generate YAML frontmatter with proper metadata

## Multi-File Output (if applicable)

For BRD and other multi-file documents:
- Create index file: `{DOC_ID}.0_index.md`
- Create section files: `{DOC_ID}.{N}_{section_slug}.md`
- Maintain cross-references between files

## BEGIN CREATION

[Template, reference documents, and context appended here]
```

### 2.4 run_ucc.sh Script Features

```bash
#!/usr/bin/env bash
# run_ucc.sh - Unified Context Creation runner

# Usage:
#   ./run_ucc.sh <doc_type> <output_path> [options]
#
# Options:
#   --from-ref <dir>        Load reference documents
#   --from-upstream <file>  Load upstream artifact
#   --template <file>       Use custom template (default: MVP template)
#   --multi-file            Generate multi-file output (for BRD)
#
# Examples:
#   ./run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
#   ./run_ucc.sh prd docs/02_PRD/PRD-01.md --from-upstream docs/01_BRD/BRD-01/
#   ./run_ucc.sh ears docs/03_EARS/EARS-01.md --from-upstream docs/02_PRD/PRD-01.md

# Features:
# - Auto-selects creation prompt based on doc_type
# - Loads author personas dynamically from skills/
# - Detects project-specific prompts (*_PROJECT.md, *_BEELOCAL.md)
# - Loads MVP template from templates/ or ai_dev_flow/
# - Appends reference/upstream documents to prompt
# - Handles multi-file output directory creation
# - Error handling with clear messages

# Environment Variables:
# - UCC_MODEL (default: opus)
# - UCC_LOAD_SKILLS (default: true)
# - UCC_PROMPT_DIR (default: script directory)
```

### 2.5 Tasks - UCC Core

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 2.1.1 | Create `UCC_PERSONAS.md` with author persona definitions | M | 1.1.2 |
| 2.1.2 | Create `run_ucc.sh` runner script with full features | L | 1.1.2 |
| 2.1.3 | Create `UCC_OUTPUT_SCHEMA.md` output format reference | S | 2.1.1 |

### 2.6 Tasks - UCC Prompts (All Layers)

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 2.2.1 | Create `UCC_PROMPT_BRD.md` (L1) | L | 2.1.1 |
| 2.2.2 | Create `UCC_PROMPT_PRD.md` (L2) | L | 2.1.1 |
| 2.2.3 | Create `UCC_PROMPT_EARS.md` (L3) | M | 2.1.1 |
| 2.2.4 | Create `UCC_PROMPT_BDD.md` (L4) | M | 2.1.1 |
| 2.2.5 | Create `UCC_PROMPT_ADR.md` (L5) | M | 2.1.1 |
| 2.2.6 | Create `UCC_PROMPT_SYS.md` (L6) | M | 2.1.1 |
| 2.2.7 | Create `UCC_PROMPT_REQ.md` (L7) | M | 2.1.1 |
| 2.2.8 | Create `UCC_PROMPT_CTR.md` (L8) | M | 2.1.1 |
| 2.2.9 | Create `UCC_PROMPT_SPEC.md` (L9) | M | 2.1.1 |
| 2.2.10 | Create `UCC_PROMPT_TSPEC.md` (L10) | M | 2.1.1 |

### 2.7 Tasks - UCRem Prompts (All Layers)

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 2.3.1 | Update `UCRem_PROMPT_BRD.md` for new structure | S | 1.1.4 |
| 2.3.2 | Create `UCRem_PROMPT_PRD.md` (L2) | M | 1.1.4 |
| 2.3.3 | Create `UCRem_PROMPT_EARS.md` (L3) | M | 1.1.4 |
| 2.3.4 | Create `UCRem_PROMPT_BDD.md` (L4) | M | 1.1.4 |
| 2.3.5 | Create `UCRem_PROMPT_ADR.md` (L5) | M | 1.1.4 |
| 2.3.6 | Create `UCRem_PROMPT_SYS.md` (L6) | M | 1.1.4 |
| 2.3.7 | Create `UCRem_PROMPT_REQ.md` (L7) | M | 1.1.4 |
| 2.3.8 | Create `UCRem_PROMPT_CTR.md` (L8) | M | 1.1.4 |
| 2.3.9 | Create `UCRem_PROMPT_SPEC.md` (L9) | M | 1.1.4 |
| 2.3.10 | Create `UCRem_PROMPT_TSPEC.md` (L10) | M | 1.1.4 |

### 2.8 Tasks - Project-Specific (BeeLocal)

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 2.4.1 | Create `UCC_PROMPT_BRD_BEELOCAL.md` | M | 2.2.1 |
| 2.4.2 | Create `UCC_PROMPT_PRD_BEELOCAL.md` | M | 2.2.2 |

---

## Phase 3: UCR Enhancement (Integrated Validation)

### 3.1 Validator Integration

UCR now includes schema validation as first pass:

```bash
# run_ucr.sh enhanced flow:
# 1. Run schema validator (if exists)
# 2. Run structure validator
# 3. Run content review (multi-persona UCR)
# 4. Combine results into unified report
```

### 3.2 Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 3.1.1 | Update `run_ucr.sh` to integrate validators | M | 1.1.3 |
| 3.1.2 | Move validator scripts to `review/validators/` | S | 1.1.3 |
| 3.1.3 | Create unified output format (validation + review) | M | 3.1.1 |
| 3.1.4 | Update UCR prompts to reference validation results | S | 3.1.3 |

---

## Phase 4: Claude Skills Refactoring

### 4.1 Current Skills Inventory

```
~/.claude/commands/
├── doc-brd.md           # BRD creation
├── doc-brd-audit.md     # BRD validation (→ UCR)
├── doc-brd-fixer.md     # BRD fix application (→ UCRem apply)
├── doc-brd-autopilot.md # BRD orchestration
├── doc-brd-validator.md # BRD schema check (→ integrated into UCR)
├── doc-prd.md           # PRD creation
├── doc-prd-audit.md     # PRD validation
├── doc-prd-fixer.md     # PRD fix application
├── doc-prd-autopilot.md # PRD orchestration
... (similar pattern for all layers)
```

### 4.2 Refactored Skills Architecture

| Current Skill | UCx Phase | New Behavior |
|---------------|-----------|--------------|
| `/doc-brd` | UCC | Wrapper → `run_ucc.sh brd` |
| `/doc-brd-audit` | UCR | Wrapper → `run_ucr.sh brd` |
| `/doc-brd-validator` | UCR | **DEPRECATED** (integrated into audit) |
| `/doc-brd-fixer` | UCRem | Wrapper → apply UCRem fixes |
| `/doc-brd-autopilot` | UCC+UCR | Orchestrates full workflow |

### 4.3 Skill Template (Thin Wrapper)

```markdown
# /doc-{type} (Refactored)

## Description
Create {TYPE} documents using UCx multi-persona authoring.

## Implementation
1. Detect project UCX directory
2. Load personas from `UCX/skills/`
3. Invoke `UCX/creation/run_ucc.sh {type}`
4. Use project-specific prompt if available

## Usage
/doc-{type} {DOC_ID} [--from-ref <dir>] [--from-upstream <file>]

## UCx Integration
- Creation: `UCX/creation/run_ucc.sh`
- Review: `UCX/review/run_ucr.sh`
- Remediation: `UCX/remediation/run_ucrem.sh`
```

### 4.4 Autopilot Skill Integration

Autopilot skills orchestrate the full UCC → UCR → UCRem workflow:

```markdown
# /doc-{type}-autopilot (Refactored)

## Workflow
1. **UCC Phase**: Create document
   - run_ucc.sh {type} {output} --from-upstream {upstream}

2. **UCR Phase**: Review document
   - run_ucr.sh {type} {output}
   - If P0/P1 findings exist → proceed to UCRem

3. **UCRem Phase**: Generate fixes
   - run_ucrem.sh {review_report} {document}

4. **Apply Phase**: Apply auto-safe fixes
   - Apply fixes with confidence=auto-safe
   - Flag auto-assisted for user completion

5. **Re-validate**: Run UCR again
   - Verify P0/P1 reduced
   - Loop if needed (max 3 iterations)
```

### 4.5 Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 4.1.1 | Create skill template that loads UCx | S | 2.1.2 |
| 4.1.2 | Refactor `/doc-brd` to use UCC | M | 4.1.1 |
| 4.1.3 | Refactor `/doc-brd-audit` to use UCR | M | 3.1.1 |
| 4.1.4 | Refactor `/doc-brd-fixer` to use UCRem | M | 2.3.1 |
| 4.1.5 | Refactor `/doc-brd-autopilot` for full UCx workflow | L | 4.1.2, 4.1.3, 4.1.4 |
| 4.1.6 | Deprecate `/doc-brd-validator` (add deprecation notice) | S | 3.1.1 |
| 4.1.7 | Refactor `/doc-prd*` skills | M | 4.1.5 |
| 4.1.8 | Refactor `/doc-ears*` skills | M | 4.1.5 |
| 4.1.9 | Refactor `/doc-adr*` skills | M | 4.1.5 |
| 4.1.10 | Refactor `/doc-bdd*` skills | M | 4.1.5 |
| 4.1.11 | Refactor remaining layer skills (SYS, REQ, CTR, SPEC, TSPEC) | L | 4.1.5 |
| 4.1.12 | Create skill manifest/index (`UCX/SKILL_INDEX.md`) | S | 4.1.11 |
| 4.1.13 | Update skill documentation | M | 4.1.11 |

---

## Phase 5: Project Setup Updates

### 5.1 BeeLocal Project Structure

```
/opt/data/b-local/b-local-docs/docs/UCX/
├── README.md                      # Project-specific README
│
├── skills -> framework/skills     # Symlink to framework skills
│
├── creation/
│   ├── run_ucc.sh -> framework/   # Symlink
│   ├── UCC_PROMPT_BRD.md -> framework/  # Symlink
│   ├── UCC_PROMPT_BRD_BEELOCAL.md      # PROJECT-SPECIFIC
│   └── UCC_PROMPT_PRD_BEELOCAL.md      # PROJECT-SPECIFIC
│
├── review/
│   ├── run_ucr.sh -> framework/   # Symlink
│   ├── UCR_PROMPT_BRD.md -> framework/  # Symlink
│   └── UCR_PROMPT_BRD_BEELOCAL.md      # PROJECT-SPECIFIC
│
└── remediation/
    ├── run_ucrem.sh -> framework/ # Symlink
    ├── UCRem_PROMPT_BRD.md -> framework/  # Symlink
    └── UCRem_PROMPT_BRD_BEELOCAL.md     # PROJECT-SPECIFIC
```

### 5.2 Project Initialization Script

```bash
#!/usr/bin/env bash
# init_ucx.sh - Initialize UCX for a project

set -euo pipefail

FRAMEWORK_UCX="${FRAMEWORK_UCX:-/opt/data/ucx_framework/ai_dev_ssd_flow/UCX}"
PROJECT_UCX="${1:-./docs/UCX}"
PROJECT_SUFFIX="${2:-PROJECT}"  # or BEELOCAL, etc.

echo "Initializing UCX in $PROJECT_UCX"
echo "Framework: $FRAMEWORK_UCX"
echo "Project suffix: $PROJECT_SUFFIX"

# Validate framework exists
if [[ ! -d "$FRAMEWORK_UCX" ]]; then
    echo "Error: Framework UCX not found at $FRAMEWORK_UCX"
    exit 1
fi

# Create project UCX directory
mkdir -p "$PROJECT_UCX"/{creation,review,remediation}

# Create symlinks to framework
ln -sf "$FRAMEWORK_UCX/skills" "$PROJECT_UCX/skills"
ln -sf "$FRAMEWORK_UCX/creation/run_ucc.sh" "$PROJECT_UCX/creation/run_ucc.sh"
ln -sf "$FRAMEWORK_UCX/review/run_ucr.sh" "$PROJECT_UCX/review/run_ucr.sh"
ln -sf "$FRAMEWORK_UCX/remediation/run_ucrem.sh" "$PROJECT_UCX/remediation/run_ucrem.sh"

# Symlink framework prompts
for phase in creation review remediation; do
    for f in "$FRAMEWORK_UCX/$phase"/*.md; do
        [[ -f "$f" ]] || continue
        ln -sf "$f" "$PROJECT_UCX/$phase/$(basename "$f")"
    done
done

# Create project README
cat > "$PROJECT_UCX/README.md" << EOF
# Project UCX Configuration

This directory contains UCX (Unified Context) configuration for this project.

## Structure

- \`skills/\` → Framework skills (symlink)
- \`creation/\` → UCC prompts (framework + project-specific)
- \`review/\` → UCR prompts (framework + project-specific)
- \`remediation/\` → UCRem prompts (framework + project-specific)

## Project-Specific Prompts

Create \`*_${PROJECT_SUFFIX}.md\` files to override framework prompts:

\`\`\`bash
# Example: Create BRD creation prompt for this project
cp creation/UCC_PROMPT_BRD.md creation/UCC_PROMPT_BRD_${PROJECT_SUFFIX}.md
# Edit with project-specific customizations
\`\`\`

## Usage

\`\`\`bash
# Create document
./creation/run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Review document
./review/run_ucr.sh brd docs/01_BRD/BRD-01

# Generate fixes
./remediation/run_ucrem.sh docs/01_BRD/BRD-01/BRD_UCR_REVIEW.md docs/01_BRD/BRD-01
\`\`\`
EOF

echo ""
echo "UCX initialized successfully!"
echo ""
echo "Next steps:"
echo "  1. Create project-specific prompts as needed:"
echo "     $PROJECT_UCX/creation/UCC_PROMPT_BRD_${PROJECT_SUFFIX}.md"
echo "     $PROJECT_UCX/review/UCR_PROMPT_BRD_${PROJECT_SUFFIX}.md"
echo "     $PROJECT_UCX/remediation/UCRem_PROMPT_BRD_${PROJECT_SUFFIX}.md"
echo ""
echo "  2. Run UCX workflow:"
echo "     ./docs/UCX/creation/run_ucc.sh brd docs/01_BRD/BRD-01"
```

### 5.3 Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 5.1.1 | Create `init_ucx.sh` project initialization script | M | 2.1.2 |
| 5.1.2 | Migrate b-local from `AI_EXPERTS/` to `UCX/` | M | 1.1.8 |
| 5.1.3 | Move b-local `*_BEELOCAL.md` prompts to new structure | S | 5.1.2 |
| 5.1.4 | Create b-local UCC project-specific prompts | M | 2.4.1 |
| 5.1.5 | Update b-local README | S | 5.1.2 |
| 5.1.6 | Test full UCx workflow on b-local BRD | M | 5.1.4 |

---

## Phase 6: Documentation Updates

### 6.1 Documentation Scope

Documentation updates span four categories:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Documentation Scope                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  UCX Internal   │    │   Framework     │                    │
│  │  Documentation  │    │  Documentation  │                    │
│  │                 │    │                 │                    │
│  │  - README       │    │  - ai_dev_flow  │                    │
│  │  - Methodology  │    │  - ai_dev_ssd   │                    │
│  │  - How-To       │    │  - SDD Layers   │                    │
│  │  - Personas     │    │  - Workflows    │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Claude Skills   │    │    Project      │                    │
│  │  Documentation  │    │  Documentation  │                    │
│  │                 │    │                 │                    │
│  │  - /doc-* help  │    │  - README       │                    │
│  │  - Examples     │    │  - CLAUDE.md    │                    │
│  │  - Deprecations │    │  - Setup Guide  │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6.2 UCX Internal Documentation

Documents within the `UCX/` directory:

| Document | Purpose | Status | Content Summary |
|----------|---------|--------|-----------------|
| `UCX/README.md` | Framework overview, quick start | UPDATE | Architecture, quick start, file structure |
| `UCX/CHANGELOG.md` | Version history | NEW | Version log, breaking changes, migration notes |
| `UCX/SKILL_INDEX.md` | Available skills reference | NEW | Skill catalog, persona mappings, usage examples |
| `UCX/docs/UNIFIED_CONTEXT_FRAMEWORK.md` | Complete UCx methodology | NEW | Philosophy, phases, integration, best practices |
| `UCX/docs/PERSONA_DESIGN_GUIDE.md` | Persona definitions | UPDATE | 12 personas, stances, layer mappings |
| `UCX/docs/HOW_TO_USE.md` | Step-by-step usage guide | NEW | Tutorials for UCC, UCR, UCRem |
| `UCX/docs/CROSS_LAYER_WORKFLOW.md` | Layer dependencies | NEW | Dependency graph, cascade workflow |
| `UCX/docs/TROUBLESHOOTING.md` | Common issues and solutions | NEW | Error handling, debugging, FAQs |

#### 6.2.1 UCX/README.md Structure

```markdown
# UCX - Unified Context Framework

## Overview
## Architecture
## Quick Start
  - UCC (Create)
  - UCR (Review)
  - UCRem (Remediate)
## File Structure
## Environment Variables
## Project Setup
## Documentation Reference
## Version History
```

#### 6.2.2 UNIFIED_CONTEXT_FRAMEWORK.md Structure

```markdown
# Unified Context Framework (UCx) Methodology

## 1. Philosophy
  - Multi-persona approach rationale
  - Single source of truth for skills
  - Consistency across document lifecycle

## 2. The Three Phases
  ### 2.1 UCC - Unified Context Creation
    - When to use
    - Author personas
    - Input sources (REF, upstream)
    - Output formats (single-file, multi-file)

  ### 2.2 UCR - Unified Context Review
    - When to use
    - Reviewer personas
    - Validation layers (schema, structure, content)
    - Priority classification (P0/P1/P2)

  ### 2.3 UCRem - Unified Context Remediation
    - When to use
    - Fixer personas
    - Confidence levels (auto-safe, auto-assisted, manual)
    - Fix application workflow

## 3. Persona System
  - Skill definitions
  - Layer-to-persona mappings
  - Persona stances (skeptical approach)

## 4. Cross-Layer Integration
  - Dependency graph
  - Upstream/downstream flow
  - Traceability

## 5. Project Customization
  - Framework vs project files
  - Project-specific prompts
  - Domain customization

## 6. Best Practices
  - When to use each phase
  - Iteration patterns
  - Quality gates
```

#### 6.2.3 HOW_TO_USE.md Structure

```markdown
# How to Use UCX

## Prerequisites
## Installation / Setup

## Tutorial 1: Create a BRD (UCC)
  - Step-by-step walkthrough
  - Example commands
  - Expected output

## Tutorial 2: Review a Document (UCR)
  - Running validation
  - Interpreting results
  - Handling P0/P1 findings

## Tutorial 3: Remediate Findings (UCRem)
  - Generating fix proposals
  - Applying auto-safe fixes
  - Completing auto-assisted fixes
  - Handling manual-required items

## Tutorial 4: Full Autopilot Workflow
  - End-to-end example
  - Iteration handling

## Tutorial 5: Project Customization
  - Creating project-specific prompts
  - Domain terminology
  - Custom P0 defaults
```

---

### 6.3 Framework-Level Documentation

Documentation outside UCX that references or integrates with UCX:

| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| `ai_dev_ssd_flow/README.md` | Framework root | SSD workflow overview | UPDATE |
| `ai_dev_flow/README.md` | Framework root | AI Dev Flow overview | UPDATE |
| `ai_dev_flow/SDD_METHODOLOGY.md` | Framework | SDD 12-layer methodology | UPDATE |
| `ai_dev_flow/WORKFLOW_GUIDE.md` | Framework | Document workflow guide | UPDATE |
| `ai_dev_flow/LAYER_REFERENCE.md` | Framework | Layer definitions | UPDATE |
| `ai_dev_flow/QUICK_START.md` | Framework | Getting started guide | UPDATE |

#### 6.3.1 Framework README Updates

Add UCX section to framework READMEs:

```markdown
## UCX - Unified Context Framework

UCX provides multi-persona document creation, review, and remediation.

### Phases
- **UCC** - Unified Context Creation (multi-persona authoring)
- **UCR** - Unified Context Review (multi-persona validation)
- **UCRem** - Unified Context Remediation (multi-persona fix generation)

### Quick Start
```bash
# Create document
./UCX/creation/run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Review document
./UCX/review/run_ucr.sh brd docs/01_BRD/BRD-01

# Remediate findings
./UCX/remediation/run_ucrem.sh BRD_UCR_REVIEW.md docs/01_BRD/BRD-01
```

See [UCX/README.md](UCX/README.md) for full documentation.
```

#### 6.3.2 SDD Methodology Updates

Update SDD documentation to reference UCX for each layer:

```markdown
## Layer 1: BRD (Business Requirements)

### Creation
Use UCX UCC phase: `./UCX/creation/run_ucc.sh brd`

### Validation
Use UCX UCR phase: `./UCX/review/run_ucr.sh brd`

### Remediation
Use UCX UCRem phase: `./UCX/remediation/run_ucrem.sh`

[Repeat for each layer...]
```

---

### 6.4 Claude Skills Documentation

Update Claude skill files to reference UCX:

| Skill Category | Files | Update Required |
|----------------|-------|-----------------|
| Creation skills | `/doc-brd`, `/doc-prd`, etc. | Reference UCC, update examples |
| Audit skills | `/doc-brd-audit`, `/doc-prd-audit`, etc. | Reference UCR, deprecate validators |
| Fixer skills | `/doc-brd-fixer`, `/doc-prd-fixer`, etc. | Reference UCRem |
| Autopilot skills | `/doc-brd-autopilot`, `/doc-prd-autopilot`, etc. | Reference full UCx workflow |
| Validator skills | `/doc-brd-validator`, etc. | Add deprecation notice |

#### 6.4.1 Skill Documentation Template

Each skill should include:

```markdown
# /doc-{type}

## Description
Create {TYPE} documents using UCx multi-persona authoring.

## UCx Integration
This skill uses the **UCX Unified Context Framework**:
- **Phase**: UCC (Unified Context Creation)
- **Runner**: `UCX/creation/run_ucc.sh`
- **Personas**: {list of author personas}

## Usage
/doc-{type} {DOC_ID} [options]

## Options
--from-ref <dir>       Load reference documents
--from-upstream <file> Load upstream artifact

## Examples
/doc-brd BRD-01 --from-ref docs/00_REF/
/doc-prd PRD-01 --from-upstream docs/01_BRD/BRD-01/

## Related Skills
- /doc-{type}-audit (UCR review)
- /doc-{type}-fixer (UCRem application)
- /doc-{type}-autopilot (full workflow)

## See Also
- UCX/docs/HOW_TO_USE.md
- UCX/creation/UCC_PROMPT_{TYPE}.md
```

#### 6.4.2 Deprecation Notice Template

For deprecated skills (e.g., validators):

```markdown
# /doc-{type}-validator

## ⚠️ DEPRECATED

This skill is deprecated. Validation is now integrated into `/doc-{type}-audit`.

### Migration
Instead of:
```
/doc-{type}-validator {DOC_ID}
/doc-{type}-audit {DOC_ID}
```

Use:
```
/doc-{type}-audit {DOC_ID}
```

The audit skill now runs both schema validation and content review.

### Removal Timeline
- Deprecated: v2.0.0 (2026-03-09)
- Removal: v3.0.0 (planned)
```

---

### 6.5 Project Documentation

Documentation for projects using UCX:

| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| `docs/UCX/README.md` | Project | Project UCX setup | CREATE |
| `CLAUDE.md` | Project root | Claude Code instructions | UPDATE |
| `docs/README.md` | Project docs | Documentation overview | UPDATE |

#### 6.5.1 Project UCX README Template

```markdown
# Project UCX Configuration

## Overview
This project uses UCX (Unified Context Framework) for document management.

## Structure
```
docs/UCX/
├── skills -> framework           # Symlink to framework skills
├── creation/                     # UCC prompts
│   ├── run_ucc.sh -> framework
│   ├── UCC_PROMPT_*.md -> framework
│   └── UCC_PROMPT_*_{PROJECT}.md # Project-specific
├── review/                       # UCR prompts
│   ├── run_ucr.sh -> framework
│   └── UCR_PROMPT_*_{PROJECT}.md
└── remediation/                  # UCRem prompts
    ├── run_ucrem.sh -> framework
    └── UCRem_PROMPT_*_{PROJECT}.md
```

## Project-Specific Customizations
- Domain terminology: {list}
- Custom P0 defaults: {list}
- Partner integrations: {list}

## Usage
[Project-specific usage examples]
```

#### 6.5.2 CLAUDE.md UCX Section

Add to project CLAUDE.md:

```markdown
### UCX Framework

This project uses UCX for document management:

**Document Creation**:
- Use `/doc-{type}` skills or `./docs/UCX/creation/run_ucc.sh`
- Project-specific prompts in `docs/UCX/creation/*_{PROJECT}.md`

**Document Review**:
- Use `/doc-{type}-audit` skills or `./docs/UCX/review/run_ucr.sh`
- Validators integrated into review

**Document Remediation**:
- Use `/doc-{type}-fixer` skills or `./docs/UCX/remediation/run_ucrem.sh`

**Full Workflow**:
- Use `/doc-{type}-autopilot` for end-to-end workflow
```

---

### 6.6 Persona Skill Documentation

Update each persona skill file in `UCX/skills/`:

| Skill File | Updates Required |
|------------|------------------|
| `architect.md` | Add UCC/UCR/UCRem role descriptions |
| `auditor.md` | Add UCC/UCR/UCRem role descriptions |
| `business_analyst.md` | Add UCC/UCR/UCRem role descriptions |
| `devils_advocate.md` | Add UCC/UCR/UCRem role descriptions |
| `integration_expert.md` | Add UCC/UCR/UCRem role descriptions |
| `operator.md` | Add UCC/UCR/UCRem role descriptions |
| `product_owner.md` | Add UCC/UCR/UCRem role descriptions |
| `qa_lead.md` | Add UCC/UCR/UCRem role descriptions |
| `requirements_specialist.md` | Add UCC/UCR/UCRem role descriptions |
| `strategist.md` | Add UCC/UCR/UCRem role descriptions |
| `tech_lead.md` | Add UCC/UCR/UCRem role descriptions |
| `ux_strategist.md` | Add UCC/UCR/UCRem role descriptions |

#### 6.6.1 Persona Skill Template

```markdown
# {Persona Name}

## Overview
{Brief description of persona expertise}

## Domain Expertise
- {Area 1}
- {Area 2}
- {Area 3}

## Skeptical Stance
{Describe the skeptical approach this persona takes}

## Role by UCx Phase

### UCC (Creation)
- **Contribution**: {What this persona adds during authoring}
- **Quality Gate**: {What this persona verifies}
- **Layers**: {Which layers use this persona for creation}

### UCR (Review)
- **Focus**: {What this persona reviews}
- **Red Flags**: {What triggers findings}
- **Layers**: {Which layers use this persona for review}

### UCRem (Remediation)
- **Fix Focus**: {What aspects of fixes this persona validates}
- **Flag for Manual**: {When this persona flags for manual review}

## Layer Assignments

| Layer | UCC | UCR | UCRem |
|-------|-----|-----|-------|
| L1 BRD | ✓ | ✓ | ✓ |
| L2 PRD | ✓ | ✓ | ✓ |
| ... | | | |
```

---

### 6.7 Documentation Tasks

#### 6.7.1 UCX Internal Documentation Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 6.1.1 | Create `UCX/README.md` with full structure | M | 1.1.6 |
| 6.1.2 | Create `UCX/CHANGELOG.md` | S | 1.1.1 |
| 6.1.3 | Create `UCX/SKILL_INDEX.md` with skill catalog | M | 4.1.12 |
| 6.1.4 | Create `UCX/docs/UNIFIED_CONTEXT_FRAMEWORK.md` | L | 2.1.2 |
| 6.1.5 | Update `UCX/docs/PERSONA_DESIGN_GUIDE.md` for UCx phases | M | 6.1.4 |
| 6.1.6 | Create `UCX/docs/HOW_TO_USE.md` with tutorials | L | 2.1.2 |
| 6.1.7 | Create `UCX/docs/CROSS_LAYER_WORKFLOW.md` | M | 2.1.2 |
| 6.1.8 | Create `UCX/docs/TROUBLESHOOTING.md` | M | 7.1.4 |

#### 6.7.2 Framework Documentation Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 6.2.1 | Update `ai_dev_ssd_flow/README.md` with UCX section | M | 6.1.1 |
| 6.2.2 | Update `ai_dev_flow/README.md` with UCX section | M | 6.1.1 |
| 6.2.3 | Update `ai_dev_flow/SDD_METHODOLOGY.md` for UCX | M | 6.1.4 |
| 6.2.4 | Update `ai_dev_flow/WORKFLOW_GUIDE.md` | M | 6.1.6 |
| 6.2.5 | Update layer documentation (L1-L10) with UCX references | L | 6.1.4 |
| 6.2.6 | Create `ai_dev_flow/UCX_INTEGRATION.md` cross-reference | M | 6.1.4 |

#### 6.7.3 Claude Skills Documentation Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 6.3.1 | Create skill documentation template | S | 4.1.1 |
| 6.3.2 | Update `/doc-brd` skill documentation | S | 4.1.2 |
| 6.3.3 | Update `/doc-brd-audit` skill documentation | S | 4.1.3 |
| 6.3.4 | Update `/doc-brd-fixer` skill documentation | S | 4.1.4 |
| 6.3.5 | Update `/doc-brd-autopilot` skill documentation | S | 4.1.5 |
| 6.3.6 | Create deprecation notice for `/doc-brd-validator` | S | 4.1.6 |
| 6.3.7 | Update all other layer skills (PRD, EARS, ADR, etc.) | M | 4.1.11 |
| 6.3.8 | Create skill quick-reference card | S | 6.3.7 |

#### 6.7.4 Project Documentation Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 6.4.1 | Create project UCX README template | S | 5.1.1 |
| 6.4.2 | Create CLAUDE.md UCX section template | S | 5.1.1 |
| 6.4.3 | Update b-local `docs/UCX/README.md` | S | 5.1.2 |
| 6.4.4 | Update b-local `CLAUDE.md` with UCX section | S | 5.1.2 |
| 6.4.5 | Update b-local `docs/README.md` | S | 5.1.2 |

#### 6.7.5 Persona Skill Documentation Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 6.5.1 | Create persona skill template | S | 6.1.5 |
| 6.5.2 | Update `architect.md` with UCx roles | S | 6.5.1 |
| 6.5.3 | Update `auditor.md` with UCx roles | S | 6.5.1 |
| 6.5.4 | Update `business_analyst.md` with UCx roles | S | 6.5.1 |
| 6.5.5 | Update `devils_advocate.md` with UCx roles | S | 6.5.1 |
| 6.5.6 | Update `integration_expert.md` with UCx roles | S | 6.5.1 |
| 6.5.7 | Update `operator.md` with UCx roles | S | 6.5.1 |
| 6.5.8 | Update `product_owner.md` with UCx roles | S | 6.5.1 |
| 6.5.9 | Update `qa_lead.md` with UCx roles | S | 6.5.1 |
| 6.5.10 | Update `requirements_specialist.md` with UCx roles | S | 6.5.1 |
| 6.5.11 | Update `strategist.md` with UCx roles | S | 6.5.1 |
| 6.5.12 | Update `tech_lead.md` with UCx roles | S | 6.5.1 |
| 6.5.13 | Update `ux_strategist.md` with UCx roles | S | 6.5.1 |

---

### 6.8 Documentation Checklist

Before Phase 6 completion, verify:

- [ ] UCX/README.md complete with architecture diagram
- [ ] UNIFIED_CONTEXT_FRAMEWORK.md covers all three phases
- [ ] HOW_TO_USE.md has working tutorials
- [ ] All 12 persona skills updated with UCx roles
- [ ] Framework READMEs reference UCX
- [ ] SDD methodology docs reference UCX for each layer
- [ ] All Claude skills have updated documentation
- [ ] Deprecated skills have deprecation notices
- [ ] Project templates created (README, CLAUDE.md)
- [ ] b-local project documentation updated
- [ ] CHANGELOG.md has complete version history
- [ ] TROUBLESHOOTING.md covers common issues

---

## Phase 7: Migration, Testing & Deprecation

### 7.1 Migration Strategy

1. **Create new UCX structure** (Phase 1-2)
2. **Keep AI_EXPERTS as symlink** during transition
3. **Update skills incrementally** (Phase 4)
4. **Validate with integration tests** (Phase 7)
5. **Deprecate AI_EXPERTS** after validation
6. **Remove symlink** in next major version

### 7.2 Rollback Procedures

| Scenario | Rollback Action |
|----------|-----------------|
| Phase 1 fails | Rename UCX back to AI_EXPERTS |
| Phase 2 fails | Remove creation/ directory, restore from backup |
| Phase 4 fails | Restore skills from git |
| Full rollback | `git checkout HEAD~1 -- AI_EXPERTS/` |

### 7.3 Integration Tests

| Test ID | Description | Validates |
|---------|-------------|-----------|
| T1 | Create BRD with UCC | Phase 2 |
| T2 | Review BRD with UCR | Phase 3 |
| T3 | Remediate BRD with UCRem | Phase 2 |
| T4 | Full autopilot workflow | Phase 4 |
| T5 | Project-specific prompt override | Phase 5 |
| T6 | Backward compatibility (AI_EXPERTS symlink) | Phase 7 |

### 7.4 Tasks

| Task ID | Description | Effort | Dependencies |
|---------|-------------|--------|--------------|
| 7.1.1 | Create migration checklist | S | - |
| 7.1.2 | Create backward compatibility symlink `AI_EXPERTS -> UCX` | S | 1.1.1 |
| 7.1.3 | Create integration test suite | M | 5.1.6 |
| 7.1.4 | Run integration tests | M | 7.1.3 |
| 7.1.5 | Update CI/CD scripts if applicable | S | 7.1.4 |
| 7.1.6 | Create deprecation notice in old locations | S | 7.1.4 |
| 7.1.7 | Document rollback procedures | S | 7.1.1 |

---

## Implementation Summary

### Task Count by Phase

| Phase | Description | Tasks | Effort |
|-------|-------------|-------|--------|
| **Phase 1** | Directory Restructure | 8 | M |
| **Phase 2** | UCC + UCRem Prompts | 23 | L |
| **Phase 3** | UCR Enhancement | 4 | M |
| **Phase 4** | Skills Refactoring | 13 | L |
| **Phase 5** | Project Setup | 6 | M |
| **Phase 6** | Documentation | 40 | L |
| **Phase 7** | Migration & Testing | 7 | M |
| **Total** | | **101** | |

### Phase 6 Documentation Breakdown

| Category | Tasks | Description |
|----------|-------|-------------|
| 6.1.x | 8 | UCX Internal Documentation |
| 6.2.x | 6 | Framework Documentation |
| 6.3.x | 8 | Claude Skills Documentation |
| 6.4.x | 5 | Project Documentation |
| 6.5.x | 13 | Persona Skill Documentation |
| **Total** | **40** | |

### Suggested Execution Order

1. **Phase 1** - Directory restructure (foundation)
2. **Phase 2** - UCC system + UCRem prompts (new capability)
3. **Phase 3** - UCR enhancement (integrate validators)
4. **Phase 6** - Documentation (capture changes)
5. **Phase 5** - Project setup (b-local migration)
6. **Phase 4** - Skills refactoring (incremental)
7. **Phase 7** - Migration, testing, cleanup (final)

### Critical Path

```
1.1.1 → 1.1.2 → 2.1.1 → 2.1.2 → 2.2.1 → 4.1.2 → 5.1.6 → 7.1.4
  │                                         │
  └──────────────────────────────────────────┘
           (Directory must exist first)
```

---

## Success Criteria

| Criterion | Metric | Validation |
|-----------|--------|------------|
| Single source of truth | All personas in `UCX/skills/` | Check no duplicate skill definitions |
| Consistent workflow | UCC → UCR → UCRem for all layers | Test autopilot on 3 layers |
| Backward compatibility | Existing `/doc-*` skills work | Run existing skill commands |
| Project customization | BeeLocal prompts override framework | Test project-specific prompt |
| Validators integrated | UCR includes schema validation | UCR output includes validation errors |
| Documentation complete | All UCx phases documented | Review docs for completeness |
| Tests pass | All integration tests green | Run test suite |

---

## Decision Log

| ID | Decision | Rationale | Date |
|----|----------|-----------|------|
| DP-1 | Directory name: `UCX/` | Short, represents framework brand | 2026-03-09 |
| DP-2 | Skills as thin wrappers | Maintain backward compatibility | 2026-03-09 |
| DP-3 | Subdirectories by phase | Clear organization | 2026-03-09 |
| DP-4 | Validators integrated into UCR | Unified review approach | 2026-03-09 |

---

## Appendix A: Complete File List

### Files to Create (New)

```
UCX/
├── ucx.sh                         # Optional unified entry point
├── CHANGELOG.md
├── SKILL_INDEX.md
│
├── creation/
│   ├── run_ucc.sh
│   ├── UCC_PERSONAS.md
│   ├── UCC_OUTPUT_SCHEMA.md
│   ├── UCC_PROMPT_BRD.md
│   ├── UCC_PROMPT_PRD.md
│   ├── UCC_PROMPT_EARS.md
│   ├── UCC_PROMPT_BDD.md
│   ├── UCC_PROMPT_ADR.md
│   ├── UCC_PROMPT_SYS.md
│   ├── UCC_PROMPT_REQ.md
│   ├── UCC_PROMPT_CTR.md
│   ├── UCC_PROMPT_SPEC.md
│   └── UCC_PROMPT_TSPEC.md
│
├── remediation/
│   ├── UCRem_PROMPT_PRD.md
│   ├── UCRem_PROMPT_EARS.md
│   ├── UCRem_PROMPT_BDD.md
│   ├── UCRem_PROMPT_ADR.md
│   ├── UCRem_PROMPT_SYS.md
│   ├── UCRem_PROMPT_REQ.md
│   ├── UCRem_PROMPT_CTR.md
│   ├── UCRem_PROMPT_SPEC.md
│   └── UCRem_PROMPT_TSPEC.md
│
├── docs/
│   ├── UNIFIED_CONTEXT_FRAMEWORK.md
│   ├── HOW_TO_USE.md
│   ├── CROSS_LAYER_WORKFLOW.md
│   └── TROUBLESHOOTING.md
│
└── init_ucx.sh
```

### Documentation Files to Create

```
# UCX Internal Documentation
UCX/README.md                              # Framework overview (rewrite)
UCX/CHANGELOG.md                           # Version history
UCX/SKILL_INDEX.md                         # Skill catalog
UCX/docs/UNIFIED_CONTEXT_FRAMEWORK.md      # Complete methodology
UCX/docs/HOW_TO_USE.md                     # Tutorials
UCX/docs/CROSS_LAYER_WORKFLOW.md           # Layer dependencies
UCX/docs/TROUBLESHOOTING.md                # Common issues

# Framework Documentation Updates
ai_dev_ssd_flow/README.md                  # Add UCX section
ai_dev_flow/README.md                      # Add UCX section
ai_dev_flow/UCX_INTEGRATION.md             # Cross-reference guide
ai_dev_flow/SDD_METHODOLOGY.md             # Update for UCX
ai_dev_flow/WORKFLOW_GUIDE.md              # Update for UCX

# Project Templates
UCX/templates/PROJECT_README.md            # Template for project UCX README
UCX/templates/CLAUDE_MD_SECTION.md         # Template for CLAUDE.md UCX section
```

### Persona Skill Files to Update

```
UCX/skills/
├── architect.md               # Add UCx role descriptions
├── auditor.md                 # Add UCx role descriptions
├── business_analyst.md        # Add UCx role descriptions
├── devils_advocate.md         # Add UCx role descriptions
├── integration_expert.md      # Add UCx role descriptions
├── operator.md                # Add UCx role descriptions
├── product_owner.md           # Add UCx role descriptions
├── qa_lead.md                 # Add UCx role descriptions
├── requirements_specialist.md # Add UCx role descriptions
├── strategist.md              # Add UCx role descriptions
├── tech_lead.md               # Add UCx role descriptions
└── ux_strategist.md           # Add UCx role descriptions
```

### Claude Skills to Update

```
~/.claude/commands/
├── doc-brd.md                 # Update for UCC
├── doc-brd-audit.md           # Update for UCR
├── doc-brd-fixer.md           # Update for UCRem
├── doc-brd-autopilot.md       # Update for full UCx
├── doc-brd-validator.md       # Add deprecation notice
├── doc-prd.md                 # Update for UCC
├── doc-prd-audit.md           # Update for UCR
├── doc-prd-fixer.md           # Update for UCRem
├── doc-prd-autopilot.md       # Update for full UCx
├── doc-prd-validator.md       # Add deprecation notice
├── doc-ears.md                # Update for UCC
├── doc-ears-audit.md          # Update for UCR
├── doc-ears-fixer.md          # Update for UCRem
├── doc-adr.md                 # Update for UCC
├── doc-adr-audit.md           # Update for UCR
├── doc-adr-fixer.md           # Update for UCRem
├── doc-bdd.md                 # Update for UCC
├── doc-bdd-audit.md           # Update for UCR
├── doc-bdd-fixer.md           # Update for UCRem
├── doc-sys.md                 # Update for UCC
├── doc-sys-audit.md           # Update for UCR
├── doc-req.md                 # Update for UCC
├── doc-req-audit.md           # Update for UCR
├── doc-ctr.md                 # Update for UCC
├── doc-ctr-audit.md           # Update for UCR
├── doc-spec.md                # Update for UCC
├── doc-spec-audit.md          # Update for UCR
├── doc-tspec.md               # Update for UCC
└── doc-tspec-audit.md         # Update for UCR
```

### Files to Move

```
AI_EXPERTS/run_ucr.sh         → UCX/review/run_ucr.sh
AI_EXPERTS/run_ucrem.sh       → UCX/remediation/run_ucrem.sh
AI_EXPERTS/UCR_PROMPT_*.md    → UCX/review/
AI_EXPERTS/UCRem_*.md         → UCX/remediation/
AI_EXPERTS/skills/            → UCX/skills/
AI_EXPERTS/README.md          → UCX/README.md (update)
AI_EXPERTS/UNIFIED_CONTEXT_REVIEW.md → UCX/docs/
AI_EXPERTS/PERSONA_DESIGN_GUIDE.md   → UCX/docs/
AI_EXPERTS/HOW_TO_AUDIT.md           → UCX/docs/
```

### Files to Update

```
UCX/README.md                 # New structure documentation
UCX/review/run_ucr.sh         # Integrate validators
UCX/remediation/run_ucrem.sh  # Update paths
All UCR_PROMPT_*.md           # Update internal references
All UCRem_PROMPT_*.md         # Update internal references
```

### Project Files (BeeLocal)

```
docs/UCX/
├── README.md                      # Create
├── creation/
│   ├── UCC_PROMPT_BRD_BEELOCAL.md # Create
│   └── UCC_PROMPT_PRD_BEELOCAL.md # Create
├── review/
│   └── UCR_PROMPT_BRD_BEELOCAL.md # Move from AI_EXPERTS
└── remediation/
    └── UCRem_PROMPT_BRD_BEELOCAL.md # Move from AI_EXPERTS
```

---

## Appendix B: Environment Variables

| Variable | Default | Phase | Description |
|----------|---------|-------|-------------|
| `UCC_MODEL` | opus | UCC | Claude model for creation |
| `UCC_LOAD_SKILLS` | true | UCC | Load persona skills |
| `UCC_PROMPT_DIR` | script dir | UCC | Custom prompt directory |
| `UCR_MODEL` | opus | UCR | Claude model for review |
| `UCR_LOAD_SKILLS` | true | UCR | Load persona skills |
| `UCR_PROMPT_DIR` | script dir | UCR | Custom prompt directory |
| `UCR_RUN_VALIDATORS` | true | UCR | Run schema validators first |
| `UCREM_MODEL` | opus | UCRem | Claude model for remediation |
| `UCREM_LOAD_SKILLS` | true | UCRem | Load fixer skills |
| `UCREM_PROMPT_DIR` | script dir | UCRem | Custom prompt directory |
| `FRAMEWORK_UCX` | /opt/.../UCX | init | Framework UCX location |
