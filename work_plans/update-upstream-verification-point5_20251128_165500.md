# Implementation Plan - Update Upstream Verification Point 5

**Created**: 2025-11-28 16:55:00 EST
**Status**: Ready for Implementation

## Objective

Change point 5 of the upstream artifact verification callout from "Create missing artifacts if required" to "Do NOT create missing upstream artifacts - skip that functionality instead."

This enforces the SDD document hierarchy: if upstream artifacts don't exist, downstream functionality should not be implemented.

## Context

- Just completed adding upstream verification guidance to all SDD framework files (39 files total)
- User requested changing point 5 to enforce strict document hierarchy flow
- Rationale: Prevents creating orphaned implementations without proper business/product justification

## Task List

### Completed
- [x] Update 13 templates with callout box after Document Control
- [x] Update 13 creation rules with verification process section
- [x] Update 12 doc-* skills with upstream verification guidance
- [x] Update TRACEABILITY.md with global upstream verification rules
- [x] Validate all updates with grep checks

### Pending
- [ ] Change point 5 text in all templates (14 files)
- [ ] Change point 5 text in all creation rules (13 files)
- [ ] Change decision rules table in creation rules
- [ ] Change point 5 text in all skills (12 files)
- [ ] Change TRACEABILITY.md decision rules and bullet point
- [ ] Validate changes

## Implementation Guide

### Text Changes Required

**In Callout Box (templates, skills)**:
- Old: `> 5. **Create missing artifacts if required**: If SDD workflow requires an upstream artifact that's missing, create it first`
- New: `> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.`

**In YAML comments (SPEC-TEMPLATE.yaml)**:
- Old: `# 5. Create missing artifacts if required: If SDD workflow requires an upstream artifact, create it first`
- New: `# 5. Do NOT create missing upstream artifacts: If upstream are missing, skip that functionality`

**In Decision Rules Tables (creation rules, TRACEABILITY.md)**:
- Old row: `| Upstream required but missing | Create upstream artifact FIRST, then reference |`
- New row: `| Upstream required but missing | Skip that functionality - do NOT implement |`

### Files to Update

**Templates (14 files)**:
- ai_dev_flow/BRD/BRD-TEMPLATE.md
- ai_dev_flow/PRD/PRD-TEMPLATE.md
- ai_dev_flow/EARS/EARS-TEMPLATE.md
- ai_dev_flow/BDD/BDD-TEMPLATE.feature
- ai_dev_flow/ADR/ADR-TEMPLATE.md
- ai_dev_flow/SYS/SYS-TEMPLATE.md
- ai_dev_flow/REQ/REQ-TEMPLATE.md
- ai_dev_flow/IMPL/IMPL-TEMPLATE.md
- ai_dev_flow/CTR/CTR-TEMPLATE.md
- ai_dev_flow/SPEC/SPEC-TEMPLATE.md
- ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml
- ai_dev_flow/TASKS/TASKS-TEMPLATE.md
- ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
- ai_dev_flow/ICON/ICON-TEMPLATE.md

**Creation Rules (13 files)**:
- ai_dev_flow/*/\*_CREATION_RULES.md

**Skills (12 files)**:
- .claude/skills/doc-*/SKILL.md

**Framework Doc (1 file)**:
- ai_dev_flow/TRACEABILITY.md

### Verification

```bash
# Verify old text is gone
grep -r "Create missing artifacts if required" ai_dev_flow/ .claude/skills/

# Verify new text is present
grep -r "Do NOT create missing upstream" ai_dev_flow/ .claude/skills/

# Check decision tables updated
grep -r "Skip that functionality" ai_dev_flow/*/*_CREATION_RULES.md
```

## References

- Related work plan: work_plans/add-upstream-verification_20251128_160558.md
- Key framework file: ai_dev_flow/TRACEABILITY.md
