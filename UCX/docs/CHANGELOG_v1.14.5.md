# UCX v1.14.5 - One-Turn Review Feature Parity

**Release Date**: 2026-03-14

## Overview

This release achieves feature parity between one-turn and multi-turn review modes, standardizes persona naming, and fixes skill directory resolution.

## Problem Statement

One-turn review (`ucx review brd ...`) was loading framework skills while multi-turn review (`ucx review brd ... --multi-turn`) correctly loaded project-specific skills.

| Review Mode | Skill Loading | Category Tagging |
|-------------|---------------|------------------|
| Multi-turn | Project-specific | YES |
| One-turn (before) | Framework fallback | NO |
| One-turn (after) | Project-specific | YES |

This caused inconsistent review quality between modes.

## Solution

Updated `UCRPhase._load_skills()` in `ucx/api/review.py` to implement project-first skill loading:

```python
def _load_skills(self, skill_names: list[str]) -> str:
    """Load skill content for personas.

    Priority order (v1.14.5+):
    1. Project-specific skills ({project_dir}/docs/UCX/skills/)
    2. Framework skills (fallback)
    """
    # Get project and framework skill directories
    project_dir = self.config.get_project_dir()
    project_skills_dir = project_dir / "docs" / "UCX" / "skills" if project_dir else None
    framework_skills_dir = self.config.get_skill_dir()

    for name in skill_names:
        # Priority 1: Project-specific skills
        if project_skills_dir and project_skills_dir.exists():
            skill_path = project_skills_dir / f"{name}.md"
            if skill_path.exists():
                # Use project skill
                ...

        # Priority 2: Framework skills (fallback)
        ...
```

## Features Now Available in One-Turn

| Feature | Multi-Turn | One-Turn (v1.14.5+) |
|---------|------------|---------------------|
| Project-specific skills | YES | YES |
| Category Tagging (CAT:xxx) | YES | YES |
| Finding Format (PREFIX-P#-NNN) | YES | YES |
| Domain-specific checklists | YES | YES |
| Skill logging (debug) | YES | YES |

## Features NOT in One-Turn (By Design)

These multi-turn features are not applicable to one-turn mode:

| Feature | Reason |
|---------|--------|
| Prior Findings Summarization | No previous responses in single call |
| Anti-Repetition Instructions | Single call with all personas |
| Context Engineering (hierarchical) | Multi-turn optimization |

## Category Tagging Additions

Added Category Tagging (`[CAT:xxx]`) sections to 3 personas that were missing them:

| Persona | Categories Added |
|---------|------------------|
| auditor | COMPL, SEC, LEG, PROC, OPS |
| fact_checker | DEF, REF, CONS, DATA, DOC |
| product_owner | FEAT, USER, ACC, SCOPE, DATA |

This ensures all findings from these personas receive proper category tagging for weighted scoring (v1.12.0+).

## Persona Naming Standardization

Renamed `integration_expert` → `integration_lead` for consistent persona/skill naming across the codebase.

| Location | Change |
|----------|--------|
| `ucx/config/layer_skills.py` | 17 occurrences renamed |
| `/UCX/skills/integration_lead.md` | File renamed (was symlink) |
| `ucx/core/persona_prompts.py` | Removed alternative name mapping |

**Audit Results**: All 14 personas now match their skill filenames exactly:
- architect, auditor, business_analyst, chairperson, chaos_engineer
- fact_checker, integration_lead, operator, product_owner, qa_lead
- requirements_specialist, strategist, tech_lead, ux_strategist

## Settings Fix

Fixed `get_skill_dir()` in `ucx/config/settings.py` to return the correct path.

| Before | After |
|--------|-------|
| `ucx/skills/personas/` (deprecated) | `/UCX/skills/` |

## Files Changed

| File | Changes |
|------|---------|
| `ucx/api/review.py` | Updated `_load_skills()` for project-first loading |
| `ucx/config/layer_skills.py` | Renamed `integration_expert` → `integration_lead` (17 occurrences) |
| `ucx/config/settings.py` | Fixed `get_skill_dir()` path |
| `ucx/core/persona_prompts.py` | Removed alternative name mapping |
| `/UCX/skills/integration_lead.md` | Renamed from `integration_expert.md` |

## Verification

```bash
# One-turn review should now log "Loaded N project-specific skills"
ucx -v review brd docs/01_BRD/BRD-01/ 2>&1 | grep -i "project-specific skill"

# Compare skill loading between modes
ucx -v review brd docs/01_BRD/BRD-01/ 2>&1 | grep -i skill
ucx -v review brd docs/01_BRD/BRD-01/ --multi-turn 2>&1 | grep -i skill
```

## Impact

- **One-turn reviews** now benefit from the same project-specific Category Tagging guidance as multi-turn reviews
- **Instruction token quality** is consistent between review modes
- **Finding categorization** is improved for weighted scoring (v1.12.0+)

## References

- [CHANGELOG_v1.14.4](CHANGELOG_v1.14.4.md) - Extraction Pattern Fixes
- [CHANGELOG_v1.12.0](CHANGELOG_v1.12.0.md) - Category Tagging Introduction
- [skills/README.md](../../b-local/b-local-docs/docs/UCX/skills/README.md) - Project Skills Documentation

---

*UCX v1.14.5 - 2026-03-14*
