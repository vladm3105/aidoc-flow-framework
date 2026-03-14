# UCX v1.14.8 - Terminology Update: Unified Prompt / Persona Prompts

**Release Date**: 2026-03-14

## Overview

This release renames the review modes from technical terms to more meaningful names:

| Old Term | New Term | Description |
|----------|----------|-------------|
| One-turn | **Unified Prompt** | Single prompt with all 12 personas |
| Multi-turn | **Persona Prompts** | Per-persona filtered prompts |

## Rationale

The new terminology better describes what each mode does:

- **Unified Prompt**: All personas review together in a single unified context
- **Persona Prompts**: Each persona gets a dedicated, focused prompt

## Changes

### Documentation Updates

| File | Changes |
|------|---------|
| `README.md` | Updated terminology throughout |
| `docs/UNIFIED_CONTEXT_REVIEW.md` | Updated mode descriptions |
| `docs/ROADMAP.md` | Updated version info |
| `docs/CHANGELOG_v1.14.5.md` | Updated references |
| `docs/CHANGELOG_v1.14.6.md` | Updated references |
| `docs/CHANGELOG_v1.14.7.md` | Updated references |

### Code Comment Updates

| File | Changes |
|------|---------|
| `ucx/version.py` | Updated version history comments |
| `ucx/api/review.py` | Updated docstrings |
| `ucx/core/review_memory.py` | Updated module docstring |
| `ucx/core/persona_prompts.py` | Updated module docstring |

### File Naming

| Old Name | New Name |
|----------|----------|
| `prompt_one_turn.txt` | `prompt_unified.txt` |
| `prompt_one_turn.meta.json` | `prompt_unified.meta.json` |

### CLI (Backwards Compatible)

The `--multi-turn` flag is preserved for backwards compatibility:

```bash
# These are equivalent:
ucx review brd docs/01_BRD/BRD-01/ --multi-turn  # Legacy
ucx review brd docs/01_BRD/BRD-01/ --persona     # New (alias)
```

## Terminology Reference

| Context | Unified Prompt | Persona Prompts |
|---------|----------------|-----------------|
| **CLI flag** | (default) | `--multi-turn` / `--persona` |
| **API method** | `review()` | `review_multi_turn()` |
| **Prompt file** | `prompt_unified.txt` | `prompt_{persona}.txt` |
| **Session dir** | `.ucx_review_session/` | `.ucx_review_session/` |

## Migration

No migration required. The terminology change is purely cosmetic and does not affect functionality.

## References

- [CHANGELOG_v1.14.7.md](CHANGELOG_v1.14.7.md) - Attention steering fix
- [UNIFIED_CONTEXT_REVIEW.md](UNIFIED_CONTEXT_REVIEW.md) - Review modes documentation

---

*UCX v1.14.8 - 2026-03-14*
