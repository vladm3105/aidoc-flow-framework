# Unified Context (UCx) Framework

## Overview

The Unified Context (UCx) Framework provides a multi-persona approach to document creation, review, and remediation in the SDD (Specification-Driven Development) workflow.

---

## Three Phases

| Phase | Acronym | Purpose | Runner |
|-------|---------|---------|--------|
| **Creation** | UCC | Multi-persona document authoring | `run_ucc.sh` |
| **Review** | UCR | Multi-persona validation | `run_ucr.sh` |
| **Remediation** | UCRem | Multi-persona fix generation | `run_ucrem.sh` |

---

## Philosophy

### Why Multi-Persona?

Different stakeholders have different concerns:

| Stakeholder | Focus | Catches |
|-------------|-------|---------|
| Architect | Structure, patterns | Design flaws |
| Auditor | Compliance, security | Regulatory gaps |
| Tech Lead | Implementation | Technical issues |
| QA Lead | Testability | Verification gaps |
| Devil's Advocate | Edge cases | Hidden assumptions |

**A single reviewer misses what another catches.** UCx applies all relevant personas to every document.

### Error Philosophy

| Phase | Worse Error | Strategy |
|-------|-------------|----------|
| **UCC** | Missing content | Over-specify, let review trim |
| **UCR** | Missing finding (False Negative) | Flag when in doubt |
| **UCRem** | Incomplete fix (Under-fix) | Manual-required when uncertain |

---

## Framework Structure

```
UCX/
├── creation/           # UCC (Unified Context Creation)
│   ├── run_ucc.sh      # Creation runner
│   ├── UCC_PERSONAS.md # Author persona definitions
│   ├── UCC_PROMPT_*.md # Layer-specific prompts
│   └── UCC_OUTPUT_SCHEMA.md
│
├── review/             # UCR (Unified Context Review)
│   ├── run_ucr.sh      # Review runner (with validation)
│   ├── UCR_PROMPT_*.md # Layer-specific prompts
│   ├── UCR_OUTPUT_*.md # Output templates
│   └── validators/     # Schema validators
│
├── remediation/        # UCRem (Unified Context Remediation)
│   ├── run_ucrem.sh    # Remediation runner
│   ├── UCRem_PERSONAS.md
│   ├── UCRem_PROMPT_*.md
│   └── UCRem_REPORT_*.md
│
├── skills/             # Persona skill definitions
│   ├── architect.md
│   ├── auditor.md
│   ├── tech_lead.md
│   └── ...
│
├── docs/               # Documentation (this directory)
│   ├── UNIFIED_CONTEXT_FRAMEWORK.md
│   ├── HOW_TO_USE.md
│   └── PERSONA_DESIGN_GUIDE.md
│
├── init_ucx.sh         # Project initialization script
└── SKILL_INDEX.md      # Claude skill integration guide
```

---

## Layer Coverage

UCx supports all SDD layers:

| Layer | Type | Creation | Review | Remediation |
|-------|------|----------|--------|-------------|
| 1 | BRD | ✓ | ✓ | ✓ |
| 2 | PRD | ✓ | ✓ | ✓ |
| 3 | EARS | ✓ | ✓ | ✓ |
| 4 | BDD | ✓ | ✓ | ✓ |
| 5 | ADR | ✓ | ✓ | ✓ |
| 6 | SYS | ✓ | ✓ | ✓ |
| 7 | REQ | ✓ | ✓ | ✓ |
| 8 | CTR | ✓ | ✓ | ✓ |
| 9 | SPEC | ✓ | ✓ | ✓ |
| 10 | TSPEC | ✓ | ✓ | ✓ |

---

## Cross-Layer Dependencies

```
L1 BRD ──┬──▶ L2 PRD ──▶ L3 EARS ──▶ L4 BDD
         │
         └──▶ L5 ADR ──▶ L6 SYS ──▶ L7 REQ ──┬──▶ L8 CTR
                                              │
                                              └──▶ L9 SPEC ──▶ L10 TSPEC
```

UCx handles dependencies with:
- `--from-ref`: Load reference documents
- `--from-upstream`: Load upstream artifacts

---

## Project-Specific Customization

### Framework vs Project Files

| Type | Location | Purpose |
|------|----------|---------|
| **Framework** | `/opt/data/.../UCX/` | Generic prompts, shared personas |
| **Project** | `./docs/UCX/` | Domain-specific prompts |

### Project Prompt Naming

Create project-specific prompts with naming convention:

- `UCC_PROMPT_BRD_PROJECT.md` - Generic project override
- `UCC_PROMPT_BRD_BEELOCAL.md` - Named project override

Runners automatically prefer project-specific prompts.

---

## Integration with Claude Skills

UCx integrates with Claude skills via thin wrappers:

| Skill | UCx Phase |
|-------|-----------|
| `/doc-{type}` | UCC |
| `/doc-{type}-audit` | UCR |
| `/doc-{type}-fixer` | UCRem |
| `/doc-{type}-autopilot` | UCC → UCR → UCRem |

See `SKILL_INDEX.md` for complete mapping.

---

## Quick Start

### 1. Initialize for Project

```bash
/opt/data/.../UCX/init_ucx.sh ./docs/UCX
```

### 2. Create Document

```bash
./docs/UCX/creation/run_ucc.sh brd ./docs/01_BRD/ --from-ref ./docs/00_REF/
```

### 3. Review Document

```bash
./docs/UCX/review/run_ucr.sh brd ./docs/01_BRD/
```

### 4. Generate Fixes

```bash
./docs/UCX/remediation/run_ucrem.sh ./docs/01_BRD/BRD_UCR_REVIEW.md ./docs/01_BRD/
```

---

## See Also

- `HOW_TO_USE.md` - Detailed usage guide
- `PERSONA_DESIGN_GUIDE.md` - Creating custom personas
- `CROSS_LAYER_WORKFLOW.md` - Layer dependencies
- `SKILL_INDEX.md` - Claude skill integration
