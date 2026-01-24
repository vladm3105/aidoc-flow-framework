---
title: "SDD Validation Framework (Complete Guide)"
tags:
  - framework
  - validation
  - overview
custom_fields:
  document_type: overview
  artifact_type: framework-support
  priority: highest
  version: "1.0"
  scope: all-document-types
---

# SDD Validation Framework (Complete Guide)

**Purpose:** Central hub for all validation guidance across the entire SDD framework (10 document layers, 5 core validation documents).

**Quick Entry Points:**
- 🎯 [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md) - **Find guides for your document type**
- 🛠️ [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) - CLI commands for validation
- 📋 [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) - Architecture and patterns
- 🤖 [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) - Decision-making framework
- 📖 [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md) - How to create guides for new types

---

## Core Framework Documents (Universal)

These apply to **all document types**:

| Document | Purpose | Quick Use |
|----------|---------|-----------|
| [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) | **Core decision rules** | When to fix document vs validator vs accept warning |
| [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md) | **Error codes & severity** | Exit codes, validation levels, standards |
| [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) | **CLI reference** | Commands for all 10 document types |
| [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) | **Architecture & design** | Master orchestrator pattern, extensible architecture |
| [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) | **AI decision framework** | For AI assistants making validation decisions |

---

## Document-Type Specific Guides

**Location:** Each layer folder has type-specific guides with `{TYPE}_` prefix

**All 10 document types follow the same pattern:**

```
{LAYER}_{FOLDER}/
├── {TYPE}_VALIDATION_STRATEGY.md          ← Quick reference
├── {TYPE}_VALIDATION_COMMANDS.md          ← Type-specific CLI
├── {TYPE}_AI_VALIDATION_DECISION_GUIDE.md ← Type-specific decisions
├── scripts/
│   ├── README.md                          ← Tool quick start
│   ├── validate_all.sh                    ← Master orchestrator
│   └── [individual validators]            ← Type-specific validators
```

### Complete List (10 Types)

| Layer | Type | Guides | Scripts | Status |
|-------|------|--------|---------|--------|
| 01 | **BRD** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-1-business-requirements-brd) | 🔄 | Planned |
| 02 | **PRD** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-2-product-requirements-prd) | 🔄 | Planned |
| 03 | **EARS** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-3-event-analysis-ears) | 🔄 | Planned |
| 04 | **BDD** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-4-behavior-driven-development-bdd) | 🔄 | Planned |
| 05 | **ADR** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-5-architecture-decision-records-adr) | 🔄 | Planned |
| 06 | **SYS** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-6-system-design-sys) | 🔄 | Planned |
| 07 | **REQ** ✅ | [REQ_VALIDATION_STRATEGY](./07_REQ/REQ_VALIDATION_STRATEGY.md) | ✅ | Complete |
| 08 | **CTR** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-8-contracts-ctr) | 🔄 | Planned |
| 09 | **SPEC** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-9-specifications-spec) | 🔄 | Planned |
| 10 | **TASKS** | [Guide Index](./VALIDATION_GUIDES_INDEX.md#layer-10-tasks-tasks) | 🔄 | Planned |

**Legend:** ✅ Complete | 🔄 Planned | ❌ Not started

---

## How to Use the Validation Framework

### I'm Running Validation on My Document

**Step 1:** Identify your document type (BRD, REQ, SPEC, etc.)

**Step 2:** Go to [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md)

**Step 3:** Find your type → Read:
- `{TYPE}_VALIDATION_COMMANDS.md` - How to run validation
- `scripts/README.md` - Quick start, troubleshooting
- `{TYPE}_VALIDATION_STRATEGY.md` - What gates check, why

**Step 4:** Run validation:
```bash
cd {TYPE_FOLDER}/scripts
bash validate_all.sh --file path/to/document.md
```

---

### Validation Failed - What Do I Do?

**Step 1:** Read the error message

**Step 2:** Check the appropriate guide:
- Type-specific: `{TYPE}_AI_VALIDATION_DECISION_GUIDE.md`
- Universal: [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md)

**Step 3:** Use decision matrix to classify issue:
- **Content missing?** → Fix document
- **Wrong template variant?** → Fix validator
- **Style/threshold issue?** → Consider cost/benefit

**Step 4:** Execute fix and re-validate

---

### I Want to Understand the Architecture

**Step 1:** Read [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md)
- Master orchestrator pattern
- Gate coverage model
- Extensible design

**Step 2:** For type-specific architecture:
- Read `{TYPE}_VALIDATION_STRATEGY.md` in relevant layer folder
- Understand type-specific gates and workflows

**Step 3:** For decision-making:
- Read [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md)
- Learn how validators are chosen, updated, accepted

---

### I'm Implementing Validation for a New Document Type

**Step 1:** Read [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md)

**Step 2:** Copy REQ template from `07_REQ/`:
- Copy `REQ_VALIDATION_STRATEGY.md` → `{TYPE}_VALIDATION_STRATEGY.md`
- Copy `REQ_VALIDATION_COMMANDS.md` → `{TYPE}_VALIDATION_COMMANDS.md`
- Copy `REQ_AI_VALIDATION_DECISION_GUIDE.md` → `{TYPE}_AI_VALIDATION_DECISION_GUIDE.md`
- Copy `scripts/` structure

**Step 3:** Adapt for your type:
- Update gate count and descriptions
- Customize validator scripts
- Adjust decision patterns

**Step 4:** Use implementation checklist in [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md)

**Step 5:** Update [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md)

---

### I'm Maintaining/Improving the Framework

**Start here:** [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md)

**Then:**
- Update validator scripts
- Update corresponding guide sections
- Test with sample documents
- Add examples to decision guide
- Update status in index

---

## Validation Flow (End-to-End)

```
┌─────────────────────────────────────────────────────────────┐
│ USER RUNS: bash scripts/validate_all.sh --file document.md  │
└────────────────────────────┬────────────────────────────────┘
                             ↓
            ┌────────────────────────────────┐
            │ Master Orchestrator            │
            │ (validate_all.sh)              │
            └────────────────┬───────────────┘
                             ↓
        ┌────────────────────────────────────────┐
        │  Delegates to Type-Specific Validators │
        ├────────────────────────────────────────┤
        │ ✓ Quality gates validator             │
        │ ✓ Template compliance checker         │
        │ ✓ SPEC-readiness scorer              │
        │ ✓ ID format validator                │
        └────────────────┬───────────────────────┘
                         ↓
        ┌────────────────────────────────────────┐
        │  Collects Results & Generates Report  │
        │  (Color-coded, exit codes)            │
        └────────────────┬───────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ USER GETS RESULTS:                                          │
│ ✅ All passed                                               │
│ ⚠️  Warnings (review recommended)                           │
│ ❌ Errors (fix required)                                    │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ USER CONSULTS GUIDES:                                       │
│ 📖 {TYPE}_VALIDATION_STRATEGY.md (what gates check)        │
│ 📖 {TYPE}_VALIDATION_COMMANDS.md (how to fix)              │
│ 📖 {TYPE}_AI_VALIDATION_DECISION_GUIDE.md (decisions)      │
│ 📖 VALIDATION_DECISION_FRAMEWORK.md (universal rules)      │
└────────────────┬────────────────────────────────────────────┘
                 ↓
        ┌────────────────────────────────┐
        │ USER FIXES ISSUE               │
        │ (Document or Validator)        │
        └────────────────┬───────────────┘
                         ↓
        ┌────────────────────────────────┐
        │ USER RE-RUNS VALIDATION        │
        │ bash validate_all.sh --file... │
        └────────────────┬───────────────┘
                         ↓
           ┌─────────────────────────────┐
           │ ✅ PASS: Ready for next     │
           │    document layer           │
           └─────────────────────────────┘
```

---

## Framework Structure at a Glance

```
ai_dev_flow/
│
├─ CORE FRAMEWORK (universal, no type prefix)
│  ├─ VALIDATION_DECISION_FRAMEWORK.md      ← Core rules
│  ├─ VALIDATION_STANDARDS.md               ← Error codes
│  ├─ VALIDATION_COMMANDS.md                ← CLI reference
│  ├─ VALIDATION_STRATEGY_GUIDE.md          ← Architecture
│  ├─ AI_VALIDATION_DECISION_GUIDE.md       ← AI framework
│  ├─ VALIDATION_GUIDES_INDEX.md            ← Navigation hub
│  └─ VALIDATION_TEMPLATE_GUIDE.md          ← Implementation template
│
└─ DOCUMENT TYPES (with {TYPE}_ prefix)
   ├─ 01_BRD/
   │  ├─ BRD_VALIDATION_STRATEGY.md
   │  ├─ BRD_VALIDATION_COMMANDS.md
   │  ├─ BRD_AI_VALIDATION_DECISION_GUIDE.md
   │  └─ scripts/
   │     ├─ validate_all.sh
   │     └─ [validators]
   │
   ├─ 07_REQ/ ✅ COMPLETE TEMPLATE
   │  ├─ REQ_VALIDATION_STRATEGY.md
   │  ├─ REQ_VALIDATION_COMMANDS.md
   │  ├─ REQ_AI_VALIDATION_DECISION_GUIDE.md
   │  └─ scripts/
   │     ├─ validate_all.sh
   │     ├─ validate_req_quality_score.sh
   │     ├─ validate_req_template.sh
   │     ├─ validate_req_spec_readiness.py
   │     ├─ validate_requirement_ids.py
   │     ├─ add_crosslinks_req.py
   │     └─ README.md
   │
   └─ 02_PRD, 03_EARS, ... (follow same pattern)
```

---

## Key Design Principles

1. **Layered Architecture**
   - Universal rules at framework level
   - Type-specific customization in layer folders
   - Clear separation of concerns

2. **Consistent Naming**
   - Framework: `VALIDATION_*.md` (no prefix)
   - Type-specific: `{TYPE}_VALIDATION_*.md` (with prefix)
   - Easy to distinguish scope

3. **Master Orchestrator Pattern**
   - Single entry point per type
   - Delegates to specialized validators
   - Unified output and exit codes

4. **Extensible by Design**
   - REQ serves as complete template
   - Pattern replicates across all types
   - New validators easy to integrate

5. **Documentation-First**
   - Guides mirror code structure
   - Examples match actual commands
   - Decisions documented and accessible

---

## Validation Workflow by Role

### Engineer (Running Validation)
1. Check [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md)
2. Find your document type
3. Read type-specific guides
4. Run validation commands
5. Fix issues using decision guide

### DevOps (CI/CD Integration)
1. Read [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md)
2. Review type-specific CLI patterns
3. Integrate into pipeline
4. Configure exit code handling
5. Monitor validation metrics

### Framework Architect
1. Read [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md)
2. Review [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md)
3. Understand extensibility model
4. Plan new validator types
5. Update [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md)

### AI Assistant (Claude, GPT-4, etc.)
1. Check [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md)
2. Consult [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md)
3. Review type-specific decision guide
4. Use decision matrix
5. Update guides with learnings

---

## Quick Links

**🎯 Navigation & Discovery**
- [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md) - Find guides by document type

**🛠️ Using Validators**
- [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) - CLI commands
- [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) - How validators work

**🤖 Making Decisions**
- [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) - Universal rules
- [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) - AI assistant guide

**📖 Learning & Extending**
- [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md) - How to create new guides
- [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md) - Standards and conventions

**📋 Complete Example**
- [07_REQ/](./07_REQ/) - Full implementation of all 3 guides + scripts

---

## Current Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Framework Foundation | ✅ Complete | 5 core documents |
| REQ Implementation | ✅ Complete | All 3 guides + scripts |
| Guides Index | ✅ Complete | All 10 types referenced |
| Template Guide | ✅ Complete | Step-by-step implementation |
| BRD/PRD/SPEC | 🔄 Planned | Ready to scale |
| Full Coverage | 🔄 In Progress | 7 remaining types |

---

## Next Steps

### Immediate (Framework Complete)
✅ Core framework documents created  
✅ REQ complete as template  
✅ Navigation index established  
✅ Template guide written  

### Short Term (Scale to Key Types)
🔄 BRD validation guides (most used)  
🔄 SPEC validation guides (code generation)  
🔄 PRD validation guides (product focus)  

### Medium Term (Full Coverage)
🔄 Remaining types (EARS, BDD, ADR, SYS, CTR, TASKS)  
🔄 Integrate into CI/CD pipelines  
🔄 Create automated validator generators  

### Long Term (Optimization)
- AI-powered validator suggestions
- Automatic gate optimization
- Performance metrics and dashboards
- Integration with code generation tools

---

## Maintenance & Updates

### When Adding New Gates
1. Update validator script
2. Update gate table in `{TYPE}_VALIDATION_STRATEGY.md`
3. Add decision pattern to `{TYPE}_AI_VALIDATION_DECISION_GUIDE.md`
4. Test with sample documents
5. Update status in index

### When Improving Documentation
1. Update relevant guide
2. Add examples to decision guide
3. Verify links work
4. Note update date in footer

### When Creating New Document Type
1. Follow [VALIDATION_TEMPLATE_GUIDE.md](./VALIDATION_TEMPLATE_GUIDE.md)
2. Copy from REQ template
3. Use implementation checklist
4. Update [VALIDATION_GUIDES_INDEX.md](./VALIDATION_GUIDES_INDEX.md)

---

**Last Updated:** 2026-01-24  
**Framework Version:** 1.0  
**Maturity:** Foundation complete, scaling in progress  
**Status:** ✅ Framework core done, 📈 Expansion phase  

---

**Quick Start:** [→ Go to VALIDATION_GUIDES_INDEX](./VALIDATION_GUIDES_INDEX.md)
