# AI Agent Memory System

## Overview

AI agents working on issues maintain persistent memory through MEMORY.md files. This enables context preservation across sessions, knowledge transfer between agents, and institutional learning.

---

## Memory File Location

| Type | Path |
|------|------|
| **Active Work** | `governance/memory/active/MEMORY-{ISSUE_NUMBER}.md` |
| **Completed Work** | `governance/memory/archive/MEMORY-{ISSUE_NUMBER}.md` |
| **Global Learnings** | `governance/memory/GLOBAL_LEARNINGS.md` |
| **Template** | `governance/templates/MEMORY.md` |

---

## Memory Lifecycle

```
Issue labeled ai:ready
    │
    ▼
┌─────────────────────────────────┐
│ agent-dispatch.yml Step 6.5    │
│ Creates MEMORY-{ISSUE}.md      │
│ from template                  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Implementation (Step 13)       │
│ AI agent reads + updates       │
│ memory during work             │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Commit (Step 16)               │
│ Memory committed with code     │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Issue Closed                   │
│ Memory moved to archive/       │
│ Key learnings → GLOBAL         │
└─────────────────────────────────┘
```

---

## When to Update Memory

| Event | Action |
|-------|--------|
| **Session Start** | Read existing memory, update "Last Updated" timestamp |
| **Key Decision** | Record in "Key Decisions" section with rationale |
| **Blocker Resolved** | Add to "Blockers & Resolutions" table |
| **Pattern Discovered** | Add to "Code Patterns Used" section |
| **File Modified** | Add to "Files Modified" table |
| **Session End** | Update "Next Session Notes" for continuity |

---

## AI Agent Instructions

### Starting Work on an Issue

```bash
# 1. Check for existing memory
ISSUE_NUM=123
MEMORY_FILE="governance/memory/active/MEMORY-${ISSUE_NUM}.md"

if [ -f "$MEMORY_FILE" ]; then
  cat "$MEMORY_FILE"
fi

# 2. Check global learnings for project patterns
cat governance/memory/GLOBAL_LEARNINGS.md 2>/dev/null || true
```

### During Implementation

Update the memory file as you work:

1. **Key Decisions**: When choosing between approaches, document the choice and rationale
2. **Blockers**: When stuck, document the blocker; when resolved, add resolution
3. **Patterns**: When reusing a project pattern, document it for future reference
4. **Files**: Track every file you modify with a brief change summary

### Completing Work

```bash
# 1. Finalize all sections
# 2. Update "Next Session Notes" even if issue is closing
# 3. Commit memory with code changes

git add governance/memory/active/MEMORY-${ISSUE_NUM}.md
git commit -m "chore: Update AI agent memory for #${ISSUE_NUM}"
```

---

## Memory Sections Reference

### Key Decisions

Record architectural choices with trade-off analysis:

```markdown
## Key Decisions

- **Used async/await over callbacks**: Matches existing codebase pattern in `src/utils/`.
  Trade-off: Requires Python 3.8+, but project already requires 3.10+.

- **Added retry logic to API calls**: Acceptance criterion #3 requires fault tolerance.
  Implemented exponential backoff (max 3 retries, 1s/2s/4s delays).
```

### Blockers & Resolutions

Track obstacles and solutions:

```markdown
## Blockers & Resolutions

| Blocker | Resolution | Date |
|---------|------------|------|
| pytest fixture not found | Added conftest.py to tests/ directory | 2026-02-18 |
| API rate limit during tests | Mocked external API calls | 2026-02-18 |
```

### Code Patterns Used

Document reusable patterns:

```markdown
## Code Patterns Used

- **Error handling**: Use `try/except` with specific exceptions, log with `logger.exception()`
- **Config loading**: Use `pydantic.BaseSettings` with `.env` file support
- **Test fixtures**: Define in `conftest.py`, use `@pytest.fixture` decorator
```

---

## Global Learnings

After issue completion, promote universally applicable learnings to `GLOBAL_LEARNINGS.md`:

```markdown
# Global Learnings

## Project Conventions

- All API endpoints return `{"data": ..., "error": ...}` structure
- Use `snake_case` for Python, `camelCase` for TypeScript
- Tests go in `tests/` directory, mirroring `src/` structure

## Common Patterns

- Database connections use `contextlib.contextmanager` pattern
- All config loaded via environment variables (no hardcoded values)
- Logging uses structured format: `logger.info("action", extra={"key": "value"})`

## Known Gotchas

- pytest-asyncio requires `pytest.mark.asyncio` decorator
- GitHub API returns 422 for stale line mappings in PR comments
```

---

## Integration with Workflows

| Workflow | Memory Action |
|----------|---------------|
| `agent-dispatch.yml` | Creates initial MEMORY.md from template (Step 6.5) |
| `agent-dispatch.yml` | Appends memory to instructions (Step 12) |
| `agent-dispatch.yml` | Commits memory with code (Step 16) |
| `pr-merge-cleanup.yml` | Archives MEMORY.md on issue close (future) |
| `extract-learnings.yml` | Monthly extraction to GLOBAL_LEARNINGS.md (future) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {DATE} | Initial creation |
