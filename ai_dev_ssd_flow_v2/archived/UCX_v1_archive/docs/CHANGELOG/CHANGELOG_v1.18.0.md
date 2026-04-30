# UCX v1.18.0 - Layer Action Handoff System

**Release Date**: 2026-03-17

## Overview

This release introduces the **Layer Action Handoff System** - a mechanism for capturing out-of-scope items during BRD review and routing them to appropriate downstream layers (PRD, EARS, BDD, ADR, CTR) without penalizing the BRD score.

## Problem Solved

BRD reviews were incorrectly flagging technical/product details as P0/P1 errors, penalizing BRD scores for items that rightfully belong in downstream layers. For example:
- Implementation algorithms (belong in SPEC via ADR)
- User story details (belong in PRD)
- Test scenarios (belong in BDD)
- API contracts (belong in CTR)

## Solution

**ACTIONS**: A new structured handoff mechanism that:
1. Captures out-of-scope items without score penalty
2. Routes requirements to appropriate downstream layers
3. Maintains traceability from BRD to downstream documents

---

## Features

### ACTION Handoff System

**Action Format:**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-{8-char-hex}
TYPE: HANDOFF
TARGET: {PRD|EARS|BDD|ADR|CTR}
PRIORITY: {P0|P1|P2}
SOURCE: {BRD_ID} Section {X.X}
PERSONA: {PERSONA_NAME}
CONTEXT: {Business context from BRD}
REQUIREMENT: {What downstream doc should specify}
<!-- UCX-ACTION-END -->
```

**Target Layers:**

| Target | Layer | Handoff Purpose |
|--------|-------|-----------------|
| PRD | L2 | Feature details, user stories, acceptance criteria |
| EARS | L3 | Formal requirement syntax |
| BDD | L4 | Behavior specifications, Gherkin scenarios |
| ADR | L5 | Architecture decisions, technical trade-offs |
| CTR | L8 | API contracts, interface definitions |

**NOT in BRD Handoff**: SPEC (L9) receives from ADR/CTR, not directly from BRD.

### Action Types

| Type | Status | Purpose |
|------|--------|---------|
| `HANDOFF` | Implemented | Transfer requirement to downstream layer |
| `INFORM` | Reserved | Context sharing, no action required |
| `REVIEW` | Reserved | Needs human review before processing |
| `DEFER` | Reserved | Out of current scope, future consideration |

### New Scripts

**extract_actions.py:**
```bash
# Get summary of all actions
python scripts/extract_actions.py report.md --format summary

# Extract ADR-targeted actions as markdown
python scripts/extract_actions.py report.md --target ADR --format md

# Extract as JSON for processing
python scripts/extract_actions.py report.md --target PRD --format json -o prd_actions.json
```

**validate_actions.py:**
```bash
# Basic validation
python scripts/validate_actions.py report.md

# Strict mode (warnings = errors)
python scripts/validate_actions.py report.md --strict
```

### Updated Review Prompt

All 11 core review personas can now create actions:
- Architect, Auditor, Tech Lead, Strategist, Chaos Engineer
- Operator, Integration Lead, Product Owner, Business Analyst
- Fact Checker, Chairperson

Each persona receives instructions to create ACTIONS for out-of-scope items instead of P0/P1/P2 findings.

### Actions Manifest

Chairperson output now includes an Actions Manifest:

```markdown
## DOWNSTREAM LAYER ACTIONS

<!-- UCX-ACTIONS-MANIFEST-START -->
### Actions Summary
| Target | Count | Priority Breakdown |
|--------|-------|-------------------|
| PRD | 3 | P0:1 P1:2 P2:0 |
| ADR | 2 | P0:1 P1:1 P2:0 |
| CTR | 1 | P0:0 P1:1 P2:0 |
| **Total** | 6 | |

### Actions Table
| ACTION_ID | Type | Target | Priority | Source | Requirement |
|-----------|------|--------|----------|--------|-------------|
| ACT-3f7a2c1b | HANDOFF | PRD | P1 | 4.2 | Define transaction tracking user stories |
| ACT-8d4e6f2a | HANDOFF | ADR | P0 | 10.2 | Document failover architecture |
<!-- UCX-ACTIONS-MANIFEST-END -->
```

### UCR Report Section 12

New section in UCR review reports:

```markdown
## 12. Downstream Layer Actions

**NOTE**: Actions are handoffs to downstream layers. They do NOT affect the BRD score.

[Actions manifest and table]
```

---

## Changes

### Added

| Item | Description |
|------|-------------|
| ACTION Handoff System | Capture out-of-scope items as structured handoffs |
| `extract_actions.py` | Extract and filter actions from review reports |
| `validate_actions.py` | Validate action format |
| Actions Manifest | Chairperson output includes action summary |
| UCR Section 12 | Downstream Layer Actions section in reports |
| Action instruction block | Added to all 11 core persona sections |

### Changed

| Item | Before | After |
|------|--------|-------|
| Score calculation | All findings affect score | Actions excluded (0 impact) |
| Out-of-scope items | P0/P1/P2 findings | HANDOFF actions |
| Persona instructions | Flag everything | Create actions for downstream items |

### Not Changed

- Score calculation formula remains: `100 - (P0*10) - (P1*3) - (P2*1)`
- ACTIONS are explicitly excluded from this formula
- All existing functionality preserved

---

## Migration

### No Breaking Changes

This release is backward compatible:
- Existing review reports remain valid
- No changes to existing CLI commands
- No changes to existing configuration

### Adoption

To use the new action system:
1. Run BRD reviews with UCX v1.18.0+
2. Reviewers will automatically generate ACTIONS for out-of-scope items
3. Use `extract_actions.py` to process actions for downstream document creation

---

## Extension Points

### Adding New Action Types

1. Add to `KNOWN_TYPES` in both scripts
2. Document in prompt
3. No structural changes needed

### Adding New Target Layers

1. Add to `KNOWN_TARGETS` in both scripts
2. Add to prompt's target table
3. No structural changes needed

### Scripts Accept Unknown Values

- Unknown TYPE: Warning (not error) - allows gradual rollout
- Unknown TARGET: Warning (not error) - allows new layers
- `--strict` flag to enforce known values only

---

## Files Modified

| File | Changes |
|------|---------|
| `ucx/prompts/templates/ucr/UCR_PROMPT_BRD.md` | Added ACTION system, updated all personas |
| `scripts/extract_actions.py` | New script (~150 lines) |
| `scripts/validate_actions.py` | New script (~100 lines) |
| `ucx/version.py` | Version bump to 1.18.0 |

---

## Verification

```bash
# 1. Run review with updated prompt
ucx review brd docs/01_BRD/BRD-01/

# 2. Validate action format
python scripts/validate_actions.py BRD-01.UCR_review_report.md
# Expected: "VALIDATION PASSED: N actions"

# 3. Get summary
python scripts/extract_actions.py BRD-01.UCR_review_report.md --format summary

# 4. Extract by target
python scripts/extract_actions.py BRD-01.UCR_review_report.md --target ADR --format md

# 5. Verify BRD score improved (out-of-scope items no longer penalize)
```

---

## References

- [PLAN-007: Layer Action Handoff](plans/PLAN-007_layer_notice_handoff.md)
- [UCR_PROMPT_BRD.md](../ucx/prompts/templates/ucr/UCR_PROMPT_BRD.md)

---

*Last Updated: 2026-03-17*
