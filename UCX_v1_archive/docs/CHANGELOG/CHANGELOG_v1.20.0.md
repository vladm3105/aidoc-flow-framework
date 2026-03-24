# CHANGELOG v1.20.0

**Release Date**: 2026-03-19
**Status**: Release Candidate
**Focus**: PRD Creation & Validation Parity with BRD

---

## Overview

v1.20.0 achieves feature parity between PRD (Layer 2) and BRD (Layer 1) validation and creation workflows. All PRD operations now follow the same unified validation patterns as BRD, with dual readiness scoring (SYS-Ready + EARS-Ready) integrated throughout the lifecycle.

---

## Major Features

### 1. PRD Creation Enhancements (PLAN-009)

**Full UCC_PROMPT_PRD Rewrite**
- Increased from 172 → ~450 lines
- Complete 21-section mandate with Section 10 (Customer-Facing Content) blocking requirement
- Section 8 layer separation note enforcement
- 13 element type codes (PRD.NN.TT.SS format)
- Diagram requirements (c4-l2, dfd-l1, sequence-*) documented
- Forbidden legacy patterns explicitly listed
- Dual scoring framework (SYS-Ready + EARS-Ready) in Document Control

**Persona Updates**
- `ucx/skills/personas/requirements_specialist.md`: PRD creation focus with layer separation enforcement
- `ucx/skills/personas/content_strategist.md` (NEW): Dedicated persona for Section 10 (Customer-Facing Content)
- 7 total personas applied during PRD creation (product_owner, ux_strategist, content_strategist, tech_lead, qa_lead, architect, requirements_specialist)

**Post-Creation Validation & Scoring**
- `ucx.api.creation.py`: Added `validate_after` parameter (default: True)
- Automatic Tier 1 validation after PRD creation
- Readiness scores calculated and injected into Document Control section
- Scorer imported from PLAN-010 module for consistency

**CLI Enhancement**
- New flags: `--validate`, `--no-validate`, `--strict` for create command
- Example: `ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --strict`

**Project-Specific PRD Prompts**
- Architecture: Projects can override with `UCC_PROMPT_PRD_PROJECT.md`
- Format: `{PROJECT}/docs/UCX/creation/UCC_PROMPT_PRD_PROJECT.md`
- Includes example for b-local-docs with domain-specific customizations

**Estimated Scores in Document Control**
- SYS-Ready Score: `[DRAFT] NN% (Target: ≥90%)`
- EARS-Ready Score: `[DRAFT] NN% (Target: ≥90%)`

### 2. PRD Validation System (PLAN-010)

**Foundation Setup**
Complete `ucx/validators/prd/` module (10 files, ~2,500 lines):

| File | Purpose | Lines |
|------|---------|-------|
| `__init__.py` | UnifiedPRDValidator class | 150 |
| `schema.py` | Constants (13 codes, 21 sections) | 200 |
| `structure.py` | Section/heading validation | 180 |
| `metadata.py` | Frontmatter validation | 120 |
| `element_codes.py` | Element ID format validation | 140 |
| `quality_gate.py` | File-level GATE checks (20 codes) | 300 |
| `corpus_gate.py` | Corpus-level checks (19 codes) | 400 |
| `scoring.py` | SYS-Ready/EARS-Ready scorer | 350 |
| `fixer.py` | Auto-fixer with UCX-ACTION | 280 |
| `duplicate_fixer.py` | Duplicate element handling | 140 |

**Schema Definition (13 Element Type Codes)**

| Code | Type | Primary Section |
|------|------|-----------------|
| 01 | Functional Requirement | 9 |
| 02 | Quality Attribute | 21 |
| 03 | Constraint | 12 |
| 04 | Assumption | 12 |
| 05 | Dependency | 7 |
| 06 | Acceptance Criteria | 11 |
| 07 | Risk | 13 |
| 08 | Metric/KPI | 5 |
| 09 | User Story | 8 |
| 11 | Use Case | 9 |
| 22 | Feature Item | 7, 9 |
| 23 | Goal | 6 |
| 24 | Stakeholder Need | 4, 15 |

**21 Mandatory Sections**

PRD documents must contain exactly 21 numbered sections:
1. Document Control
2. Executive Summary
3. Problem Statement
4. Target Audience & User Personas
5. Success Metrics (KPIs)
6. Goals & Objectives
7. Scope & Requirements
8. User Stories & User Roles (layer separation note required)
9. Functional Requirements
10. **Customer-Facing Content** (BLOCKING - no placeholders)
11. Acceptance Criteria
12. Constraints & Assumptions
13. Risk Assessment
14. Success Definition
15. Stakeholders & Communication
16. Implementation Approach
17. Budget & Resources
18. Traceability
19. References
20. EARS Enhancement Appendix
21. Quality Assurance & Testing Strategy

**Quality Gates**

- **File-Level (20 GATE checks)**:
  - PRD-E001 through PRD-E026 (tier 1 + tier 2)
  - Critical: Section 10 blocking, Section 8 layer note, dual scoring required
  - Diagram requirements: c4-l2, dfd-l1, sequence-* with alt/else

- **Corpus-Level (19 CORPUS checks)**:
  - CORPUS-E001 through CORPUS-E019
  - Cross-file: element uniqueness, section coverage, token limits
  - Consistency: file naming, BRD traceability, layer separation

**Dual Readiness Scoring (AUTHORITATIVE)**

Scoring module (`ucx/validators/prd/scoring.py`) is single source of truth used by:
- `ucx validate prd` — calculates during validation
- `ucx create prd` — calculates after creation (PLAN-009 Phase 4)
- `ucx score prd` — standalone scoring command

**SYS-Ready Score (40% + 30% + 20% + 10%)**:
- Product Completeness (40%): sections, elements, acceptance criteria
- Technical Readiness (30%): constraints, dependencies, risks
- Business Alignment (20%): goals, metrics, stakeholders
- Traceability (10%): upstream BRD, element coverage

**EARS-Ready Score (25% + 25% + 25% + 15% + 10%)**:
- Timing Profiles (25%): p50/p95/p99 for operations
- Boundary Values (25%): explicit operators (≥, >, <, ≤)
- State Machine (25%): complete with error transitions
- Fallback Paths (15%): external dependency failures
- Threshold Registry (10%): centralized values referenced

**Thresholds**:
- MVP Profile: ≥85%
- Standard Profile: ≥90%

**Auto-Fixer**

- Fixable codes: PRD-E002, PRD-E003, PRD-E004, PRD-E005, PRD-W002, PRD-W005, CORPUS-01, 02, 08, 19, SCORE-UPDATE
- UCX-ACTION output format for LLM hand-off
- Protected changes tracking for user review
- Duplicate element renumbering with guardrails

**AI Review Prompt Update**

`ucx/review/UCR_PROMPT_PRD.md`:
- Updated from BRD review template
- 10-persona review framework (same as BRD)
- Critical: false negative philosophy ("when in doubt, FLAG IT")
- Verification protocol for presence/completeness
- Quality gate integration
- Dual scoring output template
- Section 10 blocking requirement enforcement
- Layer separation validation
- Forward reference blocking

**Integration**

- `ucx/validators/prd.py`: PRDValidator class with BaseValidator interface
- `ucx/validators/registry.py`: Registered with `@register_validator(DocType.PRD)`
- `ucx/validators/common/error_codes.py`: PRD-E, PRD-W, PRD-I + CORPUS-E codes
- CLI commands: `ucx validate prd`, `ucx review prd`, `ucx remediate prd`
- Tests: `tests/validators/test_prd_validator.py` with comprehensive coverage
- Pre-commit hooks: Configured in project `.pre-commit-config.yaml`

---

## Error Code Registry

### PRD Error Codes (PRD-E)
- **PRD-E001 to E026**: File-level validation issues
- **PRD-E010**: Section 10 (Customer-Facing Content) empty ← BLOCKING
- **PRD-E011**: Section 8 layer separation note missing ← BLOCKING
- **PRD-E015, E016**: SYS-Ready/EARS-Ready below threshold ← BLOCKING
- **PRD-E020**: Given-When-Then pattern in PRD ← CRITICAL

### PRD Warning Codes (PRD-W)
- **PRD-W001 to W021**: Advisory checks (Tier 2)

### CORPUS Codes (CORPUS-E, CORPUS-W)
- **CORPUS-E001 to E019**: Cross-file validation issues
- **CORPUS-W003, W009, W010, W012, W016, W017, W018**: Advisory checks

---

## Documentation Updates

### Updated Files
- `docs/ROADMAP.md`: v1.20.0 status updated to "In Progress (v1.20.0 PRD Complete)"
- `docs/HOW_TO_USE.md`: Added PRD validation, review, and creation sections
- `docs/QUICK_START.md`: Added PRD commands and examples
- `docs/CHANGELOG/CHANGELOG_v1.20.0.md`: This document

### New Files
- `UCX/docs/plans/PLAN-009_prd_creation.md`: PRD creation implementation plan (6 phases)
- `UCX/docs/plans/PLAN-010_prd_validation.md`: PRD validation implementation plan (10 phases)

### Prompt Files Updated
- `UCX/creation/UCC_PROMPT_PRD.md`: Rewritten (172 → 450 lines)
- `UCX/review/UCR_PROMPT_PRD.md`: Updated with dual scoring and PLAN-010 integration

---

## Breaking Changes

None. v1.20.0 is fully backward compatible.

---

## Migration Guide

### For Existing BRD Projects

No changes required. BRD validation continues to work exactly as before.

### For New PRD Projects

Use the new unified PRD workflow:

```bash
# 1. Create PRD from upstream BRD
ucx create prd --output docs/02_PRD/PRD-01/ \
  --from-upstream docs/01_BRD/BRD-01/ \
  --validate

# 2. Review PRD with full AI team
ucx review prd docs/02_PRD/PRD-01/

# 3. Apply remediations
ucx remediate prd docs/02_PRD/PRD-01/

# 4. Validate and fix remaining issues
ucx validate prd docs/02_PRD/PRD-01/ --fix --report
```

---

## Performance

- **Validation Speed**: Layer 1 (Tier 1 only): ~100ms per file
- **Scoring**: ~50ms per 10KB of content
- **Review**: 10-20 minutes per PRD (10-persona multi-turn)
- **Memory**: <500MB for corpus operations

---

## QA Verification

| Test Category | Coverage | Status |
|---------------|----------|--------|
| Unit Tests | 120+ tests (schema, structure, scoring) | ✅ Pass |
| Integration Tests | Validator + Fixer workflows | ✅ Pass |
| AI Prompt Tests | UCR_PROMPT_PRD validation | ✅ Pass |
| Pre-commit Hook Tests | Manual verification in b-local-docs | ✅ Pass |

---

## Known Limitations

1. **EARS Validators**: Not included in v1.20.0; planned for v1.21.0
2. **SPEC/TASKS Validators**: Still using legacy patterns; full refactor in v2.0.0
3. **Real-time Streaming**: Not supported; planned for v2.0.0

---

## Contributors

- PRD Creation (PLAN-009): Full implementation
- PRD Validation (PLAN-010): Full implementation
- Persona Updates: content_strategist (new), requirements_specialist (enhanced)
- Documentation: Roadmap, guides, changelogs

---

## Next Steps (v1.21.0)

- [ ] EARS validators (Layer 3)
- [ ] Multi-document validation improvements
- [ ] Real-time review streaming

---

## References

- [PLAN-009: PRD Creation Improvements](plans/PLAN-009_prd_creation.md)
- [PLAN-010: PRD Validation and Remediation](plans/PLAN-010_prd_validation.md)
- [HOW_TO_USE.md](HOW_TO_USE.md) — PRD commands
- [QUICK_START.md](QUICK_START.md) — PRD examples
- [UCR_PROMPT_PRD.md](../review/UCR_PROMPT_PRD.md) — Review prompt
