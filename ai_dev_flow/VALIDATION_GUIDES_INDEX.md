---
title: "Document-Type Validation Guide Index"
tags:
  - validation
  - framework-guide
  - quick-reference
custom_fields:
  document_type: index
  artifact_type: framework-support
  priority: high
  version: "1.0"
  scope: all-document-types
---

# Document-Type Validation Guide Index

This index shows where to find validation guidance for each SDD document type.

**Navigation:**
- [Framework-Level Documents](#framework-level-documents) - Universal rules, applies to all types
- [Document-Type Specific Guides](#document-type-specific-guides) - Type-specific patterns and commands
- [How to Use This Index](#how-to-use-this-index)

---

## Framework-Level Documents

**All document types reference these universal guides:**

| Document | Purpose | Scope |
|----------|---------|-------|
| [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) | Core decision rules | When to fix document vs validator vs accept warning |
| [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md) | Error codes & standards | Exit codes, validation severity levels |
| [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) | CLI reference | Commands for all document types |
| [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) | Architecture & patterns | Master orchestrator model, gate coverage |
| [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) | Decision framework | AI assistant guidance for validation decisions |

**When to use:** Universal guidance applicable across all SDD layers.

---

## Document-Type Specific Guides

Each document type has three type-specific guides with the pattern: `{TYPE}_{GUIDE_NAME}.md`

### Layer 1: Business Requirements (BRD)

**Location:** `01_BRD/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [BRD_VALIDATION_STRATEGY.md](./01_BRD/BRD_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for BRD validation |
| [BRD_VALIDATION_COMMANDS.md](./01_BRD/BRD_VALIDATION_COMMANDS.md) | CLI commands | BRD-specific validation commands |
| [BRD_AI_VALIDATION_DECISION_GUIDE.md](./01_BRD/BRD_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | BRD-specific decision trees and edge cases |

**Scripts location:** `01_BRD/scripts/` (master orchestrator + individual validators)

**When to use:** Validating BRD documents, understanding BRD gates.

---

### Layer 2: Product Requirements (PRD)

**Location:** `02_PRD/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [PRD_VALIDATION_STRATEGY.md](./02_PRD/PRD_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for PRD validation |
| [PRD_VALIDATION_COMMANDS.md](./02_PRD/PRD_VALIDATION_COMMANDS.md) | CLI commands | PRD-specific validation commands |
| [PRD_AI_VALIDATION_DECISION_GUIDE.md](./02_PRD/PRD_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | PRD-specific decision trees and edge cases |

**Scripts location:** `02_PRD/scripts/` (master orchestrator + individual validators)

---

### Layer 3: Event Analysis (EARS)

**Location:** `03_EARS/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [EARS_VALIDATION_STRATEGY.md](./03_EARS/EARS_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for EARS validation |
| [EARS_VALIDATION_COMMANDS.md](./03_EARS/EARS_VALIDATION_COMMANDS.md) | CLI commands | EARS-specific validation commands |
| [EARS_AI_VALIDATION_DECISION_GUIDE.md](./03_EARS/EARS_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | EARS-specific decision trees and edge cases |

---

### Layer 4: Behavior-Driven Development (BDD)

**Location:** `04_BDD/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [BDD_VALIDATION_STRATEGY.md](./04_BDD/BDD_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for BDD validation |
| [BDD_VALIDATION_COMMANDS.md](./04_BDD/BDD_VALIDATION_COMMANDS.md) | CLI commands | BDD-specific validation commands |
| [BDD_AI_VALIDATION_DECISION_GUIDE.md](./04_BDD/BDD_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | BDD-specific decision trees and edge cases |

---

### Layer 5: Architecture Decision Records (ADR)

**Location:** `05_ADR/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [ADR_VALIDATION_STRATEGY.md](./05_ADR/ADR_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for ADR validation |
| [ADR_VALIDATION_COMMANDS.md](./05_ADR/ADR_VALIDATION_COMMANDS.md) | CLI commands | ADR-specific validation commands |
| [ADR_AI_VALIDATION_DECISION_GUIDE.md](./05_ADR/ADR_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | ADR-specific decision trees and edge cases |

---

### Layer 6: System Design (SYS)

**Location:** `06_SYS/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [SYS_VALIDATION_STRATEGY.md](./06_SYS/SYS_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for SYS validation |
| [SYS_VALIDATION_COMMANDS.md](./06_SYS/SYS_VALIDATION_COMMANDS.md) | CLI commands | SYS-specific validation commands |
| [SYS_AI_VALIDATION_DECISION_GUIDE.md](./06_SYS/SYS_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | SYS-specific decision trees and edge cases |

---

### Layer 7: Requirements (REQ) ✅

**Location:** `07_REQ/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [REQ_VALIDATION_STRATEGY.md](./07_REQ/REQ_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for REQ validation |
| [REQ_VALIDATION_COMMANDS.md](./07_REQ/REQ_VALIDATION_COMMANDS.md) | CLI commands | REQ-specific validation commands |
| [REQ_AI_VALIDATION_DECISION_GUIDE.md](./07_REQ/REQ_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | REQ-specific decision trees and edge cases |

**Scripts location:** `07_REQ/scripts/` (master orchestrator + 6 individual validators)

**Status:** ✅ Complete (template for other types)

---

### Layer 8: Contracts (CTR)

**Location:** `08_CTR/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [CTR_VALIDATION_STRATEGY.md](./08_CTR/CTR_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for CTR validation |
| [CTR_VALIDATION_COMMANDS.md](./08_CTR/CTR_VALIDATION_COMMANDS.md) | CLI commands | CTR-specific validation commands |
| [CTR_AI_VALIDATION_DECISION_GUIDE.md](./08_CTR/CTR_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | CTR-specific decision trees and edge cases |

---

### Layer 9: Specifications (SPEC)

**Location:** `09_SPEC/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [SPEC_VALIDATION_STRATEGY.md](./09_SPEC/SPEC_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for SPEC validation |
| [SPEC_VALIDATION_COMMANDS.md](./09_SPEC/SPEC_VALIDATION_COMMANDS.md) | CLI commands | SPEC-specific validation commands |
| [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./09_SPEC/SPEC_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | SPEC-specific decision trees and edge cases |

---

### Layer 11: Tasks (TASKS)

**Location:** `11_TASKS/`

| Document | Purpose | Quick Reference |
|----------|---------|-----------------|
| [TASKS_VALIDATION_STRATEGY.md](./11_TASKS/TASKS_VALIDATION_STRATEGY.md) | Quick reference | Gates, architecture for TASKS validation |
| [TASKS_VALIDATION_COMMANDS.md](./11_TASKS/TASKS_VALIDATION_COMMANDS.md) | CLI commands | TASKS-specific validation commands |
| [TASKS_AI_VALIDATION_DECISION_GUIDE.md](./11_TASKS/TASKS_AI_VALIDATION_DECISION_GUIDE.md) | Decision patterns | TASKS-specific decision trees and edge cases |

---

## How to Use This Index

### For Users Running Validation

**Step 1:** Identify your document type (BRD, REQ, SPEC, etc.)

**Step 2:** Go to the type-specific folder (e.g., `07_REQ/`)

**Step 3:** Read:
- **scripts/README.md** - Quick start, installation, troubleshooting
- **{TYPE}_VALIDATION_COMMANDS.md** - Exact command syntax for your type
- **{TYPE}_VALIDATION_STRATEGY.md** - Architecture, gates, workflows

**Step 4:** Run validation:
```bash
cd {TYPE_FOLDER}/scripts
bash validate_all.sh --file path/to/document.md
```

---

### For Framework Architects

**Step 1:** Read universal framework docs:
- VALIDATION_DECISION_FRAMEWORK.md (decision rules)
- VALIDATION_STRATEGY_GUIDE.md (architecture pattern)

**Step 2:** For type-specific architecture:
- Read `{TYPE}_VALIDATION_STRATEGY.md` in each layer folder

**Step 3:** To extend the framework:
- Copy REQ template from `07_REQ/` folder
- Apply to new document type (e.g., BRD, SPEC)
- Use `{TYPE}_` prefix for all type-specific files

---

### For AI Assistants Making Validation Decisions

**Step 1:** When a validation fails, read:
- Universal: [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md)
- Type-specific: `{TYPE}_AI_VALIDATION_DECISION_GUIDE.md`

**Step 2:** Use decision matrix to classify issue:
- Content missing? → Fix document
- Template variant? → Fix validator
- Style/threshold? → Consider cost/benefit

**Step 3:** Execute fix and verify

---

## File Organization Pattern

```
ai_dev_flow/
├── Framework-Level (universal, no prefix):
│   ├── VALIDATION_DECISION_FRAMEWORK.md    [Universal rules]
│   ├── VALIDATION_STANDARDS.md             [Error codes]
│   ├── VALIDATION_COMMANDS.md              [CLI for all types]
│   ├── VALIDATION_STRATEGY_GUIDE.md        [Architecture]
│   └── AI_VALIDATION_DECISION_GUIDE.md     [Decision framework]
│
└── Document-Type Specific (prefixed: TYPE_):
    ├── 01_BRD/
    │   ├── BRD_VALIDATION_STRATEGY.md
    │   ├── BRD_VALIDATION_COMMANDS.md
    │   ├── BRD_AI_VALIDATION_DECISION_GUIDE.md
    │   └── scripts/ → validate_all.sh + validators
    │
    ├── 02_PRD/
    │   ├── PRD_VALIDATION_STRATEGY.md
    │   ├── PRD_VALIDATION_COMMANDS.md
    │   ├── PRD_AI_VALIDATION_DECISION_GUIDE.md
    │   └── scripts/ → validate_all.sh + validators
    │
    ├── ...similarly for EARS, BDD, ADR, SYS...
    │
    ├── 07_REQ/ ✅ Complete template
    │   ├── REQ_VALIDATION_STRATEGY.md
    │   ├── REQ_VALIDATION_COMMANDS.md
    │   ├── REQ_AI_VALIDATION_DECISION_GUIDE.md
    │   └── scripts/ → validate_all.sh + 6 validators
    │
    └── 08_CTR, 09_SPEC, 11_TASKS
        ├── {TYPE}_VALIDATION_STRATEGY.md
        ├── {TYPE}_VALIDATION_COMMANDS.md
        ├── {TYPE}_AI_VALIDATION_DECISION_GUIDE.md
        └── scripts/ → validate_all.sh + validators
```

---

## Key Design Principles

1. **Unified Entry Point**: Each type has `scripts/validate_all.sh` master orchestrator
2. **Type-Specific Customization**: Each type has tailored gates and validation rules
3. **Consistent Navigation**: All type-specific files use `{TYPE}_` prefix
4. **Framework Scalability**: Pattern replicates across all 10 document layers
5. **Backward Compatibility**: Framework-level docs unchanged, extensible by design

---

## Validation Chain (Top to Bottom)

```
User runs: scripts/validate_all.sh --file document.md

↓
Master Orchestrator (validate_all.sh)
  ├─ Delegates to Type-Specific Validators
  ├─ Collects Results
  └─ Outputs Unified Report

↓
Type-Specific Validators (e.g., validate_req_quality_score.sh)
  ├─ Runs Gate 1-N
  ├─ Returns EXIT_CODE (0=pass, 1=warn, 2=error)
  └─ Colors output for clarity

↓
User Reviews Results & Consults Guides:
  ├─ {TYPE}_VALIDATION_STRATEGY.md (architecture)
  ├─ {TYPE}_VALIDATION_COMMANDS.md (commands)
  ├─ {TYPE}_AI_VALIDATION_DECISION_GUIDE.md (decisions)
  └─ scripts/README.md (troubleshooting)
```

---

## Status by Document Type

| Type | Framework | Guides | Scripts | Status |
|------|-----------|--------|---------|--------|
| BRD (01) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| PRD (02) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| EARS (03) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| BDD (04) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| ADR (05) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| SYS (06) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| REQ (07) | ✅ | ✅ Complete | ✅ Complete | Template |
| CTR (08) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| SPEC (09) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |
| TASKS (11) | ✅ | 🔄 Planned | 🔄 Planned | Foundation ready |

**Legend:**
- ✅ Complete
- 🔄 Planned/In Progress
- ❌ Not started

---

## Next Steps

### Immediate (Foundation Complete)
1. ✅ Framework-level docs created
2. ✅ REQ guides complete (template)
3. 🔄 Update framework docs with type-specific references

### Short Term (Scale to Other Types)
1. 🔄 Create BRD guides (copy REQ template, adapt)
2. 🔄 Create PRD guides
3. 🔄 Create SPEC guides (code generation focus)

### Medium Term (Full Coverage)
1. Create guides for remaining types (EARS, BDD, ADR, SYS, CTR, TASKS)
2. Develop validators for each type
3. Integrate into CI/CD pipelines

---

**Last Updated:** 2026-01-24  
**Status:** Framework foundation complete, scaling in progress  
**Audience:** All SDD users, framework maintainers, CI/CD operators  
**Scope:** Validation guidance index across all document types
