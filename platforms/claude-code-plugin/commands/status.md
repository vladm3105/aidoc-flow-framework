---
title: "Status — where is this project in the SDD flow"
description: "Scan the project's `docs/` tree and report per-layer state: exists, last edited, audited."
tags:
  - workflow
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Status

Answer the question "where am I in the 8-layer flow?" for the current project.
Read the `docs/` tree using the same `docs/0N_<ARTIFACT>/` layout the
PostToolUse hook (`hooks/sdd-doc-review.sh`) detects, plus the `.aidoc/`
scratch directory if present. Output is a per-layer table.

`/aidoc-flow:next` reads the same detection result and emits one concrete next
action. Run `/status` to see the map; run `/next` to be told where to step.

## Instructions

1. **Resolve the project root** — start from the current working directory.
   If `.claude/aidoc-flow.config.yaml` exists and sets `docs_root`, use that;
   otherwise default to `docs/`.

2. **Scan the docs root** for the eight canonical layer directories:

   ```text
   01_BRD  02_PRD  03_EARS  04_BDD  05_ADR  06_SPEC  07_TDD  08_IPLAN
   ```

   For each layer, determine four facts:

   | Fact | How to determine |
   |------|------------------|
   | `exists` | The directory `<docs_root>/0N_<ARTIFACT>/` is present |
   | `instances` | Count `.md` and `.yaml` files inside (excluding `00_index.*`) |
   | `last_edit` | `git log -1 --format=%cs -- <dir>` if in a git repo, else `mtime` of the newest file |
   | `audited` | An `.aidoc/<ARTIFACT>-NN.audit.*` (or equivalent project audit artifact) exists for at least one instance — heuristic; record `?` if unknown |

3. **Render the per-layer table**:

   ```text
   Project: <cwd>
   Docs root: <resolved docs_root>

   | # | Layer | Exists | Instances | Last edit  | Audited |
   |---|-------|--------|-----------|------------|---------|
   | 1 | BRD   | yes    |         2 | 2026-06-12 | yes     |
   | 2 | PRD   | yes    |         1 | 2026-06-13 | no      |
   | 3 | EARS  | no     |           |            |         |
   | … | …     | …      |           |            |         |
   | 8 | IPLAN | no     |           |            |         |
   ```

4. **Append a one-line summary** — the position counted as "highest layer
   that exists":

   ```text
   Highest layer present: PRD (2 of 8). Latest edited: PRD on 2026-06-13.
   ```

5. **No SDD layout detected** — if zero of the eight layer directories
   exist, do not print an empty table. Print:

   ```text
   No SDD layout detected under <docs_root>.

   To scaffold one, run: /aidoc-flow:project-init
   ```

6. **Stop**. Do not run audits, do not promote layers, do not call other
   skills. This command reports state; it does not change it.

## Error handling

- Not in a git repo: fall back to file mtime for `Last edit`.
- `docs_root` resolves to a path outside the current working directory: still
  scan, but include the absolute path in the header so the user can confirm.
- `.claude/aidoc-flow.config.yaml` exists but is malformed YAML: ignore it,
  use the default `docs/`, print one warning line at the top of the output.
