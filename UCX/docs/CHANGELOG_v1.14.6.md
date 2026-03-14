# UCX v1.14.6 - Session Directory Rename & Review Mode Documentation

**Release Date**: 2026-03-14

## Overview

This release improves naming clarity for session storage and adds comprehensive documentation for review modes.

## Breaking Changes

### Session Directory Rename

| Old Name | New Name | Reason |
|----------|----------|--------|
| `.doc_review_memory/` | `.ucx_review_session/` | Clearer UCX ownership and purpose |
| `final_body.md` | `assembled_report.md` | Describes actual content |

**Migration**: Delete or rename existing `.doc_review_memory/` directories. New sessions will use the new naming automatically.

```bash
# Find and rename existing directories
find . -type d -name ".doc_review_memory" -exec sh -c 'mv "$1" "$(dirname "$1")/.ucx_review_session"' _ {} \;

# Or simply delete (sessions will regenerate)
find . -type d -name ".doc_review_memory" -exec rm -rf {} +
```

## New Documentation

### Review Modes: One-Turn vs Multi-Turn

Added comprehensive documentation explaining the two review modes:

**One-Turn Review** (Default):
- Single LLM API call with all 12 personas
- Full document visibility for all personas
- Better for cross-domain issue detection
- Lower cost, faster execution

**Multi-Turn Review** (`--multi-turn`):
- Sequential API calls (one per persona)
- Persona-specific context filtering
- Prior findings summarization (anti-repetition)
- Better for large documents, deep analysis

### Documentation Locations

| Document | Section Added |
|----------|---------------|
| `UNIFIED_CONTEXT_REVIEW.md` | Full "Review Modes: One-Turn vs Multi-Turn" section |
| `README.md` | Comparison table and recommendations |

### Key Trade-offs

| Aspect | One-Turn | Multi-Turn |
|--------|----------|------------|
| API Calls | 1 | 12 |
| Document Context | Full | Filtered per persona |
| Cross-Domain Detection | Better | May miss |
| Deep Analysis | Good | Better |
| Cost | Lower | Higher |
| Resume Support | No | Yes |

### Recommendations

| Document Size | Recommendation |
|---------------|----------------|
| < 30K tokens | One-turn |
| 30K - 80K tokens | Either |
| > 80K tokens | Multi-turn |

## Files Changed

| File | Changes |
|------|---------|
| `ucx/core/review_memory.py` | `MEMORY_DIR_NAME`, `assembled_report_file` |
| `ucx/api/review.py` | Docstring update |
| `ucx/cli/main.py` | Clean memory path |
| `ucx/cli/prompts.py` | Output directory help |
| `ucx/prompts/api.py` | Default output directory |
| `ucx/prompts/document.py` | Skip patterns |
| `scripts/generate_prompts.py` | Skip patterns |
| `README.md` | Review mode documentation |
| `docs/UNIFIED_CONTEXT_REVIEW.md` | Review mode documentation |
| `docs/HOW_TO_USE.md` | Path references |
| `docs/ROADMAP.md` | Path references |
| `docs/CHANGELOG_v1.14.*.md` | Path references |
| `docs/plans/PLAN-003, PLAN-005` | Path references |

## Session Directory Structure

```
docs/01_BRD/BRD-01/.ucx_review_session/
├── session.json            # Session metadata
├── shared_context.txt      # Document content snapshot
├── prompt_architect.txt    # Prompt sent to architect
├── response_architect.txt  # Response from architect
├── prompt_auditor.txt      # ...
├── response_auditor.txt    # ...
└── assembled_report.md     # Combined final report
```

## References

- [CHANGELOG_v1.14.5](CHANGELOG_v1.14.5.md) - One-turn feature parity
- [UNIFIED_CONTEXT_REVIEW.md](UNIFIED_CONTEXT_REVIEW.md) - Review modes documentation

---

*UCX v1.14.6 - 2026-03-14*
