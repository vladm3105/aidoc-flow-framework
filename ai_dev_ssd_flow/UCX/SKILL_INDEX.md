# UCx Skill Index

This document maps Claude Skills to the UCx framework phases.

---

## Overview

The UCx framework provides three phases that map to existing Claude Skills:

| UCx Phase | Purpose | Runner Script |
|-----------|---------|---------------|
| **UCC** | Document Creation | `creation/run_ucc.sh` |
| **UCR** | Document Review | `review/run_ucr.sh` |
| **UCRem** | Document Remediation | `remediation/run_ucrem.sh` |

---

## Skill Mapping

### Layer 1: BRD (Business Requirements)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-brd` | UCC | `run_ucc.sh brd` |
| `/doc-brd-audit` | UCR | `run_ucr.sh brd` |
| `/doc-brd-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-brd-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-brd-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 2: PRD (Product Requirements)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-prd` | UCC | `run_ucc.sh prd` |
| `/doc-prd-audit` | UCR | `run_ucr.sh prd` |
| `/doc-prd-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-prd-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-prd-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 3: EARS (Formal Requirements)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-ears` | UCC | `run_ucc.sh ears` |
| `/doc-ears-audit` | UCR | `run_ucr.sh ears` |
| `/doc-ears-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-ears-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-ears-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 4: BDD (Behavior Scenarios)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-bdd` | UCC | `run_ucc.sh bdd` |
| `/doc-bdd-audit` | UCR | `run_ucr.sh bdd` |
| `/doc-bdd-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-bdd-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-bdd-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 5: ADR (Architecture Decisions)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-adr` | UCC | `run_ucc.sh adr` |
| `/doc-adr-audit` | UCR | `run_ucr.sh adr` |
| `/doc-adr-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-adr-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-adr-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 6: SYS (System Requirements)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-sys` | UCC | `run_ucc.sh sys` |
| `/doc-sys-audit` | UCR | `run_ucr.sh sys` |
| `/doc-sys-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-sys-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-sys-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 7: REQ (Atomic Requirements)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-req` | UCC | `run_ucc.sh req` |
| `/doc-req-audit` | UCR | `run_ucr.sh req` |
| `/doc-req-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-req-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-req-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 8: CTR (Data Contracts)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-ctr` | UCC | `run_ucc.sh ctr` |
| `/doc-ctr-audit` | UCR | `run_ucr.sh ctr` |
| `/doc-ctr-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-ctr-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-ctr-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 9: SPEC (Technical Specification)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-spec` | UCC | `run_ucc.sh spec` |
| `/doc-spec-audit` | UCR | `run_ucr.sh spec` |
| `/doc-spec-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-spec-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-spec-validator` | **DEPRECATED** | Integrated into UCR |

### Layer 10: TSPEC (Test Specification)

| Current Skill | UCx Phase | Integration |
|---------------|-----------|-------------|
| `/doc-tspec` | UCC | `run_ucc.sh tspec` |
| `/doc-tspec-audit` | UCR | `run_ucr.sh tspec` |
| `/doc-tspec-fixer` | UCRem | `run_ucrem.sh <report> <doc>` |
| `/doc-tspec-autopilot` | All | UCC → UCR → UCRem orchestration |
| `/doc-tspec-validator` | **DEPRECATED** | Integrated into UCR |

---

## Refactored Skill Template

### Creation Skill (`/doc-{type}`)

```markdown
# /doc-{type}

Create {TYPE} documents using UCx multi-persona authoring.

## Usage
/doc-{type} [doc_id] [options]

## Options
- `--from-ref <dir>`: Load reference documents
- `--from-upstream <file>`: Load upstream artifact
- `--template <file>`: Use specific template

## UCx Integration
Invokes: `UCX/creation/run_ucc.sh {type} <output> [options]`

## Personas
{List layer-specific personas from UCC_PERSONAS.md}
```

### Audit Skill (`/doc-{type}-audit`)

```markdown
# /doc-{type}-audit

Review {TYPE} documents using UCx multi-persona validation.

## Usage
/doc-{type}-audit <document_path> [output_file]

## UCx Integration
Invokes: `UCX/review/run_ucr.sh {type} <document> [output]`

## Phases
1. Validation (automated schema checks)
2. Content Review (multi-persona analysis)

## Output
Unified UCR report with P0/P1/P2 findings.
```

### Fixer Skill (`/doc-{type}-fixer`)

```markdown
# /doc-{type}-fixer

Apply UCRem fix proposals to {TYPE} documents.

## Usage
/doc-{type}-fixer <review_report> <document_path>

## UCx Integration
Invokes: `UCX/remediation/run_ucrem.sh <report> <document>`

## Fix Categories
- auto-safe: Apply automatically
- auto-assisted: Apply template, prompt for TODOs
- manual-required: Flag for human review
```

### Autopilot Skill (`/doc-{type}-autopilot`)

```markdown
# /doc-{type}-autopilot

Full UCx workflow for {TYPE} documents.

## Usage
/doc-{type}-autopilot [doc_id] [options]

## Workflow
1. UCC: Create document (if not exists)
2. UCR: Review and validate
3. UCRem: Generate fix proposals
4. Apply: Apply auto-safe fixes
5. Re-validate: Verify fixes

## Options
- `--from-upstream <file>`: Source artifact
- `--max-iterations <n>`: Max fix iterations (default: 3)
- `--auto-apply`: Auto-apply all auto-safe fixes
```

---

## Migration Notes

### Deprecated Skills

The following skills are deprecated in favor of UCR integrated validation:

- `/doc-brd-validator`
- `/doc-prd-validator`
- `/doc-ears-validator`
- `/doc-bdd-validator`
- `/doc-adr-validator`
- `/doc-sys-validator`
- `/doc-req-validator`
- `/doc-ctr-validator`
- `/doc-spec-validator`
- `/doc-tspec-validator`

**Migration**: Remove these skills and use `/doc-{type}-audit` instead.

### Environment Variables

Skills should check for these environment variables:

```bash
UCX_FRAMEWORK_DIR="/opt/data/docs_flow_framework/ai_dev_ssd_flow/UCX"
UCX_PROJECT_DIR="./docs/UCX"  # Project-specific
UCR_LOAD_SKILLS="true"
UCR_MODEL="opus"
UCC_MODEL="opus"
```

---

## See Also

- `creation/UCC_PERSONAS.md` - Author persona definitions
- `review/UCR_OUTPUT_UNIFIED.md` - Unified output format
- `remediation/UCRem_REPORT_SCHEMA.md` - Fix entry schema
