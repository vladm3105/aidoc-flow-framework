# UCX v1.14.5 - One-Turn Review Feature Parity

**Release Date**: 2026-03-14

## Overview

This release achieves feature parity between one-turn and multi-turn review modes by ensuring one-turn review loads project-specific skills (with Category Tagging) instead of framework skills.

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

## Files Changed

| File | Changes |
|------|---------|
| `ucx/api/review.py` | Updated `_load_skills()` for project-first loading |

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
