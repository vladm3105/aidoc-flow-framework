---
title: "Plugin Configuration Reference"
description: Schema and defaults for the optional project-local `.claude/aidoc-flow.config.yaml` consumed by `/aidoc-flow:configure`, `/aidoc-flow:budget`, and `/aidoc-flow:model`.
tags:
  - utility
  - active
custom_fields:
  document_type: reference
  priority: shared
  development_status: active
---

# Plugin Configuration Reference

The plugin works without any configuration. If a project needs to override
defaults — for example, to put the 8-layer tree under `specifications/` instead
of `docs/` — it can drop a `.claude/aidoc-flow.config.yaml` file at the project
root.

The three config commands consume this file:

- `/aidoc-flow:configure` — bulk editor for every key below
- `/aidoc-flow:budget` — guided editor for the `budget.*` keys only
- `/aidoc-flow:model` — guided editor for the `model.*` keys only

Every other plugin skill treats the file as **optional input**: absence means
"use the defaults documented here" and the skill behaves exactly as it does
today.

## File location

`.claude/aidoc-flow.config.yaml` — project-local, relative to the project root
(not the plugin install). A project that never runs `/aidoc-flow:configure`
or its siblings will never have this file, and that is the supported default.

## Schema

```yaml
# Schema version. Bumped only on a breaking format change.
schema: 1

# --- Layout ---------------------------------------------------------------

# Where the 8-layer SDD tree lives, relative to the project root. The
# `/aidoc-flow:status` and `/aidoc-flow:next` commands resolve `docs/0N_<ARTIFACT>/`
# against this prefix, and so does `hooks/sdd-doc-review.sh` when it decides
# which layer an edited document belongs to.
docs_root: docs/

# Where `/aidoc-flow:save-plan` writes implementation plan files. (Mirrors the
# legacy `.claude/CLAUDE.md` "Work Plans Directory" line; both work, this is the
# new home.)
work_plans_dir: work_plans/

# Layers to skip entirely. Subset of the canonical eight; any value outside this
# enum is a config error.
#   BRD | PRD | EARS | BDD | ADR | SPEC | TDD | IPLAN
skip_layers: []

# Output language for generated artifacts. ISO 639-1 code. Defaults to English.
output_language: en

# --- Hook behavior --------------------------------------------------------

# Controls the PostToolUse(Write|Edit) review nudge from
# `hooks/sdd-doc-review.sh`. Always advisory; never blocks the edit.
#   "on"      — nudge with the matching `doc-<layer>-audit` recommendation
#   "off"     — hook still runs but emits nothing
#   "verbose" — also append the structural-lint findings from `sdd_doc_lint`
#
# The hook finds this file by walking UP from the edited file — not from its
# working directory, which is not guaranteed to be the project root. It reads
# `review_hook` and `docs_root` with grep/sed rather than a YAML parser, so it
# keeps working when Python or PyYAML is absent; a value outside the enum is
# ignored and the default applies.
#
# Under "verbose", structural findings additionally require a project that
# adopted the framework: the edited file inside a scaffolded
# `<docs_root>/0N_<ARTIFACT>/` tree, or a project-local
# `framework/registry/LAYER_REGISTRY.yaml` or `.aidoc/` above it. The plugin
# bundles its own registry, so without that gate the linter would resolve one in
# any directory and emit findings in projects that never opted in.
#
# Note: quote "on" and "off". The three config commands parse this file as
# YAML, where unquoted `on`/`off` become the booleans true/false and are
# rejected as a config error. The review hook reads the value textually and
# accepts either form, so an unquoted value still works there — but the two
# readers then disagree about the same file, which is the reason to quote.
review_hook: "on"

# --- Budget (effort knob) -------------------------------------------------
#
# This is a *behavior* knob — it tells the doc-* skills how much work to do per
# artifact. It does NOT cap Claude Code session tokens; the plugin has no token
# meter. See `commands/budget.md` for the full caveat.

budget:
  # max      — multi-pass review, deeper checklists, longer outputs
  # standard — default
  # min      — single-pass, terse, skip optional checks
  profile: standard

  # Optional per-layer override. Same enum as `profile`. Keys are the eight
  # canonical artifact names. Missing keys inherit `profile`.
  # Example: { BRD: max, examples: min }
  profile_per_layer: {}

# --- Model (advisory) -----------------------------------------------------
#
# This is advisory. Plugin commands and skills run on whatever model the Claude
# Code session is set to. The plugin cannot switch it. `/aidoc-flow:model`
# prints copy-paste `/model <id>` commands; the user runs the native command.
# See `commands/model.md` for the full caveat.

model:
  # Recommended model when no per-layer override applies. Use a model id Claude
  # Code accepts in its native `/model <id>` command.
  default: claude-sonnet-4-6

  # Per-layer recommendation map. Keys are canonical artifact names.
  # Example: { BRD: claude-opus-4-7, IPLAN: claude-opus-4-7 }
  per_layer: {}

  # How the layer autopilots surface the per-layer recommendation before
  # drafting. Advisory: the plugin cannot read or switch the session model, so
  # this PRINTS the recommendation (it does not compare) and lets you decide.
  #   warn   — print a one-line recommendation, then proceed (default)
  #   silent — print nothing, just proceed
  #   block  — print, then wait for you to confirm or switch before drafting
  precheck: warn
```

## Defaults summary

A project with no config file behaves as if every value above is set to its
default. The summary:

| Key | Default |
|---|---|
| `schema` | `1` |
| `docs_root` | `docs/` |
| `work_plans_dir` | `work_plans/` |
| `skip_layers` | `[]` |
| `output_language` | `en` |
| `review_hook` | `on` |
| `budget.profile` | `standard` |
| `budget.profile_per_layer` | `{}` |
| `model.default` | `claude-sonnet-4-6` |
| `model.per_layer` | `{}` |
| `model.precheck` | `warn` |

## Enums (single source of truth)

These enums are referenced by command files and the conformance test that
keeps everything in sync:

- **Layer names:** `BRD | PRD | EARS | BDD | ADR | SPEC | TDD | IPLAN`
- **`review_hook`:** `on | off | verbose`
- **`budget.profile`** (and `profile_per_layer` values): `max | standard | min`
- **`model.precheck`:** `warn | silent | block`

## Editing safely

Three commands provide guided flows over this file:

| Command | Scope |
|---|---|
| `/aidoc-flow:configure` | Bulk: every key above. Also supports `configure show` (dump current values) and `configure reset` (restore defaults). |
| `/aidoc-flow:budget` | The `budget.*` subtree only. |
| `/aidoc-flow:model` | The `model.*` subtree only. |

You can also hand-edit the file directly — the commands re-read it on every
invocation. If the file becomes invalid YAML, the next command run will print a
parse error and exit without writing.

## Migration notes

The legacy `Work Plans Directory` line in `.claude/CLAUDE.md` (consumed by the
existing `/aidoc-flow:save-plan` command) remains supported. New projects
should prefer `work_plans_dir` in this file; existing projects with the legacy
line continue working unchanged.
