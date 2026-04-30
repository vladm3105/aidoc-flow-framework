# File Size Limits Standardization Fix Plan

**Created**: 2026-02-26
**Status**: Draft
**Version**: 1.2 (Added gaps #41-47: ID_NAMING_STANDARDS, additional QUICK_REFERENCE, BDD fix plan)
**Objective**: Standardize all file size limits across the framework to 800/1200 lines

## Overview

Standardize document file size limits to:
- **Target**: 800 lines per file
- **Maximum**: 1200 lines per file (absolute)

This replaces the inconsistent 300-500/600 limits currently scattered across various templates, schemas, and validation rules.

## Current State Analysis

| Current Limit | Count | Files Affected |
|---------------|-------|----------------|
| 800/1200 (correct) | 3 | BRD README, scripts README, lint_file_sizes.sh |
| 300-500/600 | 17 | READMEs, templates, schemas, framework docs, ID_NAMING_STANDARDS |
| 500 line threshold | 14 | BDD files, skills, QUICK_REFERENCE, BDD fix plan |
| 600 only (CORPUS-W005) | 8 | Quality Gate validations |

**Total unique files to update**: 39

## Gap Summary

| # | Gap | Severity | File | Line(s) |
|---|-----|----------|------|---------|
| **Phase 1: README Files** |
| 1 | PRD README: 300-500/600 | High | `02_PRD/README.md` | 424-425 |
| 2 | EARS README: 600 max | High | `03_EARS/README.md` | 281 |
| 3 | BDD README: 300-500/600 | High | `04_BDD/README.md` | 560-561 |
| **Phase 2: Creation Rules & Templates** |
| 4 | BDD Creation Rules: 300-500/600 | High | `04_BDD/BDD_MVP_CREATION_RULES.md` | 431-433 |
| 5 | CTR Template: 300-500/600 | Medium | `08_CTR/CTR-MVP-TEMPLATE.md` | 630 |
| **Phase 3: Schemas** |
| 6 | BDD Schema: max_file_lines 600 | High | `04_BDD/BDD_MVP_SCHEMA.yaml` | 261 |
| 7 | BDD Schema: split at 500 lines | High | `04_BDD/BDD_MVP_SCHEMA.yaml` | 195, 199, 201, 249, 264 |
| 8 | SPEC Schema: 600 line rule | High | `09_SPEC/SPEC_MVP_SCHEMA.yaml` | 881, 1100 |
| **Phase 4: Quality Gate Validations** |
| 9 | BRD QG: 600 warning, 1200 error | Medium | `01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md` | 218-220, 498, 510-514, 521-542, 580, 723-735 |
| 10 | PRD QG: 600 warning, 1200 error | Medium | `02_PRD/PRD_MVP_QUALITY_GATE_VALIDATION.md` | 344, 353, 355, 726 |
| 11 | EARS QG: CORPUS-W005 600 | Medium | `03_EARS/EARS_MVP_QUALITY_GATE_VALIDATION.md` | 473 |
| 12 | BDD QG: 600 lines tables | Medium | `04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md` | 316, 321-323, 548 |
| 13 | ADR QG: CORPUS-W005 600 | Medium | `05_ADR/ADR_MVP_QUALITY_GATE_VALIDATION.md` | 464, 836 |
| 14 | SYS QG: CORPUS-W005 600 | Medium | `06_SYS/SYS_MVP_QUALITY_GATE_VALIDATION.md` | 501 |
| 15 | REQ QG: CORPUS-W005 600 | Medium | `07_REQ/REQ_MVP_QUALITY_GATE_VALIDATION.md` | 625 |
| 16 | SPEC QG: CORPUS-W005 600 | Medium | `09_SPEC/SPEC_MVP_QUALITY_GATE_VALIDATION.md` | 391 |
| **Phase 5: Framework-Level Documents** |
| 17 | QUICK_REFERENCE: 300-500/600 | High | `QUICK_REFERENCE.md` | 426-427 |
| 18 | SPEC_DRIVEN_DEVELOPMENT_GUIDE: 400-500 | Medium | `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | 1250 |
| 19 | FINANCIAL_DOMAIN_CONFIG: 300-500 | Low | `FINANCIAL_DOMAIN_CONFIG.md` | TBD |
| **Phase 6: Skills** |
| 20 | doc-ears/SKILL.md: file size refs | Medium | `.claude/skills/doc-ears/SKILL.md` | TBD |
| 21 | doc-adr/SKILL.md: file size refs | Medium | `.claude/skills/doc-adr/SKILL.md` | TBD |
| **Phase 7: Archive/Examples (Low Priority)** |
| 22 | PRD archive template | Low | `02_PRD/archive/PRD-TEMPLATE.md` | 1399-1400 |
| 23 | BDD Generation Checklist | Low | `04_BDD/BDD_GENERATION_CHECKLIST.md` | TBD |
| 24 | ADR example | Low | `05_ADR/examples/ADR-01_database_selection.md` | TBD |
| 25 | SYS examples | Low | `06_SYS/examples/SYS-03_DEPLOYMENT_EXAMPLE.md` | TBD |
| 26 | SYS examples | Low | `06_SYS/examples/SYS-04_LOGIC-ONLY_EXAMPLE.md` | TBD |
| 27 | CTR example | Low | `08_CTR/examples/CTR-01_service_contract_example.md` | TBD |
| 28 | SYS archive | Low | `tmp/archive/SYS-00_index.md` | 381, 387 |
| **Phase 8: Additional BDD Files (NEW)** |
| 29 | BDD README: additional 500 pattern | High | `04_BDD/README.md` | 568 |
| 30 | BDD Validation Rules: 500 line refs | High | `04_BDD/BDD_MVP_VALIDATION_RULES.md` | 280, 282, 285, 565, 679, 783 |
| 31 | BDD Creation Rules: 500 line refs | High | `04_BDD/BDD_MVP_CREATION_RULES.md` | 85, 91, 249, 266, 269, 442, 517, 584 |
| 32 | BDD Generation Checklist: 500 line refs | Medium | `04_BDD/BDD_GENERATION_CHECKLIST.md` | 166, 178, 263 |
| **Phase 9: Additional Templates (NEW)** |
| 33 | BRD Template: 500 line ref | Medium | `01_BRD/BRD-MVP-TEMPLATE.md` | 1020 |
| 34 | PRD README: ~500 description | Low | `02_PRD/README.md` | 27 |
| **Phase 10: QUICK_REFERENCE Additional (NEW)** |
| 35 | QUICK_REFERENCE: 500 line refs | High | `QUICK_REFERENCE.md` | 462, 465, 469 |
| **Phase 11: Skills - BDD (NEW)** |
| 36 | doc-bdd-autopilot: 500 line refs | High | `.claude/skills/doc-bdd-autopilot/SKILL.md` | 329, 492, 1625 |
| 37 | doc-bdd: 500 line refs | High | `.claude/skills/doc-bdd/SKILL.md` | 94, 110, 440, 516, 553, 624 |
| **Phase 12: Skills - EARS (NEW)** |
| 38 | doc-ears-autopilot: 300 line refs | Medium | `.claude/skills/doc-ears-autopilot/SKILL.md` | 299, 1342 |
| 39 | doc-ears: 300-500/600 refs | High | `.claude/skills/doc-ears/SKILL.md` | 358-362, 545, 605, 620 |
| **Phase 13: Skills - ADR (NEW)** |
| 40 | doc-adr: 300-500/600 refs | High | `.claude/skills/doc-adr/SKILL.md` | 192-193, 543 |
| **Phase 14: Framework Standards (NEW v1.2)** |
| 41 | ID_NAMING_STANDARDS: 500 line refs | High | `ID_NAMING_STANDARDS.md` | 298, 302 |
| **Phase 15: Additional QUICK_REFERENCE (NEW v1.2)** |
| 42 | QUICK_REFERENCE: lint comment | Medium | `QUICK_REFERENCE.md` | 240 |
| 43 | QUICK_REFERENCE: exceeds limits | Medium | `QUICK_REFERENCE.md` | 434 |
| **Phase 16: BDD Fix Plan (NEW v1.2)** |
| 44 | BDD-MVP-TEMPLATE_FIX_PLAN: 300-500/600 | Medium | `04_BDD/BDD-MVP-TEMPLATE_FIX_PLAN.md` | 362-369, 465 |
| **Phase 17: Additional BDD Files (NEW v1.2)** |
| 45 | BDD Creation Rules: additional 236 | High | `04_BDD/BDD_MVP_CREATION_RULES.md` | 236 |
| 46 | BDD Generation Checklist: additional | Medium | `04_BDD/BDD_GENERATION_CHECKLIST.md` | 104, 380 |
| **Phase 18: Archive (Low Priority v1.2)** |
| 47 | IMPL GUIDE archive: 500 ref | Low | `11_TASKS/archive/IMPLEMENTATION_GUIDE.md` | 396 |

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ucx_flow_v3/.backup_file_size_limits_2026-02-26

# Backup affected files
cd /opt/data/docs_flow_framework/ucx_flow_v3

# READMEs
cp 02_PRD/README.md .backup_file_size_limits_2026-02-26/PRD_README.md
cp 03_EARS/README.md .backup_file_size_limits_2026-02-26/EARS_README.md
cp 04_BDD/README.md .backup_file_size_limits_2026-02-26/BDD_README.md

# Creation Rules & Templates
cp 04_BDD/BDD_MVP_CREATION_RULES.md .backup_file_size_limits_2026-02-26/
cp 08_CTR/CTR-MVP-TEMPLATE.md .backup_file_size_limits_2026-02-26/

# Schemas
cp 04_BDD/BDD_MVP_SCHEMA.yaml .backup_file_size_limits_2026-02-26/
cp 09_SPEC/SPEC_MVP_SCHEMA.yaml .backup_file_size_limits_2026-02-26/

# Quality Gate Validations
cp 01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 02_PRD/PRD_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 03_EARS/EARS_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 05_ADR/ADR_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 06_SYS/SYS_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 07_REQ/REQ_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/
cp 09_SPEC/SPEC_MVP_QUALITY_GATE_VALIDATION.md .backup_file_size_limits_2026-02-26/

# Framework docs
cp QUICK_REFERENCE.md .backup_file_size_limits_2026-02-26/
cp SPEC_DRIVEN_DEVELOPMENT_GUIDE.md .backup_file_size_limits_2026-02-26/

# Skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-ears .backup_file_size_limits_2026-02-26/
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-adr .backup_file_size_limits_2026-02-26/
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-bdd .backup_file_size_limits_2026-02-26/
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-bdd-autopilot .backup_file_size_limits_2026-02-26/
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-ears-autopilot .backup_file_size_limits_2026-02-26/

# Additional BDD files
cp 04_BDD/BDD_MVP_VALIDATION_RULES.md .backup_file_size_limits_2026-02-26/
cp 04_BDD/BDD_GENERATION_CHECKLIST.md .backup_file_size_limits_2026-02-26/

# Additional templates
cp 01_BRD/BRD-MVP-TEMPLATE.md .backup_file_size_limits_2026-02-26/

# v1.2 additions - Framework standards
cp ID_NAMING_STANDARDS.md .backup_file_size_limits_2026-02-26/
cp 04_BDD/BDD-MVP-TEMPLATE_FIX_PLAN.md .backup_file_size_limits_2026-02-26/
cp 11_TASKS/archive/IMPLEMENTATION_GUIDE.md .backup_file_size_limits_2026-02-26/
```

### 0.2 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   cd /opt/data/docs_flow_framework/ucx_flow_v3
   cp .backup_file_size_limits_2026-02-26/PRD_README.md 02_PRD/README.md
   cp .backup_file_size_limits_2026-02-26/EARS_README.md 03_EARS/README.md
   # ... (restore all files from backup)
   ```

2. **Partial Rollback**: Revert only affected files from backup

---

## Phase 1: README Files (High Priority)

### 1.1 PRD README.md

**File**: `02_PRD/README.md`
**Lines**: 424-425

**Current**:
```markdown
- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute)
```

**Change to**:
```markdown
- Target: 800 lines per file
- Maximum: 1200 lines per file (absolute)
```

### 1.2 EARS README.md

**File**: `03_EARS/README.md`
**Line**: 281

**Current**:
```markdown
- Maximum: 600 lines per file (absolute)
```

**Change to**:
```markdown
- Target: 800 lines per file
- Maximum: 1200 lines per file (absolute)
```

### 1.3 BDD README.md

**File**: `04_BDD/README.md`
**Lines**: 560-561

**Current**:
```markdown
- **Target**: 300-500 lines per `.feature` file
- **Maximum**: 600 lines per `.feature` file (absolute)
```

**Change to**:
```markdown
- **Target**: 800 lines per `.feature` file
- **Maximum**: 1200 lines per `.feature` file (absolute)
```

---

## Phase 2: Creation Rules & Templates

### 2.1 BDD Creation Rules

**File**: `04_BDD/BDD_MVP_CREATION_RULES.md`
**Lines**: 431-433

**Current**:
```markdown
- **Target**: 300–500 lines per `.feature` file
- **Maximum**: 600 lines (absolute)
- **Action**: If section exceeds 600 lines or approaches the upper target → Split
```

**Change to**:
```markdown
- **Target**: 800 lines per `.feature` file
- **Maximum**: 1200 lines (absolute)
- **Action**: If section exceeds 1200 lines or approaches the upper target → Split
```

### 2.2 CTR Template

**File**: `08_CTR/CTR-MVP-TEMPLATE.md`
**Line**: 630

**Current**:
```markdown
> - Target: 300–500 lines; Maximum: 600 lines (Markdown)
```

**Change to**:
```markdown
> - Target: 800 lines; Maximum: 1200 lines (Markdown)
```

---

## Phase 3: Schemas

### 3.1 BDD Schema

**File**: `04_BDD/BDD_MVP_SCHEMA.yaml`

**Changes needed**:

1. **Line 195**: Change `≤500 lines` to `≤800 lines`
2. **Line 199**: Change `section >500 lines` to `section >800 lines`
3. **Line 201**: Change `≤500 lines` to `≤800 lines`
4. **Line 249**: Change `>500 lines` to `>800 lines`
5. **Line 261**: Change `max_file_lines: 600` to `max_file_lines: 1200`
6. **Line 264**: Change `exceeds 500 lines` to `exceeds 800 lines`

### 3.2 SPEC Schema

**File**: `09_SPEC/SPEC_MVP_SCHEMA.yaml`

**Changes needed**:

1. **Line 881**: Change `not exceed 600 lines` to `not exceed 1200 lines`
2. **Line 1100**: Change `exceeds 600 lines (target: 300-500)` to `exceeds 1200 lines (target: 800)`

---

## Phase 4: Quality Gate Validations

### 4.1 Common Pattern: CORPUS-W005

All Quality Gate validation files have `CORPUS-W005` which references 600 lines. Update in:
- `01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md`
- `02_PRD/PRD_MVP_QUALITY_GATE_VALIDATION.md`
- `03_EARS/EARS_MVP_QUALITY_GATE_VALIDATION.md`
- `04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md`
- `05_ADR/ADR_MVP_QUALITY_GATE_VALIDATION.md`
- `06_SYS/SYS_MVP_QUALITY_GATE_VALIDATION.md`
- `07_REQ/REQ_MVP_QUALITY_GATE_VALIDATION.md`
- `09_SPEC/SPEC_MVP_QUALITY_GATE_VALIDATION.md`

**Standard change for CORPUS-W005**:
```markdown
# From:
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |

# To:
| CORPUS-W005 | File exceeds 1200 lines | CORPUS-10 |
```

### 4.2 BRD Quality Gate

**File**: `01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md`

Multiple locations need updating:
- Line 218-220: Target/Error thresholds
- Line 498: Severity description
- Lines 510-514: File type table
- Lines 521-542: Bash script thresholds
- Line 580: CORPUS-W005
- Lines 723-735: Additional script thresholds

### 4.3 PRD Quality Gate

**File**: `02_PRD/PRD_MVP_QUALITY_GATE_VALIDATION.md`

- Line 344: Severity description
- Line 353: Target lines
- Line 355: Error threshold
- Line 726: CORPUS-W005

### 4.4 BDD Quality Gate

**File**: `04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md`

- Line 316: Severity description
- Lines 321-323: File type table
- Line 548: CORPUS-W005

---

## Phase 5: Framework-Level Documents

### 5.1 QUICK_REFERENCE.md

**File**: `QUICK_REFERENCE.md`
**Lines**: 426-427

**Current**:
```markdown
- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute) for Markdown and feature files
```

**Change to**:
```markdown
- Target: 800 lines per file
- Maximum: 1200 lines per file (absolute) for Markdown and feature files
```

### 5.2 SPEC_DRIVEN_DEVELOPMENT_GUIDE.md

**File**: `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
**Line**: 1250

**Current**:
```markdown
  - Target 400-500 lines per domain-focused REQ with complete technical specifications
```

**Change to**:
```markdown
  - Target 800 lines per domain-focused REQ with complete technical specifications
```

---

## Phase 6: Skills (Original)

### 6.1 doc-ears/SKILL.md

**File**: `.claude/skills/doc-ears/SKILL.md`

**Lines to update**:
- Lines 358-359: Change `300-500 lines` / `600 lines` to `800` / `1200 lines`
- Line 362: Change `600 lines` to `1200 lines`
- Line 545: Change `<600 lines` to `<1200 lines`
- Line 605: Change `>300 lines` to `>800 lines`
- Line 620: Change `600 lines maximum` to `1200 lines maximum`

### 6.2 doc-adr/SKILL.md

**File**: `.claude/skills/doc-adr/SKILL.md`

**Lines to update**:
- Lines 192-193: Change `300-500 lines` / `600 lines` to `800` / `1200 lines`
- Line 543: Change `300-500 lines target, 600 max` to `800 lines target, 1200 max`

---

## Phase 7: Archive/Examples (Low Priority)

These files are in archive or examples directories and have lower priority:

- `02_PRD/archive/PRD-TEMPLATE.md`
- `04_BDD/BDD_GENERATION_CHECKLIST.md`
- `05_ADR/examples/ADR-01_database_selection.md`
- `06_SYS/examples/SYS-03_DEPLOYMENT_EXAMPLE.md`
- `06_SYS/examples/SYS-04_LOGIC-ONLY_EXAMPLE.md`
- `08_CTR/examples/CTR-01_service_contract_example.md`
- `tmp/archive/SYS-00_index.md`

---

## Phase 8: Additional BDD Files (NEW)

### 8.1 BDD README Additional

**File**: `04_BDD/README.md`
**Line**: 568

**Current**:
```markdown
- Primary files: `BDD-NN.SS_{slug}.feature` (≤12 scenarios; target 300–500 lines)
```

**Change to**:
```markdown
- Primary files: `BDD-NN.SS_{slug}.feature` (≤12 scenarios; target 800 lines)
```

### 8.2 BDD Validation Rules

**File**: `04_BDD/BDD_MVP_VALIDATION_RULES.md`

**Lines to update** (change 500 → 800):
- Line 280: `≤500 lines` → `≤800 lines`
- Line 282: `>500 Lines` → `>800 Lines`
- Line 285: `≤500 lines` → `≤800 lines`
- Line 565: `exceeds 500 lines` → `exceeds 800 lines`
- Line 679: `exceeding 500 lines` → `exceeding 800 lines`
- Line 783: `exceeds 500 lines` → `exceeds 800 lines`

### 8.3 BDD Creation Rules Additional

**File**: `04_BDD/BDD_MVP_CREATION_RULES.md`

**Lines to update** (change 500 → 800):
- Line 85: `< 500 lines` → `< 800 lines`
- Line 91: `exceed 500 lines` → `exceed 800 lines`
- Line 249: `≤500 lines` → `≤800 lines`
- Line 266: `>500 Lines` → `>800 Lines`
- Line 269: `≤500 lines` → `≤800 lines`
- Line 442: `>500 lines` → `>800 lines`
- Line 517: `>500 lines` → `>800 lines`
- Line 584: `exceeds 500 lines` → `exceeds 800 lines`

### 8.4 BDD Generation Checklist

**File**: `04_BDD/BDD_GENERATION_CHECKLIST.md`

**Lines to update**:
- Line 166: `exceeds 500 lines` → `exceeds 800 lines`
- Line 178: `≤500 lines` → `≤800 lines`
- Line 263: `exceeds 500 lines` → `exceeds 800 lines`

---

## Phase 9: Additional Templates (NEW)

### 9.1 BRD Template

**File**: `01_BRD/BRD-MVP-TEMPLATE.md`
**Line**: 1020

**Current**:
```markdown
- **If exceeding 500 lines**: Consider splitting scope across multiple BRD cycles
```

**Change to**:
```markdown
- **If exceeding 800 lines**: Consider splitting scope across multiple BRD cycles
```

### 9.2 PRD README Description

**File**: `02_PRD/README.md`
**Line**: 27

**Current**:
```markdown
**PRD-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file without sectioning (~500 lines)
```

**Change to**:
```markdown
**PRD-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file without sectioning (~800 lines)
```

---

## Phase 10: QUICK_REFERENCE Additional (NEW)

**File**: `QUICK_REFERENCE.md`

**Lines to update**:
- Line 462: `≤500 lines` → `≤800 lines`
- Line 465: `>500 Lines` → `>800 Lines`
- Line 469: `≤500 lines` → `≤800 lines`

---

## Phase 11: Skills - BDD (NEW)

### 11.1 doc-bdd-autopilot/SKILL.md

**File**: `.claude/skills/doc-bdd-autopilot/SKILL.md`

**Lines to update**:
- Line 329: `>500 lines` → `>800 lines`
- Line 492: `< 500 lines` → `< 800 lines`
- Line 1625: `exceeds 500 lines` → `exceeds 800 lines`

### 11.2 doc-bdd/SKILL.md

**File**: `.claude/skills/doc-bdd/SKILL.md`

**Lines to update**:
- Line 94: `≤500 lines` → `≤800 lines`
- Line 110: `Max 500 lines` → `Max 800 lines`
- Line 440: `>500 lines` → `>800 lines`
- Line 516: `exceeds 500 lines` → `exceeds 800 lines`
- Line 553: `>500 lines` → `>800 lines`
- Line 624: `500 lines (soft: 400)` → `800 lines (soft: 600)`

---

## Phase 12: Skills - EARS (NEW)

### 12.1 doc-ears-autopilot/SKILL.md

**File**: `.claude/skills/doc-ears-autopilot/SKILL.md`

**Lines to update**:
- Line 299: `>300 lines` → `>800 lines`
- Line 1342: `>300 lines` → `>800 lines`

---

## Phase 13: Skills - ADR (NEW)

Already covered in Phase 6.2.

---

## Phase 14: Framework Standards (NEW v1.2)

### 14.1 ID_NAMING_STANDARDS.md

**File**: `ID_NAMING_STANDARDS.md`

**Lines to update**:
- Line 298: `>500 lines` → `>800 lines`
- Line 302: `≤500 lines` → `≤800 lines`

---

## Phase 15: Additional QUICK_REFERENCE (NEW v1.2)

### 15.1 QUICK_REFERENCE.md - Additional Patterns

**File**: `QUICK_REFERENCE.md`

**Lines to update**:
- Line 240: `# Lint file sizes (target 300–500, max 600)` → `# Lint file sizes (target 800, max 1200)`
- Line 434: `> 500 target or > 600 max` → `> 800 target or > 1200 max`

---

## Phase 16: BDD Fix Plan (NEW v1.2)

### 16.1 BDD-MVP-TEMPLATE_FIX_PLAN.md

**File**: `04_BDD/BDD-MVP-TEMPLATE_FIX_PLAN.md`

**Note**: This is a fix plan document itself - update to use correct values.

**Lines to update**:
- Lines 362-363: Change `300-500 lines` / `600 lines` to `800` / `1200 lines`
- Lines 368-369: Change `Target 300-500` / `Maximum 600` to `Target 800` / `Maximum 1200`
- Line 465: Change `600 max, 300-500 target` to `1200 max, 800 target`

---

## Phase 17: Additional BDD Files (NEW v1.2)

### 17.1 BDD Creation Rules - Additional Line

**File**: `04_BDD/BDD_MVP_CREATION_RULES.md`
**Line**: 236

**Current**:
```markdown
- BDD suite would exceed 500 lines in single file
```

**Change to**:
```markdown
- BDD suite would exceed 800 lines in single file
```

### 17.2 BDD Generation Checklist - Additional Lines

**File**: `04_BDD/BDD_GENERATION_CHECKLIST.md`

**Lines to update**:
- Line 104: `target: 300-400 lines, max 500` → `target: 600-700 lines, max 800`
- Line 380: `exceeds 500 lines` → `exceeds 800 lines`

---

## Phase 18: Archive (Low Priority v1.2)

### 18.1 IMPLEMENTATION_GUIDE.md (Archive)

**File**: `11_TASKS/archive/IMPLEMENTATION_GUIDE.md`
**Line**: 396

**Note**: Archive file - low priority, update for consistency.

**Current**:
```markdown
  - And the contract definition exceeds 500 lines
```

**Change to**:
```markdown
  - And the contract definition exceeds 800 lines
```

---

## Execution Order

| Step | Phase | Action | Priority |
|------|-------|--------|----------|
| 1 | 0 | Create backups | Required |
| 2 | 1 | Update README files (PRD, EARS, BDD) | High |
| 3 | 2 | Update Creation Rules & Templates | High |
| 4 | 3 | Update Schemas (BDD, SPEC) | High |
| 5 | 4 | Update Quality Gate Validations (8 files) | Medium |
| 6 | 5 | Update Framework docs (QUICK_REFERENCE, SDD Guide) | High |
| 7 | 6 | Update Skills (doc-ears, doc-adr) | Medium |
| 8 | 7 | Update Archive/Examples | Low |
| 9 | 8 | Update Additional BDD files | High |
| 10 | 9 | Update Additional Templates | Medium |
| 11 | 10 | Update QUICK_REFERENCE additional patterns | High |
| 12 | 11 | Update doc-bdd* skills | High |
| 13 | 12 | Update doc-ears-autopilot skill | Medium |
| 14 | 14 | Update ID_NAMING_STANDARDS.md | High |
| 15 | 15 | Update QUICK_REFERENCE additional (lint, exceeds) | Medium |
| 16 | 16 | Update BDD-MVP-TEMPLATE_FIX_PLAN.md | Medium |
| 17 | 17 | Update Additional BDD files (line 236, 104, 380) | High |
| 18 | 18 | Update Archive IMPLEMENTATION_GUIDE | Low |
| 19 | - | Run validation tests | Required |

---

## Verification Checklist

### README Verification
- [ ] `01_BRD/README.md` has 800/1200 (already correct)
- [ ] `02_PRD/README.md` has 800/1200
- [ ] `02_PRD/README.md` line 27 has ~800 lines description
- [ ] `03_EARS/README.md` has 800/1200
- [ ] `04_BDD/README.md` has 800/1200
- [ ] `04_BDD/README.md` line 568 has 800 target

### Schema Verification
- [ ] `BDD_MVP_SCHEMA.yaml` has max_file_lines: 1200
- [ ] `BDD_MVP_SCHEMA.yaml` has all 500 → 800 updates
- [ ] `SPEC_MVP_SCHEMA.yaml` references 1200 lines

### BDD Files Verification
- [ ] `BDD_MVP_VALIDATION_RULES.md` - no 500 line references remain
- [ ] `BDD_MVP_CREATION_RULES.md` - no 500 line references remain
- [ ] `BDD_GENERATION_CHECKLIST.md` - no 500 line references remain

### Quality Gate Verification
- [ ] All `CORPUS-W005` references updated to 1200 lines
- [ ] All severity descriptions use 800 warning, 1200 error

### Framework Verification
- [ ] `QUICK_REFERENCE.md` has 800/1200
- [ ] `QUICK_REFERENCE.md` - no 500 line references remain
- [ ] `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` has 800 target

### Skills Verification
- [ ] `doc-bdd/SKILL.md` - no 500 line references remain
- [ ] `doc-bdd-autopilot/SKILL.md` - no 500 line references remain
- [ ] `doc-ears/SKILL.md` - uses 800/1200
- [ ] `doc-ears-autopilot/SKILL.md` - uses 800 threshold
- [ ] `doc-adr/SKILL.md` - uses 800/1200

### v1.2 Additions Verification
- [ ] `ID_NAMING_STANDARDS.md` - uses 800 threshold (lines 298, 302)
- [ ] `QUICK_REFERENCE.md` line 240 - lint comment uses 800/1200
- [ ] `QUICK_REFERENCE.md` line 434 - exceeds limits uses 800/1200
- [ ] `04_BDD/BDD-MVP-TEMPLATE_FIX_PLAN.md` - uses 800/1200 throughout
- [ ] `04_BDD/BDD_MVP_CREATION_RULES.md` line 236 - uses 800 threshold
- [ ] `04_BDD/BDD_GENERATION_CHECKLIST.md` lines 104, 380 - uses 800 threshold

---

## Estimated Changes

| Category | Files | Approx. Edits |
|----------|-------|---------------|
| README files | 4 | 8 |
| Creation Rules/Templates | 3 | 16 |
| Schemas | 2 | 10 |
| Validation Rules | 1 | 8 |
| Quality Gate Validations | 8 | 40+ |
| Framework docs | 3 | 12 |
| Skills (doc-bdd*) | 2 | 12 |
| Skills (doc-ears*) | 2 | 8 |
| Skills (doc-adr) | 1 | 4 |
| BDD Checklist | 1 | 6 |
| BDD Fix Plan | 1 | 4 |
| Archive/Examples | 8 | 16 |
| **Total** | **39** | **~144** |

---

## Validation Commands

```bash
# Verify no 300-500/600 patterns remain in active files
grep -rn "300.*500\|target.*600\|max.*600" \
  /opt/data/docs_flow_framework/ucx_flow_v3/*/README.md \
  /opt/data/docs_flow_framework/ucx_flow_v3/*/*.yaml \
  /opt/data/docs_flow_framework/ucx_flow_v3/QUICK_REFERENCE.md \
  2>/dev/null | grep -v ".backup" | grep -v "archive"

# Verify no 500 line threshold patterns remain (excluding performance/latency refs)
grep -rn "≤500\|<=500\|<500\|>500\|exceed.*500" \
  /opt/data/docs_flow_framework/ucx_flow_v3/ \
  /opt/data/docs_flow_framework/.claude/skills/ \
  --include="*.md" --include="*.yaml" \
  2>/dev/null | grep -v ".backup" | grep -vi "latency\|delay\|timeout\|ms\|token"

# Verify 800/1200 is present in key files
grep -n "800\|1200" /opt/data/docs_flow_framework/ucx_flow_v3/*/README.md | grep -i "line\|target\|max"

# Verify skills have correct limits
grep -n "800\|1200" /opt/data/docs_flow_framework/.claude/skills/doc-*/SKILL.md | grep -i "line\|target\|max"
```

---

## Notes

1. **DOCUMENT_SPLITTING_RULES.md**: This file uses token-based limits (15k/20k tokens) and explicitly states "Line Limits: Removed." This is intentional for that file and should NOT be changed.

2. **BDD Scenario Limits**: The "12 scenarios per Feature" limit is independent of line limits and should be preserved.

3. **Consistency with BRD**: BRD README already uses 800/1200, so this standardization aligns all layers with Layer 1.

4. **Token-Based Layers**: Layers 5-11 (ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS) intentionally use **token-based** limits (15k/20k tokens) in their READMEs. These should NOT be changed to line-based limits.

5. **False Positives to Exclude** (NOT file size limits - do not change):
   - `FINANCIAL_DOMAIN_CONFIG.md:210` - "Partial fill: 300 of 500 shares" (financial example)
   - `tmp/archive/EARS-00_required_documents_list.md:382` - "portfolio_delta exceeds +/-500" (business threshold)
   - `10_TSPEC/examples/FTEST-01_auth_service.md` - ">500 req/s" (performance threshold)
   - `06_SYS/examples/SYS-03_DEPLOYMENT_EXAMPLE.md` - "$500/month" (cost budget)
   - `trace-check/SKILL.md:919` - "<500MB" (memory usage)
   - `07_REQ/README.md:797` - "400-500 (focused)" (content quality metric)

---

**End of Plan**
