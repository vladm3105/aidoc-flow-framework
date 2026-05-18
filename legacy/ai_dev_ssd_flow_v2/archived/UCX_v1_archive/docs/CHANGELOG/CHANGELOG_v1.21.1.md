# UCX v1.21.1 — Create Path Resolution Fix

**Release Date**: 2026-03-20

---

## Overview

Fixes double-directory nesting when `ucx create` is called with a full canonical
`.md` output path whose parent directory already matches the document slug.

---

## Problem

When an explicit output path such as:

```
docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md
```

was passed to `ucx create`, the path resolution logic in `UCCPhase.create()`
detected the `{DOC_ID}_{slug}` pattern in the stem and unconditionally created
an extra sub-directory, producing:

```
docs/02_PRD/PRD-01_platform_architecture/
  PRD-01_platform_architecture/          ← extra, incorrect nesting
    PRD-01_platform_architecture.md
```

This caused an `IsADirectoryError` in some call forms and silently wrote to the
wrong location in others.

---

## Fix

Added a `parent_already_is_slug` guard in `UCCPhase.create()` inside
`UCX/ucx/api/creation.py`:

```python
parent_already_is_slug = output_path.parent.name == stem
if (
    output_path.suffix == ".md"
    and "_" in stem
    and re.match(rf"^[A-Z]+-\d+_", stem, re.IGNORECASE)
    and not parent_already_is_slug      # ← new guard
):
    # bare slug filename: create slug/ sub-directory
    doc_folder = output_path.parent / stem
    ...
else:
    # caller already provided canonical path: write directly
    output_path.parent.mkdir(parents=True, exist_ok=True)
    actual_output = output_path
```

---

## Behavior After Fix

| Input form | Result |
|---|---|
| Plain ID: `docs/02_PRD/PRD-01` | UCX derives slug → creates `PRD-01_platform_architecture/PRD-01_platform_architecture.md` |
| Full canonical `.md` path with matching parent | Writes directly to the specified path — no extra sub-directory |
| Custom slug `.md` without matching parent | Creates `{stem}/` sub-directory as before |

---

## Examples

```bash
# Plain ID — UCX auto-creates slug directory (unchanged behavior)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
# writes: docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md

# Explicit canonical path — writes directly, no nesting (fixed)
ucx create prd docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture
# writes: docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md
```

---

## Files Changed

| File | Change |
|---|---|
| `UCX/ucx/api/creation.py` | Added `parent_already_is_slug` guard in path resolution |
| `UCX/docs/HOW_TO_CREATE_PRD.md` | Documented three path resolution rules; added explicit canonical path example |
| `UCX/docs/HOW_TO_USE.md` | Added canonical path form to PRD create examples |
| `UCX/README.md` | Added v1.21.1 changelog entry; added canonical path example in quick-start |
