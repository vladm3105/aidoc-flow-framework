# UCX v1.17.0 - Fixer-to-LLM Hand-off System

**Release Date**: 2026-03-15
**Status**: Complete

## Summary

UCX v1.17.0 introduces a seamless hand-off system between the script-based fixer and LLM remediation. When validation runs, it automatically fixes structural issues and records what was done, what needs LLM completion, and what should not be undone. This context flows to remediation personas through the validation report.

## ⚠️ Breaking Changes

### Validation Now Always Fixes

**Before (v1.16.x)**: `ucx validate brd BRD-01` validated only; `--fix` required for fixes.

**After (v1.17.0)**: `ucx validate brd BRD-01` validates AND fixes automatically.

**Migration**:
- Remove `--fix` from all scripts and CI/CD pipelines (now default)
- Add `--no-fix` where validation-only behavior is needed
- Update pre-commit hooks to use `--no-fix` (see below)

### Pre-commit Hook Update

Pre-commit hooks should use `--no-fix` to prevent staging area conflicts:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-validate
        name: UCX BRD Validation
        entry: ucx validate brd --no-fix  # <-- ADD --no-fix
        language: system
        files: ^docs/01_BRD/
        types: [markdown]
```

## New Features

### 1. Always-Fix Validation

Validation now automatically fixes structural issues on every run:

```bash
# Default: validate + fix + report
ucx validate brd docs/01_BRD/BRD-01

# Skip fixing (validate only)
ucx validate brd docs/01_BRD/BRD-01 --no-fix

# Deprecated (shows warning)
ucx validate brd docs/01_BRD/BRD-01 --fix
```

### 2. FixerContext Data Structure

New `FixerContext` dataclass tracks fixer session results:

```python
from ucx.validators.common.result import FixerContext

ctx = FixerContext(
    session_id="abc12345",
    timestamp="2026-03-15T12:00:00Z",
    fixed_count=10,          # Fully fixed
    partial_fix_count=3,     # Script + LLM needed
    skipped_count=2,         # LLM-only
    llm_completion=[...],    # Partial fixes for LLM
    llm_only=[...],          # Semantic issues
    fixer_applied=[...],     # Protected changes
)
```

### 3. Validation Report Section 7

The validation report now includes a "Fixer Session Summary" section:

```markdown
## 7. Fixer Session Summary

**Session ID**: `abc12345`
**Timestamp**: 2026-03-15T12:00:00Z

| Metric | Count |
|--------|-------|
| Fixed (Complete) | 10 |
| Partial (LLM Completion) | 3 |
| Skipped | 2 |

### 7.1 LLM Completion Required
[Table of partial fixes needing LLM completion]

### 7.2 LLM-Only Issues
[Table of semantic issues only LLM can fix]

### 7.3 Protected Changes (Do Not Undo)
[List of script fixes to protect]

### 7.4 Machine-Readable Context
<!-- FIXER_CONTEXT_START
{JSON context}
FIXER_CONTEXT_END -->
```

### 4. LLM_COMPLETION Markers

Partial fixes insert markers in documents:

```html
<!-- LLM_COMPLETION: GATE-E010 -->
<!-- Script: Splits file at section boundaries -->
<!-- Task: Review split points for semantic coherence -->
```

### 5. Clean Markers Command

Remove markers after remediation:

```bash
ucx clean-markers docs/01_BRD/BRD-01
```

### 6. Remediation Integration

UCRem reads fixer context from validation report:

- `_load_fixer_context()` - Parses Section 7 JSON
- `_format_fixer_handoff_section()` - Injects into prompts
- Personas see "FIXER HAND-OFF CONTEXT" section

### 7. Persona Hand-off Protocol

All 6 fixer personas updated with hand-off instructions:

- architect.md
- auditor.md
- qa_lead.md
- integration_lead.md
- chaos_engineer.md
- chairperson.md

## Code Classifications

### LLM_COMPLETION_CODES

Codes where script does partial fix, LLM completes:

| Code | Script Action | LLM Task |
|------|---------------|----------|
| GATE-E010 | Splits file at section boundaries | Review split points for semantic coherence |
| BRD-W011 | Adds @diagram-request placeholder | Define system context with components |
| BRD-W012 | Adds @diagram-request placeholder | Define interaction flow |
| DIAG-E001 | Adds DIAGRAM-REQUIRED placeholder | Create Mermaid diagram |
| FWDREF-E001 | Converts to FWDREF-DEFERRED | Verify cross-document references |

### LLM_ONLY_CODES

Codes that only LLM can handle:

| Code | Reason |
|------|--------|
| CONTENT-E001 | Content quality requires semantic review |
| LOGIC-E001 | Logical consistency requires domain understanding |
| TRACE-E001 | Traceability gaps require cross-document analysis |

## Files Changed

| File | Changes |
|------|---------|
| `ucx/validators/common/result.py` | +80 lines: FixerContext, _format_fixer_section() |
| `ucx/validators/brd/fixer.py` | +90 lines: LLM codes, partial tracking, markers |
| `ucx/api/remediation.py` | +120 lines: context loading, prompt injection |
| `ucx/cli/main.py` | +60 lines: always-fix, clean-markers command |
| `skills/architect.md` | +25 lines: hand-off protocol |
| `skills/auditor.md` | +25 lines: hand-off protocol |
| `skills/qa_lead.md` | +25 lines: hand-off protocol |
| `skills/integration_lead.md` | +25 lines: hand-off protocol |
| `skills/chaos_engineer.md` | +25 lines: hand-off protocol |
| `skills/chairperson.md` | +25 lines: hand-off protocol |
| `ucx/version.py` | Version bump to 1.17.0 |

## Workflow

```
┌────────────────────────────────────────────┐
│     ucx validate brd BRD-01                │
│     (ALWAYS fixes by default)              │
└────────┬───────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          1. Validation                   │
│  └─ Identifies all issues                │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          2. BRD Fixer (automatic)        │
│  ├─ Fix issues (full or partial)         │
│  ├─ Track partial fixes (LLM_COMPLETION) │
│  ├─ Insert markers in documents          │
│  └─ Build FixerContext                   │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          3. Re-validation                │
│  └─ Verify fixes, find remaining issues  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     4. Report Generation                 │
│  ├─ Sections 1-6: Standard content       │
│  └─ Section 7: Fixer Session Summary     │
│       ├─ LLM Completion table            │
│       ├─ Protected changes list          │
│       └─ Embedded JSON (machine-readable)│
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          UCRem Remediation               │
│  ├─ Parse FIXER_CONTEXT_START block      │
│  ├─ Inject "FIXER HAND-OFF CONTEXT"      │
│  │   - Partial fixes (highest priority)  │
│  │   - LLM-only issues                   │
│  │   - Protected changes (DO NOT UNDO)   │
│  └─ Personas complete tasks              │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     ucx clean-markers BRD-01             │
│  - Remove LLM_COMPLETION markers         │
│  - Run after remediation complete        │
└──────────────────────────────────────────┘
```

## Backward Compatibility

- `--fix` flag still works (shows deprecation warning)
- Remediation works without fixer context (shows recommendation)
- Validation report without Section 7 is still valid
- Pre-v1.17.0 personas ignore hand-off section

---

*See also*: [PLAN-006_fixer_to_llm_handoff.md](plans/PLAN-006_fixer_to_llm_handoff.md), [CHANGELOG_v1.16.2.md](CHANGELOG_v1.16.2.md)
