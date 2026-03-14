# UCX v1.14.3 - QA Lead Persona & Chaos Engineer Rename

**Release Date**: 2026-03-14

## Overview

This release adds the `qa_lead` persona to the core UCX persona list and renames `devils_advocate` to `chaos_engineer` for clarity and better alignment with industry terminology.

## Changes

### 1. New Persona: qa_lead

Added `qa_lead` as a mandatory review persona responsible for testability and quality standards.

**Role**: Quality Assurance Lead responsible for testability, BDD/Gherkin standards, and test coverage.

**Focus Areas**:
- Acceptance criteria testability
- BDD/Gherkin syntax purity
- Test coverage requirements
- EARS requirement testability
- Edge case identification
- Quality metrics definition

**Section Mapping (BRD)**:
- Required: BRD-01.4, BRD-01.5, BRD-01.6, BRD-01.8
- Optional: BRD-01.7, BRD-01.10
- Skip: BRD-01.18, BRD-01.13-16

**Finding Prefix**: `QA`

**Extraction Patterns Added**:
- BDD & Gherkin Standards
- Test Coverage Requirements
- Critical Test Scenarios
- Layer-Specific Focus
- Testability Checklist
- Quality Metrics
- Scenario Anti-Patterns
- EARS Testability Assessment
- TSPEC Quality Metrics

### 2. Renamed: devils_advocate → chaos_engineer

Renamed the adversarial persona to better reflect its purpose:
- **Old name**: `devils_advocate` (prefix: DA)
- **New name**: `chaos_engineer` (prefix: CE)

**Rationale**:
- Better alignment with industry terminology (Chaos Engineering)
- Clearer indication of role (systematic fault injection analysis)
- More descriptive of actual review focus (failure modes, edge cases)

## Files Changed

| File | Changes |
|------|---------|
| `ucx/prompts/mapper.py` | Updated VALID_PERSONAS list |
| `ucx/prompts/analyzer.py` | Updated PERSONA_INSTRUCTION_TOKENS, PERSONA_BUDGET_OVERRIDES |
| `ucx/prompts/exceptions.py` | Updated PersonaNotFoundError.VALID_PERSONAS |
| `ucx/core/context_engine.py` | Updated PERSONA_PREFIX_MAP, PERSONA_SECTION_MAP, PERSONA_KEYWORDS, PERSONA_CATEGORY_MAP |
| `ucx/prompts/api.py` | Added 9 qa_lead extraction patterns |
| `skills/chaos_engineer.md` | Renamed from `devils_advocate.md` |
| `skills/README.md` | Updated persona table |

## Persona Summary (v1.14.3)

| # | Persona | Prefix | Role |
|---|---------|--------|------|
| 1 | architect | ARCH | System architecture, scalability |
| 2 | auditor | AUD | Compliance, regulatory |
| 3 | tech_lead | TL | Implementation, state machines |
| 4 | strategist | STR | Business economics |
| 5 | **chaos_engineer** | **CE** | Failure modes, edge cases |
| 6 | operator | OP | DevOps, observability |
| 7 | integration_lead | IL | Partner APIs, contracts |
| 8 | product_owner | PO | MVP scope, user stories |
| 9 | business_analyst | BA | Requirements quality |
| 10 | fact_checker | FC | Cross-validation |
| 11 | chairperson | REM | Synthesis, scoring |
| 12 | **qa_lead** | **QA** | Testability, BDD |

## Verification

```bash
# Generate all prompts (now includes qa_lead)
source .envrc
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/

# Verify qa_lead prompt exists
ls docs/01_BRD/BRD-01_platform_architecture/.doc_review_memory/prompt_qa_lead.*

# Verify chaos_engineer (not devils_advocate)
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/ -p chaos_engineer

# This should fail (old name deprecated)
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/ -p devils_advocate
# Error: Unknown persona: devils_advocate
```

## Migration Guide

### For Projects Using devils_advocate

1. Rename skill files:
```bash
mv docs/UCX/skills/devils_advocate.md docs/UCX/skills/chaos_engineer.md
```

2. Update skill file header:
```markdown
# Before
# {Project} Devil's Advocate Domain Knowledge

# After
# {Project} Chaos Engineer Domain Knowledge
```

3. Update any scripts referencing `devils_advocate` to use `chaos_engineer`

### For Projects Not Using qa_lead

The `qa_lead` persona is now included in default prompt generation. To exclude:
```bash
ucx prompt generate brd docs/01_BRD/BRD-01/ -p architect,auditor,tech_lead
# Explicit persona list excludes qa_lead
```

## Backward Compatibility

- `devils_advocate` persona name is **deprecated** (will error)
- Old skill file names (`devils_advocate.md`) no longer work (must rename to `chaos_engineer.md`)
- Framework skill fallback uses new name (`chaos_engineer`)

## References

- [CHANGELOG_v1.14.2](CHANGELOG_v1.14.2.md) - Enhanced skill extraction
- [PLAN-005: Prompt Engineering Toolset](plans/PLAN-005_prompt_engineering_toolset.md)
- [skills/README.md](../skills/README.md) - Persona list

---

*UCX v1.14.3 - 2026-03-14*
