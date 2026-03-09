# DEPRECATED

**This directory is deprecated as of 2026-03-09.**

## Replacement

All functionality in this directory has been superseded by the **UCx (Unified Context) Framework**:

```
/opt/data/docs_flow_framework/ai_dev_ssd_flow/UCX/
```

## Migration Guide

| Old Location | New Location | Notes |
|--------------|--------------|-------|
| `automation/AI_EXPERTS/` | `ai_dev_ssd_flow/UCX/skills/` | Persona definitions |
| `automation/pipelines/doc_review/` | `ai_dev_ssd_flow/UCX/review/` | UCR replaces multi-model pipeline |
| `automation/pipelines/doc_generate/` | `ai_dev_ssd_flow/UCX/creation/` | UCC replaces doc generation |
| `automation/core/` | N/A | UCX uses simpler shell scripts |

## Why Deprecated?

1. **Single-Pass is Better**: The multi-model pipeline in `pipelines/doc_review/` had 93% accuracy with false positive risks. UCX's single-pass approach achieves 100% accuracy.

2. **Unified Framework**: UCX consolidates creation, review, and remediation into one cohesive framework with consistent patterns.

3. **Simpler Architecture**: UCX eliminates the complex agent-agnostic routing in favor of direct Claude CLI usage.

4. **Better Integration**: UCX integrates with Claude Skills (`/doc-*`) for seamless workflow.

## What to Do

### For Document Reviews

**Old way (deprecated):**
```bash
./automation/pipelines/doc_review/run_review.sh docs/01_BRD/BRD-01.md
```

**New way (use UCX):**
```bash
./ai_dev_ssd_flow/UCX/review/run_ucr.sh brd docs/01_BRD/
```

### For Document Generation

**Old way (deprecated):**
```bash
./automation/pipelines/doc_generate/run_generate.sh brd
```

**New way (use UCX):**
```bash
./ai_dev_ssd_flow/UCX/creation/run_ucc.sh brd output/ --from-ref refs/
```

## Timeline

- **2026-03-09**: Deprecated
- **2026-06-09**: Planned removal (3 months notice)

## Questions?

See UCX documentation:
- `ai_dev_ssd_flow/UCX/docs/UNIFIED_CONTEXT_FRAMEWORK.md`
- `ai_dev_ssd_flow/UCX/docs/HOW_TO_USE.md`
