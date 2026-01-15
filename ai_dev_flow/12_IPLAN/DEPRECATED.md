# IPLAN (Layer 12) - DEPRECATED

**Deprecation Date**: 2026-01-15
**Replacement**: `ai_dev_flow/11_TASKS/TASKS-TEMPLATE.md`

---

## Why IPLAN Was Deprecated

IPLAN was merged into TASKS to reduce document overhead and streamline the implementation workflow.

### Before (Two Documents)
```
TASKS (Layer 11)     → WHAT to build (1450 lines)
IPLAN (Layer 12)     → HOW to execute (500 lines)
─────────────────────────────────────────────────
Total per feature:     ~2000 lines of planning docs
```

### After (One Document)
```
TASKS (Layer 11)     → WHAT + HOW unified (400-600 lines)
─────────────────────────────────────────────────
Total per feature:     ~500 lines
```

---

## Migration Guide

### IPLAN Content → TASKS Location

| IPLAN Section | TASKS Section |
|---------------|---------------|
| Verification Checklist | Development Plan Tracking (YAML block) |
| Context & Current State | Section 2: Scope |
| Implementation Steps | Section 3: Implementation Plan |
| Bash Commands | Section 4: Execution Commands |
| Validation Commands | Section 4.3: Validation Commands |
| Session Notes | Section 10: Session Log |

### Workflow Change

**Old Workflow**:
```
REQ → SPEC → TASKS → IPLAN → Code
```

**New Workflow**:
```
REQ → SPEC → TASKS → Code
```

---

## Existing IPLAN Documents

Existing IPLAN documents in projects should:

1. **Continue using them** if implementation is in progress
2. **Migrate to TASKS** for new features
3. **Archive completed IPLANs** - no need to convert historical docs

---

## References

- [TASKS-TEMPLATE.md](../11_TASKS/TASKS-TEMPLATE.md) - New unified template
- [DEVELOPMENT_PLAN_README.md](../11_TASKS/DEVELOPMENT_PLAN_README.md) - Updated workflow
