# UCX v1.21.0 — Creation Prompt History

**Release Date**: 2026-03-19
**Plan Reference**: PLAN-009 Phase 7

---

## Overview

`ucx create` now saves the fully assembled creation prompt to disk by default. Every run
produces a timestamped file in `.ucx_create_session/` alongside the output document.
This enables prompt auditing, debugging, and re-use across models.

---

## What Changed

### New: Codex CLI Backend Support

UCX CLI mode now supports OpenAI Codex CLI as a first-class backend.

Examples:

```bash
ucx --cli-tool codex --model gpt-5-codex review brd docs/01_BRD/BRD-01/
ucx --cli-tool codex --model gpt-5-codex create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
```

Additional behavior updates:
- Quota retry prompt now includes `codex` as a selectable backend.
- Retry default model for codex is `gpt-5-codex`.
- Documentation/help text now list codex among supported CLI tools.

### New: Slugged PRD Filenames from Upstream Artifacts

When `ucx create` receives a plain output path such as `PRD-01` or `PRD-01.md`,
it now derives a slug from the upstream artifact and writes a more descriptive
filename:

```text
docs/02_PRD/PRD-01                      + BRD-01_platform_architecture
-> docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md
```

Rules:
- Plain doc ID path: auto-slugged
- Explicit custom filename (`PRD-01_custom_name.md`): preserved
- No upstream slug source: falls back to `.md` extension only

### New: Prompt Saved by Default

The assembled prompt (UCC prompt + skills + template + upstream BRD content) is written to:

```
<sectioned_doc_dir>/.ucx_create_session/prompt_<type>_<YYYYMMDDTHHMMSSz>.txt
```

Each run appends a new file — previous prompts are never overwritten, creating a full
creation history per document directory.

### Self-Documenting Header

Every saved prompt file includes a metadata header:

```
# UCX Creation Prompt — PRD
# Saved: 20260319T142301Z
# Output: docs/02_PRD/PRD-01_platform_architecture.md
# From upstream: docs/01_BRD/BRD-01_platform_architecture
# Prompt size: 190,432 chars
#------------------------------------------------------------------------------
... (full prompt content)
```

### Opt-Out Flag

```bash
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --no-save-prompt
```

### CLI Output

When a prompt is saved, the path is printed after creation:

```
Created: docs/02_PRD/PRD-01_platform_architecture.md
Prompt saved: docs/02_PRD/PRD-01_platform_architecture/.ucx_create_session/prompt_prd_20260319T142301Z.txt
```

---

## Files Changed

| File | Change |
|------|--------|
| `ucx/api/creation.py` | Added `save_prompt: bool = True` to `create()`; new `_save_prompt_to_session()` method; new auto-slugging of plain output paths to `{DOC_ID}_{slug}.md`; module constant `CREATE_SESSION_DIR = ".ucx_create_session"` |
| `ucx/ai/cli_client.py` | Added `codex` CLI backend (`codex exec -`) with optional `-m` model flag |
| `ucx/ai/__init__.py` | Updated CLI factory docs and non-Claude model pass-through behavior |
| `ucx/config/settings.py` | Updated `cli_tool` description to include codex |
| `ucx/cli/main.py` | Added `codex` to `--cli-tool` choices and quota-retry backend selector; updated help text/docstring examples |
| `ucx/validators/brd/fixer.py` | Added `.ucx_create_session` to skip list (prevents validator from reading prompt files as BRD content) |
| `ucx/validators/brd/duplicate_fixer.py` | Added `.ucx_create_session` to two skip lists |
| `ucx/prompts/document.py` | Added `r"\.ucx_create_session"` to `SKIP_PATTERNS` |
| `docs/plans/PLAN-009_prd_creation.md` | Added Phase 7 documenting this feature |
| `docs/HOW_TO_CREATE_PRD.md` | Added Prompt History sections to Quick Start and Validation chapters |
| `README.md` | Added v1.21.0 entry to version table; updated Quick Start `create` example |

---

## Python API

```python
from ucx import UCCPhase, UCXConfig

ucc = UCCPhase(UCXConfig())

# Default: prompt saved automatically
doc = ucc.create("prd", "docs/02_PRD/PRD-01.md", from_upstream=brd_path)
print(doc.metadata.get("prompt_saved_path"))
# docs/02_PRD/PRD-01_platform_architecture/.ucx_create_session/prompt_prd_20260319T142301Z.txt

# Opt out
doc = ucc.create("prd", "docs/02_PRD/PRD-01.md", from_upstream=brd_path, save_prompt=False)
```

---

## Session Directory Layout

```
docs/02_PRD/PRD-01_platform_architecture/
├── PRD-01_platform_architecture.md      ← created document
└── .ucx_create_session/
    ├── prompt_prd_20260319T142301Z.txt  ← first run
    ├── prompt_prd_20260320T091500Z.txt  ← second run (different model)
    └── ...
```

Validators skip `.ucx_create_session/` automatically — no `.gitignore` entry required
(though you may add one if you prefer not to commit prompt history).

---

## Comparison with Review Sessions

| | `.ucx_review_session/` | `.ucx_create_session/` |
|---|---|---|
| Created by | `ucx review` | `ucx create` |
| Default | Always | Always (v1.21.0+) |
| Resumable | Yes (multi-persona loop) | No (single call) |
| Contents | prompt + response per persona | prompt per run |
| Cleanup | `ucx review --clean-memory` | Manual or `--no-save-prompt` |

---

## Migration

No migration required. Existing projects gain `.ucx_create_session/` on the next
`ucx create` run. To suppress: add `--no-save-prompt` or set `save_prompt=False` in
the Python API.
