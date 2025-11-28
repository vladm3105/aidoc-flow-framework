# Implementation Plan - Update doc-* Skills to Reflect Framework Changes

**Created**: 2025-11-27 15:12:00 EST
**Status**: Ready for Implementation

## Objective

Update all 14 Claude Code skills with `doc-` prefix to align with recent framework documentation changes including new rules files, validation scripts, and structural updates.

**User Requirement**: Each skill must be reviewed individually, not in batch.

## Context

Recent framework changes committed include:
- New validation scripts: `validate_ctr.sh`, `validate_impl.sh`, `validate_tasks.sh`, `validate_iplan.sh`, `validate_icon.sh`
- New rules files: `*_CREATION_RULES.md` and `*_VALIDATION_RULES.md` for CTR, TASKS, ICON, IMPL, IPLAN
- Domain neutralization: Financial examples replaced with generic software examples
- IMPL now has 4-PART structure (project management focus)
- TASKS now requires Section 8 (Implementation Contracts) with ICON integration

## Task List

### Completed
- [x] Explore codebase to identify all doc-* skills (14 found)
- [x] Analyze recent framework changes
- [x] Create detailed plan with update requirements

### Pending

#### HIGH PRIORITY
- [ ] **doc-flow/SHARED_CONTENT.md** - Update validation script status, add ICON to artifact types, update cumulative tagging
- [ ] **doc-tasks** - CRITICAL: Add Section 8 Implementation Contracts, update validation script name, neutralize examples
- [ ] **doc-impl** - Add 4-PART structure, update validation script name, neutralize examples
- [ ] **doc-ctr** - Update validation script name (validate_ctr.sh), neutralize examples
- [ ] **doc-iplan** - Update validation script name (validate_iplan.sh), neutralize examples

#### MEDIUM PRIORITY
- [ ] **doc-brd** - Verify consistency with template and rules
- [ ] **doc-prd** - Verify consistency with template and rules
- [ ] **doc-ears** - Verify consistency with template and rules
- [ ] **doc-bdd** - Verify consistency with template and rules
- [ ] **doc-adr** - Verify consistency with template and rules
- [ ] **doc-sys** - Verify consistency with template and rules
- [ ] **doc-req** - Verify consistency with template and rules
- [ ] **doc-spec** - Verify consistency with template and rules
- [ ] **doc-flow/SKILL.md** - Update orchestrator references
- [ ] **doc-validator** - Update validation scripts list

### Notes
- Domain neutralization confirmed by user: Replace financial examples with generic software examples
- Each skill reviewed individually as requested
- Validation script naming: Change `validate_{type}_template.sh` → `validate_{type}.sh`

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/.claude/skills/` directory
- Understanding of SDD framework layers (0-12)
- Reference files in `ai_dev_flow/` for accuracy

### Execution Steps

**For each skill, follow this process:**

1. Read current SKILL.md file
2. Read corresponding template and rules files from `ai_dev_flow/{TYPE}/`
3. Make required updates
4. Verify consistency

**Execution Order** (sequential, individual review):

1. `.claude/skills/doc-flow/SHARED_CONTENT.md`
   - Update Section 4 "Validation Script Status" - mark CTR, IMPL, TASKS, IPLAN, ICON as available
   - Add ICON to Section 1 "File Naming Patterns"
   - Update Section 3 cumulative tagging to include `@icon` format

2. `.claude/skills/doc-tasks/SKILL.md`
   - Change `validate_tasks_template.sh` → `validate_tasks.sh`
   - ADD Section 8 - Implementation Contracts (MANDATORY)
   - Add `@icon` to cumulative tagging examples
   - Neutralize trade_validation → data_validation examples

3. `.claude/skills/doc-impl/SKILL.md`
   - Change `validate_impl_template.sh` → `validate_impl.sh`
   - Add 4-PART structure (Project Context, Phased Implementation, Project Management, Tracking)
   - Emphasize WHO/WHAT/WHEN focus
   - Neutralize examples

4. `.claude/skills/doc-ctr/SKILL.md`
   - Change `validate_ctr_template.sh` → `validate_ctr.sh`
   - Remove "(under development)" notes
   - Neutralize examples

5. `.claude/skills/doc-iplan/SKILL.md`
   - Change `validate_iplan_template.sh` → `validate_iplan.sh`
   - Neutralize examples

6-13. Medium priority skills (doc-brd through doc-spec)
   - Verify validation script references
   - Verify cumulative tagging examples
   - Neutralize any financial examples

14. `.claude/skills/doc-flow/SKILL.md`
   - Update orchestrator references

15. `.claude/skills/doc-validator/SKILL.md`
   - Add new validation scripts to available list

### Verification
- Each updated skill should reference correct validation script name
- Domain examples should be neutralized (data_validation, not trade_validation)
- TASKS skill should have Section 8 Implementation Contracts
- IMPL skill should document 4-PART structure

## Key Patterns to Apply

### 1. Validation Script Names
Change from `validate_{type}_template.sh` to `validate_{type}.sh`

### 2. Implementation Contracts (TASKS only)
Add Section 8:
```markdown
### 8. Implementation Contracts

#### 8.1 Contracts Provided
- `@icon: ICON-NNN:ContractName`
- `@icon-role: provider`

#### 8.2 Contracts Consumed
- `@icon: ICON-NNN:ContractName`
- `@icon-role: consumer`

#### 8.3 No Contracts
If this TASKS provides no contracts and consumes no contracts, state explicitly:
"This TASKS document neither provides nor consumes implementation contracts."
```

### 3. Domain Neutralization
Replace:
- "trade_validation" → "data_validation"
- "position_limit" → "business_rule"
- "TradeOrderRequest" → "DataRequest"
- "trade_validator" → "data_validator"
- "position_repository" → "data_repository"

## References

### Primary Files to Modify
```
.claude/skills/doc-flow/SHARED_CONTENT.md
.claude/skills/doc-flow/SKILL.md
.claude/skills/doc-brd/SKILL.md
.claude/skills/doc-prd/SKILL.md
.claude/skills/doc-ears/SKILL.md
.claude/skills/doc-bdd/SKILL.md
.claude/skills/doc-adr/SKILL.md
.claude/skills/doc-sys/SKILL.md
.claude/skills/doc-req/SKILL.md
.claude/skills/doc-impl/SKILL.md
.claude/skills/doc-ctr/SKILL.md
.claude/skills/doc-spec/SKILL.md
.claude/skills/doc-tasks/SKILL.md
.claude/skills/doc-iplan/SKILL.md
.claude/skills/doc-validator/SKILL.md
```

### Reference Files (read-only for accuracy)
```
ai_dev_flow/scripts/validate_*.sh
ai_dev_flow/CTR/CTR_CREATION_RULES.md
ai_dev_flow/CTR/CTR_VALIDATION_RULES.md
ai_dev_flow/TASKS/TASKS_CREATION_RULES.md
ai_dev_flow/TASKS/TASKS_VALIDATION_RULES.md
ai_dev_flow/TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md
ai_dev_flow/IMPL/IMPL_CREATION_RULES.md
ai_dev_flow/IMPL/IMPL_VALIDATION_RULES.md
ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md
ai_dev_flow/IPLAN/IPLAN_VALIDATION_RULES.md
ai_dev_flow/ICON/ICON_CREATION_RULES.md
ai_dev_flow/ICON/ICON_VALIDATION_RULES.md
```

## Estimated Effort
- doc-flow/SHARED_CONTENT.md: 15 min
- doc-tasks (CRITICAL): 20 min
- doc-impl, doc-ctr, doc-iplan: 10 min each
- Other skills (8): 5 min each
- doc-validator: 10 min

**Total**: ~2 hours for all 14 skills + SHARED_CONTENT.md
